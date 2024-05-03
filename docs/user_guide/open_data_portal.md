# USPTO Open Data Portal - File Wrapper

Original API URL: <https://beta-data.uspto.gov/home>

:::{warning}
The USPTO's Open Data Portal is still considered a beta product. It should work well, but
there may be errors in the data.

**Also, please note that the ODP only covers applications filed on or after Jan 1, 2001.**
:::

Patent Client provides an interface to the USPTO's [Open Data Portal](https://beta-data.uspto.gov/home), which currently
provides information on pending applications, similar to [PEDS](../peds.md). The USPTO expects to retire PEDS in late 2024,
after which it will be fully replaced by the Open Data Portal.

The Open Data Portal currently only supports accessing US Application information, not patents or published applications.
Nonetheless, it provides a wealth of information about applications, including bibliographic information, file history
documents, related assignments, and more.

## Setup

The Open Data Portal requires a USPTO-issued API key. This key can be obtained at [My Api Key](https://beta-data.uspto.gov/key/myapikey), and should be set as an environment variable `PATENT_CLIENT_ODP_API_KEY`. If this variable is not set, none of the API's will work


## Basic Retrieval

Because ODP will eventually replace PEDS, the current ODP implementations of USApplication can be found by
prefixing the USApplicationManager with "odp". Here is an example of how to access the Open Data Portal:

```python
from patent_client.odp import USApplicationBiblio

app = USApplicationBiblio.objects.get("16123456") # The application itself
app.biblio # The basic bibliographic information
app.assignments # The related assignments
app.documents # The related documents
app.term_adjustments # The related term adjustments
app.foreign_priority # The related foreign priority data
app.customer_number # Information about the customer number that
app.transactions # The related transaction data
```

There are two main objects that represent an Application, the USApplicationBiblio and the USApplication. The USApplicationBiblio
object contains the basic bibliographic information, while the USApplication object contains the full application data, including all
of the subfields except documents. To reduce the burden on the USPTO website, I recommend using the USApplicationBiblio object for most
of your queries, and then use the related attributes to access the data you actually need.

## Document Downloads

To download file history information about an application, use the related `.documents` attribute. Each `Document` object has a `download` method, which can be used to download the document. For example:

```python
>>> from patent_client.odp import USApplicationBiblio

>>> app = USApplicationBiblio.objects.get("16123456")
>>> app.documents[0].download() # doctest: +SKIP
```

This will download the first document in the application's file history, and save it to the current working directory with the naming format: `{application_id} - {mail_date} - {document_code} - {document_code_description}.{type}`.

## Search

Patent Client implements the full search API, documentation for which can be found [here](https://beta-data.uspto.gov/apis/api-guidelines).
There are three basic ways to search the ODP using Patent Client, all through the USApplicationBiblio.objects.filter (or USApplication.objects.filter) interface. The specifics of the search are fully described in [this pdf](https://beta-data.uspto.gov/documents/documents/ODP-API-Query-Spec.pdf), which provides the available search fields.

### Method 1 - Basic Keyword Searches

You can use keywords to search the ODP as function arguments, like this:

```python
USApplicationBiblio.objects.filter(invention_title="A search string")
```

All the keywords work - all you need to do is use them in python-style camel_case, (i.e. inventionTitle becomes invention_title).
If you provide multiple keywords, the keywords are AND'ed together, and thus the results will only be applications that match all the criteria. Date fields can also be searched
as greater than or less than, and can be either datetime.datetime objects, or isoformat string dates (i.e. "2024-01-03"). To do date range searches, use the Django-style `__gte` and `__lte`. For example:

```python
USApplicationBiblio.objects.filter(filing_date__gte="2024-01-01", filing_date__lt="2024-02-01")
```

### Method 2 - Raw `q` Parameter Searches (Simplified Query Syntax)

Alternatively, you can search the ODP using the raw `q` parameter, which is a full-text search of the application's full text. This search style is
documented [here](https://beta-data.uspto.gov/documents/documents/ODP-API-Query-Spec.pdf). You can use the full power of the simplified search
syntax, by passing the query string as the `q` parameter. NOTE: you cannot mix the simplified search syntax with the keyword search syntax.

```python
USApplicationBiblio.objects.filter(q="inventionTitle:Ball AND filingDate:2024-01-01")
```

### Method 3 - OpenSearch Query (Advanced Query Syntax)

As a third option, the ODP supports the OpenSearch Query syntax, which is documented [here](https://beta-data.uspto.gov/apis/api-guidelines).
This is the most powerful search option, and allows for complex queries. The OpenSearch query can be passed as a dictionary to the `USApplicationBiblio.objects.filter` method, like this:

```python
USApplicationBiblio.objects.filter(query={
    "q": "Nanobody",
  "filters": [
    {
      "name": "applicationTypeLabelName",
      "value": [
        "Utility"
      ]
    }
  ],
  "rangeFilters": [
    {
      "field": "filingDate",
      "valueFrom": "2022-01-01",
      "valueTo": "2023-12-31"
    }
  ],
  "pagination": {
    "offset": 0,
    "limit": 25
  },
  "sort": [
    {
      "field": "filingDate",
      "order": "Desc"
    }
  ]})

```

