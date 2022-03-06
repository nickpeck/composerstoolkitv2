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
