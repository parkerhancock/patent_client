# Developer Overview

The goal of this project is to provide easy-to-use access to public patent data through a simple API.
The general idea is to implement a subset of the
[Django QuerySet API](https://docs.djangoproject.com/en/2.1/ref/models/querysets/). functionality for accessing
the various sources of patent data.

To facilitate this, two base classes are provided as scaffolding for adding new APIs - *Manager* and *Model* (both located in the patent_client.util module). The
Django ORM implements its functionality using three classes - a Model class that models a single record in a database,
a Manager class that provides a generic way of accessing that data, and a QuerySet that allows for sorting / filtering of data.
Here, we omit the separate QuerySet and Manager, and instead use a single Manager class that handles both QuerySet and Manager
functions.

## Managers

When filtering, ordering, or values methods are called on a Manager, it returns a new Manager object with a combination of the arguments to the old manager and the new arguments. In this way, any given Manager is *immutable*. A base, blank manager (that would return all records), is attached to searchable models as Model.objects. Most searches will begin with a call to Model.objects.filter, which adds filtering critera to the manager. Like Django managers, they support .order_by, .limit, and .offset (and, in fact, slicing just passes the start and end on to those methods). Managers also support .values and .values_list.  Unlike Django, managers also support additional conveinence functions, including:

> - Manager.to_list - converts a manger to a list of models
> - Manager.to_pandas - converts a manager to a Pandas dataframe (if pandas is available), with all model attributes as columns

Managers also support addition operations. For example, to create an application list with all applications naming two assignees, you could do this:

```python
>> apps = USApplication.objects.filter(first_named_applicant='Company A') + USApplication.objects.filter(first_named_applicant='Company B')
```

## Models

Models are special dataclasses, with some additional functionality baked-in. Fields are present as attributes on the Model. Additionally:

- The Model.objects holds a manager that would retreive every Model in data source
- The Model supports a .to_dict() method to convert it to a dictionary, and a to_pandas() method to convert it to a Pandas series.

Models can also have custom functions and properties attached to them. These vary from model to model, but consist of:

- Transformer methods - that calculate some property based on one or more Fields
- Relationships - that traverse a relationship to a related model
- Downloaders - that download some sort of content related to the model

Downloaders always return a tempfile.NamedTemporaryFile with the downloaded file contained therein.

## Schemas

Each data source also has a module called a "Schema," which is a deserialization layer that converts raw data obtained by the manager into
models. In general, the data sources accessed by patent_client are either JSON or XML documents. Both use the Marshmallow library to apply
formatting corrections, renaming conventions, etc.

## Relationships

In some circumstances, it would be nice to get information related to a model class, even if it resides on another system supported by patent_client. Relationships are how you get there. For example, if you retreive a PtabTrial object from the PTAB API, it has an attribute .us_application that will return a USApplication object from the PEDS API.

The .util package also has two functions that make this possible - 'one_to_one' and 'one_to_many'. Both functions work the same way -
they take a first argument, which is a string locating the other object, and then a keyword argument, where the keyword is a filter criteria,
and the value is an attribute on the current model to use as the value.

The only difference between the two functions is that "one_to_one" calls objects.get, returing a single object, while "one_to_many"
calls objects.filter, and returns a manager of the related objects. For example, we can use these to link the Trials and Documents as below:

```python
class PtabTrial(Model):
    ...
    documents = one_to_many('patent_client.PtabDocument', trial_number='trial_number')
    ...

class PtabDocument(Model):
    ...
    trial = one_to_one('patent_client.PtabTrial', trial_number='trial_number')
    ...
```

Once these relationships are in place, we can move from one record to the other seamlessly:

```python
>>> from patent_client import PtabProceeding
>>> a = PtabProceeding.objects.get('IPR2017-00001') # doctest +SKIP

>>> a.documents[0]
PtabDocument(document_category='Paper', document_type_name='Notice of Appeal', document_number=50, document_name='IPR2017-00001NOAFWD.pdf', document_filing_date=datetime.date(2018, 5, 16), title=None)

>>> a.documents[0].proceeding
PtabProceeding(subproceeding_type_category='IPR', proceeding_number='IPR2017-00001', proceeding_status_category='FWD Entered', proceeding_type_category='AIA Trial', respondent_party_name='SIPCO, LLC')

```
