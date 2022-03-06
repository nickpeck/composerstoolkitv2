"""Use a generator to find all the chords that can be produced from a given scale
"""

from composerstoolkit.core import Event, FiniteSequence, Container, Sequence, Constraint
from composerstoolkit.composers.solvers import develop
from composerstoolkit.composers.constraints import *
from composerstoolkit.builders.generators import *
from composerstoolkit.builders.transformers import *
from composerstoolkit.resources.rhythms import *
from composerstoolkit.composers.heuristics import *
from composerstoolkit.resources import scales

chords = Sequence.from_generator(chords_from_scale(
    scales.MEL_MINOR_SCALE_PITCH_CLASSES,
    spacing=3,
    n_voices=6,
    allow_inversions=False
)).transform(map_to_pulses(
     Sequence.from_generator(pulses([WHOLE_NOTE])).transform(loop())
)).transform(transpose(60))

Container(bpm=120, playback_rate=1)\
    .add_sequence(chords)\
    .playback()