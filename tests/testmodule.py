import os
import unittest

from mido import MidiFile

from composerstoolkit.core import Graph, Edge, Vector, Event, Sequence

class TestGraph(unittest.TestCase):

    def test_graph_is_itterable(self):
        graph = Graph()
        pitch_c = Edge(pitch=60, start_time=0, end_time=100)
        pitch_d = Edge(pitch=62, start_time=100, end_time=200)
        pitch_e = Edge(pitch=64, start_time=200, end_time=300)
        graph.add_edge(pitch_c)
        graph.add_edge(pitch_d)
        graph.add_edge(pitch_e)
        assert list(graph) == [pitch_c, pitch_d, pitch_e]

    def test_we_can_extract_the_chord_at_a_given_offset(self):
        graph = Graph()
        graph.add_edge(Edge(pitch=65, start_time=0, end_time=100))
        graph.add_edge(Edge(pitch=59, start_time=0, end_time=100))
        graph.add_edge(Edge(pitch=64, start_time=100, end_time=200))
        graph.add_edge(Edge(pitch=60, start_time=100, end_time=200))

        assert graph.get_pitches_at(0) == [59, 65]
        assert graph.get_pitches_at(99) == [59, 65]
        assert graph.get_pitches_at(100) == [60, 64]
        assert graph.get_pitches_at(200) == []

    def test_graph_to_vector_list(self):
        graph = Graph()
        # set up a simple context - just a two voice 4-3 suspension
        pitch_c = Edge(pitch=60, start_time=0, end_time=200)
        pitch_f = Edge(pitch=65, start_time=0, end_time=100)
        pitch_e = Edge(pitch=64, start_time=100, end_time=200)
        graph.add_edge(pitch_c)
        graph.add_edge(pitch_f)
        graph.add_edge(pitch_e)
        graph.add_vertex(pitch_f, pitch_e)
        graph.add_vertex(pitch_f, pitch_c)

        vertex_list = graph.get_vector_list()
        assert len(vertex_list) == 2
        assert Vector(
            pitch_delta = -1,
            time_delta = 100,
            origin = pitch_f,
            destination = pitch_e
        ) in vertex_list
        assert Vector(
            pitch_delta = -5,
            time_delta = 0,
            origin = pitch_f,
            destination = pitch_c
        ) in vertex_list

class TestMIDIParser(unittest.TestCase):

    def test_vertically_coincident_notes_linked_by_vertices(self):
        filename = os.path.join("tests", "c_major_chord.MID")
        # test is a 3 voice major triad.
        midi_file = MidiFile(filename)
        graph = Graph.from_midi_track(midi_file.tracks[0])
        assert len(graph.edges) == 3
        graph.edges.sort(key=lambda e: e.pitch, reverse=True)
        assert graph.edges[0].vertices[0] == graph.edges[1]
        assert graph.edges[1].vertices[0] == graph.edges[2]

    def test_sequential_notes_linked_by_vertices(self):
        filename = os.path.join("tests", "c_major_chord_arpeggiated.MID")
        # test is a 3 note melodic figure (C4, E4, G4)
        midi_file = MidiFile(filename)
        graph = Graph.from_midi_track(midi_file.tracks[0])
        assert len(graph.edges) == 3
        graph.edges.sort(key=lambda e: e.start_time)
        assert graph.edges[0].vertices[0] == graph.edges[1]
        assert graph.edges[1].vertices[0] == graph.edges[2]

    def test_notes_seperated_by_rests_are_not_linked(self):
        filename = os.path.join("tests", "unconnected_pitches.MID")
        # test is a 2 note figure (C4, REST, G4)
        midi_file = MidiFile(filename)
        graph = Graph.from_midi_track(midi_file.tracks[0])
        assert len(graph.edges) == 2
        graph.edges.sort(key=lambda e: e.start_time)
        assert graph.edges[0].vertices == []
        assert graph.edges[1].vertices == []

    def test_suspended_notes_are_not_horizontally_linked(self):
        filename = os.path.join("tests", "iv_i_suspension.MID")
        midi_file = MidiFile(filename)
        graph = Graph.from_midi_track(midi_file.tracks[0])
        assert len(graph.edges) == 3
        graph.edges.sort(key=lambda e: e.pitch, reverse=True)
        assert graph.edges[0].pitch == 65
        assert graph.edges[1].pitch == 64
        assert graph.edges[2].pitch == 60
        assert graph.edges[0].vertices == [graph.edges[2], graph.edges[1]]
        assert graph.edges[1].vertices == []
        assert graph.edges[2].vertices == []

class SequenceTests(unittest.TestCase):

    def test_a_transformer_can_be_applied_to_a_sequence(self):
        cts = Sequence([Event(pitches=[62], duration=100)])

        def test_modifier(sequence):
            for e in sequence.events:
                new_pitches = [p * 2 for p in e.pitches]
                yield Event(new_pitches,  e.duration * 2)

        new_seq = cts.transform(test_modifier)
        assert list(new_seq.events) == [Event(pitches=[124], duration=200)]
        assert new_seq.memento == cts
        assert list(new_seq.memento.events) == [
            Event(pitches=[62], duration=100)]

    def test_sequence_is_slicable(self):
        events = [
            Event(pitches=[60], duration=100),
            Event(pitches=[62], duration=100),
            Event(pitches=[64], duration=100),
            Event(pitches=[60], duration=100)]
        cts = Sequence(events)

        sliced = cts[0]
        assert sliced.events == [events[0]]
        sliced_middle = cts[1]
        assert sliced_middle.events == [events[1]]
        sliced_end = cts[3]
        assert sliced_end.events == [events[3]]

        sliced_head = cts[:1]
        assert sliced_end.events == events[:1]
        sliced_tail = cts[1:]
        assert sliced_tail.events == events[1:]

        sliced_portion = cts[0:3]
        assert sliced_portion.events == events[0:3]

        sliced_with_step = cts[0:3:2]
        assert sliced_with_step.events == events[0:3:2]

    # def test_to_midi_events(self):
        # cts = Sequence([
            # Event(60,100),
            # Event(62,100),
            # Event(64,100),
            # Event(60,100)])
            
        # midi = cts.to_midi_events()
        # assert midi == [
            # midievent(pitch=60, type="NOTE_ON", time=0),
            # midievent(pitch=60, type="NOTE_OFF", time=100),
            # midievent(pitch=62, type="NOTE_ON", time=100),
            # midievent(pitch=62, type="NOTE_OFF", time=200),
            # midievent(pitch=64, type="NOTE_ON", time=200),
            # midievent(pitch=64, type="NOTE_OFF", time=300),
            # midievent(pitch=60, type="NOTE_ON", time=300),
            # midievent(pitch=60, type="NOTE_OFF", time=400)]
            
    # def test_lookup(self):
        # cts = Sequence([
            # Event(60,100),
            # Event(62,100),
            # Event(64,100),
            # Event(60,100)])
            
        # assert cts.lookup(-1) == None
        # assert cts.lookup(0) == Event(60,100)
        # assert cts.lookup(50) == Event(60,100)
        # assert cts.lookup(99) == Event(60,100)
        # assert cts.lookup(100) == Event(60,100)
        # assert cts.lookup(101) == Event(62,100)
        # assert cts.lookup(400) == Event(60,100)
        # assert cts.lookup(401) == None

    def test_get_pitches(self):
        cts = Sequence([
            Event(pitches=[67], duration=100),
            Event(pitches=[60], duration=100),
            Event(pitches=[62], duration=100),
            Event(pitches=[64], duration=100),
            Event(pitches=[60], duration=100)])

        assert list(cts.pitches) == [67,60,62,64,60]

    def test_get_durations(self):
        cts = Sequence([
            Event(pitches=[67], duration=100),
            Event(pitches=[60], duration=100),
            Event(pitches=[62], duration=200),
            Event(pitches=[64], duration=100),
            Event(pitches=[60], duration=100)])

        assert list(cts.durations) == [100,100,200,100,100]

    def test_sequence_to_pitch_Set(self):
        cts = Sequence([
            Event(pitches=[67], duration=100),
            Event(pitches=[60], duration=100),
            Event(pitches=[62], duration=100),
            Event(pitches=[64], duration=100),
            Event(pitches=[60], duration=100)])
        assert cts.to_pitch_set() == {60,62,64,67}

    def test_sequence_to_pitch_class_Set(self):
        cts = Sequence([
            Event(pitches=[67], duration=100),
            Event(pitches=[60], duration=100),
            Event(pitches=[62], duration=100),
            Event(pitches=[64], duration=100),
            Event(pitches=[60], duration=100)])
        assert cts.to_pitch_class_set() == {0,2,4,7}

if __name__ == "__main__":
    unittest.main()