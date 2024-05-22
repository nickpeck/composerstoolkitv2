import unittest

import numpy as np

from composerstoolkit import *
from testcore import MockContext

class PermutationsTests(unittest.TestCase):

    def test_permutate_single_generations(self):
        assert list(Permutations([2,1,1,2])) == [
            (1, 2, 1, 2),
            (1, 1, 2, 2),
            (2, 1, 2, 1),
            (2, 2, 1, 1),
            (2, 1, 1, 2),
            (1, 2, 2, 1)]

    def test_can_flatten_the_lists(self):
        assert list(Permutations([2,1,1,2]).flatten()) == [
            1, 2, 1, 2,
            1, 1, 2, 2,
            2, 1, 2, 1,
            2, 2, 1, 1,
            2, 1, 1, 2,
            1, 2, 2, 1]

    def test_permutate_multiple_generations(self):
        assert list(Permutations([2,1,1,2], n_generations=2)) == [
            (1, 2, 1, 2),
            (1, 1, 2, 2),
            (2, 1, 2, 1),
            (2, 2, 1, 1),
            (2, 1, 1, 2),
            (1, 2, 2, 1),
            (1, 1, 1, 1, 1, 1)]
        # more complex case, 3 generations
        perms = Permutations([4,5], n_generations=3)
        assert list(perms) == [
        (4, 5), (5, 4),
        (2, 2, 3, 2),
        (2, 3, 2, 2),
        (3, 2, 2, 2),
        (2, 2, 2, 3),
        (1, 2, 1, 1, 1, 1, 1, 1),
        (1, 1, 1, 1, 2, 1, 1, 1),
        (2, 1, 1, 1, 1, 1, 1, 1),
        (1, 1, 1, 1, 1, 1, 2, 1),
        (1, 1, 1, 1, 1, 1, 1, 2),
        (1, 1, 1, 2, 1, 1, 1, 1),
        (1, 1, 1, 1, 1, 2, 1, 1),
        (1, 1, 2, 1, 1, 1, 1, 1)]

    def test_we_can_demand_the_last_gen_only(self):
        perms = Permutations([2,1,1,2],
                 n_generations=2, 
                 return_last_gen_only=True)
        assert list(perms) == [(1, 1, 1, 1, 1, 1)]

class SerialMatrixTests(unittest.TestCase):
    def test_generate_permutations_is_iterable(self):
        matrix = SerialMatrix([2,1,3])
        permutations = [p for p in matrix]
        assert permutations == [[2,1,3], [1,3,2], [3,2,1]]

    def test_can_return_numpy_array(self):
        matrix = SerialMatrix([2,1,3]).as_matrix()
        assert np.array_equal(matrix, np.array([[2,1,3], [1,3,2], [3,2,1]]))

