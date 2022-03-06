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

    def test_resultant_pitches(self):
        events = resultant_pitches(counters=[2,3])
        assert next(events) == Event(pitches=[0], duration=0)
        assert next(events) == Event(pitches=[2], duration=0)
        assert next(events) == Event(pitches=[3], duration=0)
        assert next(events) == Event(pitches=[4], duration=0)
        assert next(events) == Event(pitches=[6], duration=0)
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

    def test_rangom_noise(self):
        gen = random_noise(max_len=3)
        next(gen)
        next(gen)
        next(gen)
        with self.assertRaises(StopIteration):
            assert next(gen)

    def test_random_choice(self):
        gen = random_choice(
            choices=[Event(pitches=[60])],
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
