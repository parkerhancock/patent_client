# Patent File Wrapper Quickstart Guide

The Patent File Wrapper functionality provides access to USPTO's Patent Application Information Retrieval (PAIR) data through the Open Data Portal (ODP) API. This guide will show you how to use the manager-based functions to access and search patent file wrapper data.

## Basic Usage

First, import the `PatentFileWrapper` class:

```python
from patent_client._async.uspto.odp import PatentFileWrapper
```

The `PatentFileWrapper` class provides access to all functionality through its `objects` manager.

## Direct API Access

### Getting Application Data

To retrieve detailed information about a specific patent application:

```python
application_id = "15123456"
app_data = await PatentFileWrapper.objects.get_application_data(application_id)
```

### Getting Bibliographic Data

For basic bibliographic information:

```python
biblio_data = await PatentFileWrapper.objects.get_application_biblio_data(application_id)
```

### Getting Assignment Information

To retrieve assignment history:

```python
assignments = await PatentFileWrapper.objects.get_assignments(application_id)
```

### Getting Attorney Information

For attorney and agent details:

```python
attorney_data = await PatentFileWrapper.objects.get_attorney_data(application_id)
```

### Getting Continuity Data

To get parent/child application relationships:

```python
continuity_data = await PatentFileWrapper.objects.get_continuity_data(application_id)
```

### Getting Documents

To retrieve document information:

```python
documents = await PatentFileWrapper.objects.get_documents(application_id)
```

### Getting Transaction History

For the application's transaction history:

```python
transactions = await PatentFileWrapper.objects.get_transactions(application_id)
```

## Search Interface

The Patent File Wrapper provides a powerful search interface with Elasticsearch-like query capabilities.

### Basic Search

```python
# Search for utility patent applications
results = await PatentFileWrapper.objects.query(
    "applicationMetaData.applicationTypeLabelName:Utility"
).execute()
```

### Search with Filters

```python
# Search with status filter
results = await PatentFileWrapper.objects.filter(
    "applicationMetaData.applicationStatusDescriptionText",
    "Patented Case"
).execute()
```

### Search with Date Ranges

```python
# Search by filing date range
results = await PatentFileWrapper.objects.range(
    field="applicationMetaData.filingDate",
    from_value="2023-01-01",
    to_value="2023-12-31"
).execute()
```

### Sorting Results

```python
# Sort by filing date in descending order
results = await PatentFileWrapper.objects.sort("-applicationMetaData.filingDate").execute()
```

### Field Selection

```python
# Select specific fields to return
results = await PatentFileWrapper.objects.fields(
    "applicationNumberText",
    "applicationMetaData.filingDate",
    "applicationMetaData.applicationStatusDescriptionText"
).execute()
```

### Pagination

```python
# Paginate results
results = await PatentFileWrapper.objects.paginate(offset=0, limit=10).execute()
```

### Faceted Search

```python
# Get facets for application types and status codes
results = await PatentFileWrapper.objects.facets(
    "applicationMetaData.applicationTypeLabelName",
    "applicationMetaData.applicationStatusCode"
).execute()
```

### Combining Search Operations

You can chain multiple search operations together:

```python
results = await PatentFileWrapper.objects.query(
    "applicationMetaData.applicationTypeLabelName:Utility"
).filter(
    "applicationMetaData.applicationStatusDescriptionText",
    "Patented Case"
).range(
    field="applicationMetaData.filingDate",
    from_value="2023-01-01",
    to_value="2023-12-31"
).sort(
    "-applicationMetaData.filingDate"
).fields(
    "applicationNumberText",
    "applicationMetaData.filingDate"
).paginate(
    limit=10
).execute()
```

### Async Iteration

For large result sets, you can iterate over the results asynchronously:

```python
async for item in PatentFileWrapper.objects.query(
    "applicationMetaData.applicationTypeLabelName:Utility"
).paginate(limit=10):
    print(item.application_number_text)
```

## Response Data

The search results contain rich information about patent applications, including:

- Application metadata (filing date, status, type)
- Correspondence addresses
- Assignment history
- Attorney information
- Continuity data
- Patent term adjustments
- Transaction history
- Document information

Each response field is properly typed using Pydantic models, providing excellent IDE support and type checking. 