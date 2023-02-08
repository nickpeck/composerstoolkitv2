from typing import Callable

# based on a discussion at https://stackoverflow.com/a/71140509

class IntProperty:
    """
    Class that behaves as an integer, but has a 'value' that is delegated to a callback function.
    Can be used interchangably with integer arguments to most generators/transformers
    """
    def __init__(self, callback: Callable[[], int]):
        self._callback = callback

    @property
    def value(self):
        return self._callback()

    def _do_relational_method(self, other, method_to_run):
        func = getattr(self.value, method_to_run)
        if type(other) is IntProperty:
            return func(other.value)
        else:
            return func(other)

    def __add__(self, other):
        return self._do_relational_method(other, "__add__")

    def __sub__(self, other):
        return self._do_relational_method(other, "__sub__")

    def __mul__(self, other):
        return self._do_relational_method(other, "__mul__")

    def __truediv__(self, other):
        return self._do_relational_method(other, "__truediv__")

    def __floordiv__(self, other):
        return self._do_relational_method(other, "__floordiv__")

    def __eq__(self, other):
        return self._do_relational_method(other, "__eq__")

    def __neq__(self, other):
        return self._do_relational_method(other, "__neq__")

    def __lt__(self, other):
        return self._do_relational_method(other, "__lt__")

    def __gt__(self, other):
        return self._do_relational_method(other, "__gt__")

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return self.__str__()
