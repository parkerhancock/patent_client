import importlib
import json
from collections import OrderedDict
from copy import deepcopy
from hashlib import md5

import inflection
from dateutil.parser import parse as parse_dt


def hash_dict(dictionary):
    return md5(json.dumps(dictionary, sort_keys=True).encode("utf-8")).hexdigest()


FILTERS = {
    #'exact',
    #'iexact',
    #'contains',
    #'icontains',
    "in": lambda x, y: x in y,
    "eq": lambda x, y: x == y,
    #'gt',
    #'gte',
    #'lt',
    #'lte',
    #'startswith',
    #'istartswith',
    #'endswith',
    #'iendswith',
    #'range',
    #'date',
    #'year','
    #'month',
    #'day',
    #'week',
    #'week_day',
    #'quarter','
    #'time',
    #'hour','
    #'minute',
    #'second',
    #'isnull',
    #'regex',
    #'iregex',
}


def one_to_one(class_name, **mapping):
    module_name, class_name = class_name.rsplit(".", 1)

    @property
    def get(self):
        klass = getattr(importlib.import_module(module_name), class_name)
        filter_obj = {k: getattr(self, v) for (k, v) in mapping.items()}
        return klass.objects.get(**filter_obj)

    return get


def one_to_many(class_name, **mapping):
    module_name, class_name = class_name.rsplit(".", 1)

    @property
    def get(self):
        klass = getattr(importlib.import_module(module_name), class_name)
        filter_obj = {k: getattr(self, v) for (k, v) in mapping.items()}
        return klass.objects.filter(**filter_obj)

    return get


def recur_accessor(obj, accessor):
    if "__" not in accessor:
        a = accessor
        rest = None
    else:
        a, rest = accessor.split("__", 1)

    if hasattr(obj, a):
        new_obj = getattr(obj, a)
        if callable(new_obj):
            new_obj = new_obj()
    else:
        try:
            a = int(a)
        except ValueError:
            pass
        try:
            new_obj = obj[a]
        except (KeyError, TypeError, IndexError):
            new_obj = None
    if not rest:
        return new_obj
    else:
        return recur_accessor(new_obj, rest)


class Model(object):
    """
    Model Base Class

    Takes in a dictionary of data and :
    1. Automatically inflects all keys to underscore_case
    2. Converts any value that has "date" or "datetime" into the appropriate type
    3. Appends all keys in the dictionary as attributes on the object
    4. Attaches the original inflected data dictionary as Model.data
    """

    def __init__(self, data, **kwargs):
        self.data = self._convert_data(data)

        for k, v in self.data.items():
            setattr(self, k, self.data[k])
    
    def _convert_data(self, data):
        if isinstance(data, list):
            return [self._convert_data(a) for a in data]
        elif isinstance(data, dict):
            dictionary = {inflection.underscore(k): self._convert_data(v) for (k, v) in data.items()}
            for k, v in dictionary.items():
                try:
                    if "datetime" in k and type(v) == str:
                        dictionary[k] = parse_dt(v)
                    elif "date" in k and type(v) == str:
                        dictionary[k] = parse_dt(v).date()
                except ValueError:  # Malformed datetimes:
                    dictionary[k] = None
            return dictionary
        else:
            return data

    
    def as_dict(self):
        """Convert object to dictionary, recursively converting any objects to dictionaries themselves"""
        output = {key: getattr(self, key) for key in self.attrs if hasattr(self, key)}
        for k, v in output.items():
            if isinstance(v, list):
                output[k] = [i.asdict() if hasattr(i, "asdict") else i for i in v]
            if hasattr(v, "asdict"):
                output[k] = v.asdict()
        return output

    def __repr__(self):
        """Default representation"""
        primary_key = getattr(self, "primary_key")
        return f"<{self.__class__.__name__} {primary_key}={getattr(self, primary_key)}>"

    
    def __hash__(self):
        return hash(self.__repr__())
        

    def __eq__(self, other):
        return ((self.__class__ == other.__class__)
        and (hash(self) == hash(other)))
    
    def __ne__(self, other):
        return not self.__eq__(other)



