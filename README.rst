Overview
========

.. start-badges

.. |codecov| image:: https://codecov.io/github/parkerhancock/python-ip/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/parkerhancock/python-ip

.. |version| image:: https://img.shields.io/pypi/v/ip.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/ip

.. |commits-since| image:: https://img.shields.io/github/commits-since/parkerhancock/python-ip/v0.0.1.svg
    :alt: Commits since latest release
    :target: https://github.com/parkerhancock/python-ip/compare/v0.0.1...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/ip.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/ip

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/ip.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/ip

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/ip.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/ip


.. end-badges

Warning
==============

This project is under active development. Please treat this as a rough draft. NOT PRODUCTION READY.



A set of Django-ORM-Style accessors to publicly available intellectual property data.

Currently supports:

+---------------------------------------------------+---------------------------+-------------------+
| Office                                            |  API                      | Status            |
+===================================================+===========================+===================+
|European Patent Office (EPO)                       | OPS - INPADOC             | Partial Support   |
|                                                   +---------------------------+-------------------+
|                                                   | OPS - EPO Register        | Partial Support   |
|                                                   +---------------------------+-------------------+
|                                                   | OPS - Classification      | No Support        |
+---------------------------------------------------+---------------------------+-------------------+
|United States Patent & Trademark Office (USPTO)    | Patent - Exam (Pair-Like) | Full Support      |
|                                                   +---------------------------+-------------------+
|                                                   | Patent - Assignments      | Support Lookup    |
|                                                   +---------------------------+-------------------+
|                                                   | PTAB - Trial Documents    | Full Support      |
+---------------------------------------------------+---------------------------+-------------------+


* Free software: Apache Software License 2.0

Installation
============

::

    pip install patent_client

Documentation
=============


To use the project:

.. code-block:: python

    >>> from patent_client import Inpadoc, Epo, Assignment, USApplication
    # Fetch US Applications
    >>> app = USApplication.objects.get('15710770')
    >>> app.patent_title
    'Camera Assembly with Concave-Shaped Front Face'
    # Fetch from USPTO Assignments
    >>> assignments = Assignment.objects.filter(assignee='Google')
    >>> len(assignments)
    23860
    >>> assignments[0].id
    '47086-788'
    >>> assignments[0].conveyance_text
    'ASSIGNMENT OF ASSIGNORS INTEREST (SEE DOCUMENT FOR DETAILS).'
    # Fetch from INPADOC
    >>> pub = Inpadoc.objects.get('EP3082535A1')
    >>> pub.title
    'AUTOMATIC FLUID DISPENSER'
    >>> pub.priority_claims
    ['201314137130', '2014071849']
    # Fetch from EPO Register
    >>> epo = Epo.objects.get('EP3082535A1')
    >>> epo.title
    'AUTOMATIC FLUID DISPENSER'
    >>> epo.status
    [{'description': 'Examination is in progress', 'code': '14', 'date': '20180615'}]

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
