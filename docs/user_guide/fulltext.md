# US Patents & Published Applications

Original API URL: <http://patft.uspto.gov/netahtml/PTO/index.html>

:::{warning}
This interface has a limited capacity and occasionally throws errors because the server is
over capacity. Some rudimentary retrying is baked into this API, but sometimes even that
isn't enough. Sometimes you just have to retry later :(
:::

:::{warning}
The USPTO's Full Text interface IS NOT for bulk downloads. Please limit retrievals to 10's
of documents. That will also prevent any issues with distributing this code. If you really
want hundreds or thousands of documents, please use [Google's Public Patents Data Sets](GPAT).
:::

[GPAT]: https://console.cloud.google.com/marketplace/partners/patents-public-data

Patent Client provides an interface to the USPTO's Full Text databases.

## Basic Lookups

If you just want to fetch a patent or published application, just pass the publication number
into a "get" query, and you'll get the desired response:

```python
>>> from patent_client import Patent, PublishedApplication
>>> Patent.objects.get("10000000")
Patent(publication_number=10000000, publication_date=2018-06-19, title=Coherent LADAR using intra-pixel quadrature detection)
>>> PublishedApplication.objects.get("20200000001") # doctest:+SKIP
PublishedApplication(publication_number=20200000001, publication_date=2020-01-02, title=SYSTEM FOR CONNECTING IMPLEMENT TO MOBILE MACHINERY)

```

## Searching

Patent Client mostly implements the advanced search features of the Full Text database in
a fluent and Django-inspired way. Use it like this:

```python
>>> from patent_client import Patent
>>> tennis_patents = Patent.objects.filter(title="tennis", assignee_name="wilson")
>>> len(tennis_patents) > 10
True

```

Patent Client implements all the search fields for both Patents and Published Applications.
The associated keyword is just the underscored verison of the full name in the tables here:

- [Patent Full Text Advanced Search][PATS]
- [Published Application Full Text Advanced Search][PUBS]

[PATS]: https://patft.uspto.gov/netahtml/PTO/search-adv.htm
[PUBS]: https://appft.uspto.gov/netahtml/PTO/search-adv.html

Queries only return **stub records** that only contain the publication number and title.
If you want the full document, you can access it at the "publication" attribute:

```python
>>> from patent_client import Patent
>>> basketball_patents = Patent.objects.filter(title="basketball", issue_date="2021-05-25").order_by("patent_number")
>>> basketball_patents[0] # doctest: +SKIP
PatentResult(publication_number='D920344', title='Display screen with graphical user interface for a basketball practice device')
>>> basketball_patents[0].publication
Patent(publication_number=D920344, publication_date=2021-05-25, title=Display screen with graphical user interface for a basketball practice device)

```

### Date Ranges

Patent Client also supports **date range** features in a few flavors.

- If you want to search for a specific date, just use {code}`issue_date="2020-01-01"`.
- If you want to search for dates *before* a certain date, use {code}`issue_date_lt="2020-01-01"`
- If you want to search for dates *after* a certain date, use {code}`issue_date_gt="2020-01-01"`
- If you want to seach for a date range, use {code}`issue_date_range=("2019-01-01", "2020-01-01")`, you can also just use the "\_gt" and "\_lt" together.

All the above will accept Python dates, datetimes, or any string understandable by python's dateutil.parser, and work
for any date-like field (e.g. issue date, filing date, etc.)

### Advanced Searching

Patent Client currently does not have any built-in syntax for advanced boolean queries.
Patent Client assumes that all critera are simply "AND"ed together.

If this doesn't work for you, just use the **query** keyword, and pass whatever query you
want. Patent Client will return the results as if you had entered that into the web interface:
:::python

>>> from patent_client import Patent
>>> tennis_patents = Patent.objects.filter(query="TTL/tennis OR AN/wilson")
>>> len(tennis_patents) > 100
True

:::

## Models

```{eval-rst}
.. automodule:: patent_client.uspto.fulltext.patent.model
    :members:
    :undoc-members:
```

```{eval-rst}
.. automodule:: patent_client.uspto.fulltext.published_application.model
    :members:
    :undoc-members:
```


[PATS]: http://patft.uspto.gov/netahtml/PTO/search-adv.htm
[PUBS]: http://appft.uspto.gov/netahtml/PTO/search-adv.html
