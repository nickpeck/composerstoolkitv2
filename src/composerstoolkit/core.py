"""Composers toolkit, core classes
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Iterator, Set

import itertools
import functools
from mido import MidiTrack, Message # type: ignore

@dataclass
class Edge:
    """Represents a pitch event in a Pitch graph
    """
    pitch: int
    start_time: int
    end_time: Optional[int] = None
    vertices: List[Edge] = field(
        default_factory = lambda: []
    )
    src_event: Optional[Message] = None

class MidiTrackParser:
    """Parse a Midi track into a pitch graph
    The data should be arranged into a single track,
    with all chords aligned (quantized) so that all notes
    start at the same time point.
    
    The music should contain a consistent number of parts (voices)
    and there should be no space or overlap between chords that are
    intended to be connected in a legato manner.
    """
    def __init__(self, track: MidiTrack, graph: Graph):
        """Constructor for MidiTrackParser
        
        track - a mido MidiTrack
        graph - the Graph to the data into.
        """
        self.graph = graph
        self._midi_track = track
        self._open_notes: List[Edge] = []
        self._closed_notes: List[Edge] = []
        self._cummulative_time: int = 0

    def parse(self):
        """Parse the track and return the resulting graph.
        """
        note_events = list(
            filter(lambda x: x.is_meta is False, self._midi_track))
        for evt in note_events:
            if evt.time > 0:
                self._join_verticals()
                self._join_horizontals()
                self._cummulative_time = self._cummulative_time + evt.time
            if evt.type == "note_on":
                self._on_note_start(evt)
            if evt.type == "note_off":
                self._on_note_end(evt)
        return self.graph

    def _on_note_start(self, msg: Message):
        edge = Edge(
                pitch = msg.note,
                start_time = self._cummulative_time,
                src_event = msg
            )
        self.graph.add_edge(edge)
        self._open_notes.append(edge)

    def _on_note_end(self, msg: Message):
        for note in self._open_notes:
            if note.pitch != msg.note:
                continue
            note.end_time = self._cummulative_time
            self._closed_notes.append(note)
            self._open_notes.remove(note)

    def _join_verticals(self):
        to_connect = list(filter(
            lambda e: e.start_time == self._cummulative_time,
            self._open_notes))
        to_connect.sort(key=lambda n: n.pitch, reverse=True)
        for i in range(len(to_connect) - 1):
            self.graph.add_vertex(to_connect[i], to_connect[i+1])

    def _join_horizontals(self):
        right_chord = list(filter(
            lambda e: e.start_time == self._cummulative_time,
            self._open_notes))
        left_chord = self._closed_notes
        left_chord.sort(key=lambda n: n.pitch, reverse=True)
        right_chord.sort(key=lambda n: n.pitch, reverse=True)
        # very basic for now, just using order of notes and assuming same no voices
        for i in range(len(left_chord)):
            left = left_chord[i]
            try:
                right = right_chord[i]
                self.graph.add_vertex(left, right)
            except IndexError:
                pass
        self._closed_notes = []

@dataclass
class Vector:
    """Used to represent the relative time/pitch motion between
    two edges in a Pitch Graph

    Vectors have equality with other vectors with the same relative
    pitch/time deltas.
    """
    time_delta: int
    pitch_delta: int
    origin: Edge
    destination: Edge

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return other.time_delta == self.time_delta\
            and other.pitch_delta == self.pitch_delta

@dataclass
class Graph:
    """A representation of a musical structure used for analysis purposes.
    
    edges
    """
    edges: List[Edge] = field(
        default_factory= lambda: []
    )

    def add_edge(self, edge: Edge):
        """Add an edge to the graph
        """
        self.edges.append(edge)

    def add_vertex(self, edge1: Edge, edge2: Edge):
        """Add a vertex (implied connection) between two 
        edges already in the graph.
        """
        index = self.edges.index(edge1)
        self.edges[index].vertices.append(edge2)

    def get_vector_list(self) -> List[Vector]:
        """Return a list of (Vectors) that describes all routes
        between edges in the graph in terms of their relative pitch/time
        vectors.
        """
        vector_list = []
        for e in self.edges:
            vertices = e.vertices
            for vertex in vertices:
                vector_list.append(
                    Vector(
                        time_delta = vertex.start_time - e.start_time,
                        pitch_delta = vertex.pitch - e.pitch,
                        origin = e,
                        destination = vertex
                    )
                )
        vector_list.sort(key = lambda v : v.origin.start_time)
        return vector_list

    def __iter__(self):
        self.edges.sort(key=lambda e: e.start_time)
        for edge in self.edges:
            yield edge

    @classmethod
    def from_midi_track(cls, track: MidiTrack) -> Graph:
        """Parse a mido Miditrack into a pitch graph.
        """
        return MidiTrackParser(track, cls()).parse()

    def intersections(self, other_graph) -> List[Edge]:
        """Return a list of all possible intersections 
        between other_graph and this graph.
        """
        raise NotImplementedError("Graph.intersections")

    def get_pitches_at(self, offset: int) -> List[int]:
        """Return a list of integers that represents all
        pitches sounding at a given offset, sorted in 
        ascending numerical order.
        """
        def func(e: Edge) -> bool:
            if e.start_time > offset:
                return False
            if e.end_time is None:
                return True
            if e.end_time <= offset:
                return False
            return True

        chord = list(filter(
            func,
            self.edges
        ))
        pitches = [e.pitch for e in chord]
        pitches.sort()
        return pitches

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
        for p in self.pitches:
            edges.append(Edge(
                pitch = p,
                start_time = offset,
                end_time = self.duration + offset
            ))
        return edges

@dataclass
class Sequence:
    """Represents a linear sequence of events (single notes, chords or 'meta' type
    events
    
    events - the default 
    """
    events: Iterator[Event] = field(
        default_factory = lambda: iter(())
    )
    memento: Optional[Sequence] = None

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
        return cls(
            events = generator
        )

    def to_pitch_set(self) -> Set[int]:
        """Return a set of unique MIDI pitch numbers that comprise the sequence.
        """
        return {* (itertools.chain(self.pitches))}

    def to_pitch_class_set(self):
        """Return the set of unique pitch classes (0..11) that comprise the sequence.
        """
        pitch_set = self.to_pitch_set()
        return {*[p % 12 for p in pitch_set]}

    def transform(self, transformer: Callable[[Sequence], Iterator[Event]]) -> Sequence:
        """Convenience method for applying a transformation function to the sequence.
        Return the new sequence, allowing transformations to be chained in a single
        statement.
        """
        new_seq = self.__class__(
            events = transformer(self),
            memento = self)
        return new_seq

    def to_graph(self, offset: int=0) -> Graph:
        """Return a pitch graph representation of the sequence.
        """
        edges: List[Edge] = []
        for event in self.events:
            edges = edges + event.to_edges(offset)
        return Graph(edges)

    def __add__(self, other):
        events = self.events[:] + other.events[:]
        return self.__class__(events=events)

    def __getitem__(self, slice):
        start, stop, step = None, None, None
        try:
            start, stop, step = slice
            sliced_events = self.events[start:stop:step]
        except TypeError:
            try:
                start, stop = slice
                sliced_events = self.events[start:stop]
            except TypeError:
                start = slice
                sliced_events = self.events[start]
                if not isinstance(sliced_events , list):
                    sliced_events = [sliced_events]

        return self.__class__(events=sliced_events)

class reprwrapper(object):
    """helper to override __repr__ for a function for debugging purposes
    see https://stackoverflow.com/questions/10875442/possible-to-change-a-functions-repr-in-python
    """
    def __init__(self, repr, func):
        self._repr = repr
        self._func = func
        functools.update_wrapper(self, func)
    def __call__(self, *args, **kw):
        return self._func(*args, **kw)
    def __repr__(self):
        return self._repr(self._func)

def withrepr(reprfun):
    """decorator for reprwrapper"""
    def _wrap(func):
        return reprwrapper(reprfun, func)
    return _wrap

class Transformer():

    def __init__(self, functor):
        self._functor = functor

    def __call__(self, *args, **kwargs):
        @withrepr(
            lambda x: "<CTTransformer: {}{}>".format(
                self._functor.__name__, args + tuple(kwargs.items())))
        def transform(instance):
            nonlocal args
            nonlocal kwargs
            _kwargs = kwargs
            if "gate" in kwargs.keys():
                gate = _kwargs["gate"]
                del _kwargs["gate"]
                _args = args[:]
                return gate(self._functor, instance, *_args, **_kwargs)
            _args = [instance] + list(args)
            return self._functor(*_args, **_kwargs)
        return transform

    def __str__(self):
        return "<CTTransformer : {}>".format(self._functor.__name__)
