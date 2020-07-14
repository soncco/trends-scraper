import collections
import logging
import time
import pika
import uuid
import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from config import config as settings
from db import engine
from util import clean_title, get_number_tweets, get_utc

class Scraper:
    def __init__(self, *args, **kwargs):
        self.set_logger()

        self.registry = collections.deque(maxlen=1000)

        self.setup_rmq()

        if settings()['driver'] == 'chrome':
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        else:
            self.driver = webdriver.Firefox(executable_path=settings()['firefox_driver_path'])


    def set_logger(self):
        self.logger = logging.getLogger('scraper')
        self.logger.setLevel(logging.INFO)

        fh = logging.FileHandler(settings()['log_path'])

        fh.setLevel(logging.INFO)

        formatstr = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(formatstr)

        fh.setFormatter(formatter)

        self.logger.addHandler(fh)

    def setup_rmq(self):
        try:
            if settings()['rmq_username'] and settings()['rmq_password']:
                self.rmq = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=settings()['rmq_host'],
                        port=settings()['rmq_port'],
                        credentials=pika.credentials.PlainCredentials(
                            settings()['rmq_username'], settings()['rmq_password'])))
            else:
                self.rmq = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=settings()['rmq_host'],
                        port=settings()['rmq_port']
                    )
                )
            self.rmq_channel = self.rmq.channel()
            self.rmq_channel.queue_declare(
                queue=settings()['rmq_queue'], durable=True)
        except Exception as error:
            self.logger.error(
                "Failed to connect to RabbitMQ, exiting: %s" % error)

    def login(self):
        self.logger.info('performing login')
        self.driver.get(settings()['twitter_login_url'])

        time.sleep(2)
        self.driver.save_screenshot('login.png')
        username_field = self.driver.find_element_by_name('session[username_or_email]')
        password_field = self.driver.find_element_by_name('session[password]')

        username_field.send_keys(settings()['twitter_username'])
        time.sleep(1)

        password_field.send_keys(settings()['twitter_password'])
        time.sleep(1)

        my_button = self.driver.find_element_by_xpath("//div[@data-testid='LoginForm_Login_Button']")
        my_button.click()

        time.sleep(5)
        self.driver.save_screenshot('after_login.png')

        try:
            time.sleep(2)
            self.driver.save_screenshot('login-again.png')
            username_field = self.driver.find_element_by_name('session[username_or_email]')
            password_field = self.driver.find_element_by_name('session[password]')

            username_field.send_keys(settings()['twitter_username'])
            time.sleep(1)

            password_field.send_keys(settings()['twitter_password'])
            time.sleep(1)

            my_button = self.driver.find_element_by_xpath("//div[@data-testid='LoginForm_Login_Button']")
            my_button.click()

            time.sleep(5)
        except:
            self.logger.info('No login again')

        try:
            challenge = self.driver.find_element_by_id('challenge_response')
            challenge.send_keys(settings()['twitter_mail'])

            time.sleep(1)
            self.driver.save_screenshot('verification.png')

            button = self.driver.find_element_by_id('email_challenge_submit')
            button.click()
            self.logger.info("Twitter verification")
        except:
            self.logger.info("No verification")

    def enqueue(self, id):
        if not self.rmq.is_open:
            self.setup_rmq()

        self.rmq_channel.basic_publish(
            exchange='',
            routing_key=settings()['rmq_queue'],
            body=id,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

    def scrape(self):
        time.sleep(5)
        self.driver.save_screenshot('columns.png')
        
        try:
            element_present = EC.presence_of_element_located((By.CLASS_NAME, 'column'))
            
        except TimeoutException:
            self.logger.warning("Timed out waiting for page to load")
            return

        self.logger.info('scraping')

        columns = self.driver.find_elements_by_class_name('column')

        for column in columns:
            title_container = column.find_element_by_xpath(".//div[@data-testid='filterMessage']")
            trends = column.find_elements_by_xpath(".//div[@data-testid='trend']")

            df = pd.DataFrame(index=np.arange(0, len(trends)),
                columns=['location', 'hashtag', 'tweets_counter', 'position', 'trend_date'])

            place = clean_title(title_container.text)
            
            for key, trend in enumerate(trends):
                uid = uuid.uuid4()
                ht_container = trend.find_element_by_xpath(".//a[@data-testid='trendLink']")
                
                try:
                    count_container = trend.find_element_by_xpath(".//span[@data-testid='trendDescription']")
                except NoSuchElementException:
                    count_container = None

                count = get_number_tweets(count_container.text) if count_container is not None else 0

                trend_date = get_utc(settings()['places'][place]['tz'])

                df.loc[key] = [place, ht_container.text, count, key+1, trend_date]

                self.enqueue(uid.hex)

            self.save(df)
            print(df)
                
            print('============\n\n')

    def save(self, df):
        df.to_sql('trends', con=engine(), if_exists='append', index=False)

    def run(self):
        self.login()
        start_time = time.time()
        while 1:
            try:
                self.scrape()
            except Exception as e:
                self.logger.error('scrape() error: %s' % str(e))
            self.rmq.sleep(settings()['interval'] - (
                (time.time() - start_time) % settings()['interval']))
    

if __name__ == "__main__":
    scraper = Scraper()
    scraper.run()
