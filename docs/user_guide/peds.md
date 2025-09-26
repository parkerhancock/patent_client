# US Patent Examination Data System (PEDS)

Original API URL: <https://ped.uspto.gov/peds/>

:::{danger}
The USPTO retired the Patent Examination Data System (PEDS) on March 14, 2025. The service no longer resolves, so
live requests will fail. This page is retained for historical reference only—use the [Open Data Portal](../open_data_portal.md)
APIs for current `USApplication` access.
:::


Patent Client previously provided an interface to the USPTO Patent Examination Data System (PEDS). The examples below
capture the legacy usage but will no longer succeed against the USPTO endpoints.


PEDS is a REST-ful API that contains all the publicly available data in Patent Center (formerly PAIR).
It provides a wealth of bibliographic information on pending and issued US Patent applications, as well as PCT
applications filed with the USPTO as the Receiving oFfice. Because of this, the models returned by the USApplications API are quite complex with lots of nested data fields (e.g. transaction data, continuity data, inventors, etc.)
Use it like this:

```python
>>> from patent_client import USApplication
>>> from pprint import pprint
>>> app = USApplication.objects.get('14591909')
>>> app.patent_title
'Integrated Docking System for Intelligent Devices'
>>> app.app_filing_date
datetime.date(2015, 1, 7)

```

## Querying

There are also lots of filtering options, which make this interface great for patent
portfolio analysis. For example:

```python
>>> apps = USApplication.objects.filter(first_named_applicant='Caterpillar')
>>> len(apps) > 4000
True
>>> pprint(apps[:5].to_list())
[USApplication(appl_id='...', patent_title='...', app_status='...'),
 USApplication(appl_id='...', patent_title='...', app_status='...'),
 USApplication(appl_id='...', patent_title='...', app_status='...'),
 USApplication(appl_id='...', patent_title='...', app_status='...'),
 USApplication(appl_id='...', patent_title='...', app_status='...')]

```

A complete list of available filters can be found by calling `USApplication.objects.fields`.
