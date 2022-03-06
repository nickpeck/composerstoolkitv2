import unittest

from composerstoolkit import *

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
        ).bake()
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

    # def test_slice_looper(self):
        # transformed = self.test_seq.transform(
            # slice_looper(n_events=2,n_repeats=2)
        # ).bake()
        # print(transformed.pitches)
        # assert transformed.pitches == [
            # 60,62,64,60,62,64,60,62,64,65,67]

    def test_transpose(self):
        transformed = self.test_seq.transform(
            transpose(interval=1)
        ).bake()
        assert transformed.pitches == [61,63,65,66,68]

    def test_transpose_diatonic(self):
        transformed = self.test_seq.transform(
            transpose_diatonic(steps=1, scale=scales.C_major)
        ).bake()
        assert transformed.pitches == [62,64,65,67,69]

    def test_transpose_diatonic_pass_on_error(self):
        transformed = self.test_seq.transform(
            transpose_diatonic(steps=1,
                scale=scales.D_major,
                pass_on_error=True)
        ).bake()
        assert transformed.pitches == [60,64,66,65,69]

    def test_transpose_diatonic_exc_if_source_not_in_scale(self):
        with self.assertRaises(ValueError) as ve:
            transformed = self.test_seq.transform(
                transpose_diatonic(steps=1,
                    scale=scales.D_major,
                    pass_on_error=False)
            ).bake()

    def test_retrograde(self):
        transformed = self.test_seq.transform(
            retrograde(n_pitches=5)
        ).bake()
        assert transformed.pitches == [67,65,64,62,60]

    def test_invert(self):
        transformed = self.test_seq.transform(
            invert()
        ).bake()
        assert transformed.pitches == [60,58,56,55,53]

    def test_invert_around_upper_axis(self):
        transformed = self.test_seq.transform(
            invert(axis_pitch=60)
        ).bake()
        assert transformed.pitches == [60,58,56,55,53]

    def test_invert_around_inner_axis(self):
        transformed = self.test_seq.transform(
            invert(axis_pitch=66)
        ).bake()
        assert transformed.pitches == [72,70,68,67,65]

    def test_rotation(self):
        transformed = self.test_seq.transform(
            rotate(n_pitches=5, no_times=1)
        ).bake()
        assert transformed.pitches == [62,64,65,67,60]

    def test_aggregate(self):
        transformed = self.test_seq.transform(
            aggregate(n_voices=5, duration=1)
        ).bake()
        assert transformed.events == [
            Event(pitches=[60,62,64,65,67], duration=1)
        ]

    def test_rhythmic_augmentation(self):
        transformed = self.test_seq.transform(
            rhythmic_augmentation(multiplier=2)
        ).bake()
        assert transformed.durations == [2,2,2,2,2]

    def test_rhythmic_diminution(self):
        transformed = self.test_seq.transform(
            rhythmic_diminution(factor=2)
        ).bake()
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
        ).bake()
        assert transformed.events == [
            Event(pitches=[60], duration=1),
            Event(pitches=[62], duration=2),
            Event(pitches=[65], duration=1),
            Event(pitches=[67], duration=1)
        ]


if __name__ == "__main__":
    unittest.main()