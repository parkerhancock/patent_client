
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

    def __getitem__(self, key):
        if type(key) == slice:
            indices = list(range(len(self)))[key.start : key.stop : key.step]
            return [self.__getitem__(index) for index in indices]
        else:
            if key < 0:
                key = len(self) - key
            data = self.obj_set[key].dict
            #import pdb; pdb.set_trace()
            if self.fields:
                data = {k:data[k] for k in self.fields}
            if self.values_list:
                data = tuple(data[k] for k, v in data.items())
                if len(self.fields) == 1 and self.flat:
                    data = data[0]
            return data