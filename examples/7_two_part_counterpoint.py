"""Using the backtracking solver to generate a melodic line,
and then a lower voice that fits together with this, in
counterpoint in the style of Fux.
Note the use of probability gates to allow a degree
of felxibility in the application of the constraints.
"""
from composerstoolkit import *
from composerstoolkit.resources import scales

voice1 = backtracking_solver(
        Event(pitches=[60], duration=QUARTER_NOTE),
    constraints=[
        constraint_range(55, 127),
        constraint_in_set(scales.C_major),
        constraint_no_leaps_more_than(2),
        # enforce a V-I cadence at the end :
        constraint_notes_are(15, [59]),
        constraint_notes_are(16, [60])],
    heuristics=[
        # force the line to stay roughly level in shape
        heuristic_single_pitch(60, 10)],
    n_events=16,
)

voice1 = Sequence(voice1.events).transform(tie_repeated()).bake()

voice2 = backtracking_solver(
        Event(pitches=[52], duration=QUARTER_NOTE),
    constraints=[
        constraint_range(0, 65),
        probability_gate(
            constraint_in_set(scales.C_major),
            probability=0.08),
        constraint_no_leaps_more_than(4),
        constraint_no_voice_crossing(voice1),
        # limit the vertical intervals to octaves min/maj 3rds, 5ths and min/maj 6ths
        probability_gate(
            constraint_restrict_to_intervals({0,3,4,7,8,9}, voice1),
            probability=0.1),
        constraint_no_consecutives({0,5,7}, voice1),
        # enforce a V-I cadence at the end
        constraint_notes_are(15, [55]),
        constraint_notes_are(16, [52])],
    heuristics=[],
    n_events=16,
)

voice2 = Sequence(voice2.events).transform(tie_repeated()).bake()

Context.get_context().new_sequencer(bpm=60, playback_rate=1)\
    .add_sequence(voice1)\
    .add_sequence(voice2)\
    .playback()
