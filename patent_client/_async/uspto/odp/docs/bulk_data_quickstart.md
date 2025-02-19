# USPTO Bulk Data Quickstart Guide

The USPTO Open Data Portal (ODP) Bulk Data functionality provides access to large datasets of patent and trademark information. This guide will show you how to use the manager-based functions to access and search bulk data products.

## Basic Usage

First, import the `BulkData` class:

```python
from patent_client._async.uspto.odp import BulkData
```

The `BulkData` class provides access to all functionality through its `objects` manager.

## Direct Product Access

### Getting a Specific Product

To retrieve information about a specific bulk data product:

```python
# Get the Patent File Wrapper Pre-Grant product
product_id = "PTFWPRE"
product = await BulkData.objects.get_product(
    product_identifier=product_id,
    include_files=True,  # Include file details in response
    latest=True  # Only return latest version of files
)
```

You can also filter the files within a product by date:

```python
product = await BulkData.objects.get_product(
    product_identifier=product_id,
    file_data_from_date="2023-01-01",
    file_data_to_date="2023-12-31",
    include_files=True
)
```

## Search Interface

The Bulk Data interface provides a powerful search capability to find products and datasets.

### Basic Text Search

```python
# Search across all fields
results = await BulkData.objects.query(q="patent assignment").execute()

# Search specific fields
results = await BulkData.objects.query(
    product_title="Patent File Wrapper",
    product_description="bulk data"
).execute()
```

### Filtering by Product Attributes

```python
# Filter by labels
results = await BulkData.objects.query(
    labels=["PATENT", "TRADEMARK"]
).execute()

# Filter by categories
results = await BulkData.objects.query(
    categories="Patent file wrapper"
).execute()

# Filter by file types
results = await BulkData.objects.query(
    file_types=["JSON", "XML"]
).execute()
```

### Pagination

Control the number of results returned:

```python
results = await BulkData.objects.paginate(
    offset=0,  # Skip this many results
    limit=10   # Return at most this many results
).execute()
```

### Search Options

Configure additional search behavior:

```python
results = await BulkData.objects.options(
    include_files=True,  # Include file details in results
    latest=True,        # Only return latest versions
    facets=True         # Include faceted search results
).execute()
```

### Combining Search Operations

You can chain multiple search operations together:

```python
results = await BulkData.objects.query(
    product_title="Patent File Wrapper"
).options(
    include_files=True,
    latest=True
).paginate(
    limit=10
).execute()
```

## Response Data

The bulk data search results contain detailed information about available products:

- Product metadata (title, description, short name)
- Labels and categories
- Dataset information
- File details (when include_files=True)
  - File names and paths
  - File sizes and types
  - Data date ranges
  - Version information

Each response field is properly typed using Pydantic models, providing excellent IDE support and type checking.

## Common Product Identifiers

Here are some commonly used product identifiers:

- `PTFWPRE`: Patent File Wrapper Pre-Grant Data
- `PTFWPST`: Patent File Wrapper Post-Grant Data
- `ASGN`: Patent Assignment Data
- `TDFW`: Trademark File Wrapper Data
- `TMOG`: Trademark Official Gazette Data

## Best Practices

1. Use `latest=True` when you only need the most recent version of files
2. Use date filters when working with specific time periods
3. Include `facets=True` to understand the distribution of products in your search results
4. Use pagination to handle large result sets efficiently
5. Specify only the fields you need in your search to optimize response times

## Error Handling

The API may return errors for various reasons:

- Invalid product identifiers
- Invalid date formats
- Missing required parameters
- API rate limiting
- Network issues

All errors are properly typed and include descriptive messages to help diagnose the issue. 