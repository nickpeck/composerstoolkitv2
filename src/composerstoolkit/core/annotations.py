from __future__ import annotations
from dataclasses import dataclass, field
import os
from time import sleep
import signal
import sys
from typing import Any, Dict, List, Optional, Callable, Iterator, Set
from threading import Thread

import itertools
import functools

from midiutil.MidiFile import MIDIFile # type: ignore
from mido import MidiTrack, Message # type: ignore

class ReprWrapper:
    """helper to override __repr__ for a function for debugging purposes
    see https://stackoverflow.com/questions/10875442/possible-to-change-a-functions-repr-in-python
    """
    def __init__(self, rep, func):
        self._repr = rep
        self._func = func
        functools.update_wrapper(self, func)
    def __call__(self, *args, **kw):
        return self._func(*args, **kw)
    def __repr__(self):
        return self._repr(self._func)

def withrepr(reprfun):
    """decorator for ReprWrapper"""
    def _wrap(func):
        return ReprWrapper(reprfun, func)
    return _wrap

class Transformer():
    """Wrapper class for transformer functions.
    Can be used as a decorator, making it easy to
    re-use a transformation with a given configuration.
    """

    def __init__(self, functor):
        self._functor = functor

    def __call__(self, *args, **kwargs):
        @withrepr(
            lambda x: "<Transformer: {}{}>".format(
                self._functor.__name__, args + tuple(kwargs.items())))
        def transform(instance: Sequence) -> Sequence:
            nonlocal args
            nonlocal kwargs
            _kwargs = kwargs
            _args = [instance] + list(args)
            return self._functor(*_args, **_kwargs)
        return transform

    def __str__(self):
        return "<Transformer : {}>".format(self._functor.__name__)

class Constraint():
    """Wrapper class for constraint functions.
    Can be used as a decorator, making it easy to
    re-use a constraint against different contexts
    """
    class Konstraint:
        def __init__(self, functor, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            self.functor = functor
        def __call__(self, context: Context) -> bool:
            _kwargs = self.kwargs
            _args = [context] + list(self.args)
            return self.functor(*_args, **_kwargs)
        def __or__(self, other):
            return lambda c: self(c) | other(c)
        def __repr__(self):
            return "<Constraint: {}{}>".format(
            self.functor.__name__, self.args + tuple(self.kwargs.items()))

    def __init__(self, functor):
        self._functor = functor

    def __call__(self, *args, **kwargs):
        return Constraint.Konstraint(self._functor, *args, **kwargs)

    def __str__(self):
        return "<Constraint : {}>".format(self._functor.__name__)
