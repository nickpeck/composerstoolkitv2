import os
import types
import unittest
from unittest.mock import patch

from mido import MidiFile

from composerstoolkit import *

class TestGraph(unittest.TestCase):

    def test_graph_is_itterable(self):
        graph = Graph()
        pitch_c = Edge(pitch=60, start_time=0, end_time=1)
        pitch_d = Edge(pitch=62, start_time=1, end_time=2)
        pitch_e = Edge(pitch=64, start_time=3, end_time=3)
        graph.add_edge(pitch_c)
        graph.add_edge(pitch_d)
        graph.add_edge(pitch_e)
        assert list(graph) == [pitch_c, pitch_d, pitch_e]

    def test_we_can_extract_the_chord_at_a_given_offset(self):
        graph = Graph()
        graph.add_edge(Edge(pitch=65, start_time=0, end_time=1))
        graph.add_edge(Edge(pitch=59, start_time=0, end_time=1))
        graph.add_edge(Edge(pitch=64, start_time=1, end_time=2))
        graph.add_edge(Edge(pitch=60, start_time=1, end_time=2))

        assert graph.get_pitches_at(0) == [59, 65]
        assert graph.get_pitches_at(.99) == [59, 65]
        assert graph.get_pitches_at(1) == [60, 64]
        assert graph.get_pitches_at(2) == []

    def test_we_can_derrive_a_markov_table(self):
        graph = Graph()
        pitch_c = Edge(pitch=60, start_time=0, end_time=2)
        pitch_f = Edge(pitch=65, start_time=0, end_time=1)
        pitch_e = Edge(pitch=64, start_time=1, end_time=2)
        graph.add_edge(pitch_c)
        graph.add_edge(pitch_f)
        graph.add_edge(pitch_e)
        graph.add_vertex(pitch_f, pitch_e)
        graph.add_vertex(pitch_f, pitch_c)

        expected = {i:{i:0 for i in range(12)} for i in range(12)}
        expected[5][0] = 0.5
        expected[5][4] = 0.5
        markov = graph.to_markov_table()
        assert markov == expected

    def test_that_an_edge_without_end_time_is_considered_open(self):
        graph = Graph()
        graph.add_edge(Edge(pitch=65, start_time=0, end_time=None))
        assert graph.get_pitches_at(1.5) == [65]

    def test_graph_to_vector_list(self):
        graph = Graph()
        # set up a simple context - just a two voice 4-3 suspension
        pitch_c = Edge(pitch=60, start_time=0, end_time=2)
        pitch_f = Edge(pitch=65, start_time=0, end_time=1)
        pitch_e = Edge(pitch=64, start_time=1, end_time=2)
        graph.add_edge(pitch_c)
        graph.add_edge(pitch_f)
        graph.add_edge(pitch_e)
        graph.add_vertex(pitch_f, pitch_e)
        graph.add_vertex(pitch_f, pitch_c)

        vertex_list = graph.get_vector_list()
        assert len(vertex_list) == 2
        assert Vector(
            pitch_delta = -1,
            time_delta = 1,
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
        pitch_b = Edge(pitch=59, start_time=2, end_time=3)
        pitch_c = Edge(pitch=60, start_time=3, end_time=4)
        pitch_f = Edge(pitch=65, start_time=0, end_time=1)
        pitch_e = Edge(pitch=64, start_time=1, end_time=2)

        assert Vector(
            pitch_delta = -1,
            time_delta = 1,
            origin = pitch_f,
            destination = pitch_e
        ) == Vector(
            pitch_delta = -1,
            time_delta = 1,
            origin = pitch_c,
            destination = pitch_b
        )

        assert Vector(
            pitch_delta = -1,
            time_delta = 1,
            origin = pitch_f,
            destination = pitch_e
        ) != Vector(
            pitch_delta = -5,
            time_delta = 1,
            origin = pitch_e,
            destination = pitch_b
        )

        assert Vector(
            pitch_delta = -1,
            time_delta = 1,
            origin = pitch_f,
            destination = pitch_e
        ) != Edge(pitch=59, start_time=2, end_time=3)

    def test_to_vector_indexed_dict(self):
        graph = Graph()
        pitch1 = Edge(pitch=65, start_time=0, end_time=1)
        pitch2 = Edge(pitch=59, start_time=0, end_time=1)
        pitch3 = Edge(pitch=64, start_time=1, end_time=2)
        pitch4 = Edge(pitch=60, start_time=1, end_time=2)
        graph.add_edge(pitch1)
        graph.add_edge(pitch2)
        graph.add_edge(pitch3)
        graph.add_edge(pitch4)
        graph.add_vertex(pitch1, pitch3)
        graph.add_vertex(pitch2, pitch4)
        graph.add_vertex(pitch1, pitch2)
        graph.add_vertex(pitch3, pitch4)
        arr = graph.to_vector_indexed_array()
        assert arr[(-1,1)] == [[pitch1, pitch3]]
        assert arr[(1,1)] == [[pitch2, pitch4]]
        assert arr[(-4,0)] == [[pitch3, pitch4]]
        assert arr[(-6,0)] == [[pitch1, pitch2]]

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
        evt = Event(pitches=[60,64,67], duration=1)
        assert evt.to_edges() == [
            Edge(pitch=60, start_time=0, end_time=1),
            Edge(pitch=64, start_time=0, end_time=1),
            Edge(pitch=67, start_time=0, end_time=1)
        ]

    def test_we_can_get_the_pitch_class_set(self):
        evt = Event(pitches=[60,64,67], duration=1)
        pcs = evt.to_pitch_class_set()
        assert pcs == {0,4,7}

    def test_event_is_hashable(self):
        evt1 = Event(pitches=[60,64,67], duration=1)
        evt2 = Event(pitches=[60,64,67], duration=1)
        evt3 = Event(pitches=[60,64,68], duration=1)
        evt4 = Event(pitches=[60,64,68], duration=2)
        assert hash(evt1) == hash(evt2)
        assert hash(evt1) != hash(evt3)
        assert hash(evt1) != hash(evt4)

    def test_get_can_calculate_motion_costs_between_events(self):
        evt1 = Event(pitches=[60,64,67])
        evt2 = Event(pitches=[60,64,67])
        assert evt1.movement_cost_to(evt2) == 0
        evt3 = Event(pitches=[61,65,68])
        assert evt1.movement_cost_to(evt3) == 3
        # uneven no of voices are not counted in the cost
        evt4 = Event(pitches=[60,64,67,71])
        assert evt1.movement_cost_to(evt4) == 0
        evt5 = Event(pitches=[60,64])
        assert evt1.movement_cost_to(evt5) == 0
        # inversional eqivalence
        assert Event([60]).movement_cost_to(Event([69])) == 3
        evt6 = Event(pitches=[])
        assert evt1.movement_cost_to(evt6) == 0
        assert evt6.movement_cost_to(evt1) == 0

class SequenceTests(unittest.TestCase):

    def test_can_create_seq_from_generator_function(self):
        seq = Sequence.from_generator(
            cantus([60,64,67])
        )
        events = list(seq.events)
        assert len(events) == 3

    def test_a_transformer_can_be_applied_to_a_sequence(self):
        seq = Sequence([Event(pitches=[62], duration=1)])

        def test_modifier(sequence):
            for e in sequence.events:
                new_pitches = [p * 2 for p in e.pitches]
                yield Event(new_pitches,  e.duration * 2)

        new_seq = seq.transform(test_modifier)
        assert list(new_seq.events) == [Event(pitches=[124], duration=2)]

    def test_two_sequences_can_be_added(self):
        seq1 = Sequence([
            Event(pitches=[67], duration=1),
            Event(pitches=[60], duration=1)])

        seq2 = Sequence([
            Event(pitches=[62], duration=1),
            Event(pitches=[64], duration=1),
            Event(pitches=[60], duration=1)])

        seq3 = seq1 + seq2
        assert list(seq3.events) == [
            Event(pitches=[67], duration=1),
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=1),
            Event(pitches=[64], duration=1),
            Event(pitches=[60], duration=1)]

    def test_get_pitches(self):
        seq = Sequence([
            Event(pitches=[67], duration=1),
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=1),
            Event(pitches=[64], duration=1),
            Event(pitches=[60], duration=1)])

        assert list(seq.pitches) == [67,60,62,64,60]

    def test_get_durations(self):
        seq = Sequence([
            Event(pitches=[67], duration=1),
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=2),
            Event(pitches=[64], duration=1),
            Event(pitches=[60], duration=1)])

        assert list(seq.durations) == [1,1,2,1,1]

    def test_we_can_form_a_finite_sequence(self):
        seq = Sequence([
            Event(pitches=[67], duration=1),
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=2),
            Event(pitches=[64], duration=1),
            Event(pitches=[60], duration=1)]).bake()

        assert isinstance(seq.events, list)

    def test_we_can_tap_a_sequence(self):
        seq = Sequence([
            Event(pitches=[67], duration=1),
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=2),
            Event(pitches=[64], duration=1),
            Event(pitches=[60], duration=1)])
        tapped = seq.tap()
        # note how this gives us independant iterators:
        assert next(tapped.events).pitches == [67]
        assert next(tapped.events).pitches == [60]
        assert next(seq.events).pitches == [67]
        assert next(seq.events).pitches == [60]
        assert next(tapped.events).pitches == [62]

