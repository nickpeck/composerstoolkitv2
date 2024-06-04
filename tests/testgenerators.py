import unittest

from composerstoolkit import *

class TestGenerators(unittest.TestCase):
    def test_cantus(self):
        events = cantus([60,61])
        assert next(events) == Event(pitches=[60], duration=0)
        assert next(events) == Event(pitches=[61], duration=0)
        with self.assertRaises(StopIteration):
            assert next(events)

    def test_pulses(self):
        events = pulses([WHOLE_NOTE,HALF_NOTE])
        assert next(events) == Event(pitches=[], duration=WHOLE_NOTE)
        assert next(events) == Event(pitches=[], duration=HALF_NOTE)
        with self.assertRaises(StopIteration):
            assert next(events)

    def test_collision_pattern_2_3(self):
        events = collision_pattern(2,3)
        assert next(events) == Event(pitches=[], duration=2)
        assert next(events) == Event(pitches=[], duration=1)
        assert next(events) == Event(pitches=[], duration=1)
        assert next(events) == Event(pitches=[], duration=2)
        with self.assertRaises(StopIteration):
            assert next(events)

    def test_collision_pattern_equal_inputs(self):
        events = collision_pattern(2,2,2)
        assert next(events) == Event(pitches=[], duration=2)
        with self.assertRaises(StopIteration):
            assert next(events)

    def test_collision_pattern_max_len(self):
        events = collision_pattern(2,3, max_len=4)
        #print(list(events))
        assert next(events) == Event(pitches=[], duration=2)
        assert next(events) == Event(pitches=[], duration=1)
        assert next(events) == Event(pitches=[], duration=1)
        with self.assertRaises(StopIteration):
            assert next(events)

        events = collision_pattern(2,3, max_len=3)
        #print(list(events))
        assert next(events) == Event(pitches=[], duration=2)
        assert next(events) == Event(pitches=[], duration=1)
        with self.assertRaises(StopIteration):
            assert next(events)

    def test_resultant_pitches(self):
        events = resultant_pitches(counters=[2,3])
        assert next(events) == Event(pitches=[0], duration=0)
        assert next(events) == Event(pitches=[2], duration=0)
        assert next(events) == Event(pitches=[3], duration=0)
        assert next(events) == Event(pitches=[4], duration=0)
        assert next(events) == Event(pitches=[6], duration=0)
        with self.assertRaises(StopIteration):
            assert next(events)

    def test_resultant_pitches_one_input_only(self):
        events = resultant_pitches(counters=[2])
        assert next(events) == Event(pitches=[0], duration=0)
        assert next(events) == Event(pitches=[2], duration=0)
        with self.assertRaises(StopIteration):
            assert next(events)

    def test_axis_melody_contract(self):
        pf = pitches.PitchFactory()
        events = axis_melody(
            axis_pitch=pf("C4"),
            scale=range(0,127),
            max_steps=2)
        assert next(events) == Event(pitches=[pf("D4")], duration=0)
        assert next(events) == Event(pitches=[pf("Bb3")], duration=0)
        assert next(events) == Event(pitches=[pf("Db4")], duration=0)
        assert next(events) == Event(pitches=[pf("B3")], duration=0)
        assert next(events) == Event(pitches=[pf("C4")], duration=0)

    def test_axis_melody_exc_with_unknown_direction(self):
        pf = pitches.PitchFactory()
        events = axis_melody(
            axis_pitch=pf("C4"),
            scale=range(0,127),
            max_steps=2,
            direction="blah")
        with self.assertRaises(Exception) as e:
            next(events)

    def test_axis_melody_exc_with_axis_pitch_not_in_scale(self):
        pf = pitches.PitchFactory()
        events = axis_melody(
            axis_pitch=pf("Db4"),
            scale=scales.C_major,
            max_steps=2)
        with self.assertRaises(Exception) as e:
            next(events)

    def test_axis_melody_expand(self):
        pf = pitches.PitchFactory()
        events = axis_melody(
            axis_pitch=pf("C4"),
            scale=range(0,127),
            max_steps=2,
            direction="expand")
        assert next(events) == Event(pitches=[pf("C4")], duration=0)
        assert next(events) == Event(pitches=[pf("Db4")], duration=0)
        assert next(events) == Event(pitches=[pf("B3")], duration=0)
        assert next(events) == Event(pitches=[pf("D4")], duration=0)
        assert next(events) == Event(pitches=[pf("Bb3")], duration=0)

    def test_random_noise(self):
        gen = random_noise(max_len=3)
        next(gen)
        next(gen)
        next(gen)
        with self.assertRaises(StopIteration):
            assert next(gen)

    def test_random_noise_infinate(self):
        gen = random_noise()
        events = random_noise()
        assert isinstance(next(gen), Event)

    def test_random_choice(self):
        gen = random_choice(
            choices=[Event(pitches=[60], duration=1)],
            max_len=3)
        assert next(gen).pitches == [60]
        assert next(gen).pitches == [60]
        assert next(gen).pitches == [60]
        with self.assertRaises(StopIteration):
            assert next(gen)

    def test_using_markov_table(self):
        seq = FiniteSequence(events=[
            Event(pitches=[60], duration=1),
            Event(pitches=[60], duration=1),
            Event(pitches=[60], duration=1)
        ])
        gen = using_markov_table(
            starting_event=Event(pitches=[60]),
            markov_table=seq.to_graph().to_markov_table(),
            max_len=3)
        assert next(gen).pitches == [60]
        assert next(gen).pitches == [60]
        assert next(gen).pitches == [60]
        with self.assertRaises(StopIteration):
            assert next(gen)

    def test_using_markov_table_infinate(self):
        seq = FiniteSequence(events=[
            Event(pitches=[60], duration=1),
            Event(pitches=[60], duration=1),
            Event(pitches=[60], duration=1)
        ])
        gen = using_markov_table(
            starting_event=Event(pitches=[60]),
            markov_table=seq.to_graph().to_markov_table())
        assert next(gen).pitches == [60]
        assert next(gen).pitches == [60]

    def test_random_slice(self):
        seq = FiniteSequence(events=[
            Event(pitches=[60], duration=1),
            Event(pitches=[60], duration=1),
            Event(pitches=[60], duration=1)
        ])
        gen = random_slice(
            base_seq = seq,
            slice_size = 1,
            max_len = 3
        )
        assert next(gen) in seq.events
        assert next(gen) in seq.events
        assert next(gen) in seq.events
        with self.assertRaises(StopIteration):
            assert next(gen)

    def test_random_slice_infinate(self):
        seq = FiniteSequence(events=[
            Event(pitches=[60], duration=1),
            Event(pitches=[60], duration=1),
            Event(pitches=[60], duration=1)
        ])
        gen = random_slice(
            base_seq = seq
        )
        assert next(gen) in seq.events

    def test_random_slice_no_slice_size(self):
        seq = FiniteSequence(events=[
            Event(pitches=[60], duration=1),
            Event(pitches=[60], duration=1),
            Event(pitches=[60], duration=1)
        ])
        gen = random_slice(
            base_seq = seq,
            slice_size = 1
        )
        assert next(gen) in seq.events

    def test_chord_cycle(self):
        pf = pitches.PitchFactory()
        gen = chord_cycle(
            start = Event([pf("C4"),pf("E4"),pf("G4")]),
            scale = scales.C_major,
            cycle_of = -3,
            voice_lead = False,
            max_len = 3
        )
        assert next(gen).pitches == [pf("C4"),pf("E4"),pf("G4")]
        assert next(gen).pitches == [pf("G3"),pf("B3"),pf("D4")]
        assert next(gen).pitches == [pf("D3"),pf("F3"),pf("A3")]
        with self.assertRaises(StopIteration):
            assert next(gen)

    def test_chord_cycle_w_voice_lead(self):
        pf = pitches.PitchFactory()
        gen = chord_cycle(
            start = Event([pf("C4"),pf("E4"),pf("G4")]),
            scale = scales.C_major,
            cycle_of = -3,
            voice_lead = True,
            max_len = 3
        )
        assert next(gen).pitches == [pf("C4"),pf("E4"),pf("G4")]
        assert next(gen).pitches == [pf("D4"),pf("G4"),pf("B4")]
        assert next(gen).pitches == [pf("D4"),pf("F4"),pf("A4")]
        with self.assertRaises(StopIteration):
            assert next(gen)

    def test_chord_cycle_raises_exc_if_start_not_in_scale(self):
        pf = pitches.PitchFactory()
        gen = chord_cycle(
            start = Event([pf("Db4"),pf("Gb4"),pf("Bb4")]),
            scale = scales.C_major,
            cycle_of = -3,
            voice_lead = False,
            max_len = 3
        )
        assert next(gen).pitches == [pf("Db4"),pf("Gb4"),pf("Bb4")]
        with self.assertRaises(Exception) as e:
            assert next(gen)

    def test_chords_from_scale(self):
        pf = pitches.PitchFactory()
        gen = chords_from_scale(
            pitch_classes = scales.MAJ_SCALE_PITCH_CLASSES,
            spacing=2,
            n_voices=3,
            allow_inversions = False
        )
        assert next(gen).pitches == [pf("C-1"),pf("E-1"),pf("G-1")]
        assert next(gen).pitches == [pf("D-1"),pf("F-1"),pf("A-1")]
        assert next(gen).pitches == [pf("E-1"),pf("G-1"),pf("B-1")]
        assert next(gen).pitches == [pf("F-1"),pf("A-1"),pf("C0")]
        assert next(gen).pitches == [pf("G-1"),pf("B-1"),pf("D0")]

    def test_select_chords(self):
        pf = pitches.PitchFactory()
        lexicon = list(chords_from_scale(scales.C_major, n_voices=3, spacing=2)) +\
            list(chords_from_scale(scales.D_major, n_voices=3, spacing=2))
        gen = select_chords(event=Event([pf("C4"),pf("E4"),pf("G4")]),
                scales=[scales.D_major],
                chord_lexicon = lexicon)
        evt1 = next(gen)
        assert evt1 in lexicon
        assert {* evt1.pitches}.difference(scales.C_major) == set()
        evt2 = next(gen)
        assert evt2 in lexicon
        assert {* evt2.pitches}.difference(scales.D_major) == set()
        with self.assertRaises(StopIteration):
            assert next(gen)

    def test_we_can_create_variations(self):
        seq = FiniteSequence([
            Event(pitches=[60], duration=1),
            Event(pitches=[60], duration=1)])

        @Transformer
        def my_trans(seq):
            for event in seq.events:
                yield Event(
                    [e+1 for e in event.pitches],
                    event.duration)

        my_variations = Sequence.from_generator(
            variations(
                seq,
                transformer = my_trans(),
                repeats_per_var = 1
            ))

        assert next(my_variations.events).pitches == [60]
        assert next(my_variations.events).pitches == [60]
        assert next(my_variations.events).pitches == [61]
        assert next(my_variations.events).pitches == [61]
        assert next(my_variations.events).pitches == [62]
        assert next(my_variations.events).pitches == [62]

class TestChordWindow(unittest.TestCase):
    def test_chord_window(self):
        row = [1,2,3,4,5]
        g = chord_window(row, window_size=4)
        assert list(g) == [
            Event(pitches=[1,2,3,4]),
            Event(pitches=[2,3,4,5]),
            Event(pitches=[3,4,5,1]),
            Event(pitches=[4,5,1,2]),
            Event(pitches=[5,1,2,3])
        ]

    def test_chord_window_non_overlap(self):
        row = [1,2,3,4,5]
        g = chord_window(row, window_size=4, overlap=False)
        assert list(g) == [
            Event(pitches=[1,2,3,4]),
            Event(pitches=[5,1,2,3])
        ]

    def test_exception_raised_if_window_larger_than_row(self):
        row = [1,2,3,4,5]
        next(chord_window(row, window_size=5))
        with self.assertRaises(Exception) as e:
            next(chord_window(row, window_size=6))


if __name__ == "__main__":
    unittest.main()
