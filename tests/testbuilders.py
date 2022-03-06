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

if __name__ == "__main__":
    unittest.main()