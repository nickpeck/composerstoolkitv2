"""
In this example, we try to generate a melodic figure that curves upwards using increasingly  faster note values.
Rather than random generation, we use 90 degs of a sine wave as our guide.
The transformers consult the guide for each value, and then choose the nearest pitch, and rhythm from the available
domain of pitches and rhythms (in this case, notes of C major, and durations 1-12)
"""

from random import choices
import more_itertools
import math

from composerstoolkit import *

pitch_domain = list(scales.C_major)
rhythm_domain = list(range(1,12))
pf = PitchFactory()
N_EVENTS = 20

def my_generator():
    for i in range(N_EVENTS):
        yield Event(pitches=pitch_domain, duration=1)

@Transformer
def curve_upwards(seq: Sequence):
    time_elapsed = 0
    for event in seq.events:
        time_elapsed = time_elapsed + event.duration
        target_note = shapes.curve_target(time_elapsed, start_value=30, end_value=127)
        nearest_pitch = sorted(pitch_domain, reverse=False, key=lambda i: abs(i - target_note))[0]
        yield event.extend(pitches=[nearest_pitch])

@Transformer
def increase_density(seq: Sequence, starting_duration=6):
    time_elapsed = 0
    for event in seq.events:
        time_elapsed = time_elapsed + event.duration
        target_dur = shapes.curve_target(time_elapsed, start_value=rhythm_domain[-1], end_value=rhythm_domain[0])
        next_dur = sorted(rhythm_domain, reverse=False, key=lambda i: abs(i - target_dur))[0]
        yield event.extend(duration=next_dur)

seq = Sequence.from_generator(my_generator())\
    .transform(
        curve_upwards()
    )\
    .transform(
        increase_density()
    )

sequencer = Sequencer(debug=True, playback_rate=50).add_sequences(seq)

sequencer.playback()