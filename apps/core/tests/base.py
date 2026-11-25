import pytest


class PytestBase:
    """
    Base test class providing database access fixture for Pytest.
    """
    pytestmark = pytest.mark.django_db