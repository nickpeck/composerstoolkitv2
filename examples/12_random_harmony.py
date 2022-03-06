"""Randomly sort a set of modes and move a voicing through
the resulting sequence of tonalities, maintaining best voice leading
via a lexicon of acceptable chord voicings.
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
from composerstoolkit.resources import scales, pitches, chords
from composerstoolkit.builders.permutators import Permutations

pf = pitches.PitchFactory()

# arbitary selection of scales
modes = [set(m) for m in [
    scales.D_major,
    scales.E_major,
    scales.C_mel_minor,
    scales.B_major,
    scales.Bb_major
]]

# library of 5-note quartal voicings from each scale
chord_lexicon = list(chords_from_scale(scales.D_major, n_voices=5, spacing=3))\
    + list(chords_from_scale(scales.E_major, n_voices=5, spacing=3))\
    + list(chords_from_scale(scales.B_major, n_voices=5, spacing=3))\
    + list(chords_from_scale(scales.C_mel_minor, n_voices=5, spacing=3))\
    + list(chords_from_scale(scales.Bb_major, n_voices=5, spacing=3))

random.shuffle(modes)

# Starting event, a typical quartal voicing using notes drawn from c major
start = Event([
    pf("D3"),
    pf("G4"),
    pf("C4"),
    pf("F4"),
    pf("A4")],
    duration=WHOLE_NOTE)

progression = Sequence.from_generator(
    voice_lead(event=start,
    scales=Permutations(starting_list=modes).flatten(),
    chord_lexicon = chord_lexicon)
).transform(fit_to_range(
    min_pitch = pf("C3"),
    max_pitch = pf("C9")
))

Container(bpm=300, playback_rate=1)\
    .add_sequence(progression)\
    .playback()
