import pypay
try:
    from unittest import mock # Python 3
except ImportError:
    import mock


class TestPDTConfirmAPI(object):
    
    def test_pdt_confirm_calls_paypal_pdt_with_id_and_token_args_and_sandbox_false(self):
        mock_paypal_pdt = mock.MagicMock()
        with mock.patch('pypay.api.PaypalPDT', mock_paypal_pdt):
            response = pypay.pdt_confirm('id', 'token')
        mock_paypal_pdt.assert_called_with('id', 'token', sandbox=False)
    
    def test_pdt_confirm_returns_a_paypal_response_object_with_processed_data(self, mrf):
        mock_response = mrf.response('SUCCESS\nfirst_name=Joe+Black\nitem_number=\n')
        mock_post = mock.MagicMock(return_value=mock_response)
        with mock.patch('pypay.payments.requests.post', mock_post):
            response = pypay.pdt_confirm('id', 'token')
        assert isinstance(response, pypay.payments.PaypalResponse)
        assert response.confirmed
        assert response.details == {'first_name': 'Joe Black', 'item_number': ''}


class TestIPNConfirmAPI(object):
    
    def test_ipn_confirm_calls_paypal_ipn_with_query_string_arg_and_sandbox_false(self):
        mock_paypal_ipn = mock.MagicMock()
        with mock.patch('pypay.api.PaypalIPN', mock_paypal_ipn):
            response = pypay.ipn_confirm('tx=id')
        mock_paypal_ipn.assert_called_with('tx=id', sandbox=False)
    
    def test_ipn_confirm_returns_a_paypal_response_object_with_processed_data(self, mrf):
        mock_response = mrf.response('VERIFIED')
        mock_post = mock.MagicMock(return_value=mock_response)
        query = 'first_name=Joe+Black\n&item_number=\n'
        with mock.patch('pypay.payments.requests.post', mock_post):
            response = pypay.ipn_confirm(query)
        assert isinstance(response, pypay.payments.PaypalResponse)
        assert response.confirmed
        assert response.details == {'first_name': 'Joe Black', 'item_number': ''}
