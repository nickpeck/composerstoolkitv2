"""Presents an infinate-length series of chords derived from
the 6th mode of limited transposition
"""
from composerstoolkit.core import Event, Sequence, Container
from composerstoolkit.builders.generators import cantus, pulses
from composerstoolkit.builders.transformers import loop, map_to_pulses, transpose, aggregate
from composerstoolkit.builders.permutators import Permutations
from composerstoolkit.resources.rhythms import *
from composerstoolkit.resources.scales import MODE_6_PITCH_CLASSES

even_pulse = Sequence.from_generator(
    pulses([WHOLE_NOTE]))\
    .transform(loop())

chords = Sequence.from_generator(
    cantus(
        Permutations(MODE_6_PITCH_CLASSES).flatten()))\
    .transform(transpose(48))\
    .transform(loop())\
    .transform(map_to_pulses(even_pulse))\
    .transform(aggregate(3, WHOLE_NOTE))

Container(bpm=100, playback_rate=1)\
    .add_sequence(chords)\
    .playback()
