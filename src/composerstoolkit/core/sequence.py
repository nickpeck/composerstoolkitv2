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

import fluidsynth # type: ignore
from midiutil.MidiFile import MIDIFile # type: ignore
from mido import MidiTrack, Message # type: ignore

@dataclass
class Event:
    """Represents a discrete musical event, which might be a single note,
    chord or meta event (eg dynamic, or controller change).
    """
    pitches: List[int] = field(
        default_factory = lambda: []
    )
    duration: int = 0
    meta: Dict[str, Any] = field(
        default_factory = lambda: {}
    )

    def to_edges(self, offset: int=0) -> List[Edge]:
        """Return the event as a single edge, or a list
        of connected edges, in the case that there are multiple pitches
        (a chord).
        """
        edges = []
        for pitch in self.pitches:
            edges.append(Edge(
                pitch = pitch,
                start_time = offset,
                end_time = self.duration + offset
            ))
        return edges

    def to_pitch_class_set(self):
        return {*[p % 12 for p in self.pitches]}

@dataclass
class Sequence:
    """Represents a linear sequence of events (single notes, chords or 'meta' type
    events).
    """
    events: Iterator[Event] = field(
        default_factory = lambda: iter(())
    )
    #memento: Optional[Sequence] = None

    def __post_init__(self):
        if isinstance(self.events, list):
            self.events = iter(self.events[:])

    @property
    def pitches(self) -> Iterator[int]:
        """Return a generator expression yielding the ordered list of MIDI
        pitch numbers that comprise the sequence.
        """
        return itertools.chain.from_iterable((e.pitches for e in self.events))

    @property
    def durations(self) -> Iterator[int]:
        """Return a generator expression yielding the ordered list of durations
        that comprise the sequence.
        """
        return (e.duration for e in list(self.events))

    @classmethod
    def from_generator(cls, generator: Iterator[Event]) -> Sequence:
        """Return a new Sequence using the seed of a given generator function.
        """
        return cls(
            events = generator
        )

    def transform(self, transformer: Callable[[Sequence], Iterator[Event]]) -> Sequence:
        """Convenience method for applying a transformation function to the sequence.
        Return the new sequence, allowing transformations to be chained in a single
        statement.
        """
        new_seq = self.__class__(
            events = transformer(self))
        return new_seq

    def bake(self) -> FiniteSequence:
        """Convert a sequence into a FiniteSequence
        """
        return FiniteSequence(list(self.events))

    def tap(self) -> Sequence:
        """Returns a copy of the sequence.
        This can be advanced through without affecting the iteration
        state of the current sequence.
        """
        a,b = itertools.tee(seq.events)
        self.events = a
        return Sequence(events=b)

    def __add__(self, other):
        """Allows sequences to be added together.
        """
        events = itertools.chain.from_iterable([self.events, other.events])
        return self.__class__(events=events)

@dataclass
class FiniteSequence:
    events: List[Event]

    @property
    def pitches(self) -> List[int]:
        """Return a list of the ordered list of MIDI
        pitch numbers that comprise the sequence.
        """
        return [pitch for event in self.events for pitch in event.pitches]

    @property
    def durations(self) -> List[int]:
        """Return a list of the ordered list of durations
        that comprise the sequence.
        """
        return [e.duration for e in self.events]

    @property
    def duration(self) -> int:
        """Return the total duration of the Sequence
        """
        return sum(self.durations)

    def to_sequence(self) -> Sequence:
        return Sequence(events=iter(self.events))

    def to_pitch_set(self) -> Set[int]:
        """Return a set of unique MIDI pitch numbers that comprise the sequence.
        """
        return set(self.pitches)

    def to_pitch_class_set(self):
        """Return the set of unique pitch classes (0..11) that comprise the sequence.
        """
        pitch_set = self.to_pitch_set()
        return {*[p % 12 for p in pitch_set]}

    def to_graph(self, offset: int=0) -> Graph:
        """Return a pitch graph representation of the sequence.
        """
        edges: List[Edge] = []
        for event in self.events:
            edges = edges + event.to_edges(offset)
        return Graph(edges)

    def event_at(self, beat_offset: int) -> Optional[Event]:
        if beat_offset > self.duration:
            return None
        offset = 0
        for event in self.events:
            offset = offset + event.duration
            if offset >= beat_offset:
                return event
        return None

    def variations(self,
        transformer: Callable[[Sequence], Iterator[Event]],
        n_times: Optional[int] = None,
        repeats_per_var=1) -> Sequence:

        def compose_vars():
            i=0
            def is_terminal():
                if n_times is None:
                    return True
                return i <= n_times

            _events = self.events[:]

            while is_terminal():
                if i == 0:
                    for _i in range(repeats_per_var):
                        for event in self.events:
                            yield event
                else:
                    cloned = FiniteSequence(_events)
                    new_seq = transformer(Sequence(cloned.events))
                    _events = []
                    for event in new_seq:
                        _events.append(event)
                    for _i in range(repeats_per_var):
                        for event in _events:
                            yield event
                i = i + 1
        return Sequence(events=compose_vars())

    def __getitem__(self, slice_index):
        start, stop, step = None, None, None
        try:
            start, stop, step = slice_index
            sliced_events = self.events[start:stop:step]
        except TypeError:
            try:
                start, stop = slice_index
                sliced_events = self.events[start:stop]
            except TypeError:
                start = slice_index
                sliced_events = self.events[start]
                if not isinstance(sliced_events , list):
                    sliced_events = [sliced_events]

        return self.__class__(events=sliced_events)

@dataclass(frozen=True)
class Context:
    event: Event
    sequence: Sequence
    beat_offset: int = 0
    previous: Optional[Event] = None
