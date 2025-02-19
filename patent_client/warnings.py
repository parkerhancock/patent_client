import warnings
import functools

class DeprecatedMeta(type):
    def __new__(mcls, name, bases, namespace, **kwargs):
        deprecation_msg = kwargs.get('deprecation_msg', "This class is deprecated")
        
        # Wrap every public callable attribute using the custom message
        for attr_name, attr_value in namespace.items():
            if not attr_name.startswith('_'):
                if callable(attr_value):
                    namespace[attr_name] = mcls._wrap_method(attr_value, name, deprecation_msg)
                elif isinstance(attr_value, classmethod):
                    # Handle class methods specially
                    original_func = attr_value.__func__
                    wrapped_func = mcls._wrap_method(original_func, name, deprecation_msg)
                    namespace[attr_name] = classmethod(wrapped_func)
                    
        cls = super().__new__(mcls, name, bases, namespace)
        cls.__deprecation_msg__ = deprecation_msg
        return cls

    @staticmethod
    def _wrap_method(func, cls_name, msg):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(f"{cls_name} is deprecated: {msg}", DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper