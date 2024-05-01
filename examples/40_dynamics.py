"""
modulates the volume parameter to crossfade between two repeated pitches a 5th apart
"""

from composerstoolkit import *
import math

def set_volume(event, value):
    event.meta["volume"] = value

seq1 = Sequence(events=[Event([60], 1)])\
    .transform(loop())\
    .transform(
        cyclic_modulation(
            period = 60,
            starting_deg = 270,
            modulator = set_volume
        )
    )

seq2 = Sequence(events=[Event([67], 1)])\
    .transform(loop())\
    .transform(
        cyclic_modulation(
            period = 60,
            starting_deg = 180,
            modulator = set_volume
        )
    )

sequencer = Sequencer(debug=True).add_sequences(seq1, seq2)

sequencer.playback()