class FiniteSequenceTests(unittest.TestCase):

    def test_we_can_get_the_duration(self):
        seq = FiniteSequence([
            Event(pitches=[67], duration=1),
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=1),
            Event(pitches=[64], duration=1),
            Event(pitches=[60], duration=1)])
        assert seq.duration == 5

    def test_we_can_get_the_durations(self):
        seq = FiniteSequence([
            Event(pitches=[67], duration=1),
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=1),
            Event(pitches=[64], duration=1),
            Event(pitches=[60], duration=1)])
        assert seq.durations == [1,1,1,1,1]

    def test_we_can_count_the_events_using_len(self):
        seq = FiniteSequence([
            Event(pitches=[67], duration=1),
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=1),
            Event(pitches=[64], duration=1),
            Event(pitches=[60], duration=1)])
        assert len(seq) == 5

    def test_a_seq_is_hashable(self):
        seq1 = FiniteSequence([
            Event(pitches=[67], duration=1)])
        seq2 = FiniteSequence([
            Event(pitches=[67], duration=1)])
        seq3 = FiniteSequence([
            Event(pitches=[68], duration=1)])
        seq4 = FiniteSequence([
            Event(pitches=[67], duration=0)])
        assert hash(seq1) == hash(seq2)
        assert hash(seq1) != hash(seq3)
        assert hash(seq1) != hash(seq4)

    def test_we_can_make_a_sequence(self):
        seq = FiniteSequence([
            Event(pitches=[67], duration=1),
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=1),
            Event(pitches=[64], duration=1),
            Event(pitches=[60], duration=1)])

        seq = seq.to_sequence()
        assert next(seq.events) == Event(pitches=[67], duration=1)

    def test_we_can_get_the_pitch_set(self):
        seq = FiniteSequence([
            Event(pitches=[67], duration=1),
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=1),
            Event(pitches=[64], duration=1),
            Event(pitches=[60], duration=1)])
        assert seq.to_pitch_set() == {60,62,64,67}

    def test_sequence_to_pitch_class_set(self):
        seq = FiniteSequence([
            Event(pitches=[67], duration=1),
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=1),
            Event(pitches=[64], duration=1),
            Event(pitches=[60], duration=1)])
        assert seq.to_pitch_class_set() == {0,2,4,7}

    def test_finite_sequence_is_slicable(self):
        events = [
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=1),
            Event(pitches=[64], duration=1),
            Event(pitches=[60], duration=1)]
        seq = FiniteSequence(events)

        sliced = seq[0]
        assert sliced.events == [events[0]]
        sliced_middle = seq[1]
        assert sliced_middle.events == [events[1]]
        sliced_end = seq[3]
        assert sliced_end.events == [events[3]]

        sliced_head = seq[:1]
        assert sliced_end.events == events[:1]
        sliced_tail = seq[1:]
        assert sliced_tail.events == events[1:]

        sliced_portion = seq[0:3]
        assert sliced_portion.events == events[0:3]

        sliced_with_step = seq[0:3:2]
        assert sliced_with_step.events == events[0:3:2]

    def test_we_can_get_the_event_at_an_offset(self):
        seq = FiniteSequence([
            Event(pitches=[67], duration=1),
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=1),
            Event(pitches=[64], duration=1),
            Event(pitches=[60], duration=1)])

        assert seq.event_at(0) == Event(pitches=[67], duration=1)
        assert seq.event_at(2.5) == Event(pitches=[62], duration=1)
        assert seq.event_at(10) == None

    def test_we_can_create_a_graph(self):
        g = FiniteSequence([
            Event(pitches=[67], duration=1),
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=1),
            Event(pitches=[64], duration=1),
            Event(pitches=[60], duration=1)]).to_graph()

        assert len(g.edges) == 5
        assert g.edges[0].start_time == 0
        assert g.edges[1].start_time == 1

    def test_create_it_from_a_graph(self):
        seq = FiniteSequence([
            Event(pitches=[67], duration=1),
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=1),
            Event(pitches=[64], duration=1),
            Event(pitches=[60], duration=1)])
        g = seq.to_graph()
        assert FiniteSequence.from_graph(g) == seq
        assert len(g.edges) == 5

    def test_we_can_make_time_slices(self):
        seq = FiniteSequence([
            Event(pitches=[67], duration=1),
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=1),
            Event(pitches=[64], duration=1),
            Event(pitches=[60], duration=1)])

        assert seq.time_slice(0, 2).events == [
            Event(pitches=[67], duration=1),
            Event(pitches=[60], duration=1)
        ]
        assert seq.time_slice(2, 4).events == [
            Event(pitches=[62], duration=1),
            Event(pitches=[64], duration=1)
        ]
        assert seq.time_slice(4, 6).events == [
            Event(pitches=[60], duration=1)
        ]
        assert seq.time_slice(0, 3).events == [
            Event(pitches=[67], duration=1),
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=1)
        ]
        assert seq.time_slice(3, 6).events == [
            Event(pitches=[64], duration=1),
            Event(pitches=[60], duration=1)
        ]


    def test_time_slices_truncate_slice_to_fit_window(self):
        seq = FiniteSequence([
            Event(pitches=[67], duration=0.5),
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=1),
            Event(pitches=[64], duration=2),
            Event(pitches=[60], duration=1)])

        assert seq.time_slice(0, 1).events == [
            Event(pitches=[67], duration=0.5),
            Event(pitches=[60], duration=0.5)
        ]
        assert seq.time_slice(2, 5).events == [
            Event(pitches=[62], duration=0.5),
            Event(pitches=[64], duration=2),
            Event(pitches=[60], duration=0.5)
        ]
        assert seq.time_slice(5, 10).events == [
            Event(pitches=[60], duration=0.5)
        ]

    def test_to_vectors(self):
        seq = FiniteSequence([
            Event(pitches=[67], duration=1),
            Event(pitches=[60], duration=2),
            Event(pitches=[62], duration=1),
            Event(pitches=[64], duration=3),
            Event(pitches=[60], duration=1)])
        vectors = seq.to_vectors()
        assert vectors == [(-7, 1), (2, 2), (2, 1), (-4, 3)]

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
        seq = FiniteSequence([
            Event(pitches=[67], duration=1)])
        c.add_sequence(seq)
        assert c.sequences[0] == (1, 0, seq)

    def test_can_add_a_sequence_on_a_given_channel_and_offset(self):
        c = Container(bpm=300, playback_rate=2)
        seq = FiniteSequence([
            Event(pitches=[67], duration=1)])
        c.add_sequence(seq, channel_no=3, offset=100)
        assert c.sequences[0] == (3, 100, seq)

    def test_can_save_to_midi_file(self):
        filename = "test.MID"
        c = Container(bpm=100, playback_rate=1)
        seq = FiniteSequence([
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=1)])
        c.add_sequence(seq)
        c.save_as_midi_file(filename)
        # test we can parse it back in:
        midi_file = MidiFile(filename)
        graph = Graph.from_midi_track(midi_file.tracks[1])
        assert graph.edges[0].pitch == 60
        assert graph.edges[0].start_time == 0
        assert graph.edges[0].end_time == 1
        assert graph.edges[1].pitch == 62
        assert graph.edges[1].start_time == 1
        assert graph.edges[1].end_time == 2

    def test_can_playback(self):
        c = Container(synth=DummyPlayback(), debug=False)
        seq = FiniteSequence([
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=1)])
        c.add_sequence(seq)
        c.playback()

class AnnotationsTests(unittest.TestCase):
    def test_constraint_annotation_str_form(self):
        @Constraint
        def length_is(
            seq: FiniteSequence,
            l: int):
            return len(seq) == 1

        c = length_is(4)
        assert str(c) == "<Constraint: length_is(4,)>"

    def test_constraint_check(self):
        @Constraint
        def length_is(
            seq: FiniteSequence,
            l: int):
            return len(seq) == 1

        c = length_is(1)
        assert c(FiniteSequence([])) == False
        assert c(FiniteSequence([Event([], None)])) == True

    def test_constraint_or(self):
        @Constraint
        def length_is_0(
            seq: FiniteSequence):
            return len(seq) == 0
        @Constraint
        def length_is_1(
            seq: FiniteSequence):
            return len(seq) == 1

        c = length_is_0() | length_is_1()
        assert c(FiniteSequence([])) == True
        assert c(FiniteSequence([Event([], None)])) == True

    def test_transformer_annotation_str_form(self):
        @Transformer
        def as_is(
            seq: FiniteSequence,
            l: int):
            return seq

        t = as_is(4)
        assert str(t) == "<Transformer: as_is(4,)>"


if __name__ == "__main__":
    unittest.main()