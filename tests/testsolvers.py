import unittest

from composerstoolkit import *

class TestCLPSolver(unittest.TestCase):
    def test_we_can_derive_a_solution(self):
        solver = CLP(
            source_material = [
                FiniteSequence([
                    Event([60], 1),
                    Event([62], 1),
                    Event([64], 1),
                ])
            ],
            n_voices = 2,
            max_len_beats = 16
        )
        solution = next(solver)
        assert len(solution.voices) == 2
        assert solution.voices[0].duration == 16
        assert solution.voices[1].duration == 16

    def test_we_can_derive_multiple_unique_solutions(self):
        solver = CLP(
            source_material = [
                FiniteSequence([
                    Event([60], 1),
                    Event([62], 1),
                    Event([64], 1),
                ])
            ],
            n_voices = 2,
            max_len_beats = 16,
            transformations = [
                transpose(1),
                transpose(-1),
                transpose(2),
                transpose(-2)
            ]
        )
        solution1 = next(solver)
        solution2 = next(solver)
        assert [solution1.voices[0].pitches, solution1.voices[1].pitches] !=\
               [solution2.voices[0].pitches, solution2.voices[1].pitches]

    def test_clp_solver_global_constraints(self):
        solver = CLP(
            source_material = [
                FiniteSequence([
                    Event([60], 1),
                    Event([62], 1),
                    Event([64], 1),
                ])
            ],
            n_voices = 1,
            max_len_beats = 16,
            transformations = [
                transpose(1),
                transpose(-1),
                transpose(2),
                transpose(-2)
            ]
        )

        solver.add_constraint(
            constraint_range(minimum=55, maximum=65))
        solver.add_constraint(
            constraint_in_set(scales.F_major))

        solution = next(solver)
        assert len(solution.voices) == 1
        for part in solution.voices:
            assert min(part.pitches) >= 55
            assert max(part.pitches) <= 65
            assert set(part.pitches).difference(scales.F_major) == set()
            assert part.duration ==16

    def test_clp_solver_per_voice_constraints(self):
        solver = CLP(
            source_material = [
                FiniteSequence([
                    Event([60], 1),
                    Event([62], 1),
                    Event([64], 1),
                ])
            ],
            n_voices = 2,
            max_len_beats = 16,
            transformations = [
                transpose(1),
                transpose(-1),
                transpose(2),
                transpose(-2)
            ]
        )

        solver.voices[0].add_constraint(
            constraint_in_set(scales.F_major))
        solver.voices[1].add_constraint(
            constraint_in_set(scales.E_major))

        solution = next(solver)
        assert len(solution.voices) == 2
        assert set(solution.voices[0].pitches).difference(scales.F_major) == set()
        assert set(solution.voices[1].pitches).difference(scales.E_major) == set()

    # def test_clp_solver_with_heuristics_minimise(self):
        # solver = CLP(
            # source_material = [
                # FiniteSequence([
                    # Event([60], 1),
                    # Event([62], 1),
                    # Event([64], 1),
                # ])
            # ],
            # n_voices = 1,
            # max_len_beats = 16,
            # transformations = [
                # transpose(1),
                # transpose(-1),
                # transpose(2),
                # transpose(-2)
            # ],
            # heuristics = [
                # minimise(pitch_range()),
                # minimise(repeated_notes()),
            # ]
        # )
        # assert len(solution.voices) == 1
        # assert solution.voices[0].duration == 16

if __name__ == "__main__":
    unittest.main()
