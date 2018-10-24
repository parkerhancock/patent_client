from collections import OrderedDict
from hashlib import md5
import json
from importlib import import_module
from copy import deepcopy
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
        self.data = {inflection.underscore(k):v for (k,v) in data.items()}
        for k, v in self.data.items():
            try:
                if 'datetime' in k and type(v) == str:
                    self.data[k] = parse_dt(v)
                elif 'date' in k and type(v) == str:
                    self.data[k] = parse_dt(v).date()
            except ValueError: # Malformed datetimes:
                self.data[k] = None
            setattr(self, k, self.data[k])


class Manager:
    def __init__(self, *args, **kwargs):
        self.args = args,
        self.kwargs = kwargs

    def filter(self, *args, **kwargs):
        return self.__class__(*args, *self.args, **{**kwargs, **self.kwargs})

        """ Next step would be to implement application-layer filters
        for key, value in kwargs.items():
            selector, operator = key.rsplit('__', 1)
            if operator not in FILTERS:
                operator = 'eq'
                accessor = key
            selector_lambda = lambda x: accessor(x, accessor)
            self.objs = filter(lambda x: FILTERS[operator](selector_lambda(x), value), self.objs)
        """
    
    def order_by(self, *args, **kwargs):
        kwargs = deepcopy(self.kwargs)
        if 'sort' not in kwargs:
            kwargs['sort'] = list()
        kwargs['sort'] += args
        return self.__class__(*self.args, **{**kwargs, **self.kwargs})
    
    def get(self, *args, **kwargs):
        args = [a for a in args + self.args if a]
        manager = self.__class__().filter(*args, **{**self.kwargs, **kwargs})
        if len(manager) > 1:
            doc_nos = '\n'.join([str(r) for r in manager])
            raise ValueError('More than one document found!\n' + doc_nos)
        return manager.first()

    def exclude(self, **kwargs):
        raise NotImplemented(f'{self.__class__} has no exclude method')

    def count(self):
        return len(self)

    def __len__(self):
        raise NotImplemented(f'{self.__class__} has no length method')

    def first(self):
        return self[0]

    def all(self):
        return iter(self)

    def values(self, *fields):
        return self.__class__(
        *self.args, 
        **{
            **self.kwargs, 
            **dict(
                values__fields=fields,
                values__list=False)}
        )
    
    def values_list(self, *fields, flat=False):
        return self.__class__(
        *self.args, 
        **{
            **self.kwargs, 
            **dict(
                values__fields=fields,
                values__list=True,
                values__flat=flat,
                )}
        )
        self.kwargs['values__fields'] = fields
        return ValuesSet(self, *fields, values_list=True, flat=flat)

    def __getitem__(self, key):
        if type(key) == slice:
            indices = list(range(len(self)))[key.start : key.stop : key.step]
            return [self.__getitem__(index) for index in indices]
        else:
            obj = self.get_item(key)
            if 'values__fields' in self.kwargs:
                data = obj.data
                fdata = OrderedDict()
                for k in self.kwargs['values__fields']:
                    key = k.replace('__', '_')
                    value = recur_accessor(obj, k)
                    fdata[key] = value 
                data = fdata
                if self.kwargs.get('values__list', False):
                    data = tuple(data[k] for k, v in data.items())
                    if len(self.kwargs['values__fields']) == 1 and self.kwargs['values__flat']:
                        data = data[0]
                return data
            else:
                return obj
                