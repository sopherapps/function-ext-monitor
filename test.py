import unittest
from unittest import mock

from main import external_function_monitor

PASSING_URL = 'http://passing-url.com/test.json'
NON_EXISTENT_URL = 'http://passing-url-does-not-exist.com/anothertest.json'


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

        def ok(self):
            if self.status_code == 201:
                return True
            return False

    if args[0] == PASSING_URL:
        return MockResponse({"key1": "value1"}, 201)
    elif args[0] == NON_EXISTENT_URL:
        return MockResponse({"error": "value2"}, 500)

    return MockResponse(None, 404)


@external_function_monitor(PASSING_URL, interval=6, foo='bar')
def simple_addition(first_number, second_number):
    """
    This function adds the first_number to the second_number
    and returns the sum
    """
    return first_number + second_number


@external_function_monitor(NON_EXISTENT_URL, interval=6, foo='bar')
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

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_send_report(self, mock_post):
        """
        The decorator should be able to send a report every time
        the function is called
        """
        first_number = 6
        second_number = 9

        # self.assertRaises(Exception, simple_addition_with_misconfigured_decorator(first_number, second_number))

        simple_addition(first_number, second_number)

        self.assertIn(mock.call(PASSING_URL), mock_post.call_args_list)


if __name__ == '__main__':
    unittest.main()
