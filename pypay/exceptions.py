
class InvalidPaypalData(Exception):
    """
    Raised when data to be sent to Paypal fails validation
    """

class RequestError(Exception):
    """
    Raised when something goes wrong connecting to Paypal
    """
    pass
