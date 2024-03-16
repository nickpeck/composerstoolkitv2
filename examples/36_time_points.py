from decimal import Decimal
import random

from composerstoolkit.core import Event, FiniteSequence, Sequencer, Sequence, Constraint
from composerstoolkit.composers.solvers import develop
from composerstoolkit.composers.constraints import *
from composerstoolkit.builders.generators import *
from composerstoolkit.builders.transformers import *
from composerstoolkit.resources.rhythms import *
from composerstoolkit.composers.heuristics import *
from composerstoolkit.resources import scales

row_pcs = list(scales.CHROMATIC_SCALE_PITCH_CLASSES)
random.shuffle(row_pcs)

# pitch_class: position in meter
time_point_set = {i:i for i in range(0, 12)}
print(time_point_set)

rhythm_transformer = rhythmic_time_points(time_points=time_point_set, meter_duration_beats=12)

def my_gate1(context):
    return random.choice([True, False])

p0 = Sequence.from_generator(cantus(row_pcs)) \
    .transform(loop()) \
    .transform(transpose(60)) \
    .transform(gated(transpose(12), my_gate1)) \
    .transform(rhythm_transformer)

i0 = Sequence.from_generator(cantus(row_pcs)) \
    .transform(loop()) \
    .transform(invert(0)) \
    .transform(transpose(54)) \
    .transform(gated(transpose(-12), my_gate1)) \
    .transform(rhythm_transformer)

mysequencer = Context.get_context().new_sequencer(bpm=120, playback_rate=4) \
    .add_sequence(p0) \
    .add_sequence(i0)

mysequencer.playback()
