import functools
import time

import pytest


NULLABLE = {"blank": True, "null": True}


class PytestBase:
    pytestmark = pytest.mark.django_db


def try_it(max_attempts, timeout, exceptions):
    """
    This is a decorator for making multiple attempts to run some code with a timeouts.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        raise e
                    time.sleep(timeout)

        return wrapper

    return decorator


def time_it(label="TimeIt"):
    """
    This is a decorator for measure the execution time of some code.
    Example usage:
    @time_it("Label")
    def my_function():
        # some code
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            print(f"{label} ({func.__name__}) {duration:.4f}s")
            return result

        return wrapper

    return decorator


class TimeIt:
    """
    This is a context manager for measure the execution time of some code.
    Example usage:
    with TimeIt("Label"):
        # some code
    """

    def __init__(self, label="TimeIt"):
        self.label = label

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        print(f"{self.label}: {self.duration:.4f}s")
