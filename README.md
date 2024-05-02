[![patent_client_logo](https://raw.githubusercontent.com/parkerhancock/patent_client/master/docs/_static/patent_client_logo.svg)](https://patent-client.readthedocs.io)

[![Build](https://github.com/parkerhancock/patent_client/actions/workflows/build.yaml/badge.svg)](https://github.com/parkerhancock/patent_client/actions/workflows/build.yaml)
[![codecov](https://codecov.io/gh/parkerhancock/patent_client/branch/master/graph/badge.svg?token=pWsiQLHi6r)](https://codecov.io/gh/parkerhancock/patent_client)
[![Documentation](https://img.shields.io/readthedocs/patent-client/stable)](https://patent-client.readthedocs.io/en/stable/)


[![PyPI](https://img.shields.io/pypi/v/patent-client?color=blue)](https://pypi.org/project/patent-client)
[![PyPI - Python Versions](https://img.shields.io/pypi/pyversions/patent-client)](https://pypi.org/project/patent-client)
[![Downloads](https://static.pepy.tech/badge/patent_client/month)](https://pepy.tech/project/patent_client)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev)

# Summary

A powerful library for accessing intellectual property, featuring:

- 🍰 **Ease of use:** All sources use a simple unified API inspired by [Django-ORM][DORM].
- 🐼 **Pandas Integration:** Results are easily castable to [Pandas Dataframes and Series][PANDAS].
- 🚀 **Performance:** Fetched data is retrieved using the [httpx][httpx] library with native HTTP/2 and asyncio support, and cached using the [hishel][hishel] library for super-fast queries, and [yankee][yankee] for data extraction.
- 🌐 **Async/Await Support:** All API's (optionally!) support the async/await syntax.
- 🔮 **Pydantic v2 Support:** All models retrieved are [Pydantic v2 models][pydantic] with all the goodness that comes with them!

Docs, including a fulsome Getting Started and User Guide are available on [Read the Docs](http://patent-client.readthedocs.io). The Examples folder includes examples of using `patent_client` for
many common IP tasks

## ⭐ New in v5 ⭐

Version 5 brings a new and more reliable way to provide synchronous and asynchronous access to the various APIs.
In version 5, like in version 3, you can just `from patent_client import [Model]` and get a synchronous version
of the model. No asynchronous methods or functionality at all. Or you can do `from patent_client._async import [Model]`
and get an asynchronous version of the model.

Version 5 also brings support for the USPTO's new [Open Data Portal](https://beta-data.uspto.gov/home), a system currently in beta that is scheduled to replace the current Patent Examination Data System in late 2024.

## Coverage

- [United States Patent & Trademark Office][USPTO]

  - [Patent Examination Data][PEDS] - Full Support
  - [Open Data Portal][ODP] - Full Support
  - [Global Dossier][GD] - Full Support
  - [Patent Assignment Data][Assignment] - Lookup Support
  - [Patent Trial & Appeal Board API v2][PTAB] - Supports Proceedings, Decisions, and Documents
  - [Patent Public Search][PPS] - Full Support
  - [Bulk Data Storage System][BDSS] - Full Support


- [European Patent Office - Open Patent Services][OPS]

  - Inpadoc - Full Support
  - EPO Register - No Support (in progress)
  - Classification - No Support

* Free software: Apache Software License 2.0

[DORM]: https://docs.djangoproject.com/en/4.0/topics/db/queries/
[PANDAS]: https://pandas.pydata.org/docs/
[httpx]: https://www.python-httpx.org/
[hishel]: https://hishel.com/
[yankee]: https://github.com/parkerhancock/yankee
[Assignment]: user_guide/assignments.html
[OPS]: https://patent-client.readthedocs.io/en/latest/user_guide/epo.html
[PPS]:  https://patent-client.readthedocs.io/en/latest/user_guide/fulltext.html
[PEDS]: https://patent-client.readthedocs.io/en/latest/user_guide/peds.html
[PTAB]: https://patent-client.readthedocs.io/en/latest/user_guide/ptab.html
[USPTO]: http://developer.uspto.gov
[BDSS]: https://patent-client.readthedocs.io/en/latest/user_guide/bulk_data.html
[GD]: https://patent-client.readthedocs.io/en/latest/user_guide/global_dossier.html
[pydantic]: https://docs.pydantic.dev/latest/
[ODP]: https://patent-client.readthedocs.io/en/latest/user_guide/open_data_portal.html


## Installation

```
pip install patent_client
```

If you only want access to USPTO resources, you're done!
However, additional setup is necessary to access EPO Inpadoc and EPO Register resources. See the [Docs](http://patent-client.readthedocs.io).


## Quick Start

To use the project:

```python
# Import the model classes you need
>>> from patent_client import Inpadoc, Assignment, USApplication

# Fetch US Applications
>>> app = USApplication.objects.get('15710770')
>>> app.patent_title
'Camera Assembly with Concave-Shaped Front Face'

# Fetch from USPTO Assignments
>>> assignments = Assignment.objects.filter(assignee='Google')
>>> len(assignments) > 23000
True
>>> assignment = Assignment.objects.get('47086-788')
>>> assignment.conveyance_text
'ASSIGNMENT OF ASSIGNORS INTEREST'

# Fetch from INPADOC
>>> pub = Inpadoc.objects.get('EP3082535A1')
>>> pub.biblio.title
'AUTOMATIC FLUID DISPENSER'

```

## Async Quick Start

To use async with Patent Client, just import the classes you need from the async module. All methods
and iterators that access data or create a network request are asynchronous.

```python
from patent_client._async import USApplication

apps = list()
async for app in USApplication.objects.filter(first_named_applicant="Google"):
  apps.append(app)

app = await USApplication.objects.aget("16123456")

```

<!-- RTD-IGNORE -->

## Documentation

Docs, including a fulsome Getting Started are available on [Read the Docs](http://patent-client.readthedocs.io).

<!-- END-RTD-IGNORE -->

# Development

To run the all tests run:

```
pytest
```

A developer guide is provided in the [Documentation](http://patent-client.readthedocs.io).
Pull requests welcome!

# Related projects

- [Python EPO OPS Client](https://github.com/55minutes/python-epo-ops-client)
- [Google Public Patent Data](https://github.com/google/patents-public-data)
- [PatentsView API Wrapper](https://github.com/mikeym88/PatentsView-API-Wrapper)
- [USPTO Scrapy Scraper](https://github.com/blazers08/USPTO)

