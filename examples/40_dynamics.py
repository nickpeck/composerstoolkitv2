from composerstoolkit import *
import math

@Transformer
def fade_in_and_out(seq: Sequence, period=60, starting_deg=270):
    i = 0
    for event in seq.events:
        sin = math.sin(math.radians((360 * i/period) - (360-starting_deg)))
        volume = 127 * ((sin+1)/2)
        event.meta["volume"] = int(volume)
        i = i + event.duration
        yield event


seq = Sequence(events=[Event([60], 1)])\
    .transform(loop())\
    .transform(
        fade_in_and_out()
    )


sequencer = Sequencer(debug=True, dump_midi=True).add_sequence(seq)

sequencer.playback()

