from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Callable

from mido import MidiTrack, Message # type: ignore

@dataclass
class Edge:
    """Represents a pitch event
    """
    pitch: int
    start_time: int
    end_time: Optional[int] = None
    vertices: List[Edge] = field(
        default_factory = lambda: []
    )
    src_event: Optional[Message] = None

# CTGenerator = NewType("CTGenerator",
    # Callable[..., Iterator[Edge]])
# CTPermutator = NewType("CTPermutator",
    # Callable[[Iterator[Edge]], Iterator[Iterator[Edge]]])
# CTTransformer = NewType("CTTransformer",
    # Callable[[Iterator[Edge]], [Iterator[Edge]]])

class MidiTrackParser:
    """Parse a Midi track into a pitch graph
    """
    def __init__(self, track: MidiTrack, graph: Graph):
        """
        """
        self.graph = graph
        self._midi_track = track
        self._open_notes: List[Edge] = []
        self._closed_notes: List[Edge] = []
        self._cummulative_time: int = 0

    def parse(self):
        note_events = list(
            filter(lambda x: x.is_meta is False, self._midi_track))
        for evt in note_events:
            if evt.time > 0:
                print("-"*20)
                print("time", self._cummulative_time + evt.time)
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
            print("MADE VERTICAL CONNECTION", to_connect[i].pitch, "->", to_connect[i+1].pitch)
            #to_connect[i].vertices.append(to_connect[i+1])
            self.graph.add_vertex(to_connect[i], to_connect[i+1])

    def _join_horizontals(self):
        right_chord = list(filter(
            lambda e: e.start_time == self._cummulative_time,
            self._open_notes))
        left_chord = self._closed_notes
        left_chord.sort(key=lambda n: n.pitch, reverse=True)
        right_chord.sort(key=lambda n: n.pitch, reverse=True)
        # very basic for now, just using order of notes and assuming same no voices
        print("LEFT (closed notes)", [n.pitch for n in left_chord])
        print("RIGHT (open notes)", [n.pitch for n in right_chord])
        for i in range(len(left_chord)):
            left = left_chord[i]
            try:
                right = right_chord[i]
                #left.vertices.append(right)
                self.graph.add_vertex(left, right)
                print("MADE HORIZONTAL CONNECTION", left.pitch,"->",  right.pitch)
            except IndexError:
                pass
        self._closed_notes = []

@dataclass
class Vector:
    time_delta: int
    pitch_delta: int
    origin: Edge
    destination: Edge

    def __eq__(self, other: Vector) -> bool:
        return other.time_delta == self.time_delta\
            and other.pitch_delta == self.pitch_delta

@dataclass
class Graph:
    edges: List[Edge] = field(
        default_factory= lambda: []
    )

    def add_edge(self, edge: Edge):
        self.edges.append(edge)

    def add_vertex(self, edge1: Edge, edge2: Edge):
        index = self.edges.index(edge1)
        self.edges[index].vertices.append(edge2)

    def get_vector_list(self):
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
        return MidiTrackParser(track, cls()).parse()

    def intersections(self, other_graph) -> List[Edge]:
        raise NotImplementedError("Graph.intersections")

    def get_pitches_at(self, offset: int) -> List[int]:
        chord = list(filter(
            lambda e: e.start_time <= offset and e.end_time > offset,
            self.edges
        ))
        pitches = [e.pitch for e in chord]
        pitches.sort()
        return pitches

class CTSequence:
    @staticmethod
    def from_generator(generator: Callable) -> CTSequence:
        raise NotImplementedError("Sequence.from_generator")

    def permutate(self,
        permutator: Callable) -> CTSequence:
        raise NotImplementedError("Sequence.permutate")

    def transform(self,
        transformer: Callable) -> CTSequence:
        raise NotImplementedError("Sequence.transform")

    def to_graph(self) -> Graph:
        raise NotImplementedError("Sequence.to_graph")
