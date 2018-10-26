Getting Started
^^^^^^^^^^^^^^^

Installation
============

To install 

.. code-block:: console

    pip install patent_client

If you are only interested in using the USPTO API's, no further setup is necessary. Skip ahead to the next section.

If you want to take advantage of the European Patent Office's Open Patent Services, 
which supports Inpadoc and Epo Register documents, you will need to set up your API key. You can do this in one of two ways:

System Wide Configuration (Recommended)
---------------------------------------

**Step 1:** Go to `EPO Open Patent Services <https://www.epo.org/searching-for-patents/data/web-services/ops.html#tab-1>`_ and 
register a new account (Free up to 4GB of data / month, which is more than sufficient).

**Step 2:** Log in to EPO OPS, and click on "My Apps," add a new app, and write down the corresponding API *Consumer Key* and *Consumer Key Secret*.

**Step 3:** Import patent_client from anywhere. E.g. 

.. code-block:: console

    $ python
    Python 3.6.5 (default, Jul 12 2018, 11:37:09)
    >>> import patent_client

This will set up an empty settings file, located at **~/.iprc**. The IPRC file is a JSON object containing settings for the project.

**Step 4:** Edit the IPRC file to contain your user key and secret. E.g. 

.. code-block:: json

    {
        "EpoOpenPatentServices": {
            "ApiKey": "<Consumer Key Here>",
            "Secret": "<Consumer Key Secret Here>"
        }
    }

**Step 5:** PROFIT! Every time you import a model that requires EPO OPS access, you will automatically be logged on using that key and secret.

Environment Variables (Less Recommended)
----------------------------------------

Alternatively, you can set the environment variables as:

.. code-block:: console

    EPO_KEY="<Consumer Key Here>"
    EPO_SECRET="<Consumer Key Secret Here>"


Basic Use
=========

All data is accessible through an `Active Record <https://en.wikipedia.org/wiki/Active_record_pattern>`_ model 
inspired by the `Django ORM Query API <https://docs.djangoproject.com/en/2.1/topics/db/queries/>`_. In particular, the API to Patent Client is a subset
of the official `Django QuerySet API <https://docs.djangoproject.com/en/2.1/ref/models/querysets/>`_. To access data, first import the model
representing the data you want. E.g. 

.. code-block:: python

    from patent_client import USApplication

All the API's used in this library are **Read Only**, so there is no way to add, delete, or modify records. Data is queried by applying filters,
orders, and by slicing the related "objects" attribute. For example, if you wanted all patent applications filed by "Google LLC," you would write

.. code-block:: python

    google_apps = USApplication.objects.filter(first_named_applicant='Google LLC')

This returns a manager that can access all US Applications where the first named applicant is "Google LLC." You can also apply ordering to the records, such as:

.. code-block:: python

    google_apps = google_apps.order_by('appl_filing_date')

which sorts the applications by filing date. Notice that calls to ".filter," and ".order_by" can be chained, and each chained function returns a unique manager. All the filter and order by parameters accumulate, such that:

.. code-block:: python

    microsoft_pats = (USApplication.objects
                    .filter(first_named_applicant='Microsoft')
                    .filter(app_status='Patented Case')
                    .order_by('patent_issue_date')
                    )

returns a manager that returns all applications with Microsoft listed as the first applicant, that have issued as patents, and in order of their patent issue date (ascending order).

Once you have a manager, the data contained by the manager can be accessed in a few ways. Record objects can be obtained by slicing or iterating on the manager itself.

.. code-block:: python

    app = microsoft_pats[0]
    app
    '<USApplication(appl_id=13656185)>'
    app.patent_title
    'DOWNHOLE APPARATUS FOR ELECTRICAL POWER GENERATION FROM SHAFT FLEXURE'
    app.app_status
    'Patented Case'
    app.patent_number
    '9093875'
    apps = microsoft_pats[:3]
    apps
    '[<USApplication(appl_id=13656185)>, <USApplication(appl_id=13660608)>, <USApplication(appl_id=13672932)>]'

The data can also be accessed in other ways. Just like the Django QuerySet API, Patent Client supports the 
`values <https://docs.djangoproject.com/en/2.1/ref/models/querysets/#values>`_ and 
`values_list <https://docs.djangoproject.com/en/2.1/ref/models/querysets/#values-list>`_ methods.

.. code-block:: python

    microsoft_pats.values('appl_id', 'patent_title')[:3]
    [
        OrderedDict([('appl_id', '13656185'), ('patent_title', 'DOWNHOLE APPARATUS FOR ELECTRICAL POWER GENERATION FROM SHAFT FLEXURE')]), 
        OrderedDict([('appl_id', '13660608'), ('patent_title', 'Hybrid Bearings for Downhole Motors')]), 
        OrderedDict([('appl_id', '13672932'), ('patent_title', 'DOUBLE SHAFT DRILLING APPARATUS WITH HANGER BEARINGS')])
    ]
    microsoft_pats.values_list('patent_title', flat=True)[:3]
    [
        'DOWNHOLE APPARATUS FOR ELECTRICAL POWER GENERATION FROM SHAFT FLEXURE', 
        'Hybrid Bearings for Downhole Motors', 
        'DOUBLE SHAFT DRILLING APPARATUS WITH HANGER BEARINGS'
    ]

Pandas Integration
==================

The models provided by Patent Client are also very useful with the `Pandas <https://pandas.pydata.org/>`_ library.
Because the .values() manager produces OrderedDict objects, dataframes can be created quickly and easily. Just 
specify the columns you want to .values, and feed that into pd.DataFrame.from_records.

.. code-block:: python

    import pandas as pd
    from patent_client import USApplication

    pd.DataFrame.from_records(
        (USApplication.objects
            .filter(first_named_applicant='Microsoft')
            .values('appl_id', 'patent_number', 'patent_title')[:3]
        )
    )
        appl_id patent_number                                       patent_title
    0  13656185       9093875  DOWNHOLE APPARATUS FOR ELECTRICAL POWER GENERA...
    1  13660608       9045941                Hybrid Bearings for Downhole Motors
    2  13672932       9309720  DOUBLE SHAFT DRILLING APPARATUS WITH HANGER BE...
    
Caching
=======

Patent Client uses a file-based cache for all API requests. For the time being, it is a fairly naiive cache, and 
will only return results from the cache if the "filter" and "order by" criteria are exactly the same. 

Because patent data changes over time, cache entries are only good for 1 week by default. After the cache file is
older than that, it will be deleted the next time the library is imported. Or they can be manually deleted whenever.

The individual cache files are also given human-readable names, to the extent practicable, so they can be inspected,
if you wish.

You can see the
cache in your home directory at "~/.patent_client":
::
    $HOME
    |-/.patent_client
      |-epo
      |-uspto_assignments
      |-uspto_examination_data
      |-ptab





