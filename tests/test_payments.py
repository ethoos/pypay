import pypay
import pytest
try:
    from unittest import mock # Python 3
except ImportError:
    import mock


class TestPaypalPayments(object):
    
    def test_to_paypal_response_returns_paypal_response_with_correct_attributes(self):
        payments = pypay.payments.PaypalPayments()
        payments.confirmed = True
        payments.details = {'first_name': 'Joe Black'}
        resp = payments.to_paypal_response()
        assert isinstance(resp, pypay.payments.PaypalResponse)
        assert resp.confirmed is True
        assert resp.details == {'first_name': 'Joe Black'}


class TestPaypalResponse(object):
    
    def test_args_are_set_as_properties(self):
        resp = pypay.payments.PaypalResponse('confirmed', 'details')
        assert resp.confirmed == 'confirmed'
        assert resp.details == 'details'


class TestPaypalPDT(object):
    
    def test_string_transaction_id_and_token_are_accepted(self):
        pdt = pypay.payments.PaypalPDT('id', 'token')
        assert pdt.transaction_id == 'id'
        assert pdt.identity_token == 'token'
    
    def test_non_string_transaction_id_raises_invalid_paypal_data(self):
        with pytest.raises(pypay.exceptions.InvalidPaypalData):
            pdt = pypay.payments.PaypalPDT(123, 'token')
    
    def test_non_string_indentity_token_raises_invalid_paypal_data(self):
        with pytest.raises(pypay.exceptions.InvalidPaypalData):
            pdt = pypay.payments.PaypalPDT('id', 123)
    
    def test_send_confirmation_posts_correct_params_and_defaults_to_live_endpoint(self, mrf):
        mock_response = mrf.response('SUCCESS')
        mock_post = mock.MagicMock(return_value=mock_response)
        pdt = pypay.payments.PaypalPDT('id', 'token')
        with mock.patch('pypay.payments.requests.post', mock_post):
            pdt.send_confirmation()
        mock_post.assert_called_with(pdt.live_endpoint, params={'cmd': '_notify-synch', 'at': 'token', 'tx': 'id'})
    
    def test_send_confirmation_uses_sandbox_endpoint_when_sandbox_true(self, mrf):
        mock_response = mrf.response('SUCCESS')
        mock_post = mock.MagicMock(return_value=mock_response)
        pdt = pypay.payments.PaypalPDT('id', 'token', sandbox=True)
        with mock.patch('pypay.payments.requests.post', mock_post):
            pdt.send_confirmation()
        mock_post.call_args[0] == (pdt.sandbox_endpoint,)
    
    def test_send_confirmation_sets_response_when_status_is_200(self, mrf):
        mock_response = mrf.response('SUCCESS')
        mock_post = mock.MagicMock(return_value=mock_response)
        pdt = pypay.payments.PaypalPDT('id', 'token')
        with mock.patch('pypay.payments.requests.post', mock_post):
            pdt.send_confirmation()
        assert pdt.response == mock_response
    
    def test_send_confirmation_raises_request_error_when_response_not_200(self, mrf):
        mock_response = mrf.response('SUCCESS', status_code=404)
        mock_post = mock.MagicMock(return_value=mock_response)
        pdt = pypay.payments.PaypalPDT('id', 'token')
        with mock.patch('pypay.payments.requests.post', mock_post):
            with pytest.raises(pypay.exceptions.RequestError):
                pdt.send_confirmation()
    
    def test_send_confirmation_raises_request_error_when_requests_raises_exception(self, mrf):
        mock_response = mrf.response('SUCCESS')
        mock_post = mock.MagicMock()
        mock_post.side_effect = pypay.payments.requests.exceptions.ConnectionError('Broken')
        pdt = pypay.payments.PaypalPDT('id', 'token')
        with mock.patch('pypay.payments.requests.post', mock_post):
            with pytest.raises(pypay.exceptions.RequestError) as e:
                pdt.send_confirmation()
                assert e.args[0] == 'Broken'
    
    def test_process_response_sets_confirmed_for_success(self, mrf):
        pdt = pypay.payments.PaypalPDT('id', 'token')
        pdt.response = mrf.response('SUCCESS')
        pdt.process_response()
        assert pdt.confirmed is True
    
    def test_process_response_sets_not_confirmed_for_fail(self, mrf):
        pdt = pypay.payments.PaypalPDT('id', 'token')
        pdt.response = mrf.response('FAIL')
        pdt.process_response()
        assert pdt.confirmed is False
    
    def test_process_response_splits_response_data_to_dict(self, mrf):
        pdt = pypay.payments.PaypalPDT('id', 'token')
        pdt.response = mrf.response('SUCCESS\nfirst_name=Joe\n\nitem_number=\n')
        pdt.process_response()
        assert isinstance(pdt.details, dict)
        assert pdt.details == {'first_name': 'Joe', 'item_number': ''}
    
    def test_process_response_handles_urlencoded_chars_in_response_data(self, mrf):
        pdt = pypay.payments.PaypalPDT('id', 'token')
        pdt.response = mrf.response('SUCCESS\nfirst_name=Joe+Black\nlast_name=De%27audney')
        pdt.process_response()
        assert pdt.details == {'first_name': 'Joe Black', 'last_name': 'De\'audney'}


