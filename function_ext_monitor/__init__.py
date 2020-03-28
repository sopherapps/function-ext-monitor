import socket
import json
import requests
import multiprocessing

__version__ = "0.0.3"


def send_report(report_server_url, data_as_dict={}, headers={}):
    """
    Makes a POST request to the report server. Ideally,
    the server should be able to upsert the old record
    because this POST request will be made every time the function is run
    """
    response = requests.post(report_server_url, data=json.dumps(data_as_dict),
                             headers={'Content-Type': 'application/json', **headers})
    if not response.ok:
        raise requests.exceptions.HTTPError('Sending report failed. \nresponse:\n %s' % response.reason)


def external_function_monitor(report_server_url, headers={}, **data):
    def decorator(function):
        def wrapper(*args, **kwargs):
            """the wrapper function"""
            function_name = function.__name__
            host_name = socket.gethostname()
            report_data = {'function_name': function_name, 'host_name': host_name, **data}
            # send_report(report_server_url, data_as_dict=report_data)
            reporting = multiprocessing.Process(target=send_report, args=(report_server_url,),
                                                kwargs={'data_as_dict': report_data, 'headers': headers})
            reporting.start()
            return function(*args, **kwargs)

        return wrapper

    return decorator
