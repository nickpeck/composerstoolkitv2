"""Here we use material generated using the concept of axis that coalesce
around the scale tonic.
There are three elements to the texture:
- an offbeat melodic line (violin, flute, synth?)
- a chord progression as a series of arpeggios (vibraphone, harp?)
- a baseline (cello?)
"""
from decimal import Decimal

from composerstoolkit.core import Event, FiniteSequence, Container, Sequence, Constraint
from composerstoolkit.composers.solvers import develop
from composerstoolkit.composers.constraints import *
from composerstoolkit.builders.generators import *
from composerstoolkit.builders.transformers import *
from composerstoolkit.resources.rhythms import *
from composerstoolkit.composers.heuristics import *
from composerstoolkit.resources import scales, pitches
from composerstoolkit.builders.permutators import Permutations

pf = pitches.PitchFactory()

melody = Sequence.from_generator(
    axis_melody(
        axis_pitch = pf("C6"),
        scale = scales.C_mel_minor,
        steps = 14,
        direction="contract"
)).transform(map_to_pulses(
     Sequence.from_generator(collision_pattern(4,5)).transform(loop())
)).transform(fit_to_range(
    min_pitch = pf("G5"),
    max_pitch = pf("C7")
)).transform(rhythmic_augmentation(
    multiplier = 2
)).transform(loop(
))

baseline = melody.transform(loop(
)).transform(fit_to_range(
    min_pitch = pf("G0"),
    max_pitch = pf("G2")
)).transform(rhythmic_augmentation(
    multiplier = 3
))

melody = melody.transform(linear_interpolate(
    steps = 8,
    constrain_to_scale = list(scales.C_mel_minor)
)).transform(tie_repeated(
))

accompaniment = Sequence.from_generator(
    axis_melody(
        axis_pitch = pf("C3"),
        scale = scales.C_mel_minor,
        steps = 14,
        direction="contract"
)).transform(map_to_pulses(
     Sequence.from_generator(pulses([WHOLE_NOTE])).transform(loop())
)).transform(concertize(
    voicing = [2,4,6],
    scale = scales.C_mel_minor,
    direction="up"
)).transform(fit_to_range(
    min_pitch = pf("G3"),
    max_pitch = pf("G4")
)).transform(arpeggiate(
)).transform(loop(
))

Container(bpm=120, playback_rate=1)\
    .add_sequence(melody, offset=EIGHTH_NOTE)\
    .add_sequence(accompaniment)\
    .add_sequence(baseline)\
    .playback()
