# USPTO Bulk Data Storage System

API URL: <https://developer.uspto.gov/api-catalog/bdss>

## Basic Usage

This API supports several of the BDSS API endpoints. But there are no general database lookups (i.e. using filter / limit / offset / order_by), only the following methods are supported:

- `Product.objects.filter_latest()` - Provides an iterator of `Product` objects from the /products/all/latest endpoint.
- `Product.objects.filter_by_name(name)` - Provides an iterator of `Product` objects that contain the text provided as `name`.
- `Product.objects.get_by_short_name(short_name)` - Gets a `Product` object corresponding to the BDSS short name.
- `File.objects.filter_by_short_name(short_name, from_date, to_date)` - Returns an iterator of File objects corresponding to the short name, starting with `from_date` and ending with `to_date`, inclusive.

The primary endpoint to be used here is the `File.objects.filter_by_short_name`, which returns all files associted with the short name as provided in the table below. You can optionally include from_date and to_date if it is helpful. Otherwise, they default to the complete range of the related product.

Once you have a `File` object, you can call either `File.download` to download the file, or `await File.adownload` to download it asynchronously.

If you want to view metadata related to the product, then use the `Product` endpoints.


## Supported Products

```{csv-table}
:file: products.csv
:widths: 10, 10, 50

```