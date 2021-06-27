import os
from datetime import timedelta


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    BITCOIN_API_URL = "https://api.coindesk.com/v1/bpi/currentprice/UAH.json"
    USERS_FILE_NAME = 'users.txt'
    BTC_CACHE_FILE_NAME = 'btc_price.txt'
    CACHED_TIME = timedelta(minutes=10)
