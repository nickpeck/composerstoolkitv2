from composerstoolkit import *

artificial_scale = resultant_pitches(counters=[3,4,9], start_at=50)

chords = Sequence.from_generator(artificial_scale)\
    .transform(aggregate(4, HALF_NOTE)).bake(n_events=5)

seq = Sequence(
    events=Permutations([
        Event(pitches=[48], duration=QUARTER_NOTE),
        Event(pitches=[43], duration=QUARTER_NOTE),
        Event(pitches=[], duration=QUARTER_NOTE),
        Event(pitches=[41], duration=QUARTER_NOTE)]).flatten()
    ).transform(transpose(24)).bake(n_beats=20)

Context.get_context().new_sequencer(bpm=100, playback_rate=1)\
    .add_sequence(seq)\
    .add_sequence(chords)\
    .show_notation()\
    .playback()