class TestPaypalIPN(object):
    
    def test_string_for_query_params_is_accepted(self):
        ipn = pypay.payments.PaypalIPN('tx=id&name=Joe')
        assert ipn.query_params == 'tx=id&name=Joe'
    
    def test_dict_for_query_params_is_accepted_and_urlencoded(self):
        ipn = pypay.payments.PaypalIPN({'tx': 'id', 'name': 'Joe De\'jure'})
        assert ipn.query_params == 'name=Joe+De%27jure&tx=id' or ipn.query_params == 'tx=id&name=Joe+De%27jure'
    
    def test_non_string_or_dict_query_params_raises_invalid_paypal_data(self):
        with pytest.raises(pypay.exceptions.InvalidPaypalData):
            ipn = pypay.payments.PaypalIPN(123)
    
    def test_send_confirmation_builds_correct_post_url_and_defaults_to_live_endpoint(self, mrf):
        mock_response = mrf.response('VERIFIED')
        mock_post = mock.MagicMock(return_value=mock_response)
        query = 'payment_status=Confirmed'
        ipn = pypay.payments.PaypalIPN(query)
        with mock.patch('pypay.payments.requests.post', mock_post):
            ipn.send_confirmation()
        post_url = '{0}?{1}&{2}'.format(ipn.live_endpoint, 'cmd=_notify-validate', query)
        mock_post.assert_called_with(post_url, headers={'content_type': 'x-www-form-urlencoded'})
    
    def test_send_confirmation_uses_sandbox_endpoint_when_sandbox_true(self, mrf):
        mock_response = mrf.response('VERIFIED')
        mock_post = mock.MagicMock(return_value=mock_response)
        ipn = pypay.payments.PaypalIPN('payment_status=Confirmed', sandbox=True)
        with mock.patch('pypay.payments.requests.post', mock_post):
            ipn.send_confirmation()
        mock_post.call_args[0][0].split('?')[0] == ipn.sandbox_endpoint
    
    def test_send_confirmation_sets_response_when_status_is_200(self, mrf):
        mock_response = mrf.response('VERIFIED')
        mock_post = mock.MagicMock(return_value=mock_response)
        ipn = pypay.payments.PaypalIPN('payment_status=Confirmed')
        with mock.patch('pypay.payments.requests.post', mock_post):
            ipn.send_confirmation()
        assert ipn.response == mock_response
    
    def test_send_confirmation_raises_exception_when_response_not_200(self, mrf):
        mock_response = mrf.response('VERIFIED', status_code=404)
        mock_post = mock.MagicMock(return_value=mock_response)
        ipn = pypay.payments.PaypalIPN('payment_status=Confirmed')
        with mock.patch('pypay.payments.requests.post', mock_post):
            with pytest.raises(pypay.exceptions.RequestError):
                ipn.send_confirmation()
    
    def test_send_confirmation_raises_exception_when_requests_raises_exception(self, mrf):
        mock_response = mrf.response('VERIFIED')
        mock_post = mock.MagicMock()
        mock_post.side_effect = pypay.payments.requests.exceptions.ConnectionError('Broken')
        ipn = pypay.payments.PaypalIPN('payment_status=Confirmed')
        with mock.patch('pypay.payments.requests.post', mock_post):
            with pytest.raises(pypay.exceptions.RequestError) as e:
                ipn.send_confirmation()
                assert e.args[0] == 'Broken'
    
    def test_process_response_sets_confirmed_for_success(self, mrf):
        ipn = pypay.payments.PaypalIPN('payment_status=Confirmed')
        ipn.response = mrf.response('VERIFIED')
        ipn.process_response()
        assert ipn.confirmed is True
    
    def test_process_response_sets_not_confirmed_for_fail(self, mrf):
        ipn = pypay.payments.PaypalIPN('payment_status=Confirmed')
        ipn.response = mrf.response('INVALID')
        ipn.process_response()
        assert ipn.confirmed is False
    
    def test_process_response_splits_query_string_to_dict(self, mrf):
        ipn = pypay.payments.PaypalIPN('first_name=Joe&item_number=')
        ipn.process_response()
        assert isinstance(ipn.details, dict)
        assert ipn.details == {'first_name': 'Joe', 'item_number': ''}
    
    def test_process_response_handles_urlencoded_chars_in_query_string(self, mrf):
        ipn = pypay.payments.PaypalIPN('first_name=Joe+Black&last_name=De%27audney')
        ipn.process_response()
        assert ipn.details == {'first_name': 'Joe Black', 'last_name': 'De\'audney'}
