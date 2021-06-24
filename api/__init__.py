from flask_restful import Api
from flask import Flask
from config import Config


def create_app(config_class=Config):
    """
    Function for creating an exemplar of flask app
    :param config_class: config class with properties of app
    :return: created app
    """

    app = Flask(__name__)
    app.config.from_object(config_class)
    api = Api(app)

    from api.rest.users import LoginUser, RegisterUser
    from api.rest.bitcoin import BitcoinPrice

    api.add_resource(RegisterUser, '/user/create')
    api.add_resource(LoginUser, '/user/login')
    api.add_resource(BitcoinPrice, '/btcRate')

    return app
