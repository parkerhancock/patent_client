Developer Overview
^^^^^^^^^^^^^^^^^^

The goal of this project is to provide easy-to-use access to public patent data through a simple API.
The general idea is to implement a subset of the 
`Django QuerySet API <https://docs.djangoproject.com/en/2.1/ref/models/querysets/>`_. functionality for accessing
the various sources of patent data. 

To facilitate this, two base classes are provided as scaffolding for adding new APIs - *Manager* and *Model* (both located in the patent_client.util module). The 
Django ORM implements its functionality using three classes - a Model class that models a single record in a database,
a Manager class that provides a generic way of accessing that data, and a QuerySet that allows for sorting / filtering of data.
Here, we omit the separate QuerySet and Manager, and instead use a single Manager class that handles both QuerySet and Manager
functions.

Managers
--------

When filtering, ordering, or values methods are called on a Manager, it returns a new Manager object with a combination of the arguments to the old manager and the new arguments. In this way, any given Manager is *immutable*.

When slicing, the Manager resolves its keyword arguments, and returns Model objects populated with data.

The PTAB client is a particularly clean implementation using the base Manager and Model. Because there is significant overlap between the 
PTAB Trials and Documents endpoints, a common manager is built called PtabManager:

.. code-block:: python

    class PtabManager(Manager):
        page_size = 25

        def get_item(self, key):
            offset = int(key / self.page_size) * self.page_size
            position = (key % self.page_size)
            data = self.request(dict(offset=offset))
            results = data['results']
            return self.get_obj_class()(results[position])
        
        def __len__(self):
            response = self.request()
            response_data = response
            return response_data['metadata']['count']
            
        def request(self, params=dict()):
            params = {**{self.primary_key: self.args}, **self.kwargs, **params}
            params = {inflection.camelize(k, uppercase_first_letter=False): v for (k, v) in params.items()}
            response = session.get(self.base_url, params=params)
            return response.json()

The only methods that must be implemented are "__len__" and "get_item." 

Get_item is just a version of __getitem__ that only returns the record at a specific integer position. The 
generic __getitem__ on Manager simply calls get_item for each item in a slice. The get_item method should return a Model object.

Request is a custom method added to support actually hitting the endpoint. Different custom methods can be added to support
functionality like this. Then, to customize it for Ptab Trials, all we need to do is:

.. code-block:: python

    class PtabTrialManager(PtabManager):
        base_url = 'https://ptabdata.uspto.gov/ptab-api/trials'
        obj_class = 'patent_client.uspto_ptab.PtabTrial'
        primary_key = 'trial_number'

The only two required attributes are "obj_class," which is a string pointing to the class used for specific records, and 
"primary_key" which is used to convert positional arguments into keyword arguments. For example, the call ::

    PtabTrial.objects.get('IPR2016-00800')
    # is effectively converted to
    PtabTrial.objects.get(trial_number='IPR2016-00800')

The "base_url" attribute is used by the request method of the base manager to identify the endpoint. 

Models
------

Because PTABTrials have no special methods (such as downloading a file), the model is simply:

.. code-block:: python

    class PtabTrial(Model):
        objects = PtabDocumentManager()
        def __repr__(self):
            return f'<PtabTrial(trial_number={self.trial_number})>'

The base model takes in its constructor a dictionary of data, and attaches an attribute to the object for each key, containing its value. 
Additional methods can be added in order to add new functionality to the model. For example, the PtabDocument object provides a .download method.
The download method looks like this:

.. code-block:: python

    class PtabDocument(Model):
        objects = PtabDocumentManager()

        def download(self, path='.'):
            url = self.links[1]['href']
            extension = mimetypes.guess_extension(self.media_type)
            base_name = self.title.replace('/', '_') + extension
            name = os.path.join(path, base_name)
            response = session.get(url, stream=True)
            with open(name, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

        def __repr__(self):
            return f'<PtabDocument(title={self.title})>'

Relationships
-------------

What would also be great is if the Trial and Document models could talk to each other. That is, can we fetch PtabDocuments from
a PtabTrial object, and can we fetch the corresponding PtabTrial object from a PtabDocument? Why yes, yes we can.

The .util package also has two functions that make this possible - 'one_to_one' and 'one_to_many'. Both functions work the same way - 
they take a first argument, which is a string locating the other object, and then a keyword argument, where the keyword is a filter criteria,
and the value is an attribute on the current model to use as the value. 

The only difference between the two functions is that "one_to_one" calls objects.get, returing a single object, while "one_to_many"
calls objects.filter, and returns a manager of the related objects. For example, we can use these to link the Trials and Documents as below:

.. code-block:: python

    class PtabTrial(Model):
        ...
        documents = one_to_many('patent_client.PtabDocument', trial_number='trial_number')
        ...

    class PtabDocument(Model):
        ...
        trial = one_to_one('patent_client.PtabTrial', trial_number='trial_number')
        ...

Once these relationships are in place, we can move from one record to the other seamlessly:

.. code-block:: python

    >>> from patent_client import PtabTrial
    >>> a = PtabTrial.objects.get('IPR2017-00001')
    >>> a.documents
    <patent_client.uspto_ptab.PtabDocumentManager object at 0x10f678b38>
    >>> a.documents[0]
    <PtabDocument(title=Petitioner's Power of Attorney)>
    >>> a.documents[0].trial
    <PtabTrial(trial_number=IPR2017-00001)>


