import requests
import json
import jwt
from functools import wraps
from datetime import datetime, timedelta
from flask import abort, request
from flask_restful import Resource
from config import Config


def file_cached(file_name):
    """
    Decorator to cache BTC price into file
    :param file_name: name of file to cache
    :return: deco
    """
    def decorator(func):
        try:
            with open(file_name, 'r') as file:
                cache = json.load(file)
        except (IOError, ValueError):
            cache = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            if cache:
                index = str(len(cache) - 1)
                cashed_time = datetime.strptime(cache[index].get('time'), '%Y-%m-%dT%H:%M:%S.%f')
                if cashed_time + timedelta(minutes=10) > datetime.now():
                    return cache[index].get('price')
            item = {
                'time': datetime.now().isoformat(),
                'price': func(*args, **kwargs)
            }
            cache[str(len(cache))] = item
            with open(file_name, 'w') as file:
                json.dump(cache, file)
            return item['price']

        return wrapper

    return decorator


@file_cached(Config.BTC_CACHE_FILE_NAME)
def get_current_rate():
    """
    Obtain current BTC - UAH rate
    :return: rate or None
    """
    url = Config.BITCOIN_API_URL
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['bpi']['UAH']['rate_float']
    return None


def token_required(f):
    """
    Decorator for token required authentication
    :param f: function
    :return: deco
    """
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return {'message': 'a valid token is missing'}

        try:
            jwt.decode(token, Config.SECRET_KEY, algorithms="HS256")
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, jwt.exceptions.DecodeError):
            return {'message': 'token is invalid'}

        return f(*args, **kwargs)

    return decorator


class BitcoinPrice(Resource):
    method_decorators = {'get': [token_required]}

    def get(self):
        """
        API GET BTC rate
        :return: rate in json format
        """
        rate = get_current_rate()
        if rate:
            return {"rate": rate}
        else:
            abort(503)
