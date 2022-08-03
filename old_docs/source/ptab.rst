Patent Trial & Appeal Board
^^^^^^^^^^^^^^^^^^^^^^^^^^^
API URL: https://developer.uspto.gov/api-catalog/ptab-api-v2

.. note::
    Only publicly accessible documents are available. Any document that is marked confidential is not accessible.

Patent Client provides an interface to the `PTAB Public API v2 <https://developer.uspto.gov/api-catalog/ptab-api-v2>`_.
This API provides access to three data object types:

    - **PtabProceeding** - A PTAB Trial, Patent Appeal, Interference, or other type of PTAB PtabProceeding
    - **PtabDocument** - A file history document associated with a PtabProceeding
    - **PtabDecision** - A formal decision from a PtabProceeding (e.g. institution decision, final decision, etc.)

Date Ranges
===========
All fields are query-able. Date fields can be queried by range by including "to" or "from" in the keyword argument.
For example, fetching all proceedings decided after a date would look like this:

.. code-block:: python

    PtabProceeding.objects.filter(accorded_filing_from_date="2020-01-01")

The syntax is a little odd, but this is how the underlying API works.
This is a band-aid until `Django-style keyword accessors <https://docs.djangoproject.com/en/dev/ref/models/querysets/#id4>`_. can be implemented.

Models
======

.. automodule:: patent_client.uspto.ptab.model
    :members:
    :undoc-members:
