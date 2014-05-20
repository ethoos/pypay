from .exceptions import InvalidPaypalData, RequestError
from six.moves import urllib
import requests
import six


class PaypalPayments(object):
    """
    Base Paypal payments class. Defines endpoints and allows a processed
    Paypal response to be conferted into a PaypalResponse object
    """
    
    live_endpoint = 'https://www.paypal.com/cgi-bin/webscr'
    sandbox_endpoint = 'https://www.sandbox.paypal.com/cgi-bin/webscr'
    
    sandbox = False
    response = None
    confirmed = False
    details = None
    
    def send_confirmation(self):
        raise NotImplementedError()
    
    def process_response(self):
        raise NotImplementedError()
    
    def to_paypal_response(self):
        return PaypalResponse(self.confirmed, self.details)


class PaypalResponse(object):
    """
    Wrapper around Paypal response data for more consistent api
    """
    
    def __init__(self, confirmed, details):
        self.confirmed = confirmed
        self.details = details


class PaypalPDT(PaypalPayments):
    """
    For a given TransactionID confirm a payment via Paypal PDT and
    process the response
    """
    
    def __init__(self, transaction_id, identity_token, sandbox=False):
        if not transaction_id or not isinstance(transaction_id, six.string_types):
            raise InvalidPaypalData('{0} is not a valid Paypal TransactionID'.format(transaction_id))
        if not identity_token or not isinstance(identity_token, six.string_types):
            raise InvalidPaypalData('{0} is not a valid Paypal identity token'.format(identity_token))
        self.transaction_id = transaction_id
        self.identity_token = identity_token
        self.sandbox = sandbox
    
    def send_confirmation(self):
        endpoint = self.live_endpoint if not self.sandbox else self.sandbox_endpoint
        params = {'cmd': '_notify-synch', 'tx': self.transaction_id, 'at': self.identity_token}
        try:
            self.response = requests.post(endpoint, params=params)
        except requests.exceptions.RequestException as e:
            raise RequestError(e.args[0])
        if self.response.status_code != 200:
            raise RequestError('Paypal returned a {0} status'.format(self.response.status_code))
    
    def process_response(self):
        if self.response:
            data = self.response.text.strip().split('\n')
            self.confirmed = True if data[0].strip() == 'SUCCESS' else False
            self.details = {}
            for field in data[1:]:
                if field:
                    name, value = field.split('=', 1)
                    self.details[name] = urllib.parse.unquote_plus(value.strip())


class PaypalIPN(PaypalPayments):
    """
    For a given query string confirm a payment via Paypal IPN and
    process the response
    """
    
    def __init__(self, query_string, sandbox=False):
        if not isinstance(query_string, six.string_types):
            raise InvalidPaypalData('{0} is not a valid IPN query string'.format(query_string))
        self.query_string = query_string
        self.sandbox = sandbox
    
    def send_confirmation(self):
        endpoint = self.live_endpoint if not self.sandbox else self.sandbox_endpoint
        headers = {'content_type': 'x-www-form-urlencoded'}
        post_url = '{0}?{1}&{2}'.format(endpoint, 'cmd=_notify-validate', self.query_string)
        try:
            self.response = requests.post(post_url, headers=headers)
        except requests.exceptions.RequestException as e:
            raise RequestError(e.args[0])
        if self.response.status_code != 200:
            raise RequestError('Paypal returned a {0} status'.format(self.response.status_code))
    
    def process_response(self):
        if self.response:
            if self.response.text.strip() == 'VERIFIED':
                self.confirmed = True
            else:
                self.confirmed = False
        self.details = dict((k, v[0].strip()) for (k, v) in urllib.parse.parse_qs(self.query_string, keep_blank_values=True).items()) # no dict comprehensions in Python 2.6 :(
