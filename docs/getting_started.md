# Getting Started

## Installation

To install

```console
pip install patent_client
```

If you are only interested in using the USPTO API's, no further setup is necessary. Skip ahead to the next section.

If you want to take advantage of the European Patent Office's Open Patent Services,
which supports Inpadoc and Epo Register documents, you will need to set up your API key:

### How to get an EPO OPS API key

**Step 1:** Go to [EPO Open Patent Services](https://www.epo.org/searching-for-patents/data/web-services/ops.html#tab-1) and
register a new account (Free up to 4GB of data / month, which is usually more than sufficient).

**Step 2:** Log in to EPO OPS, and click on "My Apps," add a new app, and write down the corresponding API *Consumer Key* and *Consumer Key Secret*.

**Step 3:** Import patent_client from anywhere. E.g.

```console
$ python
Python 3.6.5 (default, Jul 12 2018, 11:37:09)
>>> import patent_client

```

This will set up an empty settings file, located at **~/.patent_client_config.yaml**. The config file is a YAML file containing settings for the project.

**Step 4:** Edit the config file to contain your user key and secret. E.g.

```yaml
DEFAULT:
    BASE_DIR: ~/.patent_client
    LOG_FILE: patent_client.log
    LOG_LEVEL: INFO

EPO:
    API_KEY: <Key Here>
    API_SECRET: <Secret Here>
ITC:
    USERNAME:
    PASSWORD:

```

**Step 5:** PROFIT! Every time you import a model that requires EPO OPS access, you will automatically be logged on using that key and secret.

### Environment Variables (Less Recommended)

Alternatively, you can set the environment variables as:

```console
PATENT_CLIENT__EPO_API_KEY="<Consumer Key Here>"
PATENT_CLIENT__EPO_SECRET="<Consumer Key Secret Here>"
```

## Basic Use

All data is accessible through an [Active Record](https://en.wikipedia.org/wiki/Active_record_pattern) model
inspired by the [Django ORM Query API](https://docs.djangoproject.com/en/2.1/topics/db/queries/). In particular, the API to Patent Client is a subset
of the official [Django QuerySet API](https://docs.djangoproject.com/en/2.1/ref/models/querysets/). To access data, first import the model
representing the data you want. E.g.

```python
from patent_client import USApplication
```

All of the models are accessible directly at patent_client. Further, all the API's used in this library are **Read Only**, so there is no way to add, delete, or modify records.

### Managers

Data is queried by applying filters, orders, limits, and offsets to a model's "objects" attribute. What follows is a brief introduction. Please note that this doesn't cover a lot of advanced functionality that is documented in the {doc}`Manager docs <api>`.
For example, if you wanted all patent applications filed by "Google LLC," you would write

```python
>>> from patent_client import USApplication

>>> google_apps = USApplication.objects.filter(first_named_applicant='Google LLC')

>>> len(google_apps) > 1000
True

```

This returns a manager that can access all US Applications where the first named applicant is "Google LLC." In addition to passing search parameters, you can also do other standard database-like
operations, including ordering, limits, and offsets - as .order_by, .limit, and .offset, respectively. Each of these operations merely returns a modified manager that will return the requested results. They can also be chained in any order. E.g.:

```python
microsoft_pats = (USApplication.objects
                .filter(first_named_applicant='Microsoft')
                .filter(app_status='Patented Case')
                .order_by('patent_issue_date')
                .limit(10)
                )
```

This manager returns the first 10 applications with Microsoft listed as the first applicant, that have issued as patents, and in order of their patent issue date (ascending order).

Once you have a manager, the results can be accessed in a few ways. Record objects can be obtained by slicing or iterating on the manager itself. Passing a single index returns
a single specific object, as shown below:

```python
>>> from patent_client import USApplication

>>> microsoft_pats = (USApplication.objects
...             .filter(first_named_applicant='Microsoft')
...             .filter(app_status='Patented Case')
...             .order_by('patent_issue_date')
...             .limit(10)
...             )

>>> app = microsoft_pats[0] # doctest:+SKIP

>>> app # doctest:+SKIP
USApplication(appl_id='15592928', patent_title='CRYPTLET IDENTITY', app_status='Patented Case')

>>> app.patent_title # doctest:+SKIP
'CRYPTLET IDENTITY'

>>> app.app_status # doctest:+SKIP
'Patented Case'
```

In contrast, passing a slice with a start and a step is merely an alias for `Model.offset` and `Model.limit`, and returns a modified `Manager` object, which is likewise accessible by index.
Managers can also be converted into other collection forms in several ways:

```python
# Pandas DataFrames
microsoft_apps.to_pandas()# ß doctest:+SKIP
        app_attr_dock_number app_cls_sub_cls app_confr_number app_cust_number  ...                                       transactions wipo_early_pub_date wipo_early_pub_number                                                obj
0               402409-US-NP      380/044000             9742           69316  ...  [{'code': 'PUBTC', 'date': 2020-03-06, 'descri...                None                  None  USApplication(appl_id='15592928', patent_title...
1              402553-US-CNT      382/118000             8785           69316  ...  [{'code': 'EML_NTR', 'date': 2020-02-27, 'desc...                None                  None  USApplication(appl_id='16573677', patent_title...
2                  359108.01      717/168000             6521           69316  ...  [{'code': 'EML_NTR', 'date': 2020-02-27, 'desc...                None                  None  USApplication(appl_id='15042835', patent_title...
3   359127-US-NP 1777.312US1      707/720000             8010          127265  ...  [{'code': 'WPIR', 'date': 2020-02-26, 'descrip...                None                  None  USApplication(appl_id='15084366', patent_title...
4               13768.2950.2      726/004000             1074           47973  ...  [{'code': 'EML_NTR', 'date': 2020-02-27, 'desc...                None                  None  USApplication(appl_id='15374735', patent_title...
5              330345-US-CNT      717/136000             6127           69316  ...  [{'code': 'EML_NTR', 'date': 2020-02-27, 'desc...                None                  None  USApplication(appl_id='15465547', patent_title...
6  14917.1958USD1/334132USD1      345/473000             7123           27488  ...  [{'code': 'EML_NTR', 'date': 2020-02-27, 'desc...                None                  None  USApplication(appl_id='15470234', patent_title...
7                  331792.02      718/001000             7391           39254  ...  [{'code': 'EML_NTR', 'date': 2020-02-27, 'desc...                None                  None  USApplication(appl_id='14670895', patent_title...
8               356456-US-NP      320/135000             1830           69316  ...  [{'code': 'EML_NTR', 'date': 2020-02-27, 'desc...                None                  None  USApplication(appl_id='14678144', patent_title...
9                  339968.01      709/203000             2161           69316  ...  [{'code': 'EML_NTR', 'date': 2020-02-27, 'desc...                None                  None  USApplication(appl_id='14076715', patent_title...

# List in fluent style
>>> microsoft_pats.to_list() # doctest:+SKIP

[USApplication(appl_id='15592928', patent_title='CRYPTLET IDENTITY', app_status='Patented Case'), USApplication(appl_id='16573677', patent_title='INTELLIGENT ASSISTANT', app_status='Patented Case'), USApplication(appl_id='15042835', patent_title='STYLUS FIRMWARE UPDATES',
app_status='Patented Case'), USApplication(appl_id='15084366', patent_title='COMPUTATIONAL-MODEL OPERATION USING MULTIPLE SUBJECT REPRESENTATIONS', app_status='Patented Case'), USApplication(appl_id='15374735', patent_title='SHARE TOKEN ISSUANCE FOR DECLARATIVE DOCUMENT
AUTHORING', app_status='Patented Case'), USApplication(appl_id='15465547', patent_title='DYNAMIC DATA AND COMPUTE RESOURCE ELASTICITY', app_status='Patented Case'), USApplication(appl_id='15470234', patent_title='ANIMATIONS FOR SCROLL AND ZOOM', app_status='Patented Case'
), USApplication(appl_id='14670895', patent_title='EMULATING MIXED-CODE PROGRAMS USING A VIRTUAL MACHINE INSTANCE', app_status='Patented Case'), USApplication(appl_id='14678144', patent_title='Battery Management in a Device with Multiple Batteries', app_status='Patented C
ase'), USApplication(appl_id='14076715', patent_title='GEO-DISTRIBUTED DISASTER RECOVERY FOR INTERACTIVE CLOUD APPLICATIONS', app_status='Patented Case')]

# List with standard python cast
>>> list(microsoft_pats) # doctest:+SKIP

[USApplication(appl_id='15592928', patent_title='CRYPTLET IDENTITY', app_status='Patented Case'), USApplication(appl_id='16573677', patent_title='INTELLIGENT ASSISTANT', app_status='Patented Case'), USApplication(appl_id='15042835', patent_title='STYLUS FIRMWARE UPDATES',
app_status='Patented Case'), USApplication(appl_id='15084366', patent_title='COMPUTATIONAL-MODEL OPERATION USING MULTIPLE SUBJECT REPRESENTATIONS', app_status='Patented Case'), USApplication(appl_id='15374735', patent_title='SHARE TOKEN ISSUANCE FOR DECLARATIVE DOCUMENT
AUTHORING', app_status='Patented Case'), USApplication(appl_id='15465547', patent_title='DYNAMIC DATA AND COMPUTE RESOURCE ELASTICITY', app_status='Patented Case'), USApplication(appl_id='15470234', patent_title='ANIMATIONS FOR SCROLL AND ZOOM', app_status='Patented Case'
), USApplication(appl_id='14670895', patent_title='EMULATING MIXED-CODE PROGRAMS USING A VIRTUAL MACHINE INSTANCE', app_status='Patented Case'), USApplication(appl_id='14678144', patent_title='Battery Management in a Device with Multiple Batteries', app_status='Patented C
ase'), USApplication(appl_id='14076715', patent_title='GEO-DISTRIBUTED DISASTER RECOVERY FOR INTERACTIVE CLOUD APPLICATIONS', app_status='Patented Case')]
```

Managers also behave like Django QuerySets, and support [values](https://docs.djangoproject.com/en/2.1/ref/models/querysets/#values) and
[values_list](https://docs.djangoproject.com/en/2.1/ref/models/querysets/#values-list) methods.

```python
>>> microsoft_pats.values('appl_id', 'patent_title')[:3].to_list() # doctest:+SKIP
]
    OrderedDict([('appl_id', '15592928'), ('patent_title', 'CRYPTLET IDENTITY')]),
    OrderedDict([('appl_id', '16573677'), ('patent_title', 'INTELLIGENT ASSISTANT')]),
    OrderedDict([('appl_id', '15042835'), ('patent_title', 'STYLUS FIRMWARE UPDATES')])
]

>>> microsoft_pats.values_list('appl_id', 'patent_title')[:3].to_list() # doctest:+SKIP
[
    ('15592928', 'CRYPTLET IDENTITY'),
    ('16573677', 'INTELLIGENT ASSISTANT'),
    ('15042835', 'STYLUS FIRMWARE UPDATES')
]

>>> microsoft_pats.values_list('patent_title', flat=True)[:3].to_list() # doctest:+SKIP
[
    'CRYPTLET IDENTITY',
    'INTELLIGENT ASSISTANT',
    'STYLUS FIRMWARE UPDATES'
]
```