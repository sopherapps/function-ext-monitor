import inspect
import socket
import json
import requests
import multiprocessing

__version__ = "0.0.5"


def get_class_that_defined_method(method):
    """
    Returns the class that defined the method
    Got implementation from stackoverflow
    http://stackoverflow.com/a/25959545/3903832
    """
    # for bound methods
    if inspect.ismethod(method):
        for cls in inspect.getmro(method.__self__.__class__):
            if cls.__dict__.get(method.__name__) is method:
                return cls.__name__
        method = method.__func__  # fallback to __qualname__ parsing

    # for unbound methods
    if inspect.isfunction(method):
        cls = getattr(inspect.getmodule(method),
                      method.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0])
        if isinstance(cls, type):
            return cls.__name__


def convert_functions_in_dict_to_values(dict_to_convert):
    """
    When passed a dictionary that contains functions as some of its
    values, it converts them to their responses
    """
    return {key: value() if hasattr(value, '__call__') else value for key, value in dict_to_convert.items()}


def send_report(report_server_url, data_as_dict={}, headers={}):
    """
    Makes a POST request to the report server. Ideally,
    the server should be able to upsert the old record
    because this POST request will be made every time the function is run
    """
    processed_data = convert_functions_in_dict_to_values(data_as_dict)
    response = requests.post(report_server_url, data=json.dumps(processed_data),
                             headers={'Content-Type': 'application/json', **headers})
    if not response.ok:
        raise requests.exceptions.HTTPError('Sending report failed. \nresponse:\n %s' % response.reason)


def external_function_monitor(report_server_url, headers={}, **data):
    def decorator(function):
        def wrapper(*args, **kwargs):
            """the wrapper function"""
            function_name = function.__name__
            class_name = get_class_that_defined_method(function)

            if class_name:
                function_name = '%s.%s' %(class_name, function_name)

            host_name = socket.gethostname()
            report_data = {'function_name': function_name, 'host_name': host_name, **data}
            # send_report(report_server_url, data_as_dict=report_data)
            reporting = multiprocessing.Process(target=send_report, args=(report_server_url,),
                                                kwargs={'data_as_dict': report_data, 'headers': headers})
            reporting.start()
            return function(*args, **kwargs)

        return wrapper

    return decorator
