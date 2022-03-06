from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
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
class Edge:
    """Represents a pitch event in a Pitch graph
    """
    pitch: int
    start_time: int
    end_time: Optional[int] = None
    vertices: List[Edge] = field(
        repr = False,
        default_factory = lambda: []
    )
    src_event: Optional[Message] = field(
        repr = False,
        default_factory = lambda: None
    )

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
    def __init__(self, 
            track: MidiTrack,
            graph: Graph,
            ticks_per_beat = 960):
        """Constructor for MidiTrackParser:
        track - a mido MidiTrack
        graph - the Graph to the data into.
        """
        self.graph = graph
        self._midi_track = track
        self._open_notes: List[Edge] = []
        self._closed_notes: List[Edge] = []
        self._cummulative_time: int = 0
        self.ticks_per_beat = ticks_per_beat

    def parse(self):
        """Parse the track and return the resulting graph.
        """
        note_events = list(
            filter(lambda x: x.is_meta is False, self._midi_track))
        for evt in note_events:
            if evt.time > 0:
                self._join_verticals()
                self._join_horizontals()
                self._cummulative_time = self._cummulative_time +\
                    (evt.time/self.ticks_per_beat)
            if evt.type == "note_on":
                if evt.velocity == 0:
                    self._on_note_end(evt)
                    continue
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

    def to_vector_indexed_array(self):
        arr = {}
        for edge in self.edges:
            vertices = edge.vertices
            for vertex in vertices:
                time_delta = vertex.start_time - edge.start_time
                pitch_delta = vertex.pitch - edge.pitch
                index = (pitch_delta, time_delta)
                try:
                    arr[index].append([edge, vertex])
                except KeyError:
                    arr[index] = [[edge, vertex]]
        return arr

    def to_markov_table(self) -> Dict[int, Dict[int, int]]:
        """Generates a Markov table for the musical structure.
        The table tells us the overall probability from one pitch class
        to the next, expressed as a float between 0 - 1.
        
        {from_pitch_class: {to_pitch_class: probability...} ...}
        """
        result = {i:{i:0 for i in range(12)} for i in range(12)}
        for edge in self.edges:
            from_pitch_class = edge.pitch % 12
            for vertex in edge.vertices:
                to_pitch_class = vertex.pitch % 12
                count = result[from_pitch_class][to_pitch_class]
                result[from_pitch_class][to_pitch_class] = count + 1
        for from_pitch_class, probabilities in result.items():
            total = sum(probabilities.values())
            if total == 0:
                continue
            for to_pitch_class, probability in probabilities.items():
                result[from_pitch_class][to_pitch_class] =\
                    float(Decimal(str(probability)) / Decimal(str(total)))
        return result

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
