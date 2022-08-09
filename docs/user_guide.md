# User Guide

## Introduction

Patent Client permits a fluent style for querying and manipulating IP data.
The recommended way of using it is in a three-step process:

1.  Query the data (filter/limit/offset/order_by)
2.  Reshape the data (values)
3.  Process the data (.to_pandas, etc.)

### A Simple Example
By way of example, let's look at the patent porfolio for Google, looking
at just the most recent 20 filed (and publicly available) applications:

#### 1. Query the Data

:::python
from patent_client import USApplication

apps = (USApplication.objects
        .filter(first_named_applicant="Google")
        .order_by("-appl_filing_date")
        .limit(20)
        )

:::

This is step 1 - querying the data. Consult the documentation for further details on
available filtering critera. This creates a problem, though. While it
fetches the relevant data, but probably provides too much to be useful.
At least for a single report. So let's reshape the result!

#### 2. Reshape the Data

We only want certain fields, so we can do this:

:::python
apps = (USApplication.objects
        .filter(first_named_applicant="Google")
        .order_by("-appl_filing_date")
        .limit(20)
        .values("appl_id", "app_filing_date", "patent_title", "patent_number", "issue_date")
        )
:::

Now we've reshaped the data by limiting what information we have. But let's say
we also want the full name of the first inventor. That can be done using the `values` function,
by using dotted notation to get what we want:

:::python
apps = (USApplication.objects
        # Step 1 - Query the Data
        .filter(first_named_applicant="Google")
        .order_by("-appl_filing_date")
        .limit(20)
        # Step 2 - Reshape the Data
        .values("appl_id", "app_filing_date", "patent_title", "patent_number", "issue_date", "inventors.0.name")
        )
:::

So, now we've reshaped the data into a convenient format. With this, we can convert to a
pandas dataframe, a list, ingest it into a database, iterate over the results, etc.

#### 3. Process the Data

That's nice, but maybe we want to actually want to do something else.
Like calculate the average time from filing to issuance. We can do that using `pandas`, we just need
to convert our result to something Pandas can deal with. So let's do that:

:::python
apps = (USApplication.objects
        # Step 1 - Query the Data
        .filter(first_named_applicant="Google")
        .order_by("-appl_filing_date")
        .limit(20)
        # Step 2 - Reshape the Data
        .values("appl_id", "app_filing_date", "patent_title", "patent_number", "issue_date", "inventors.0.name")
        # Step 3 - Process the data
        .to_pandas()
        .assign(time_to_issue=lambda df: df.issue_date - df.app_filing_date)
        .mean()
        .time_to_issue
        )
:::

## Advanced Data Reshaping

The trick to doing interesting and complicated things with `patent_client` is all about data reshaping.
Reshaping can be done using three methods on a manager: `.values`, `.unpack`, and `.explode`.

### The Values Function

The `.values` method on a manager is perhaps the most powerful and complex feature of `patent_client`. When `.values` is called, the manager becomes an iterator of `Row` objects, a `dict`-like container
object with flexible contents.

**Simple Attribute Fetching & Renaming:** Each argument becomes a field in the result, and each keyword argument can be used to create a renamed result. Additionally, you can pass a dictionary using the keyword `fields` to rename fields things that
can't be keyword arguments. Using USApplication as an example, you can do this:

:::python

apps = (USApplication.objects
        .filter(first_named_applicant="Google")
        .order_by("-appl_filing_date")
        .limit(20)
        .values("appl_id", title="patent_title", fields={"Application Filing Date": "appl_filing_date"})

:::

**Complex Attribute Fetching:** When resolving fields for a `Row`, you can select properties of the model
that aren't actually fields, including related objects from other API's. Patent client will automate
the retrieval of the related items. Additionally, you can use dotted notation to fetch fields on
related objects:

:::python

apps = (USApplication.objects
        .filter(first_named_applicant="Google")
        .order_by("-appl_filing_date")
        .limit(20)
        .values(
            "priority_date", # a calculated property
            "patent.us_refs", # US references cited in the patent - retreived from the Fulltext Patent API
            )

:::

**Indexes in Attribute Fetching:** Sometimes a related object is a list of things, and you only want
one. Like maybe you only want the first named inventor. You can include numeric values in dotted notation
to fetch that.

:::python

apps = (USApplication.objects
        .filter(first_named_applicant="Google")
        .order_by("-appl_filing_date")
        .limit(20)
        .values(
            "inventors.0.name", # Fetches the first inventor listed, and selects the name off of that value
            )

:::

### Unpack and Explode

The other two key data reshaping functions are `.unpack` and `.explode`.

**Unpacking Data:** The `.unpack` method allows nested structured data to be "unpacked" into columns of a row. For example, if you wanted the name and address of the first named inventor, you could do this:

:::python

apps = (USApplication.objects
        .filter(first_named_applicant="Google")
        .order_by("-appl_filing_date")
        .limit(20)
        .values(
            first_named_inventor="inventors.0", # An Inventor object has a name and an address field.
            )
        .unpack("first_named_inventor")

:::

In the result, this produces a row that has columns for `first_named_invetor.name`, `first_named_invetor.address`, and `first_named_invetor.rank_no`. Additionally, if there is no risk of colliding with other
columns, `.unpack` can be passed a keyword argument `prefix=false` to suppress prefixes.

**Exploding Data:** The `.explode` function is essentially the same thing as [`pandas.DataFrame.explode`][explode], but is included here so that data reshaping can be done before moving from patent_client `Row` objects to `DataFrame` objects. In essence, it takes a row that has a nested list of data, and produces
one row for each object in the nested list.

For example, if you wanted a list of transactions, but annotated with the application number, you could do this:

:::python

apps = (USApplication.objects
        .get("16123456)
        .values(
            "appl_id", "transactions"
            )
        .explode("transactions")
        .unpack("transactions")

:::

[explode]: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.explode.html
