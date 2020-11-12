US Full Text Patents & Published Applications
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Original API URL: http://patft.uspto.gov/netahtml/PTO/index.html

.. warning::
    The USPTO's Full Text interface IS NOT for bulk downloads. Please limit retrievals to 10's 
    of documents. That will also prevent any issues with distributing this code. If you really 
    want hundreds or thousands of documents, please use `Google's Public Patents Data Sets <GPAT>`_.

.. _GPAT: https://console.cloud.google.com/marketplace/partners/patents-public-data

Patent Client provides an interface to the USPTO's Full Text databases.

Basic Lookups
=============

If you just want to fetch a patent or published application, just pass the publication number
into a "get" query, and you'll get the desired response:

.. code-block:: python

    >>> from patent_client import Patent, PublishedApplication
    >>> Patent.objects.get("10000000")
    Patent(publication_number=10000000, publication_date=2018-06-19, title=Coherent LADAR using intra-pixel quadrature detection)
    >>> PublishedApplication.objects.get("20200000001")
    PublishedApplication(publication_number=20200000001, publication_date=2020-01-02, title=SYSTEM FOR CONNECTING IMPLEMENT TO MOBILE MACHINERY)

Searching
=========

Patent Client mostly implements the advanced search features of the Full Text database in
a fluent and Django-inspired way. Use it like this:

.. code-block:: python

    >>> from patent_client import Patent
    >>> tennis_patents = Patent.objects.filter(title="tennis", assignee_name="wilson")
    >>> len(tennis_patents) > 10
    True

Patent Client implements all the search fields for both Patents and Published Applications.
The associated keyword is just the underscored verison of the full name in the tables here:

* `Patent Full Text Advanced Search <PATS>`_
* `Published Application Full Text Advanced Search <PUBS>`_

.. _PATS: http://patft.uspto.gov/netahtml/PTO/search-adv.htm
.. _PUBS: http://appft.uspto.gov/netahtml/PTO/search-adv.html

However, Patent Client currently does not have any built-in for advanced boolean queries. 
Patent Client assumes that all critera are simply "AND"ed together. 

If this doesn't work for you, just use the *query* keyword, and pass whatever query you
want. Patent Client will return the results as if you had entered that into the web interface:

.. code-block:: python

    >>> from patent_client import Patent
    >>> tennis_patents = Patent.objects.filter(query="TTL\tennis OR AN\wilson")
    >>> len(tennis_patents) > 100
    True

Queries only return **stub records** that only contain the publication number and title.
If you want the full document, you can access it at the "publication" attribute:

.. code-block:: python

    >>> from patent_client import Patent
    >>> basketball_patents = Patent.objects.filter(title="basketball")
    >>> basketball_patents[0]
    PatentResult(publication_number='10814199', title='Basketball shooting training device')
    >>> basketball_patents[0].publication
    Patent(publication_number=10814199, publication_date=2020-10-27, title=Basketball shooting training device)

Models
======

.. automodule:: patent_client.uspto.fulltext.patent.model
    :members:
    :undoc-members:

.. automodule:: patent_client.uspto.fulltext.published_application.model
    :members:
    :undoc-members: