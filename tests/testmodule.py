import os
import types
import unittest

from mido import MidiFile

from composerstoolkit.core import (Graph, Edge, Vector,
    Event, Sequence, FiniteSequence, Container)

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

    def test_that_an_edge_without_end_time_is_considered_open(self):
        graph = Graph()
        graph.add_edge(Edge(pitch=65, start_time=0, end_time=None))
        assert graph.get_pitches_at(150) == [65]

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

    def test_vector_has_equality_with_vectors_of_same_pitch_time_delta(self):
        pitch_b = Edge(pitch=59, start_time=200, end_time=300)
        pitch_c = Edge(pitch=60, start_time=300, end_time=400)
        pitch_f = Edge(pitch=65, start_time=0, end_time=100)
        pitch_e = Edge(pitch=64, start_time=100, end_time=200)

        assert Vector(
            pitch_delta = -1,
            time_delta = 100,
            origin = pitch_f,
            destination = pitch_e
        ) == Vector(
            pitch_delta = -1,
            time_delta = 100,
            origin = pitch_c,
            destination = pitch_b
        )

        assert Vector(
            pitch_delta = -1,
            time_delta = 100,
            origin = pitch_f,
            destination = pitch_e
        ) != Vector(
            pitch_delta = -5,
            time_delta = 100,
            origin = pitch_e,
            destination = pitch_b
        )

        assert Vector(
            pitch_delta = -1,
            time_delta = 100,
            origin = pitch_f,
            destination = pitch_e
        ) != Edge(pitch=59, start_time=200, end_time=300)

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

class EventTests(unittest.TestCase):

    def test_we_can_convert_an_event_to_set_of_edges(self):
        evt = Event(pitches=[60,64,67], duration=100)
        assert evt.to_edges() == [
            Edge(pitch=60, start_time=0, end_time=100),
            Edge(pitch=64, start_time=0, end_time=100),
            Edge(pitch=67, start_time=0, end_time=100)
        ]

class SequenceTests(unittest.TestCase):

    def test_a_transformer_can_be_applied_to_a_sequence(self):
        cts = Sequence([Event(pitches=[62], duration=100)])

        def test_modifier(sequence):
            for e in sequence.events:
                new_pitches = [p * 2 for p in e.pitches]
                yield Event(new_pitches,  e.duration * 2)

        new_seq = cts.transform(test_modifier)
        assert list(new_seq.events) == [Event(pitches=[124], duration=200)]

    def test_two_sequences_can_be_added(self):
        seq1 = Sequence([
            Event(pitches=[67], duration=100),
            Event(pitches=[60], duration=100)])

        seq2 = Sequence([
            Event(pitches=[62], duration=100),
            Event(pitches=[64], duration=100),
            Event(pitches=[60], duration=100)])

        seq3 = seq1 + seq2
        assert list(seq3.events) == [
            Event(pitches=[67], duration=100),
            Event(pitches=[60], duration=100),
            Event(pitches=[62], duration=100),
            Event(pitches=[64], duration=100),
            Event(pitches=[60], duration=100)]

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

    def test_we_can_form_a_finite_sequence(self):
        cts = Sequence([
            Event(pitches=[67], duration=100),
            Event(pitches=[60], duration=100),
            Event(pitches=[62], duration=200),
            Event(pitches=[64], duration=100),
            Event(pitches=[60], duration=100)]).bake()

        assert isinstance(cts.events, list)

class FiniteSequenceTests(unittest.TestCase):

    def test_we_can_get_the_duration(self):
        cts = FiniteSequence([
            Event(pitches=[67], duration=100),
            Event(pitches=[60], duration=100),
            Event(pitches=[62], duration=100),
            Event(pitches=[64], duration=100),
            Event(pitches=[60], duration=100)])
        assert cts.duration == 500

    def test_we_can_get_the_durations(self):
        cts = FiniteSequence([
            Event(pitches=[67], duration=100),
            Event(pitches=[60], duration=100),
            Event(pitches=[62], duration=100),
            Event(pitches=[64], duration=100),
            Event(pitches=[60], duration=100)])
        assert cts.durations == [100,100,100,100,100]

    def test_we_can_make_a_sequence(self):
        cts = FiniteSequence([
            Event(pitches=[67], duration=100),
            Event(pitches=[60], duration=100),
            Event(pitches=[62], duration=100),
            Event(pitches=[64], duration=100),
            Event(pitches=[60], duration=100)])

        seq = cts.to_sequence()
        assert next(seq.events) == Event(pitches=[67], duration=100)

    def test_we_can_get_the_pitch_set(self):
        cts = FiniteSequence([
            Event(pitches=[67], duration=100),
            Event(pitches=[60], duration=100),
            Event(pitches=[62], duration=100),
            Event(pitches=[64], duration=100),
            Event(pitches=[60], duration=100)])
        assert cts.to_pitch_set() == {60,62,64,67}

    def test_sequence_to_pitch_class_set(self):
        cts = FiniteSequence([
            Event(pitches=[67], duration=100),
            Event(pitches=[60], duration=100),
            Event(pitches=[62], duration=100),
            Event(pitches=[64], duration=100),
            Event(pitches=[60], duration=100)])
        assert cts.to_pitch_class_set() == {0,2,4,7}

    def test_finite_sequence_is_slicable(self):
        events = [
            Event(pitches=[60], duration=100),
            Event(pitches=[62], duration=100),
            Event(pitches=[64], duration=100),
            Event(pitches=[60], duration=100)]
        cts = FiniteSequence(events)

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

    def test_we_can_get_the_event_at_an_offset(self):
        cts = FiniteSequence([
            Event(pitches=[67], duration=100),
            Event(pitches=[60], duration=100),
            Event(pitches=[62], duration=100),
            Event(pitches=[64], duration=100),
            Event(pitches=[60], duration=100)])

        assert cts.event_at(0) == Event(pitches=[67], duration=100)
        assert cts.event_at(250) == Event(pitches=[62], duration=100)
        assert cts.event_at(1000) == None

    def test_we_can_create_a_graph(self):
        g = FiniteSequence([
            Event(pitches=[67], duration=100),
            Event(pitches=[60], duration=100),
            Event(pitches=[62], duration=100),
            Event(pitches=[64], duration=100),
            Event(pitches=[60], duration=100)]).to_graph()

        assert len(g.edges) == 5

class ContainerTests(unittest.TestCase):

    def test_defaults_options(self):
        c = Container()
        assert c.options["synth"] != None
        assert c.options["bpm"] == 120
        assert c.options["playback_rate"] == 1

    def test_option_overrides(self):
        c = Container(bpm=300, playback_rate=2)
        assert c.options["synth"] != None
        assert c.options["bpm"] == 300
        assert c.options["playback_rate"] == 2

    def test_can_add_a_sequence(self):
        c = Container(bpm=300, playback_rate=2)
        cts = FiniteSequence([
            Event(pitches=[67], duration=100)])
        c.add_sequence(cts)
        assert c.sequences[0] == (0, 0, cts)

    def test_can_add_a_sequence_on_a_given_channel_and_offset(self):
        c = Container(bpm=300, playback_rate=2)
        cts = FiniteSequence([
            Event(pitches=[67], duration=100)])
        c.add_sequence(cts, channel_no=3, offset=100)
        assert c.sequences[0] == (3, 100, cts)

    def test_can_save_to_midi_file(self):
        filename = "test.MID"
        c = Container(bpm=100, playback_rate=1)
        cts = FiniteSequence([
            Event(pitches=[60], duration=100)])
        c.add_sequence(cts)
        c.save_as_midi_file(filename)
        # test we can parse it back in:
        midi_file = MidiFile(filename)
        graph = Graph.from_midi_track(midi_file.tracks[0])
        assert graph.edges[0].pitch == 60
        assert graph.edges[0].start_time == 0
        assert graph.edges[0].end_time == 100


if __name__ == "__main__":
    unittest.main()