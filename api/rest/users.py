import datetime
import json
import jwt
from passlib.hash import argon2
from flask_restful import Resource, abort, reqparse
from config import Config
parser = reqparse.RequestParser()
parser.add_argument("email", type=str)
parser.add_argument("password", type=str)


def hash_password(password):
    """
    Create password hash
    :param password: password to hash
    :return: password hash
    """
    return argon2.hash(password)


def verify_password(password, password_hash):
    """
    Verifies password with password hash
    :param password: password
    :param password_hash: password hash
    :return: True or False
    """
    return argon2.verify(password, password_hash)


def get_users():
    """
    Get users data from file
    :return: dict with user data
    """
    try:
        with open(Config.USERS_FILE_NAME, 'r') as file:
            users = json.load(file)
    except (IOError, ValueError):
        users = {}
    return users


def save_users(users):
    """
    Save users data into file
    :param users: dict with users
    :return: None
    """
    with open(Config.USERS_FILE_NAME, 'w') as file:
        json.dump(users, file)


class RegisterUser(Resource):
    """
    Registration endpoint API
    """

    def __init__(self):
        args = parser.parse_args()
        self.email = args.get("email")
        self.password = args.get("password")

        if not self.email or not self.password:
            abort(400, message="You should specify email and password!")

        self.password_hash = hash_password(self.password)
        self.users = get_users()

    def post(self):
        if self.email in self.users:
            abort(409, message="User with such email already exist!")

        self.users[self.email] = self.password_hash
        save_users(self.users)

        return {"message": "User created"}, 201


class LoginUser(Resource):
    """
    Login endpoint API
    """

    def __init__(self):
        args = parser.parse_args()
        self.email = args.get("email")
        self.password = args.get("password")

        if not self.email or not self.password:
            abort(400, message="You should specify email and password!")

        self.users = get_users()

    def post(self):

        if self.email not in self.users:
            abort(404, message="User doesn't exist!")

        if verify_password(self.password, self.users.get(self.email)):
            token = jwt.encode({'email': self.email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(
                minutes=30)}, Config.SECRET_KEY)
            return {'token': token}

        abort(400, message="Wrong password!")
