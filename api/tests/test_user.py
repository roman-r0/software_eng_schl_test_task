import unittest
import jwt
import json
import os
from config import Config
from api import create_app
from api.rest.users import save_users, get_users, RegisterUser, LoginUser


class TestGetUsers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.file_path = os.path.join(os.path.abspath(os.getcwd()), Config.USERS_FILE_NAME)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.file_path)

    def test_get_users__should_return_empty_dict(self):
        self.assertEqual(get_users(), {})

    def test_get_users__should_return_users_dict(self):
        expected = {'email': 'password'}
        with open(self.file_path, 'w') as file:
            json.dump(expected, file)
        self.assertEqual(get_users(), expected)


class TestSaveUsers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.file_path = os.path.join(os.path.abspath(os.getcwd()), Config.USERS_FILE_NAME)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.file_path)

    def test_save_users__should_create_file(self):
        save_users({})
        self.assertTrue(os.path.exists(self.file_path))

    def test_save_users__should_save_data_into_file(self):
        expected = {'email': 'password'}
        save_users(expected)
        with open(self.file_path) as file:
            self.assertEqual(json.load(file), expected)


class TestRegisterUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(Config)
        cls.client = cls.app.test_client()
        cls.file_path = os.path.join(os.path.abspath(os.getcwd()), Config.USERS_FILE_NAME)

    def tearDown(self):
        try:
            os.remove(self.file_path)
        except FileNotFoundError:
            pass

    def test_register_user__should_register_user(self):
        response = self.client.post("/user/create", data={'email': 'email', 'password': 'password'})
        self.assertEqual(response.status_code, 201)

    def test_register_user__should_return_400(self):
        response = self.client.post("/user/create")
        self.assertEqual(response.status_code, 400)

    def test_register_user__should_return_409(self):
        self.client.post("/user/create", data={'email': 'email', 'password': 'password'})
        response = self.client.post("/user/create", data={'email': 'email', 'password': 'password'})
        self.assertEqual(response.status_code, 409)


class TestLoginUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(Config)
        cls.client = cls.app.test_client()
        cls.file_path = os.path.join(os.path.abspath(os.getcwd()), Config.USERS_FILE_NAME)

    def tearDown(self):
        try:
            os.remove(self.file_path)
        except FileNotFoundError:
            pass

    def test_login_user__should_return_400(self):
        response = self.client.post("/user/login")
        self.assertEqual(response.status_code, 400)

    def test_login_user__should_return_404(self):
        response = self.client.post("/user/login", data={'email': 'email', 'password': 'password'})
        self.assertEqual(response.status_code, 404)

    def test_login_user__should_return_400_for_incorrect_password(self):
        self.client.post("/user/create", data={'email': 'email', 'password': 'password'})
        response = self.client.post("/user/login", data={'email': 'email', 'password': 'password1'})
        self.assertEqual(response.status_code, 400)

    def test_login_user__should_return_token(self):
        self.client.post("/user/create", data={'email': 'email', 'password': 'password'})
        response = self.client.post("/user/login", data={'email': 'email', 'password': 'password'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)
