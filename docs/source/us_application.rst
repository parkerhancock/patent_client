US Applications
^^^^^^^^^^^^^^^
Original API URL: https://ped.uspto.gov/peds/

.. warning::
    The PEDS interface is under active development by the USPTO. Occasionally documented filtering
    and ordering criteria will fail. Failed filters return no results. Failed ordering critera just
    have no effect.

Patent Client provides an interface to the USPTO Patent Examination Data System (PEDS).

PEDS is a REST-ful API that contains some - but not all - of the application data available
through PAIR. Notably, it is missing file history documents. Nevertheless, it provides a wealth of bibliographic information on pending and issued US
Patent applications. Because of this, the models returned by the USApplications API are quite complex with lots of nested data fields (e.g. transaction data, continuity data, inventors, etc.)
Use it like this:

.. code-block:: python

    >>> from patent_client import USApplication
    >>> from pprint import pprint
    >>> app = USApplication.objects.get('14591909')
    >>> app.patent_title
    'Integrated Docking System for Intelligent Devices'
    >>> app.app_filing_date
    datetime.date(2015, 1, 7)

There are also lots of filtering options, which make this interface great for patent
portfolio analysis. For example:

.. code-block:: python

    >>> apps = USApplication.objects.filter(first_named_applicant='Caterpillar')
    >>> len(apps) > 4000
    True
    >>> pprint(apps[:5].to_list())
    [USApplication(appl_id='...', patent_title='...', app_status='...'),
     USApplication(appl_id='..., patent_title='...', app_status='...'),
     USApplication(appl_id='...', patent_title='...', app_status='...'),
     USApplication(appl_id='...', patent_title='...', app_status='...'),
     USApplication(appl_id='...', patent_title='...', app_status='...')]

Models
======

.. automodule:: patent_client.uspto.peds.model
    :members:
    :undoc-members:
