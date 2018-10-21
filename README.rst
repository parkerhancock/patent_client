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

A set of Django-ORM-Style accessors to publicly available intellectual property data.

Currently supports:

+---------------------------------------------------+---------------------------+-------------------+
| Office                                            |  API                      | Status            |
+===================================================+===========================+===================+
|European Patent Office (EPO)                       | OPS - INPADOC             | Full Support      |
|                                                   +---------------------------+-------------------+
|                                                   | OPS - EPO Register        | Full Support      |
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

    pip install ip

Documentation
=============


To use the project:

.. code-block:: python

    >>> from ip import Inpadoc, Epo, Assignment, USApplication
    >>> pub = Inpadoc.objects.get('EP3082535A1')
    >>> pub.bib_data
    {'title': 'AUTOMATIC FLUID DISPENSER', 'publication': {'country': 'EP', 'number': '3082535', 'kind': 'A1', 'date': '20161026'}, 'application': {'country': 'EP', 'number': '14833316', 'kind': 'A', 'date': None}, 'intl_class': ['A47K5/12AI', 'A47K5/122AI', 'B05B9/00AI', 'B05B9/08AI', 'B05B12/12AI'], 'cpc_class': ['A47K 5/1211', 'A47K 5/1217', 'A47K 5/122', 'B05B 9/002', 'B05B 9/0838', 'B05B 12/122'], 'priority_claims': ['201314137130', '2014071849'], 'applicants': ['TOASTER LABS, INC'], 'inventors': ['BUCKALTER, Amy, ', 'HADLEY, Jonathan, B, ', 'DIENER, Alexander, M, ', 'WILL, Kristin, M, ', 'MULLER, Lilac, ','SPENCE, Jeanine'], 'abstract': '', 'references_cited': []}
    >>> epo = Epo.objects.get('EP3082535A1')
    >>> epo.bib_data
    {'status': [{'description': 'Examination is in progress', 'code': '14', 'date': '20180615'}], 'publications': [{'country': 'WO', 'number': '2015095864', 'kind': 'A1', 'date': '20150625'}, {'country': 'EP', 'number': '3082535', 'kind': 'A1', 'date': '20161026'}], 'intl_class': ['A47K5/12, A47K5/122, B05B9/00, B05B9/08, B05B12/12'], 'applications': [{'country': 'EP', 'number': '14833316', 'date': '20141222'}, {'country': 'WO', 'number': 'WO2014US71849'}], 'filing_language': 'en', 'priority_claims': [{'kind': 'national', 'number': '201314137130', 'date': '20131220'}], 'applicants': [{'name': 'Toaster Labs, Inc.', 'address': '2212 Queen Anne Avenue N.\nSeattle, WA 98109\nUS'}], 'inventors': [{'name': 'BUCKALTER, Amy', 'address': '118 Galer Street\nSeattle, WA 98109\nUS'}, {'name': 'HADLEY, Jonathan, B.', 'address': '225 Logan Avenue 341\nRenton, WA 98057\nUS'}, {'name': 'DIENER, Alexander, M.', 'address': '2826 25th Avenue West\nSeattle, WA 98199\nUS'}, {'name': 'WILL, Kristin, M.', 'address': '3043 61st Street\nSeattle, WA 98107\nUS'}, {'name': 'MULLER, Lilac', 'address': '15719 165th Place NE\nWoodinville, WA 98072\nUS'}, {'name': 'SPENCE, Jeanine', 'address': '6513 NE 190th Street\nKenmore, WA 98028\nUS'}], 'designated_states': ['EP', 'AL', 'AT', 'BE', 'BG', 'CH', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES','FI', 'FR', 'GB', 'GR', 'HR', 'HU', 'IE', 'IS', 'IT', 'LI', 'LT', 'LU', 'LV', 'MC', 'MK', 'MT', 'NL', 'NO', 'PL', 'PT', 'RO', 'RS', 'SE', 'SI', 'SK', 'SM', 'TR'], 'title': 'AUTOMATIC FLUID DISPENSER', 'citations': [{'phase': 'international-search-report', 'office': 'EP', 'citation': {'country': 'FR', 'number': '2873048'}, 'category': 'XI', 'relevant_passages': '(OCEANIQUES SOC EN COMMANDITE S [FR]) [X] 1 * page  11, line  26  - page  19, line  3; figures 2,3 * [I] 4;'}, {'phase': 'international-search-report', 'office': 'EP', 'citation': {'country': 'US', 'number': '2004226962'}, 'category': 'YA', 'relevant_passages': '(MAZURSKY RICHARD [US], et al) [Y] 1-3 * paragraph  [0022]  - paragraph  [0033]; figures 1-7 * [A] 5-21;'}, {'phase': 'international-search-report', 'office': 'EP','citation': {'country': 'EP', 'number': '2225988'}, 'category': 'YA', 'relevant_passages': '(GOJO IND INC [US]) [Y] 1-3 * paragraph  [0010]  - paragraph  [0018]; figure - * [A] 5-21;'}, {'phase': 'international-search-report', 'office': 'EP', 'citation': {'country': 'US', 'number': '2012085780'}, 'category': 'A', 'relevant_passages': '(LANDAUER KONRAD [US]) [A] 1-21 * paragraph  [0026]  - paragraph  [0032]; figures 1-7 *'}]}
    >>> assignments = Assignment.objects.filter(assignee='Google')
    >>> len(assignments)
    23860
    >>> assignments[0].pat_assignor_name
    ['MULLINS, SCOTT', 'CONNER, BRIAN']
    >>> assignments[0].dict
    {'id': '47086-788', 'display_id': '047086-0788', 'reel_no': '47086', 'frame_no': '788','last_update_date': '2018-10-12', 'purge_indicator': 'N', 'recorded_date': '2018-10-05', 'page_count': '2', 'conveyance_text': 'ASSIGNMENT OF ASSIGNORS INTEREST (SEE DOCUMENT FOR DETAILS).', 'assignment_record_has_images': 'Y', 'attorney_dock_num': '104248-5226-US', 'corr_name': 'DOUGLAS J. CRISMAN', 'corr_address1': 'MORGAN, LEWIS & BOCKIUS', 'corr_address2': '1400 PAGE MILL ROAD', 'corr_address3': 'PALO ALTO, CA 94304', 'pat_assignor_earliest_ex_date': '2018-09-24', 'pat_assignor_name': ['MULLINS, SCOTT', 'CONNER, BRIAN'], 'pat_assignor_ex_date': ['2018-09-24', '2018-10-04'], 'pat_assignor_date_ack': ['0000-01-01T00:00:00Z', '0000-01-01T00:00:00Z'], 'pat_assignee_name': 'GOOGLE LLC', 'pat_assignee_address1': '1600 AMPHITHEATRE PARKWAY', 'pat_assignee_address2': None, 'pat_assignee_city': 'MOUNTAIN VIEW', 'pat_assignee_state': 'CALIFORNIA', 'pat_assignee_country_name': None, 'pat_assignee_postcode': '94043', 'invention_title': 'Camera Assembly with Concave-Shaped Front Face', 'invention_title_lang': 'en', 'appl_num': '15710770', 'filing_date': '2017-09-20', 'intl_publ_date': None, 'intl_reg_num': None, 'inventors': 'Mark Kraz, Kevin Edward Booth, Tyler Scott Wilson, Nicholas Webb, Jason Evans Goulden, William Dong, Jeffrey Law, Rochus Jacob, Adam Duckworth Mittleman, Oliver Mueller, Scott Mullins,Brian Conner', 'issue_date': None, 'pat_num': None, 'pct_num': None, 'publ_date': '2018-07-05', 'publ_num': '20180191929', 'pat_assignor_name_size': 2, 'pat_assignor_name_type_size': 2, 'pat_assignor_ex_date_size': 2, 'pat_assignor_date_ack_size': 2, 'pat_assignee_name_size': 2, 'pat_assignee_name_type_size': 0, 'pat_assignee_address1_size': 1, 'pat_assignee_address2_size': 1, 'pat_assignee_city_size': 1, 'pat_assignee_state_size': 1, 'pat_assignee_country_name_size': 1, 'pat_assignee_postcode_size': 1, 'invention_title_size': 1, 'invention_title_id_size': 1, 'invention_title_lang_size': 1, 'appl_num_size': 1, 'filing_date_size': 1, 'intl_publ_date_size': 1, 'intl_reg_num_size': 1, 'inventors_size': 1, 'issue_date_size': 1, 'pat_num_size': 1, 'pct_num_size': 1, 'publ_date_size': 1, 'publ_num_size': 1, 'invention_title_first': 'Camera Assembly with Concave-Shaped Front Face', 'invention_title_lang_first': 'en', 'appl_num_first': '15710770', 'filing_date_first': '2017-09-20', 'intl_publ_date_first': None, 'intl_reg_num_first': None, 'inventors_first': 'Mark Kraz, Kevin Edward Booth, Tyler Scott Wilson, Nicholas Webb, Jason Evans Goulden, William Dong, Jeffrey Law, Rochus Jacob, Adam Duckworth Mittleman, Oliver Mueller, Scott Mullins, Brian Conner', 'issue_date_first': None, 'pat_num_first': None, 'pct_num_first': None, 'publ_date_first': '2018-07-05', 'publ_num_first': '20180191929', 'pat_assignor_name_first': 'MULLINS, SCOTT', 'pat_assignee_name_first': 'GOOGLE LLC', '_version_': 1614157495418224640, 'image_url': 'http://legacy-assignments.uspto.gov/assignments/assignment-pat-047086-0788.pdf'}
    >>> app = USApplicaiton.objects.get('15710770')
    >>> app.patent_title
    'Camera Assembly with Concave-Shaped Front Face'

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