class Manager:
    """
    Manager Base Class

    This class is essentially a configurable generator. It is intended to be initialized 
    as an empty object at Model.objects. Users can then modify the manager by calling either:
        
        Manager.filter -> adds filter criteria
        Manager.sort -> adds sorting criteria
        Manager.options -> adds key:value options

    All methods should return a brand-new manager with the appropriate parameters re-set. The 
    Manager also has a special method to fetch a single matching object:

        Manager.get -> adds filter critera, and returns the first object if only one object is found, else raises an Exception

    The manager's attributes are stored in a dictionary at Manager.config. Config has the following structure:

        {
            'filter': {
                key: value,
                key: value,
            },
            'order_by': [value, value, value],
            'values': [value, value, value]
            'options': {
                key: value
            }
        }
        
    """
    test_mode = False
    
    def __init__(self, config=dict(filter=dict(), order_by=list(), options=dict()), values=list()):
        self.config = config

    def filter(self, *args, **kwargs):
        if args:
            kwargs[self.primary_key] = args
        for k in kwargs.keys():
            if k not in self.allowed_filters:
                raise ValueError(f'{k} is not a permitted filter parameter')

        new_config = deepcopy(self.config)
        new_config['filter'] = {**new_config['filter'], **kwargs}
        return self.__class__(new_config)

    def order_by(self, *args):
        """Take arguments, and store in a special keyword argument called 'sort' """
        new_config = deepcopy(self.config)
        new_config['order_by'] = list(new_config['order_by']) + list(args)
        return self.__class__(new_config)

    def set_options(self, **kwargs):
        new_config = deepcopy(self.config)
        new_config['options'] = {**new_config['options'], **kwargs}
        return self.__class__(new_config)

    def get(self, *args, **kwargs):
        """Implement a new manager with the requested keywords, and if the length is 1,
        return that record, else raise an exception"""
        manager = self.filter(*args, **kwargs)
        if len(manager) > 1:
            doc_nos = "\n".join([str(r) for r in manager])
            raise ValueError("More than one document found!\n" + doc_nos)
        return manager.first()

    def count(self):
        return len(self)

    def __len__(self):
        raise NotImplementedError(f"{self.__class__} has no length method")

    def first(self):
        try:
            return self[0]
        except StopIteration:
            raise ValueError('No matching records found!')

    def all(self):
        return iter(self)

    def values(self, *fields):
        """Return new manager with special keywords 'values__fields' and 'values__list'"""
        new_config = deepcopy(self.config)
        new_config['values'] = fields
        new_config['options']['values_iterator'] = True
        new_config['options']['values_list'] = False
        return self.__class__(new_config)

    def values_list(self, *fields, flat=False):
        """Same as values, but adds an additional parameter for "flat" lists """
        new_config = deepcopy(self.config)
        new_config['values'] = fields
        new_config['options']['values_iterator'] = True
        new_config['options']['values_list'] = True
        new_config['options']['values_list_flat'] = flat
        return self.__class__(new_config)


    def get_item(self, key):
        raise NotImplementedError(f"{self.__class__} has no get_item method")

    #def __iter__(self):
    #    """Returns a generator for items from this manager"""
    #    raise NotImplementedError(f"{self.__class__} has no iterator method!")

    def __getitem__(self, key):
        """resolves slices and keys into Model objects. Relies on .get_item(key) to obtain
        the record itself"""
        if type(key) == slice:
            indices = list(range(len(self)))[key.start : key.stop: key.step]
            return [self.__getitem__(index) for index in indices]
        else:
            if key >= len(self):
                raise StopIteration
            obj = self.get_item(key)
            options = self.config['options']

            if options.get('values_iterator') == True:
                data = obj.data
                fdata = OrderedDict()
                for k in self.config["values"]:
                    value = recur_accessor(obj, k)
                    fdata[k] = value
                data = fdata
                if options.get('values_list', False):
                    data = tuple(data[k] for k, v in data.items())
                    if (
                        len(self.config['values']) == 1
                        and options.get('values_list_flat', False)
                    ):
                        data = data[0]
                return data
            else:
                return obj
    
