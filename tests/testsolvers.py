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

    # def test_w_constraints(self):
        # solver = CLP(
            # source_material = [
                # FiniteSequence([
                    # Event([60], 1),
                    # Event([62], 1),
                    # Event([64], 1),
                # ])
            # ],
            # n_voices = 3,
            # max_len_beats = 16,
            # transformations = [
                # transpose(1),
                # transpose(-1)
            # ]
        # )

        # solver.add_constraint(
            # solver.voices[0],
            # constraint=constraint_notes_are(
                # beat_offset = 15,
                # pitches=[60]))

        # solver.add_constraint(
            # constraint=constraint_use_chords(
                # chords = [{},{}],
                # voices=solver.voices))

        # solution = next(solver)
        # print(solution[0].pitches)

if __name__ == "__main__":
    unittest.main()
