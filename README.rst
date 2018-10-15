========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - |
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|



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

A set of ORM-style clients for publicly available Ppatent data

* Free software: Apache Software License 2.0

Installation
============

::

    pip install ip

Documentation
=============


To use the project:

.. code-block:: python

    import ip
    ip.longest()


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
