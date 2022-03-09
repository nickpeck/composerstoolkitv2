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
        assert len(solution) == 2
        assert solution[0].duration == 16
        assert solution[1].duration == 16

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
        assert len(solution) == 1
        for part in solution:
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
        assert len(solution) == 2
        assert set(solution[0].pitches).difference(scales.F_major) == set()
        assert set(solution[1].pitches).difference(scales.E_major) == set()

if __name__ == "__main__":
    unittest.main()
