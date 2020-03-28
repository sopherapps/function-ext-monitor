# function-ext-monitor

This package provides a decorator to wrap around a function so that a report is sent to external server every time function runs.
**under heavy development**

## Dependencies

- [Requests](https://requests.readthedocs.io/en/master/)

## How to install

- Run the command below in your terminal

  ```bash
  pip install function-ext-monitor
  ```

## How to use

- Given that the function you wish to monitor is the `simple_addition` function in the code below,here is how you would go about it.

  ```python
  from function_ext_monitor import external_function_monitor

  EXTRA_DATA_TO_SEND = {
      # maybe how often do you expect this function to be called
      'interval_in_seconds': 7,
      # maybe who wrote it
      'author': 'John Doe',
      # even functions can be added to dynamically
      # generate values when the function is called
      'timestamp': lambda _: datetime.datetime.now(),
      'headers': {
          # Any custom headers. Again, feel free to pass in a function
          # to generate headers on the fly,
          'Authorization': 'Bearer your-auth-token',
        }
        ....
    }

    @external_function_monitor('http://endpoint-to-send-data-to', **EXTRA_DATA_TO_SEND)
    def simple_addition(first_number, second_number):
        """
        This function adds the first_number to the second_number
        and returns the sum
        """
        return first_number + second_number
  ```

  **Note**

  - By default, the decorator includes the name of the computer and the name of the function in the data sent to the remote endpoint.
  - It also adds `'Content-Type': 'application/json'` to the headers
  - It sends the data by spinning up a separate process so that interference with the running program is minimal
  - Every time the function it decorates (in the above example `simple_addition`) runs, a POST request is sent the remote server specified in the first argument. It is upto the developer to decide whether they will overwrite the existing record for that function or to keep a continuously growing log of records on that function.

## License

Copyright (c) 2020 Martin Ahindura Licensed under the [MIT License](./LICENSE)
