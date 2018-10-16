FILTERS = [
    #'exact',
    #'iexact',
    #'contains',
    #'icontains',
    #'in',
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
]


def accessor(obj, accessor):
    k_list = accessor.split('__')
    first_key = k_list.pop(0)
    name_list = [first_key, ]
    if hasattr(obj, first_key):
        item = getattr(obj, first_key)
    else:
        item = obj.dict[first_key]
    while k_list:
        key = k_list.pop(0)
        try:
            key = int(key)
        except ValueError:
            name_list.append(key)
        item = item[key]
    key = '_'.join(name_list)
    return (key, item)


class BaseSet:
    def values(self, *fields):
        return ValuesSet(self, *fields)
    
    def values_list(self, *fields, flat=False):
        return ValuesSet(self, *fields, values_list=True, flat=flat)
    
class ValuesSet:
    def __init__(self, obj_set, *fields, values_list=False, flat=False):
        self.obj_set = obj_set
        self.fields = fields
        self.values_list = values_list
        self.flat = flat

    def __len__(self):
        return len(self.obj_set)

    def __repr__(self):
        return f'<ValuesSet(obj_set={repr(self.obj_set)})>'

    def __getitem__(self, key):
        if type(key) == slice:
            indices = list(range(len(self)))[key.start : key.stop : key.step]
            return [self.__getitem__(index) for index in indices]
        else:
            if key < 0:
                key = len(self) - key
            obj = self.obj_set[key]
            data = obj.dict
            if self.fields:
                fdata = dict()
                for k in self.fields:
                    key, item = accessor(obj, k)
                    fdata[key] = item
                data = fdata
            if self.values_list:
                data = tuple(data[k] for k, v in data.items())
                if len(self.fields) == 1 and self.flat:
                    data = data[0]
            return data