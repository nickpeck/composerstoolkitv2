from composerstoolkit import *

artificial_scale = Sequence.from_generator(
    resultant_pitches(counters=[3,4,9], start_at=50)).bake()

chords = Sequence.from_generator(artificial_scale)\
    .transform(aggregate(4, HALF_NOTE))

seq = Sequence(
    events=Permutations([
        Event(pitches=[48], duration=QUARTER_NOTE),
        Event(pitches=[43], duration=QUARTER_NOTE),
        Event(pitches=[], duration=QUARTER_NOTE),
        Event(pitches=[41], duration=QUARTER_NOTE)]).flatten()
    ).transform(transpose(24))

Context.get_context().new_sequencer(bpm=100, playback_rate=1)\
    .add_sequence(seq.bake())\
    .add_sequence(chords.bake())\
    .show_notation()\
    .playback()