class TransformerTests(unittest.TestCase):
    def setUp(self):
        self.test_seq = Sequence([
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=1),
            Event(pitches=[64], duration=1),
            Event(pitches=[65], duration=1),
            Event(pitches=[67], duration=1)
        ])

    def test_of_loop_n_times(self):
        transformed = self.test_seq.transform(
            loop(n_times=1)
        ).bake(n_events=10)
        assert transformed.pitches == [
            60,62,64,65,67,60,62,64,65,67]

    def test_of_loop_negative_inout_raises_exc(self):
        with self.assertRaises(Exception) as e:
            transformed = self.test_seq.transform(
                loop(n_times=-1)
            ).bake()

    def test_of_loop_infinate(self):
        transformed = self.test_seq.transform(
            loop()
        )
        pitches = [next(transformed.events).pitches[-1] for i in range(500)]
        assert pitches[-5:] == [60,62,64,65,67]

    def test_slice_looper(self):
        transformed = self.test_seq.transform(
            slice_looper(n_events=2,n_repeats=2)
        ).bake(n_events=9)
        assert transformed.pitches == [
            60,62,60,62,64,65,64,65,67]

    def test_feedback(self):
        transformed = self.test_seq.transform(
            feedback(n_events=2)
        ).bake(n_events=5)
        chords = [e.pitches for e in transformed.events]
        assert chords == [
            [60],
            [60, 62],
            [60, 62, 64],
            [60, 62, 64, 65],
            [60, 62, 64, 65, 67]]

    def test_transpose(self):
        transformed = self.test_seq.transform(
            transpose(interval=1)
        ).bake(n_events=5)
        assert transformed.pitches == [61,63,65,66,68]

    def test_transpose_diatonic(self):
        transformed = self.test_seq.transform(
            transpose_diatonic(steps=1, scale=scales.C_major)
        ).bake(n_events=5)
        assert transformed.pitches == [62,64,65,67,69]

    def test_transpose_diatonic_pass_on_error(self):
        transformed = self.test_seq.transform(
            transpose_diatonic(steps=1,
                scale=scales.D_major,
                pass_on_error=True)
        ).bake(n_events=5)
        assert transformed.pitches == [60,64,66,65,69]

    def test_transpose_diatonic_pass_on_out_of_bounds(self):
        transformed = self.test_seq.transform(
            transpose_diatonic(steps=1,
                scale=[],
                pass_on_error=True)
        ).bake(n_events=5)
        assert transformed.pitches == [60, 62, 64, 65, 67]

    def test_transpose_diatonic_exc_if_source_not_in_scale(self):
        with self.assertRaises(ValueError) as ve:
            transformed = self.test_seq.transform(
                transpose_diatonic(steps=1,
                    scale=scales.D_major,
                    pass_on_error=False)
            ).bake(n_events=5)

    def test_retrograde(self):
        transformed = self.test_seq.transform(
            retrograde(n_pitches=5)
        ).bake(n_events=5)
        assert transformed.pitches == [67,65,64,62,60]

    def test_invert(self):
        transformed = self.test_seq.transform(
            invert()
        ).bake(n_events=5)
        assert transformed.pitches == [60,58,56,55,53]

    def test_invert_empty_seq(self):
        transformed = Sequence([]).transform(
            invert()
        ).bake(n_events=5)
        assert transformed.pitches == []

    def test_invert_around_upper_axis(self):
        transformed = self.test_seq.transform(
            invert(axis_pitch=60)
        ).bake(n_events=5)
        assert transformed.pitches == [60,58,56,55,53]

    def test_invert_around_inner_axis(self):
        transformed = self.test_seq.transform(
            invert(axis_pitch=66)
        ).bake(n_events=5)
        assert transformed.pitches == [72,70,68,67,65]

    def test_rotation(self):
        transformed = self.test_seq.transform(
            rotate(n_pitches=5, no_times=1)
        ).bake(n_events=5)
        assert transformed.pitches == [62,64,65,67,60]

    def test_aggregate(self):
        transformed = self.test_seq.transform(
            aggregate(n_voices=5, duration=1)
        ).bake(n_events=1)
        assert transformed.events == [
            Event(pitches=[60,62,64,65,67], duration=1)
        ]

    def test_aggregate_different_no_voices(self):
        transformed = self.test_seq.transform(
            aggregate(n_voices=4, duration=1)
        ).bake(n_events=2)
        assert transformed.events == [
            Event(pitches=[60,62,64,65], duration=1),
            Event(pitches=[67], duration=1)
        ]

    def test_rhythmic_augmentation(self):
        transformed = self.test_seq.transform(
            rhythmic_augmentation(multiplier=2)
        ).bake(n_events=5)
        assert transformed.durations == [2,2,2,2,2]

    def test_rhythmic_diminution(self):
        transformed = self.test_seq.transform(
            rhythmic_diminution(factor=2)
        ).bake(n_events=5)
        assert transformed.durations == [0.5,0.5,0.5,0.5,0.5]

    def test_tie_repeated(self):
        seq = Sequence([
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=1),
            Event(pitches=[62], duration=1),
            Event(pitches=[65], duration=1),
            Event(pitches=[67], duration=1)
        ])
        transformed = seq.transform(
            tie_repeated()
        ).bake(n_events=4)
        assert transformed.events == [
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=2),
            Event(pitches=[65], duration=1),
            Event(pitches=[67], duration=1)
        ]

    def test_fit_to_range_lower(self):
        transformed = self.test_seq.transform(
            fit_to_range(min_pitch=48, max_pitch=60)
        ).bake(n_events=5)
        assert transformed.pitches == [60,50,52,53,55]

    def test_fit_to_range_upper(self):
        transformed = self.test_seq.transform(
            fit_to_range(min_pitch=72, max_pitch=84)
        ).bake(n_events=5)
        assert transformed.pitches == [72,74,76,77,79]

    def test_fit_raises_exc_if_range_less_than_8va(self):
        with self.assertRaises(Exception) as e:
            transformed = self.test_seq.transform(
                fit_to_range(min_pitch=48, max_pitch=55)
            ).bake(n_events=5)

    def test_fit_raises_exc_if_min_less_than_max(self):
        with self.assertRaises(Exception) as e:
            transformed = self.test_seq.transform(
                fit_to_range(min_pitch=60, max_pitch=48)
            ).bake(n_events=5)

    def test_concertize_upwards(self):
        transformed = self.test_seq.transform(
            concertize(
                scale=scales.C_major,
                voicing=[2,4],
                direction="up")
        ).bake(n_events=5)
        chords = [e.pitches for e in transformed.events]
        assert chords == [
            [60,64,67],
            [62,65,69],
            [64,67,71],
            [65,69,72],
            [67,71,74],
        ]

    def test_concertize_with_rests(self):
        transformed = Sequence([Event([], 1)]).transform(
            concertize(
                scale=scales.C_major,
                voicing=[2,4],
                direction="up")
        ).bake(n_events=5)
        chords = [e.pitches for e in transformed.events]
        assert chords == [[]]

    def test_concertize_downwards(self):
        transformed = self.test_seq.transform(
            concertize(
                scale=scales.C_major,
                voicing=[2,4],
                direction="down")
        ).bake(n_events=5)
        chords = [e.pitches for e in transformed.events]
        assert chords == [
            [60,57,53],
            [62,59,55],
            [64,60,57],
            [65,62,59],
            [67,64,60]]

    def test_arpeggiate(self):
        seq = Sequence([
            Event(pitches=[60,62,64,65,67], duration=5),
        ])
        transformed = seq.transform(
            arpeggiate()
        ).bake(n_events=5)
        assert transformed.events == [
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=1),
            Event(pitches=[64], duration=1),
            Event(pitches=[65], duration=1),
            Event(pitches=[67], duration=1)
        ]

    def test_displacement(self):
        transformed = self.test_seq.transform(
            displacement(interval=1)
        ).bake(n_events=6)
        assert transformed.events == [
            Event(pitches=[], duration=1),
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=1),
            Event(pitches=[64], duration=1),
            Event(pitches=[65], duration=1),
            Event(pitches=[67], duration=1)
        ]

    def test_monody(self):
        seq = Sequence([
            Event(pitches=[60,62,64,65,67], duration=1),
        ])
        transformed = seq.transform(
            monody()
        ).bake(n_events=1)
        assert transformed.events == [
            Event(pitches=[67], duration=1)
        ]

    def test_monody_handles_rests(self):
        seq = Sequence([
            Event(pitches=[], duration=1),
        ])
        transformed = seq.transform(
            monody()
        ).bake(n_events=1)
        assert transformed.events == [
            Event(pitches=[], duration=1)
        ]

    def test_modal_quantize(self):
        transformed = self.test_seq.transform(
            modal_quantize(scale=scales.D_major)
        ).bake(n_events=5)
        assert transformed.pitches == [
            59,62,64,64,67]

    def test_rhythmic_quantize(self):
        seq = Sequence([
            Event(pitches=[60], duration=0.98),
            Event(pitches=[62], duration=1),
            Event(pitches=[64], duration=1.45),
            Event(pitches=[65], duration=1.1)
        ])
        transformed = seq.transform(
            rhythmic_quantize(resolution=1.0)
        ).bake(n_events=4)
        assert transformed.events == [
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=1),
            Event(pitches=[64], duration=1),
            Event(pitches=[65], duration=1)]

    def test_filter_events(self):
        my_filter = lambda e: e.pitches[-1] % 2 == 0
        transformed = self.test_seq.transform(
            filter_events(condition=my_filter)
        ).bake(n_events=2)
        assert transformed.events == [
            Event(pitches=[65], duration=1),
            Event(pitches=[67], duration=1)]

    def test_filter_events_replace_w_rest(self):
        my_filter = lambda e: e.pitches[-1] % 2 == 0
        transformed = self.test_seq.transform(
            filter_events(
                condition=my_filter,
                replace_w_rest=True)
        ).bake(n_events=5)
        assert transformed.events == [
            Event(pitches=[], duration=1),
            Event(pitches=[], duration=1),
            Event(pitches=[], duration=1),
            Event(pitches=[65], duration=1),
            Event(pitches=[67], duration=1)]

    def test_gated_transformer(self):
        my_gate = lambda c: c.beat_offset % 2 == 0
        def _context():
            i = 0
            while True:
                c = MockContext(
                    sequencer = None,
                    beat_offset = i,
                    time_offset_secs = i
                )
                yield c
                i = i + 1
        
        context = _context()
        
        transformed = self.test_seq.transform(
            gated(
                transformer=transpose(interval=12),
                condition=my_gate,
                get_context=lambda : next(context))
        ).bake(n_events=5)
        assert transformed.pitches == [
            72,62,76,65,79]

    def test_batch_transformer(self):
        transformed = self.test_seq.transform(
            batch(
                transformations=[
                    transpose(interval=2),
                    retrograde(n_pitches=5)])
        ).bake(n_events=5)
        assert transformed.pitches == [
            69,67,66,64,62]

    def test_random_transformations(self):
        transformed = self.test_seq.transform(
            random_transformation(
                transformations=[
                    transpose(interval=1),
                    retrograde(n_pitches=5)])
        ).bake(n_events=5)
        assert transformed.pitches in [
            [61,63,65,66,68],
            [67,65,64,62,60]]

    def test_map_to_pulses(self):
        pulse_seq = Sequence([Event([], d) for d in [1,2,3,4,5,6]])
        transformed = self.test_seq.transform(
            map_to_pulses(pulse_sequence=pulse_seq)
        ).bake(n_events=5)
        assert transformed.pitches == [60,62,64,65,67]
        assert transformed.durations == [1,2,3,4,5]

    def test_map_to_pulses_empty_pulse_seq(self):
        pulse_seq = Sequence([])
        transformed = self.test_seq.transform(
            map_to_pulses(pulse_sequence=pulse_seq)
        ).bake(n_events=5)
        assert transformed.pitches == [60,62,64,65,67]
        assert transformed.durations == [0,0,0,0,0]

    def test_map_to_pitches(self):
        pitch_seq = Sequence([Event([p], 1) for p in [1,2,3,4,5]])
        transformed = self.test_seq.transform(
            map_to_pitches(pitch_sequence=pitch_seq)
        ).bake(n_events=5)
        assert transformed.pitches == [1,2,3,4,5]
        assert transformed.durations == [1,1,1,1,1]

    def test_map_to_pitches_empty_pitch_seq(self):
        pitch_seq = Sequence([])
        transformed = self.test_seq.transform(
            map_to_pitches(pitch_sequence=pitch_seq)
        ).bake(n_events=5)
        assert transformed.pitches == []
        assert transformed.durations == [1,1,1,1,1]

    def test_explode_intervals_linear(self):
        transformed = self.test_seq.transform(
            explode_intervals(
                n_events=5,
                factor=2,
                mode="linear")
        ).bake(n_events=5)
        assert transformed.pitches == [60,64,68,71,75]

    def test_explode_intervals_single_event_input(self):
        transformed = Sequence([
            Event([60], 1)
        ]).transform(
            explode_intervals(
                n_events=1,
                factor=2,
                mode="linear")
        ).bake(n_events=1)
        assert transformed.pitches == [60]

    def test_explode_intervals_exponential(self):
        transformed = self.test_seq.transform(
            explode_intervals(
                n_events=5,
                factor=2,
                mode="exponential")
        ).bake(n_events=5)
        assert transformed.pitches == [60,64,68,70,74]

    def test_explode_intervals_unrecognised_mode(self):
        with self.assertRaises(Exception) as e:
            transformed = self.test_seq.transform(
                explode_intervals(
                    n_events=5,
                    factor=2,
                    mode="blah")
            ).bake(n_events=5)

    def test_linear_interpolate(self):
        seq = Sequence([
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=1),
            Event(pitches=[64], duration=1)
        ])
        transformed = seq.transform(
            linear_interpolate(steps=2)
        ).bake(n_events=5)
        assert transformed.pitches == [60,61,62,63,64]

    def test_linear_interpolate_single_event(self):
        seq = Sequence([
            Event(pitches=[60], duration=1)
        ])
        transformed = seq.transform(
            linear_interpolate(steps=2)
        ).bake(n_events=1)
        assert transformed.pitches == [60]

    def test_linear_interpolate_repeated_pitch(self):
        seq = Sequence([
            Event(pitches=[60], duration=1),
            Event(pitches=[60], duration=1)
        ])
        transformed = seq.transform(
            linear_interpolate(steps=2)
        ).bake(n_events=2)
        assert transformed.pitches == [60, 60]

    def test_linear_interpolate_constrain_to_scale(self):
        seq = Sequence([
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=1),
            Event(pitches=[64], duration=1)
        ])
        transformed = seq.transform(
            linear_interpolate(
                steps=2,
                constrain_to_scale=scales.C_major)
        ).bake(n_events=5)
        assert transformed.pitches == [60,60,62,62,64]

    def test_motivic_interpolation(self):
        motive = FiniteSequence([
            Event(pitches=[1], duration=1),
            Event(pitches=[2], duration=1),
            Event(pitches=[0], duration=1)
        ])
        seq = Sequence([
            Event(pitches=[60], duration=3),
            Event(pitches=[63], duration=3),
        ])
        transformed = seq.transform(
            motivic_interpolation(motive=motive)
        ).bake(n_events=6)
        assert transformed.events == [
            Event([60], 1),
            Event([61], 1),
            Event([59], 1),
            Event([63], 1),
            Event([64], 1),
            Event([62], 1)]

    def test_motivic_interpolation_exc_if_not_finiteseq(self):
        motive = Sequence([
            Event(pitches=[1], duration=1),
            Event(pitches=[2], duration=1),
            Event(pitches=[0], duration=1)
        ])
        seq = Sequence([
            Event(pitches=[60], duration=3),
            Event(pitches=[63], duration=3),
        ])
        with self.assertRaises(Exception) as e:
            transformed = seq.transform(
                motivic_interpolation(motive=motive)
            ).bake(n_events=5)

    def test_motivic_interpolation_exc_if_motive_starts_w_rest(self):
        motive = FiniteSequence([Event([], 1)])
        seq = Sequence([
            Event(pitches=[60], duration=3),
            Event(pitches=[63], duration=3),
        ])
        with self.assertRaises(Exception) as e:
            transformed = seq.transform(
                motivic_interpolation(motive=motive)
            ).bake(n_events=5)

    def test_motivic_interpolation_exc_if_seq_contains_rests(self):
        motive = FiniteSequence([Event([1], 1)])
        seq = Sequence([
            Event(pitches=[], duration=3),
            Event(pitches=[], duration=3),
        ])
        transformed = seq.transform(
            motivic_interpolation(motive=motive)
        ).bake(n_events=2)
        assert transformed.events == [
            Event(pitches=[], duration=3),
            Event(pitches=[], duration=3),
        ]

    def test_motivic_interpolation_w_rests(self):
        motive = FiniteSequence([
            Event(pitches=[1], duration=1),
            Event(pitches=[], duration=1),
            Event(pitches=[], duration=1)
        ])
        seq = Sequence([
            Event(pitches=[60], duration=3),
            Event(pitches=[63], duration=3),
        ])
        transformed = seq.transform(
            motivic_interpolation(motive=motive)
        ).bake(n_events=6)
        assert transformed.events == [
            Event([60], 1),
            Event([], 1),
            Event([], 1),
            Event([63], 1),
            Event([], 1),
            Event([], 1)]

    def test_random_mutation(self):
        seq = Sequence([Event([0],1) for i in range(1000)])
        transformed = seq.transform(
            random_mutation(
                key_function=lambda e,v: Event([v], e.duration),
                choices=[1],
                threshold=0.5
            )
        ).bake(n_events=1000)
        new_pitches = transformed.pitches
        mutated = list(filter(lambda e: e == 1, new_pitches))
        assert len(mutated) > 400 and len(mutated) < 600

    def test_tintinnabulation_below(self):
        seq = Sequence([Event([0], 1)]).transform(tintinnabulation(t_voice_pcs={0,4,7}, position="below"))
        assert next(seq.events).pitches == [0,-5]
        seq = Sequence([Event([2], 1)]).transform(tintinnabulation(t_voice_pcs={0,4,7}, position="below"))
        assert next(seq.events).pitches == [2,0]
        seq = Sequence([Event([5], 1)]).transform(tintinnabulation(t_voice_pcs={0,4,7}, position="below"))
        assert next(seq.events).pitches == [5,4]
        seq = Sequence([Event([8], 1)]).transform(tintinnabulation(t_voice_pcs={0,4,7}, position="below"))
        assert next(seq.events).pitches == [8,7]
        seq = Sequence([Event([12], 1)]).transform(tintinnabulation(t_voice_pcs={0,4,7}, position="below"))
        assert next(seq.events).pitches == [12,7]
        seq = Sequence([Event([13], 1)]).transform(tintinnabulation(t_voice_pcs={0,4,7}, position="below"))
        assert next(seq.events).pitches == [13,12]

    def test_tintinnabulation_above(self):
        seq = Sequence([Event([0], 1)]).transform(tintinnabulation(t_voice_pcs={0,4,7}, position="above"))
        assert next(seq.events).pitches == [0,4]
        seq = Sequence([Event([2], 1)]).transform(tintinnabulation(t_voice_pcs={0,4,7}, position="above"))
        assert next(seq.events).pitches == [2,4]
        seq = Sequence([Event([5], 1)]).transform(tintinnabulation(t_voice_pcs={0,4,7}, position="above"))
        assert next(seq.events).pitches == [5,7]
        seq = Sequence([Event([8], 1)]).transform(tintinnabulation(t_voice_pcs={0,4,7}, position="above"))
        assert next(seq.events).pitches == [8,12]
        seq = Sequence([Event([12], 1)]).transform(tintinnabulation(t_voice_pcs={0,4,7}, position="above"))
        assert next(seq.events).pitches == [12,16]
        seq = Sequence([Event([13], 1)]).transform(tintinnabulation(t_voice_pcs={0,4,7}, position="above"))
        assert next(seq.events).pitches == [13,16]

    def test_tintinnabulation_abovebelow(self):
        events = [Event([i], 1) for i in range(2,9)]
        seq = Sequence(events).transform(tintinnabulation(t_voice_pcs={0,4,7}, position="abovebelow"))
        event_pitches = [e.pitches for e in seq.events]
        assert(event_pitches == [[2,4], [3,0], [4,7], [5,4], [6,7], [7,4], [8,12]])

    def test_tintinnabulation_belowabove(self):
        events = [Event([i], 1) for i in range(2,9)]
        seq = Sequence(events).transform(tintinnabulation(t_voice_pcs={0,4,7}, position="belowabove"))
        event_pitches = [e.pitches for e in seq.events]
        assert(event_pitches == [[2,0], [3,4], [4,0], [5,7], [6,4], [7,12], [8,7]])

    def test_split_voices(self):
        seq1 = Sequence()
        seq2 = Sequence()
        seq3 = Sequence()
        seq4 = Sequence()
        events = [Event([1,2,3], 1), Event([4,5],2), Event([], 1)]
        seq = Sequence(events).transform(split_voices(seq1, seq2, seq3, seq4))
        list(seq.events)
        assert list(seq1.events) == [Event([1], 1), Event([4], 2), Event([], 1)]
        assert list(seq2.events) == [Event([2], 1), Event([5], 2), Event([], 1)]
        assert list(seq3.events) == [Event([3], 1), Event([], 2), Event([], 1)]
        assert list(seq4.events) == [Event([], 1), Event([], 2), Event([], 1)]

    def test_split_voices_double_lead(self):
        seq1 = Sequence()
        seq2 = Sequence()
        seq3 = Sequence()
        seq4 = Sequence()
        events = [Event([1,2,3], 1), Event([4,5],2), Event([], 1)]
        seq = Sequence(events).transform(split_voices(seq1, seq2, seq3, seq4, mode="doublelead"))
        list(seq.events)
        assert list(seq1.events) == [Event([1], 1), Event([4], 2), Event([], 1)]
        assert list(seq2.events) == [Event([1], 1), Event([4], 2), Event([], 1)]
        assert list(seq3.events) == [Event([2], 1), Event([4], 2), Event([], 1)]
        assert list(seq4.events) == [Event([3], 1), Event([5], 2), Event([], 1)]


if __name__ == "__main__":
    unittest.main()