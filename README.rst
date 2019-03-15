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

* `European Patent Office - Open Patent Services <OPS>`_

  * Inpadoc - Full Support
  * EPO Register - Full Support
  * Classification - No Support

* `United States Patent & Trademark Office <USPTO>`_

  * `Patent Examination Data <PEDS>`_ - Full Support
  * `Patent Assignment Data <Assignment>`_ - Lookup Support
  * `Patent Trial & Appeal Board API <PTAB>`_ - Full Support

* `United States International Trade Commission <ITC>`_

  * `Electronic Document Information System (EDIS) API <EDIS>`_ - Full Support

.. _OPS: http://ops.epo.org
.. _USPTO: http://developer.uspto.gov
.. _PEDS: https://developer.uspto.gov/api-catalog/ped
.. _Assignment: https://developer.uspto.gov/api-catalog/patent-assignment-search-beta
.. _PTAB: https://developer.uspto.gov/api-catalog/ptab-api
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
This project is narrowly scoped to only public documented API's available without charge
(at least for moderate usage). Scrapers of HTML websites are not permitted. But PR's to
add support for new API's are more than welcome.

Pull requests welcome!

Related projects
================

* `Python EPO OPS Client <https://github.com/55minutes/python-epo-ops-client>`_
* `Google Public Patent Data <https://github.com/google/patents-public-data>`_
