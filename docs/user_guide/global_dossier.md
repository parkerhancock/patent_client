# Global Dossier (EXPERIMENTAL)

API URL: <https://globaldossier.uspto.gov>

:::{warning}
This module is **EXPERIMENTAL** which means its API may change in the future
:::

## Basic Usage

This API tracks the user interface on the [USPTO's Global Dossier](GD). There are no general database lookups (i.e. using filter / limit / offset / order_by), only `.get` calls work.

### To Fetch A GlobalDossier File

To fetch a Global Dossier file, you need three parameters - an office, a number type, and a number. By default, it assumes the lookup is for a U.S. Application number. But if it isn't a valid application number, then you must specifiy a type. So these work:

```python
from patent_client import GlobalDossier
file = GlobalDossier.objects.get("16123456") # US App
file = GlobalDossier.objects.get("6013599", type="patent") #US Patent
file = GlobalDossier.objects.get("20010000001", type="publication") # US Publication
```

You can also specify directly all three parameters:
```python
from patent_client import GlobalDossier
file = GlobalDossier.objects.get("16123456", type="application", office="US") # US App
```

Additionally, patent_client will attempt to infer a country and publication type from a given string, and provide informative errors if it needs more information:
```python
>>> from patent_client import GlobalDossier
>>> GlobalDossier.objects.get("EP1000000")
GlobalDossier(id=1000000, type=publication, country=EP)
>>> GlobalDossier.objects.get("AU1234567")
Traceback (most recent call last):
...
patent_client.uspto.global_dossier.query.QueryException: While country was detected as AU, no type can be inferred. Please pass a 'type' keyword to specify application/publication
```

### Basic Data Structure

A Global Dossier file is a collection of related applications across several patent offices. When you fetch the file, the individual applications are in the `GlobalDossier.applications` attribute. This will be all applications related to the application you searched.

Often, we don't want the entire worldwide file - we just want one. As a convienence function, you can use the related `GlobalDossierApplication` to fetch a single application. The query syntax is the same as the above - it is just a shortcut to the speific application:
```python
>>> from patent_client import GlobalDossierApplication
>>> GlobalDossierApplication.objects.get("16123456")
GlobalDossierApplication(app_num=16123456, country_code=US)

```

The GlobalDossier interface also provides downloadable document lists for its files. You can find those at `GlobalDossierApplication.documents` (entire file history), `GlobalDossierApplication.office_actions` (for office actions only), and `GlobalDossierApplication.document_list` (includes metadata). Any document can be downloaded by calling the `.download` method, optionally with an output path.

[GD]: https://globaldossier.uspto.gov