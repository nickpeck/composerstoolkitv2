"""Composers toolkit, core classes
"""

from __future__ import annotations
from dataclasses import dataclass, field
from time import sleep
from typing import Any, Dict, List, Optional, Callable, Iterator, Set, Tuple

import itertools
import functools
import fluidsynth # type: ignore
from midiutil.MidiFile import MIDIFile # type: ignore
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
    and should be aligned to the grid,
    ie there should be no space or overlap between chords that are
    intended to be connected in a legato manner.
    """
    def __init__(self, track: MidiTrack, graph: Graph):
        """Constructor for MidiTrackParser:
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
        for i, left in enumerate(left_chord):
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
        for edge in self.edges:
            vertices = edge.vertices
            for vertex in vertices:
                vector_list.append(
                    Vector(
                        time_delta = vertex.start_time - edge.start_time,
                        pitch_delta = vertex.pitch - edge.pitch,
                        origin = edge,
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
        def func(edge: Edge) -> bool:
            if edge.start_time > offset:
                return False
            if edge.end_time is None:
                return True
            if edge.end_time <= offset:
                return False
            return True

        chord = list(filter(
            func,
            self.edges
        ))
        pitches = [edge.pitch for edge in chord]
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
        for pitch in self.pitches:
            edges.append(Edge(
                pitch = pitch,
                start_time = offset,
                end_time = self.duration + offset
            ))
        return edges

@dataclass
class Sequence:
    """Represents a linear sequence of events (single notes, chords or 'meta' type
    events).
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

    @property
    def duration(self) -> int:
        """Return the total duration of the Sequence
        """
        return sum(self.durations)

    @classmethod
    def from_generator(cls, generator: Iterator[Event]) -> Sequence:
        """Return a new Sequence using the seed of a given generator function.
        """
        return cls(
            events = generator
        )

    def to_midi_events(self, time_offset=0) -> Tuple[int, str, int]:
        events = list(self.events)
        results = []
        for e in events:
            for pitch in e.pitches:
                results.append((
                    pitch,
                    "note_on",
                    time_offset
                ))
                results.append((
                    pitch,
                    "note_off",
                    time_offset + e.duration
                ))
            time_offset = time_offset + e.duration
        # sort by time
        results.sort(key=lambda x: x[2], reverse=False)
        return results

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
        def transform(instance):
            nonlocal args
            nonlocal kwargs
            _kwargs = kwargs
            if "gate" in kwargs:
                gate = _kwargs["gate"]
                del _kwargs["gate"]
                _args = args[:]
                return gate(self._functor, instance, *_args, **_kwargs)
            _args = [instance] + list(args)
            return self._functor(*_args, **_kwargs)
        return transform

    def __str__(self):
        return "<Transformer : {}>".format(self._functor.__name__)

class Container():
    """Provides a context for playing back multiple sequences
    or rendering them out to a MIDI file.
    """
    def __init__(self,  **kwargs):
        """Optional args:
        synth - a synthesier function (defaults to fluidsynth)
        bpm - int
        playback_rate - defaults to 1
        """
        if "synth" not in kwargs:
            # intialise a fallback synth
            synth = fluidsynth.Synth()
            synth.start()
            sfid = synth.sfload("Nice-Steinway-v3.8.sf2")
            synth.program_select(0, sfid, 0, 0)
            kwargs["synth"] = synth

        self.options = {
            "bpm": 120,
            "playback_rate": 1,
            "synth": None
        }
        self.sequences = []
        self.options.update(kwargs)

    def add_sequence(self, seq, **kwargs):
        """Add a sequence to the playback container.
        optional args:
            offset (default 0)
            channel_no (defaults to the next available channel)
        """
        try:
            offset = kwargs["offset"]
        except KeyError:
            offset = 0
        try:
            channel_no = kwargs["channel_no"]
        except KeyError:
            channel_no = len(self.sequences)
        self.sequences.append((channel_no, offset, seq))
        return self

    def playback(self):
        stack = []
        counter = 0
        synth = self.options["synth"]
        playback_rate = self.options["playback_rate"]
        all_midi_events = []
        dynamic = 60
        for (channel_no, offset,seq) in self.sequences:
            for me in seq.to_midi_events(offset):
                # (pitch, type, time)
                all_midi_events.append((me[0], me[1], me[2] / playback_rate))
        all_midi_events = sorted(all_midi_events, key=lambda x: x[2])
        count = 0
        for event in all_midi_events:
            if event[2] != count:
                sleep(event[2] - count)
            count = event[2]
            if event[1] == "note_on":
                synth.noteon(0, event[0], dynamic)
            elif event[1] == "note_off":
                synth.noteoff(0, event[0])


    def save_as_midi_file(self, filename):
        """Save the contents of the container as a MIDI file
        """
        midifile = MIDIFile(len(self.sequences), eventtime_is_ticks=True)
        for (channel_no, offset, seq) in self.sequences:
            midifile.addTrackName(channel_no, offset, "Channel {}".format(channel_no))
            count = offset
            for event in seq.events:
                for pitch in event.pitches:
                    midifile.addNote(channel_no, 0, pitch, count, event.duration, 60)
                count = count + event.duration
        midifile.addTempo(0, 0, self.options["bpm"])
        with open(filename, 'wb') as outf:
            midifile.writeFile(outf)
