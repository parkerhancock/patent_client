from collections import OrderedDict
from hashlib import md5
import json

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


def accessor(obj, accessor):
    k_list = accessor.split('__')
    first_key = k_list.pop(0)
    name_list = [first_key, ]
    if hasattr(obj, first_key):
        item = getattr(obj, first_key)
    else:
        item = obj.dict.get(first_key, None)
    while k_list:
        key = k_list.pop(0)
        if item == None:
            name_list.append(key)
            continue
        try:
            key = int(key)
        except ValueError:
            name_list.append(key)
        if type(item) == list:
            try:
                item = item[key]
            except IndexError:
                item=None
        else:
            item = item.get(key, None)
    key = '_'.join(name_list)
    return (key, item)


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
                    key, item = accessor(obj, k)
                    fdata[key] = item
                data = fdata
            if self.values_list:
                data = tuple(data[k] for k, v in data.items())
                if len(self.fields) == 1 and self.flat:
                    data = data[0]
            return data