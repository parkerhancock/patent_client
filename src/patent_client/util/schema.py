from marshmallow import fields
from .manager import ListManager 

class ListField(fields.List):
    def _deserialize(self, *args, **kwargs):
        out = super(ListField, self)._deserialize(*args, **kwargs)
        return ListManager(out)


from typing import *
import datetime
from functools import partial
from dateutil.parser import parse as parse_dt

default_date_parser = partial(parse_dt, fuzzy=True)

class Schema():
    __model__ = NotImplementedError()

    def __init__(self):
        self.fields = {k: getattr(self, k) for k in self.__dir__() if isinstance(getattr(self, k), Field)}
        for name, field in self.fields.items():
            if field.data_key == None:
                field.data_key = name
        
    def deserialize(self, data):
        output = dict()
        for k, v in self.fields.items():
            output[k] = v.deserialize(data)
        try:
            return self.__model__(**output)
        except TypeError as e:
            raise TypeError(f"Model {self.__model__} failed to load!: {e.args[0]}")

class Field():
    output_type = Any
    def __init__(self, data_key=None, required=True, formatter=lambda x: x, pre_load=lambda x:x, debug=False):
        self.data_key = data_key
        self.formatter = formatter
        self.pre_load = pre_load
        self.required = required
        self.debug=debug
        
    def fetch(self, data):
        output = data
        try:
            for k in self.data_key.split('.'):
                output = output[k]
        except KeyError as e:
            if not self.required:
                return None
            else:
                print(f"Failed to fetch required data {self.data_key} from {data}")
                raise e
        except TypeError as e:
            print(f"Failed to to fetch {k} from {output}! original data was {data}")
            raise e
        return output
    
    def load(self, data):
        return data
    
    def deserialize(self, data) -> Any:
        if self.debug: print(f"Deserializing {type(self)} with data key {self.data_key}")
        data = self.fetch(data)
        if data is None and not self.required:
            return None
        if self.debug: print(f"Raw Data is {repr(data)}")
        data = self.pre_load(data)
        if self.debug: print(f"Pre-Loaded data is {repr(data)}")
        data = self.load(data)
        if self.debug: print(f"Loaded data is {repr(data)}")
        data = self.formatter(data)
        if self.debug: print(f"Formatted data is {repr(data)}")
        return data
    
# Basic Data Type Fields

class StringField(Field):
    def load(self, data) -> str:
        return str(data).strip() if data is not None else None
   
class IntField(Field):
    def __init__(self, data_key=None, allow_none=False, *args, **kwargs, ):
        super(IntField, self).__init__(data_key, *args, **kwargs)
        self.allow_none = allow_none
    
    def load(self, data) -> int:
        if data is None and self.allow_none:
            return int(0)
        else:
            return int(data)
    
class FloatField(Field):
    def load(self, data) -> float:
        return float(data)

class DatetimeField(Field):
    def __init__(self, data_key=None, converter=default_date_parser, *args, **kwargs):
        super(DatetimeField, self).__init__(data_key, *args, **kwargs)
        self.converter = converter

    def load(self, data) -> datetime.date:
        if not data:
            return None
        elif isinstance(data, datetime.datetime):
            return data
        else:
            return self.converter(data)

class DateField(DatetimeField):
    def load(self, data) -> datetime.date:
        data = super(DateField, self).load(data)
        if type(data) == datetime.date:
            return data
        if type(data) == datetime.datetime:
            return data.date()

# Utility Field Types

class ConstantField(Field):
    def __init__(self, constant=None, *args, **kwargs):
        super(ConstantField, self).__init__(*args, **kwargs)
        self.constant = constant
    
    def deserialize(self, data):
        return self.constant

class CombineField(Field):
    def __init__(self, combine_func=None, output_type=None, data_key=None, **fields):
        self.fields = fields
        self.output_type = output_type
        self.combine_func = combine_func if combine_func is not None else lambda x: x
        self.data_key=data_key
        
    def deserialize(self, data):
        try:
            elements = {k: v.deserialize(data) for k, v in self.fields.items()}
            return self.load(elements)
        except KeyError:
            return None
        
    def load(self, data):
        return self.combine_func(data)
       
class Nested(Field):
    def __init__(self, schema, many=False, data_key=None, required=True, formatter=lambda x: x, pre_load = lambda x: x, debug=False):
        self.schema = schema() if callable(schema) else schema
        self.many = many
        self.data_key = data_key
        self.output_type = list if many else dict
        self.formatter=formatter
        self.pre_load = pre_load
        self.required = required
        self.debug = debug
        
    def deserialize(self, data):
        data = super(Nested, self).deserialize(data)
        if data is None:
            return list() if self.many else None
        if self.many == True:
            return list(self.schema.deserialize(item) for item in data)
        else:
            try:
                return self.schema.deserialize(data)
            except TypeError as e:
                raise TypeError(f"{e.args[0]}, Did you intend many=True?")
        
