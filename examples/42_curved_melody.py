"""
In this example, we try to generate a melodic figure that curves upwards using increasingly faster note values.
Rather than random generation, we use 90 degs of a sine wave as our guide.
The transformers consult the guide for each value, and then choose the nearest pitch, and nearest rhythm from the available
domain of pitches and rhythms (in this case, notes of C major, and durations 1-12)
"""

from random import choices
import more_itertools
import math

from composerstoolkit import *

pitch_domain = list(scales.C_major)
rhythm_domain = list(range(1,12))
pf = pitches.PitchFactory()
N_EVENTS = 20

def my_generator():
    for i in range(N_EVENTS):
        yield Event(pitches=pitch_domain, duration=1)

# upwards trending sine
melodic_curve = shapes.Curve(
    bounds_x=(0, N_EVENTS), # number of time-points
    bounds_y=(30, 127), # range of midi pitch values
    bounds_deg=(0, 90)
)

# downwards trending sine
durations_curve = shapes.Curve(
    bounds_x=(0, N_EVENTS), # number of time-points
    bounds_y=(sorted(rhythm_domain)[0], sorted(rhythm_domain)[-1]), # range of durations
    bounds_deg=(90, 180)
)

# if mathplotlib - view graphs
# melodic_curve.plot(y_label="MIDI pitch")
# durations_curve.plot(y_label="Duration")

@Transformer
def curve_upwards(seq: Sequence):
    time_elapsed = 0
    for event in seq.events:
        time_elapsed = time_elapsed + event.duration
        target_note = melodic_curve.y(time_elapsed)
        nearest_pitch = sorted(pitch_domain, reverse=False, key=lambda i: abs(i - target_note))[0]
        yield event.extend(pitches=[nearest_pitch])

@Transformer
def increase_density(seq: Sequence, starting_duration=6):
    time_elapsed = 0
    for event in seq.events:
        time_elapsed = time_elapsed + event.duration
        target_dur = durations_curve.y(time_elapsed)
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