"""Explores modifying a sequence by random paramter mutation.
"""

from composerstoolkit.core import Event, FiniteSequence, Container, Sequence, Constraint
from composerstoolkit.composers.solvers import develop
from composerstoolkit.composers.constraints import *
from composerstoolkit.builders.generators import *
from composerstoolkit.builders.transformers import *
from composerstoolkit.resources.rhythms import *
from composerstoolkit.composers.heuristics import *
from composerstoolkit.resources import scales, pitches, chords
from composerstoolkit.builders.permutators import Permutations

cmaj_one_8va = [p + 60 for p in scales.MAJ_SCALE_PITCH_CLASSES]

def mutate_pitch(event, value):
    return Event([value], event.duration)

def mutation_duration(event, value):
    return Event(event.pitches, value)

even_pulse = Sequence.from_generator(
    pulses([QUARTER_NOTE]))\
    .transform(loop())

seq = Sequence.from_generator(
    cantus(cmaj_one_8va)
).transform(
    map_to_pulses(even_pulse)
).transform(
    loop()
).transform(
    random_mutation(
        key_function = mutate_pitch,
        choices = cmaj_one_8va,
        threshold =0.8)
).transform(
    random_mutation(
        key_function = mutation_duration,
        choices = [0.5,1],
        threshold =0.3)
)

Container(bpm=150, playback_rate=1)\
    .add_sequence(seq)\
    .playback()
