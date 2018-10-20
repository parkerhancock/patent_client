from collections import OrderedDict
from hashlib import md5
import json
from importlib import import_module
from dateutil.parser import parse as parse_dt
import inflection

def hash_dict(dictionary):
    return md5(json.dumps(dictionary, sort_keys=True).encode('utf-8')).hexdigest()


FILTERS = {
    #'exact',
    #'iexact',
    #'contains',
    #'icontains',
    'in': lambda x, y: x in y,
    'eq': lambda x, y: x == y,
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
    module_name, class_name = class_name.rsplit('.', 1)
    @property
    def get(self):
        klass = getattr(import_module(module_name), class_name)
        filter_obj = {k: getattr(self, v) for (k, v) in mapping.items()}
        return klass.objects.get(**filter_obj)
    return get

def one_to_many(class_name, **mapping):
    module_name, class_name = class_name.rsplit('.', 1)
    @property
    def get(self):
        klass = getattr(import_module(module_name), class_name)
        filter_obj = {k: getattr(self, v) for (k, v) in mapping.items()}
        return klass.objects.filter(**filter_obj)
    return get


def recur_accessor(obj, accessor):
    if '__' not in accessor:
        a = accessor
        rest = None
    else:
        a, rest = accessor.split('__', 1)
    
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
        except (KeyError, TypeError):
            new_obj=None
    if not rest:
        return new_obj
    else:
        return recur_accessor(new_obj, rest)

class Model(object):
    def __init__(self, data):
        self.dict = {inflection.underscore(k):v for (k,v) in data.items()}
        for k, v in self.dict.items():
            try:
                if 'datetime' in k and type(v) == str:
                    self.dict[k] = parse_dt(v)
                elif 'date' in k and type(v) == str:
                    self.dict[k] = parse_dt(v).date()
            except ValueError: # Malformed datetimes:
                self.dict[k] = None
            setattr(self, k, self.dict[k])


class BaseSet:
    def filter(self, **kwargs):
        for key, value in kwargs.items():
            selector, operator = key.rsplit('__', 1)
            if operator not in FILTERS:
                operator = 'eq'
                accessor = key
            selector_lambda = lambda x: accessor(x, accessor)
            self.objs = filter(lambda x: FILTERS[operator](selector_lambda(x), value), self.objs)

    def values(self, *fields):
        return ValuesSet(self, *fields)
    
    def values_list(self, *fields, flat=False):
        return ValuesSet(self, *fields, values_list=True, flat=flat)
    
class ValuesSet:
    def __init__(self, objs, *fields, values_list=False, flat=False):
        self.objs = objs
        self.fields = fields
        self.values_list = values_list
        self.flat = flat

    def __len__(self):
        return len(self.objs)

    def __repr__(self):
        return f'<ValuesSet(objs={repr(self.objs)})>'

    def __getitem__(self, key):
        if type(key) == slice:
            indices = list(range(len(self)))[key.start : key.stop : key.step]
            return [self.__getitem__(index) for index in indices]
        else:
            if key < 0:
                key = len(self) - key
            obj = self.objs[key]
            data = obj.dict
            if self.fields:
                fdata = OrderedDict()
                for k in self.fields:
                    key = k.replace('__', '_')
                    value = recur_accessor(obj, k)
                    fdata[key] = value 
                data = fdata
            if self.values_list:
                data = tuple(data[k] for k, v in data.items())
                if len(self.fields) == 1 and self.flat:
                    data = data[0]
            return data