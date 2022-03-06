"""Randomly sort a set of modes and move a voicing through
the resulting sequence of tonalities, maintaining best voice leading.
"""
from decimal import Decimal
import random

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

modes = [set(m) for m in [
    scales.D_major,
    scales.E_major,
    scales.Ab_mel_minor,
    scales.Db_mel_minor,
    scales.B_major
]]

random.shuffle(modes)

start = Event([
    pf("C4"),
    pf("E4"),
    pf("G4")],
    duration=WHOLE_NOTE)

progression = Sequence.from_generator(
    voice_lead(event=start,
    scales=Permutations(starting_list=modes).flatten())
).transform(fit_to_range(
    min_pitch = pf("C3"),
    max_pitch = pf("C9")
))

Container(bpm=120, playback_rate=1)\
    .add_sequence(progression)\
    .playback()