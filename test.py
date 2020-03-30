import unittest
import socket
import json
import requests

from function_ext_monitor import external_function_monitor
from unittest import mock

PASSING_URL = 'http://passing-url.com/test.json'
NON_EXISTENT_URL = 'http://passing-url-does-not-exist.com/anothertest.json'
EXTRA_DATA_TO_SEND = {'interval': 6, 'foo': 'bar'}


class Counter:
    counter = 1

    @classmethod
    def increment_counter(cls):
        """Just a function that increments a class counter and return it"""
        cls.counter += 1
        return cls.counter


def mocked_requests_post(*args, **kwargs):
    """
    This method will be used by the mock to replace requests.get
    """

    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        @property
        def ok(self):
            if self.status_code == 201:
                return True
            return False

        @property
        def reason(self):
            if self.status_code == 201:
                return 'OK'
            return 'Server Error'

    if args[0] == PASSING_URL:
        return MockResponse({"key1": "value1"}, 201)
    elif args[0] == NON_EXISTENT_URL:
        return MockResponse({"error": "value2"}, 500)

    return MockResponse(None, 404)


class MockProcess:
    def __init__(self, target=lambda x: None, args=(), kwargs={}):
        self.target = target
        self.args = args
        self.kwargs = kwargs

    def start(self):
        self.target(*self.args, **self.kwargs)


@external_function_monitor(PASSING_URL, **EXTRA_DATA_TO_SEND)
def simple_addition(first_number, second_number):
    """
    This function adds the first_number to the second_number
    and returns the sum
    """
    return first_number + second_number


@external_function_monitor(NON_EXISTENT_URL, **EXTRA_DATA_TO_SEND)
def simple_addition_with_misconfigured_decorator(first_number, second_number):
    """
    This function adds the first_number to the second_number
    and returns the sum
    """
    return first_number + second_number


class TestFunctionExtMonitor(unittest.TestCase):
    """
    Tests for the package function-ext-monitor
    """

    def setUp(self) -> None:
        """Initialize some variables"""
        self.first_number = 6
        self.second_number = 9

    @mock.patch('multiprocessing.Process', new=MockProcess)
    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_send_report(self, mock_post):
        """
        The decorator should be able to send a report every time
        the function is called
        """
        simple_addition(self.first_number, self.second_number)
        data_parameter_as_dict = {
            'function_name': 'simple_addition',
            'host_name': socket.gethostname(),
            **EXTRA_DATA_TO_SEND
        }
        self.assertIn(mock.call(PASSING_URL,
                                data=json.dumps(data_parameter_as_dict),
                                headers={'Content-Type': 'application/json'}), mock_post.call_args_list)

    @mock.patch('multiprocessing.Process', new=MockProcess)
    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_failed_server_response(self, mock_post):
        """
        The decorator should raise an exception if the request
        to the reporting server fails
        """
        self.assertRaises(requests.exceptions.HTTPError,
                          simple_addition_with_misconfigured_decorator, self.first_number, self.second_number)

    @mock.patch('multiprocessing.Process', new=MockProcess)
    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_extra_data_dict_with_function_values(self, mock_post):
        """
        The decorator should convert values that are functions in the kwargs of the
        decorator to their return values at the time of when the function runs.
        Good for timestamps
        """
        new_extra_data = {**EXTRA_DATA_TO_SEND, 'counter': lambda: Counter.increment_counter()}

        @external_function_monitor(PASSING_URL, **new_extra_data)
        def another_simple_addition(first_number, second_number):
            """
            Just adds the first number to the second number and returns the sum
            """
            return first_number + second_number

        original_counter = Counter.counter
        for loop in range(1, 4):
            # call the function
            another_simple_addition(self.first_number, self.second_number)
            # the value in counter should have also increased by 1
            data_parameter_as_dict = {
                'function_name': 'another_simple_addition',
                'host_name': socket.gethostname(),
                **EXTRA_DATA_TO_SEND,
                'counter': original_counter + loop
            }
            self.assertIn(mock.call(PASSING_URL,
                                    data=json.dumps(data_parameter_as_dict),
                                    headers={'Content-Type': 'application/json'}), mock_post.call_args_list)


if __name__ == '__main__':
    unittest.main()
