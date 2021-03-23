.. image:: https://travis-ci.org/parkerhancock/patent_client.svg?branch=master
    :target: https://travis-ci.org/parkerhancock/patent_client

.. image:: https://codecov.io/gh/parkerhancock/patent_client/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/parkerhancock/patent_client

.. image:: https://img.shields.io/pypi/v/patent_client.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/patent_client

.. image:: https://img.shields.io/pypi/wheel/patent_client.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/patent_client

.. image:: https://img.shields.io/pypi/pyversions/patent_client.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/patent_client

Overview
========

A set of Django-ORM-Style accessors to publicly available intellectual property data.

Currently supports:

* `United States Patent & Trademark Office <USPTO>`_

  * `Patent Full Text Databases <PATFT>`_ - Full Support
  * `Patent Examination Data <PEDS>`_ - Full Support (**Including File History Documents!**)
  * `Patent Assignment Data <Assignment>`_ - Lookup Support
  * `Patent Trial & Appeal Board API v2 <PTAB>`_ - Supports Proceedings, Decisions, and Documents

* `United States International Trade Commission <ITC>`_

  * `Electronic Document Information System (EDIS) API <EDIS>`_ - Partial Support (no document downloads)

* `European Patent Office - Open Patent Services <OPS>`_

  * Inpadoc - Full Support
  * EPO Register - No Support (in progress)
  * Classification - No Support

.. _OPS: http://ops.epo.org
.. _USPTO: http://developer.uspto.gov
.. _PATFT: http://http://patft.uspto.gov/
.. _PEDS: https://developer.uspto.gov/api-catalog/ped
.. _Assignment: https://developer.uspto.gov/api-catalog/patent-assignment-search-beta
.. _PTAB: https://developer.uspto.gov/api-catalog/ptab-api-v2
.. _ITC: https://www.usitc.gov/
.. _EDIS: https://edis.usitc.gov/external/

* Free software: Apache Software License 2.0

Installation
============

::

    pip install patent_client

If you only want access to USPTO resources, you're done!
However, additional setup is necessary to access EPO Inpadoc and EPO Register resources. See the `Docs <http://patent-client.readthedocs.io>`_.

Documentation
=============

The easiest way to get started is with `Patent Client Examples <https://github.com/parkerhancock/patent_client_examples>`_. The examples repository has
a list of Jupyter notebooks showing application examples of the patent_client library.

Docs, including a fulsome Getting Started are available on `Read the Docs <http://patent-client.readthedocs.io>`_.

SUPER QUICK START
-----------------

To use the project:

.. code-block:: python

    # Import the model classes you need
    >>> from patent_client import Inpadoc, Assignment, USApplication, Patent

    # Fetch US Patents with the word "tennis" in their title issued in 2010
    >>> pats = Patent.objects.filter(title="tennis", issue_date="2010-01-01->2010-12-31")
    >>> len(pats) > 10
    True
    
    # Look at the first one
    >>> pats[0].publication
    Patent(publication_number=7841958, publication_date=2010-11-30, title=Modular table tennis game)

    # Fetch US Applications
    >>> app = USApplication.objects.get('15710770')
    >>> app.patent_title
    'Camera Assembly with Concave-Shaped Front Face'

    # Fetch from USPTO Assignments
    >>> assignments = Assignment.objects.filter(assignee='Google')
    >>> len(assignments) > 23000
    True
    >>> assignment = Assignment.objects.get('47086-788')
    >>> assignment.conveyance_text
    'ASSIGNMENT OF ASSIGNORS INTEREST'

    # Fetch from INPADOC
    # >>> pub = Inpadoc.objects.get('EP3082535A1')
    # >>> pub.biblio.title
    # 'AUTOMATIC FLUID DISPENSER'

    # Fetch from EPO Register (NOTE: This is broken right now :( )
    #>>> epo = Epo.objects.get('EP3082535A1')
    #>>> epo.title
    #'AUTOMATIC FLUID DISPENSER'
    #>>> epo.status
    #[{'description': 'Examination is in progress', 'code': '14', 'date': '20180615'}]

Other Languages
===============

Merely as a way to explore other languages and technologies, I have built a few (partial) ports of this
library to other languages:

* `patent_client_js <https://github.com/parkerhancock/patent_client_js>`_ - ES6 Javascript (PEDS / PTAB / Assignments support (ASYNC!))
* `patent_client_java <https://github.com/parkerhancock/patent_client_java>`_ - Java (Ptab API only)
* `patent_client_scala <https://github.com/parkerhancock/patent_client_scala>`_ - Scala (Ptab API only)
* `patent_client_ruby <https://github.com/parkerhancock/patent_client_ruby>`_ - Ruby (Nothing Works Yet)

Development
===========

To run the all tests run::

    pytest

A developer guide is provided in the `Documentation <http://patent-client.readthedocs.io>`_.
Pull requests welcome!

Related projects
================

* `Python EPO OPS Client <https://github.com/55minutes/python-epo-ops-client>`_
* `Google Public Patent Data <https://github.com/google/patents-public-data>`_
