import inflection
from collections import OrderedDict
from dateutil.parser import parse as parse_dt


class Model(object):
    """
    Model Base Class

    Takes in a dictionary of data and :
    1. Automatically inflects all keys to underscore_case
    2. Converts any value that has "date" or "datetime" into the appropriate type
    3. Appends all keys in the dictionary as attributes on the object
    4. Attaches the original inflected data dictionary as Model.data
    """

    attrs = None

    def __init__(self, data, backref=None, **kwargs):

        self.data = self._convert_data(data)
        try:
            for k in self.attrs:
                setattr(self, k, self.data.get(k, None))
        except AttributeError as e:
            pass
        except Exception as e:
            self.error = e
        self.backref = backref

    def __eq__(self, other):
        key = self.attrs[0]
        return getattr(self, key, None) == getattr(other, key, None)

    def __iter__(self):
        for attr in self.attrs:
            value = getattr(self, attr, None)
            if value:
                yield (attr, value)

    def _convert_data(self, data):
        if isinstance(data, list):
            return [self._convert_data(a) for a in data]
        elif isinstance(data, dict):
            dictionary = {
                inflection.underscore(k): self._convert_data(v)
                for (k, v) in data.items()
            }
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

    def __repr__(self):
        """Default representation"""
        repr_string = (
            f"<{self.__class__.__name__} {self.attrs[0]}={getattr(self, self.attrs[0])}"
        )
        if hasattr(self, "error"):
            repr_string += f" error={self.error}"
        return repr_string + ">"

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and dict(self) == dict(other)

    def as_dict(self):
        return OrderedDict(self)
