from .payments import PaypalPDT, PaypalIPN


def pdt_confirm(transaction_id, token, sandbox=False):
    """
    API - confirm a transaction via Paypal PDT and return
    a PaypalResponse instance with the processed response data
    """
    pdt = PaypalPDT(transaction_id, token, sandbox=sandbox)
    pdt.send_confirmation()
    pdt.process_response()
    return pdt.to_paypal_response()


def ipn_confirm(query_string, sandbox=False):
    """
    API - confirm a transaction via Paypal IPN and return
    a PaypalResponse instance with the processed response data
    """
    ipn = PaypalIPN(query_string, sandbox=sandbox)
    ipn.send_confirmation()
    ipn.process_response()
    return ipn.to_paypal_response()
