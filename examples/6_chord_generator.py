"""Presents an infinate-length series of chords derived from
an artifical scale constructed from the resultant pattern
of 3 different integers.
"""
from composerstoolkit import *

artificial_scale = Sequence.from_generator(
    resultant_pitches(counters=[3,4,9], start_at=40)).bake()

chords = Sequence.from_generator(artificial_scale)\
    .transform(loop())\
    .transform(aggregate(4, HALF_NOTE))

mysequencer = Context.get_context().new_sequencer(bpm=100, playback_rate=1, debug=True)\
    .add_sequence(chords)

mysequencer.playback()
