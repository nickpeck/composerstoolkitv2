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

durations = Sequence.from_generator(pulses({1}))\
            .transform(loop())

def my_gate1(context):
    return random.choice([True, False])

@Transformer
def chordal_aggregate(seq):
    n_voices = random.choice([1,2,3])
    buffer = []
    for event in seq.events:
        for pitch in event.pitches:
            if len(buffer) < n_voices - 1:
                buffer.append(pitch)
            else:
                buffer.append(pitch)
                yield Event(pitches=sorted(buffer), duration=event.duration)
                buffer = []
                n_voices = random.choice([1,2,3,4])

@Transformer
def rhythmic_aggregate(seq):
    diminution_factor = Decimal('1.0') / Decimal('3')
    notes_in_burst = random.choice([1,2,3,4])
    buffer = []
    for event in seq.events:
        if len(buffer) < notes_in_burst - 1:
            buffer.append(event)
        else:
            buffer.append(event)
            for event in buffer:
                yield Event(
                    pitches=event.pitches,
                    duration=float(event.duration * diminution_factor)
                )
            buffer = []
            notes_in_burst = random.choice([1,2,3,4])

p0 = Sequence.from_generator(cantus(row_pcs))\
        .transform(loop())\
        .transform(transpose(60))\
        .transform(gated(transpose(12), my_gate1))\
        .transform(map_to_pulses(durations))\
        .transform(gated(rhythmic_aggregate(), my_gate1))

i0 = Sequence.from_generator(cantus(row_pcs))\
        .transform(loop())\
        .transform(invert(0))\
        .transform(transpose(54))\
        .transform(gated(transpose(-12), my_gate1))\
        .transform(gated(chordal_aggregate(), my_gate1))\
        .transform(map_to_pulses(durations))\
        .transform(gated(rhythmic_aggregate(), my_gate1))

mysequencer = Context.get_context().new_sequencer(bpm=120, playback_rate=1)\
    .add_sequence(p0)\
    .add_sequence(i0)
    
mysequencer.playback()
