from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.get("https://www.youtube.com/")
driver.save_screenshot('/Users/brau/Documents/Maestría/tesis/dailytrend/screen.png')
element_text = driver.find_element_by_id("title").text
print(element_text)