"""
Takes a steady stream of middle C s and illustrates how to
create a more varied texture by higher order transformations.

'Gates' allow us to control when a transformation is applied,
using a controller function.

'Batches' allow us to group multiple transformations.

Both of these act as transformers in themselves, so can be
chained ad infinitum.
"""

from composerstoolkit.core import Event, Sequence, Container
from composerstoolkit.builders.transformers import (loop, batch,
    transpose, gated, rhythmic_augmentation, rhythmic_diminution)
from composerstoolkit.builders.permutators import Permutations
from composerstoolkit.resources.rhythms import *

def my_gate1(context):
    return context.beat_offset % 5 == 0

def my_gate2(context):
    return context.beat_offset % 9 == 0

seq = Sequence(events=[
        Event(pitches=[60], duration=QUARTER_NOTE),
    ]).transform(loop())\
    .transform(
        gated(
            rhythmic_augmentation(2),
            my_gate2))\
    .transform(
        gated(
            batch([
                transpose(12),
                rhythmic_diminution(0.5)])
          , my_gate2))

Container(bpm=240, playback_rate=1)\
    .add_sequence(seq)\
    .playback()
