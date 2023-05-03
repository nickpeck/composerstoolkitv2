from composerstoolkit import *

pf = pitches.PitchFactory()

source = FiniteSequence(events=[
    Event(pitches=[pf("C4")], duration=QUARTER_NOTE),
    Event(pitches=[pf("D4")], duration=QUARTER_NOTE),
    Event(pitches=[pf("E4")], duration=QUARTER_NOTE),
    Event(pitches=[pf("C4")], duration=QUARTER_NOTE),
    Event(pitches=[pf("C4")], duration=QUARTER_NOTE),
    Event(pitches=[pf("D4")], duration=QUARTER_NOTE),
    Event(pitches=[pf("E4")], duration=QUARTER_NOTE),
    Event(pitches=[pf("C4")], duration=QUARTER_NOTE),
    Event(pitches=[pf("E4")], duration=QUARTER_NOTE),
    Event(pitches=[pf("F4")], duration=QUARTER_NOTE),
    Event(pitches=[pf("G4")], duration=HALF_NOTE),
    Event(pitches=[pf("E4")], duration=QUARTER_NOTE),
    Event(pitches=[pf("F4")], duration=QUARTER_NOTE),
    Event(pitches=[pf("G4")], duration=HALF_NOTE),
    Event(pitches=[pf("G4")], duration=EIGHTH_NOTE),
    Event(pitches=[pf("A4")], duration=EIGHTH_NOTE),
    Event(pitches=[pf("G4")], duration=EIGHTH_NOTE),
    Event(pitches=[pf("F4")], duration=EIGHTH_NOTE),
    Event(pitches=[pf("E4")], duration=QUARTER_NOTE),
    Event(pitches=[pf("C4")], duration=QUARTER_NOTE),
    Event(pitches=[pf("G4")], duration=EIGHTH_NOTE),
    Event(pitches=[pf("A4")], duration=EIGHTH_NOTE),
    Event(pitches=[pf("G4")], duration=EIGHTH_NOTE),
    Event(pitches=[pf("F4")], duration=EIGHTH_NOTE),
    Event(pitches=[pf("E4")], duration=QUARTER_NOTE),
    Event(pitches=[pf("C4")], duration=QUARTER_NOTE),
    Event(pitches=[pf("C4")], duration=QUARTER_NOTE),
    Event(pitches=[pf("G3")], duration=QUARTER_NOTE),
    Event(pitches=[pf("C4")], duration=HALF_NOTE),
    Event(pitches=[pf("C4")], duration=QUARTER_NOTE),
    Event(pitches=[pf("G3")], duration=QUARTER_NOTE),
    Event(pitches=[pf("C4")], duration=HALF_NOTE),
])


constraints = [
    constraint_in_set(scales.C_major),
    #constraint_restrict_to_intervals(upper_voice=source, allow_intervals = [2,3,4,5,7]),
    constraint_no_consecutives(upper_voice=source, deny_intervals = [2,5,7])
]

canons = canon_finder(source, constraints)

canons.reverse()

for canon in canons:
    if canon.duration > 40:
        continue
    print(canon.meta["canon"])
    Context.get_context().new_sequencer(bpm=200, playback_rate=1, debug=False)\
        .add_sequence(source)\
        .add_sequence(canon)\
        .playback()