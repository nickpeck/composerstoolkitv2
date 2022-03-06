"""Using randomly chosen variations to generate a constantly
evolving texture from a given cell.
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

pf = pitches.PitchFactory()


base_seq = FiniteSequence(events=[
        Event([pf("C6")], duration=QUARTER_NOTE),
        Event([pf("Eb6")], duration=EIGHTH_NOTE),
        Event([pf("C6")], duration=EIGHTH_NOTE),
        Event([pf("F6")], duration=QUARTER_NOTE),
        Event([pf("C6")], duration=EIGHTH_NOTE),
        Event([pf("Eb6")], duration=QUARTER_NOTE),
        Event([pf("C6")], duration=EIGHTH_NOTE),
        Event([pf("F6")], duration=QUARTER_NOTE)]
)

melodic_variations1 = base_seq.variations(
    n_times = None,
    transformer = random_transformation([
        rotate(7),
        invert(axis_pitch=pf("C6")),
        map_to_pitches(base_seq),
        map_to_pulses(base_seq)
    ]),
    repeats_per_var=2
).transform(
    modal_quantize(scale=scales.Bb_major)
)

melodic_variations2 = base_seq.variations(
    n_times = None,
    transformer = random_transformation([
        rotate(7),
        invert(axis_pitch=pf("C6")),
        map_to_pitches(base_seq),
        map_to_pulses(base_seq),
        rhythmic_augmentation(2),
        rhythmic_diminution(0.5)
    ]),
    repeats_per_var=2
).transform(
    modal_quantize(scale=scales.Bb_major)
)

Container(bpm=150, playback_rate=1)\
    .add_sequence(melodic_variations1)\
    .add_sequence(melodic_variations2)\
    .playback()
