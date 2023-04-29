# US Patents & Published Applications

Original API URL: <https://ppubs.uspto.gov/pubwebapp>

:::{warning}
This API is currently broken due to changes on the USPTO website to discourage automated tools from accessing Public Patents Search
:::

:::{warning}
The USPTO's Public Search interface IS NOT for bulk downloads. Please limit retrievals to 10's
of documents. That will also prevent any issues with distributing this code. If you really
want hundreds or thousands of documents, please use [Google's Public Patents Data Sets](GPAT).
:::

[GPAT]: https://console.cloud.google.com/marketplace/partners/patents-public-data

Patent Client provides an interface to the USPTO's [Public Search] databases.

[Public Search]: https://ppubs.uspto.gov/pubwebapp/static/pages/landing.html

## Api Structure

There are two general types of objects returned from this API - bibliographic records, and full documents. Bibliographic records
contain all the basic information about the patent. Full documents include the full specification text, references cited, and other data.
To be nice to the USPTO, please use bibliographic record endpoints whenever possible, falling back to the full documents only when absolutely necessary.
Forr that reason, the bibliographic record search is unrestricted, however
to prevent abuse, I have limited searches of full documents to queries that produce 20 or fewer results.

There are a few classes for accessing this API:

- `PublicSearch` - Search bibliographic records across all databases
- `PublicSearchDocument` - Search full documents across all databases
- `PatentBiblio` - Search patent bibliographic records since ~1979
- `Patent` - Search full documents for patents since ~1979
- `PublishedApplicationBiblio` - Search published application bibliographic records
- `PublishedApplication` - Search published application full documents

## Document Retrieval

If you just want to fetch a patent or published application, just pass the publication number
into a "get" query, and you'll get the desired response:

```python
>>> from patent_client import Patent, PublishedApplication
>>> Patent.objects.get("10000000")
Publication(publication_number=10000000, publication_date=2018-06-19, patent_title=Coherent LADAR using intra-pixel quadrature detection)
>>> PublishedApplication.objects.get("20200000001")
Publication(publication_number=20200000001, publication_date=2020-01-02, patent_title=SYSTEM FOR CONNECTING IMPLEMENT TO MOBILE MACHINERY)

```

## Searching

The full Public Search query language is available for use by passing the special keyword "query" with a string:

```python
>>> from patent_client import PublicSearch
>>> result = PublicSearch.objects.filter(query='"6103599".PN. OR @APD=20210101')

```

Documentation on this query language is here:
 - [Training Document On Query Syntax (PDF)](QUERY_SYNTAX)
 - [Available Search Fields](SEARCH_FIELDS)

[QUERY_SYNTAX]: https://ppubs.uspto.gov/pubwebapp/static/assets/files/Search%20overview%20QRG%20-%20Patent%20Public%20Search.pdf
[SEARCH_FIELDS]: https://ppubs.uspto.gov/pubwebapp/static/pages/searchable-indexes.html

Patent Client also implements a subset of the searchable indexes in a fluent and Django-inspired way. Use it like this:

```python
>>> from patent_client import PatentBiblio
>>> tennis_patents = PatentBiblio.objects.filter(patent_title="tennis", assignee="wilson")
>>> len(tennis_patents) > 10
True

```

Below are the supported fields:

### Public Search Supported Fields
```{eval-rst}

.. csv-table::
    :file: ../../src/patent_client/uspto/public_search/query_config.csv
    :header-rows: 1
```


### Date Ranges

Patent Client also supports **date range** features in a few flavors.

- If you want to search for a specific date, just use {code}`issue_date="2020-01-01"`.
- If you want to search for dates *before* a certain date, use {code}`issue_date_lt="2020-01-01"`
- If you want to search for dates *after* a certain date, use {code}`issue_date_gt="2020-01-01"`
- If you want to seach for a date range, use {code}`issue_date_range=("2019-01-01", "2020-01-01")`, you can also just use the "\_gt" and "\_lt" together.

All the above will accept Python dates, datetimes, or any string understandable by python's dateutil.parser, and work
for any date-like field (e.g. issue date, filing date, etc.)


## Image Downloads

Any object can be downloaded locally as a pdf by calling `.download_images`.


## Models

```{eval-rst}
.. autoclass:: patent_client.uspto.public_search.model.PublicSearch
    :members:
    :undoc-members:

.. autoclass:: patent_client.uspto.public_search.model.PublicSearchDocument
    :members:
    :undoc-members:

.. autoclass:: patent_client.uspto.public_search.model.PatentBiblio
    :members:
    :undoc-members:

.. autoclass:: patent_client.uspto.public_search.model.Patent
    :members:
    :undoc-members:

.. autoclass:: patent_client.uspto.public_search.model.PublishedApplication
    :members:
    :undoc-members:

.. autoclass:: patent_client.uspto.public_search.model.PublishedApplicationBiblio
    :members:
    :undoc-members:

```

