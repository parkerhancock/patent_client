# Async / Await Support

Under the hood, `patent_client` is 100% async. But no worries! All the functionality is optional. You can still use the synchronous methods without changing your codebase. But if you want to use async/await syntax, here's what you do:

## Iterataors

Any object that can be iterated now also supports the async iterator protocol:

```python
from patent_client import USApplication

async for app in USApplication.objects.filter(first_named_applicant="Tesla"):
    # do something

```

## I/O Methods

All methods that trigger I/O have an async version prefixed with the letter `a`. For example:

```python
from patent_client import USApplication

# These do the same thing, but the second uses await
app = USApplication.objects.get("16123456")
app = await USApplication.objects.aget("16123456")

```

| Synchronous Method | Async/Await Method |
| ------------------ | ------------------ |
| `.get`             | `.aget`            |
| `.first`           | `.afirst`          |
| `.to_list`         | `.ato_list`        |
| `.to_pandas`       | `.ato_pandas`      |

Several models also have a `.download` method. All of those also have a mirror-image `.adownload`.

## Related Objects

Some of the objects have "related" objects. For example if you have a `USApplication`, you can get
related PTAB Trials at `USApplication.ptab_proceedings`. These are currently all still synchronous
but an async version is on the roadmap.