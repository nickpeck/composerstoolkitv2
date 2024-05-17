"""Presents an infinate-length texture composed of random slices of a
4-note sequence in the upper voice, over an ostinato composed out of
permutations of another 4-note group.
"""

from composerstoolkit import *

ostinato = Sequence(
    events=Permutations([
        Event(pitches=[48], duration=QUARTER_NOTE),
        Event(pitches=[43], duration=QUARTER_NOTE),
        Event(pitches=[45], duration=QUARTER_NOTE),
        Event(pitches=[41], duration=QUARTER_NOTE)]).flatten()
    )\
    .transform(loop())

seq_upper = Sequence.from_generator(random_slice(
    Sequence(events=[
        Event(pitches=[60], duration=QUARTER_NOTE),
        Event(pitches=[62], duration=HALF_NOTE),
        Event(pitches=[64], duration=DOTTED(HALF_NOTE)),
        Event(pitches=[59], duration=WHOLE_NOTE),
    ])
))

Context.get_context().new_sequencer(bpm=240, playback_rate=1, queue_size=40)\
    .add_sequence(seq_upper)\
    .add_sequence(ostinato)\
    .playback()

# this idea would also work well when applied to percussion/drum fragment
