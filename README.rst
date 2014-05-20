pypay
=====

pypay provides a clean API for confirming Paypal payments via PDT or IPN. It takes the boilerplate out of interacting with these services and normalises the Paypal response into something sensible.

Under the hood pypay uses the excellent `Requests <https://github.com/kennethreitz/requests>`_ library for handling http.


Installation
------------


.. sourcecode:: bash

    pip install pypay


Usage
-----

To check a payment via `PDT <https://developer.paypal.com/docs/classic/paypal-payments-standard/integration-guide/paymentdatatransfer/>`_


.. sourcecode:: python

    import pypay

    response = pypay.pdt_confirm('your_transaction_id', 'your_identity_token')


To check a payment via `IPN <https://developer.paypal.com/docs/classic/ipn/integration-guide/IPNIntro/>`_


.. sourcecode:: python

    import pypay

    response = pypay.ipn_confirm('query_params_from_paypal')


You can pass the query params as either a string (e.g. 'quantity=1&name=joe') or a dict. This is particularly useful if you're using Django as you can drop in request.POST and everything with just work.


Response objects
~~~~~~~~~~~~~~~~~~~

Response objects always have two properties


.. sourcecode:: python

    response.confirmed # bool indicating if payment is verified

    response.details # dict containing all the Paypal variables that were returned


Handling exceptions
~~~~~~~~~~~~~~~~~~~

In the event of a problem making the http call to Paypal, pypay will raise a ``pypay.exceptions.RequestError``.

The values passed to ``pdt_confirm`` and ``ipn_confirm`` are sanity checked and a ``pypay.exceptions.InvalidPaypalData`` will be raised if they are of the wrong type.


Python version support
----------------------

pypay runs on Python 2.6, 2.7, 3.3 and 3.4 using the `Six <https://pythonhosted.org/six/>`_ compatibility library.


Running tests
-------------

Run the test suite with `Tox <http://tox.readthedocs.org/en/latest/>`_


.. sourcecode:: bash

    pip install tox



Tests are written with `pytest <http://pytest.org/latest/>`_
