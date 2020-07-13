from contextlib import suppress
import sqlalchemy
from datetime import datetime
from dateutil import *
from dateutil.tz import *

def clean_title(title):
    return title.replace('Trends for ', '').strip()

def get_number_tweets(number):
    thousand = 1
    million = 1
    number = number.replace(' Tweets', '')
    number = number.split('K')

    with suppress(Exception):
        if number[1] is not None:
            thousand = 1000
        

    number = number[0].split('M')

    with suppress(Exception):
        if number[1] is not None:
            million = 1000000        

    number = number[0].replace(',', '')

    return int(float(number) * thousand * million)

def get_utc(utc):
    utc_zone = tz.gettz(utc)
    local_zone = tz.tzlocal()
    local_time = datetime.now()
    utc_time = local_time.astimezone(utc_zone)
    return utc_time
