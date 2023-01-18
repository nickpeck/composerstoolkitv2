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

from . graph import Edge, Graph

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
    
    def extend(self, pitches=None, duration=None, meta=None) -> Event:
        if pitches is None:
            pitches = self.pitches.copy()
        if duration is None:
            duration = self.duration
        if meta is None:
            meta = self.meta.copy()
        return Event(pitches=pitches, duration=duration, meta=meta)

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

    def movement_cost_to(self, event: Event) -> int:
        other_pcs = sorted(list(event.to_pitch_class_set()))
        self_pcs = sorted(list(self.to_pitch_class_set()))
        costs = []
        for i, pc in enumerate(self_pcs):
            try:
                cost = abs(other_pcs[i] - pc)
                if cost > 6:
                    cost = cost - 6
                costs.append(cost)
            except IndexError:
                break
        return sum(costs)

    def __hash__(self):
        return hash(" ".join([str(p) for p in self.pitches])) + hash(self.duration)

@dataclass
class Sequence:
    """Represents a linear sequence of events (single notes, chords or 'meta' type
    events).
    """
    events: Iterator[Event] = field(
        default_factory = lambda: iter(())
    )
    meta: Dict[str, Any] = field(
        default_factory = lambda: {}
    )
    #memento: Optional[Sequence] = None
    
    def extend(self, events=None, meta=None) -> Sequence:
        a,b = itertools.tee(self.events)
        self.events = a
        if events is None:    
            events = b
        if meta is None:
            meta = self.meta.copy()
        return Sequence(events=events, meta=meta)

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
    def from_generator(cls, generator: Iterator[Event], meta=None) -> Sequence:
        """Return a new Sequence using the seed of a given generator function.
        """
        if meta is None:
            meta = {}
        return cls(
            events = generator,
            meta = meta
        )

    def transform(self, transformer: Callable[[Sequence], Iterator[Event]]) -> Sequence:
        """Convenience method for applying a transformation function to the sequence.
        Return the new sequence, allowing transformations to be chained in a single
        statement.
        """
        new_seq = self.extend(
            events = transformer(self))
        return new_seq

    def bake(self, n_beats=None) -> FiniteSequence:
        """Convert a sequence into a FiniteSequence
        """
        if n_beats is None:
            return FiniteSequence(list(self.events))
        _events = []
        for i in range(n_beats):
            _events.append(next(self.events))
        return FiniteSequence(list(self.events))

    def tap(self) -> Sequence:
        """Returns a copy of the sequence.
        This can be advanced through without affecting the iteration
        state of the current sequence.
        """
        return self.extend()

    def __add__(self, other):
        """Allows sequences to be added together.
        """
        events = itertools.chain.from_iterable([self.events, other.events])
        return self.__class__(events=events)

@dataclass
class FiniteSequence:
    events: List[Event] = field(
        default_factory = lambda: []
    )
    meta: Dict[str, Any] = field(
        default_factory = lambda: {}
    )
    
    def extend(self, events=None, meta=None) -> FiniteSequence:
        if events is None:
            events = self.events.copy()
        if meta is None:
            meta = self.meta.copy()
        return FiniteSequence(events=events, meta=meta)

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

    def to_vectors(self) -> List[Tuple[int, int]]:
        vectors = []
        for i in range(0, len(self.events) -1):
            left = self.events[i]
            right = self.events[i+1]
            vectors.append((
                right.pitches[-1] - left.pitches[-1],
                left.duration))
        return vectors

    def retrograde(self) -> FiniteSequence:
        """Return the sequence, reversed
        """
        return self.extend(events=list(reversed(self.events)))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.to_vectors() == other.to_vectors()

    def __len__(self):
        return len(self.events)

    def __hash__(self):
        return sum([hash(e) for e in self.events])

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
            offset = offset + event.duration
        return Graph(edges)

    @classmethod
    def from_graph(cls, graph: Graph):
        edges = list(graph) # already sorted by time
        events = []
        key_func = lambda e: e.start_time
        for start_time, group in itertools.groupby(edges, key_func):
            edges = list(group)
            pitches = [e.pitch for e in edges]
            pitches = sorted(pitches)
            duration = edges[-1].end_time - edges[-1].start_time
            events.append(Event(pitches, duration))
        return cls(events)

    def event_at(self, beat_offset: int) -> Optional[Event]:
        if beat_offset > self.duration:
            return None
        offset = 0
        for event in self.events:
            offset = offset + event.duration
            if offset >= beat_offset:
                return event

    def time_slice(self, start_beats: int, end_beats: int) -> FiniteSequence:
        """Return a new sequence, that contains the events
        of the current sequence between the window
        start_beats and end_beats.
        Closing event durations that overrun the window are truncated to fit.
        """
        current_time = 0
        events = []

        for event in self.events:
            if current_time >= end_beats:
                # we are past the window
                break

            if current_time >= start_beats:
                if event.duration + current_time > end_beats:
                    # event overlaps the end of the window
                    truncated_duration = event.duration + current_time - end_beats
                    events.append(
                        event.extend(duration=truncated_duration))
                else:
                    # event is within the window
                    events.append(event)
            elif current_time < start_beats \
                and current_time + event.duration > start_beats:
                # event overlaps the start of the window
                truncated_duration = event.duration + current_time - start_beats
                events.append(
                    event.extend(duration=truncated_duration))

            current_time = current_time + event.duration

        return self.extend(events=events)

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

    def __add__(self, other: FiniteSequence) -> FiniteSequence:
        return self.extend(events=self.events + other.events)
