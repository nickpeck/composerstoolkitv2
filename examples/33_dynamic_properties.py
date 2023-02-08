"""This introduces 'dyanamic' properties that allow us to delegate previously fixed args
of transformers to a function that is computed at runtime. This makes it easy
to create transformers that change/shape a musical sequence over time.

In this example, we generate a stream of random notes and pass it through a transformer
that forces the notes into a given octave space that rises upwards every 60 beats.
"""

from composerstoolkit import *

def max_pitch():
    if mysequencer.context is not None:
        x = int(mysequencer.context.beat_offset) % 60
        if x >= 24:
            return x
    return 24

def min_pitch():
    if mysequencer.context is not None:
        x = int(mysequencer.context.beat_offset % 60)
        if x > 24:
            return x - 24
    return 12


line = Sequence.from_generator(random_noise()).transform(fit_to_range(
    max_pitch = IntProperty(max_pitch),
    min_pitch = IntProperty(min_pitch)
))

mysequencer = Sequencer(bpm=300, debug=True) \
    .add_sequence(line, channel_no=1)

mysequencer.playback()
