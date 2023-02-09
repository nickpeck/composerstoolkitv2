"""Defines some helper classes that wrap python-builtin types.
These allow the value of the object to be defered to a callback function.
In the case of composerstoolkit - this is useful in the cases where we
might want to interchangably pass a primitive or computed variable into a transformer function,
without changing the interface of that function (see examples\33_dynamic_properties.py)
"""

class DelegateMetaclass(type):
    OPERATORS = []

    def __new__(meta, name, bases, attrs):

        def __init__(self, cb):
            self._cb = cb

        def __str__(self):
            return str(self._cb())

        def __repr__(self):
            return self.__str__()

        def delegator(oper):
            def f(self, other=None):
                return delegate(self, oper, other)
            return f

        def delegate(self, method_to_run, other=None):
            func = getattr(self._cb(), method_to_run)
            if other is None:
                    return func()
            if type(other) is type(self):
                return func(other._cb())
            else:
                return func(other)

        for oper in meta.OPERATORS:
            if oper not in attrs:
                attrs[oper] = delegator(oper)

        attrs.update({
            '__init__': __init__,
            '__str__': __str__,
            '__repr__': __repr__
        })

        return type.__new__(meta, name,   bases, attrs)


class IntType(DelegateMetaclass):
    OPERATORS = ['__abs__', '__add__', '__sub__', '__mul__', '__div__',
                 '__radd__', '__rsub__', '__rmul__', '__truediv__', '__rtruediv__',
                 '__floordiv__', '__rfloordiv__', '__eq__',
                 '__lt__', '__gt__', '__neg__']

class ListType(DelegateMetaclass):
    OPERATORS = ['__len__', '__getitem__',
                 '__iter__', '__reversed__']

class SetType(DelegateMetaclass):
    OPERATORS = ['__eq__', '__hash__',
                 'copy', 'difference', 'discard', 'intersection',
                 'isdisjoint', 'issubset', 'issuperset',
                'symmetric_difference', 'union']

class StrType(DelegateMetaclass):
    OPERATORS = ['__len__', '__getitem__',
                 '__iter__', '__reversed__',  'capitalize', 'casefold', 'center',
                 'count', 'encode', 'endswith', 'expandtabs', 'find', 'format',
                 'format_map', 'index', 'isalnum', 'isalpha', 'isascii', 'isdecimal',
                 'isdigit', 'isidentifier', 'islower', 'isnumeric', 'isprintable', 'isspace', 'istitle', 'isupper',
                'join', 'ljust', 'lower', 'lstrip', 'maketrans', 'partition', 'replace', 'rfind', 'rindex',
                 'rjust', 'rpartition', 'rsplit', 'rstrip', 'split', 'splitlines',
                 'startswith', 'strip', 'swapcase', 'title', 'translate', 'upper', 'zfill']



class IntProp(metaclass=IntType):
    pass

class BoolProp(IntProp):
    pass

class ListProp(metaclass=ListType):
    pass

class SetProp(metaclass=SetType):
    pass

class StrProp(metaclass=StrType):
    pass
