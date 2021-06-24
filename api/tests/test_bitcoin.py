import datetime
import os.path
import unittest
from unittest import mock
import jwt
from freezegun import freeze_time
from api import create_app
from config import Config
from api.rest.bitcoin import file_cached, get_current_rate, token_required


class TestGetCurrentRate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class MockResponse:
            def __init__(self, json, code):
                self._json = json
                self.status_code = code

            def json(self):
                return self._json

        cls._mock_response = MockResponse

    def test_get_current_rate__should_return_rate(self):
        with mock.patch("api.rest.bitcoin.requests.get") as requests_mock:
            requests_mock.return_value = self._mock_response(code=200, json={"bpi": {"UAH": {"rate_float": 100.0}}})
            self.assertEqual(get_current_rate.__wrapped__(), 100.0)

    def test_get_current_rate__should_return_none(self):
        with mock.patch("api.rest.bitcoin.requests.get") as requests_mock:
            requests_mock.return_value = self._mock_response(code=401, json={})
            self.assertIsNone(get_current_rate.__wrapped__())


class TestFileCached(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._file_name = 'test_btc.txt'
        cls._path = os.path.abspath(os.getcwd())

    def setUp(self):
        self._mock = mock.MagicMock()
        self._decorated = file_cached(self._file_name)(self._mock)

    def tearDown(self):
        os.remove(os.path.join(self._path, self._file_name))

    def test_file_cached__should_create_file(self):
        self._mock.return_value = 100.0
        self._decorated()
        self.assertTrue(os.path.exists(os.path.join(self._path, self._file_name)))

    def test_file_cached__should_cache_value(self):
        self._mock.side_effect = [100.0, 200.0]
        self._decorated()
        self.assertEqual(self._decorated(), 100.0)

    def test_file_cached__should_return_new_value(self):
        self._mock.side_effect = [100.0, 200.0]
        with freeze_time("2021-06-24T10:02:44.087285"):
            self.assertEqual(self._decorated(), 100.0)
        self.assertEqual(self._decorated(), 200.0)


class TestTokenRequired(unittest.TestCase):
    def setUp(self):
        self.app = create_app(Config)
        self.client = self.app.test_client()
        self.mock = mock.MagicMock()
        self.decorated = token_required(self.mock)

    def test_token_required__should_return_login_message(self):
        with self.app.test_request_context():
            expected = {'message': 'a valid token is missing'}
            self.assertEqual(self.decorated(), expected)

    def test_token_required__should_return_token_invalid_message(self):
        with self.app.test_request_context(headers={"x-access-tokens": "test"}):
            expected = {'message': 'token is invalid'}
            self.assertEqual(self.decorated(), expected)

    def test_token_required__should_return_func_value(self):
        self.mock.return_value = 100.0
        test_token = jwt.encode({'email': 'email', 'exp': datetime.datetime.utcnow() + datetime.timedelta(
            minutes=30)}, Config.SECRET_KEY)
        with self.app.test_request_context(headers={"x-access-tokens": test_token}):
            self.assertEqual(self.decorated(), 100.0)


class TestBitcoinPrice(unittest.TestCase):
    def setUp(self):
        self.app = create_app(Config)
        self.client = self.app.test_client()

    def test_bitcoin_price__should_return_login_message(self):
        test_token = jwt.encode({'email': 'email', 'exp': datetime.datetime.utcnow() + datetime.timedelta(
            minutes=30)}, Config.SECRET_KEY)

        with mock.patch("api.rest.bitcoin.get_current_rate") as patched_get_rate:
            patched_get_rate.return_value = None
            response = self.client.get('/btcRate', headers={"x-access-tokens": test_token})
            self.assertEqual(response.status_code, 503)

    def test_bitcoin_price__should_return_rate(self):
        test_token = jwt.encode({'email': 'email', 'exp': datetime.datetime.utcnow() + datetime.timedelta(
            minutes=30)}, Config.SECRET_KEY)

        with mock.patch("api.rest.bitcoin.get_current_rate") as patched_get_rate:
            patched_get_rate.return_value = 100.0
            response = self.client.get('/btcRate', headers={"x-access-tokens": test_token})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {'rate': 100.0})
