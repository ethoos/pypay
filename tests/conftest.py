import pytest


class MockResponse(object):
    """
    Mock a response object from the requests library
    """
    
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code


class MockResponseFactory(object):
    """
    Easily generate mock response objects
    """
    
    def response(self, text, status_code=200):
        return MockResponse(text, status_code)


@pytest.fixture(scope='session')
def mrf():
    return MockResponseFactory()
