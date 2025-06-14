from composerstoolkit import *
from composerstoolkit.resources import scales

seq = Sequence(events=(Event([i], 1) for i in infinityseries.infinityseries(60,61)))


Context.get_context().new_sequencer(bpm=240, playback_rate=1)\
    .add_sequence(seq)\
    .playback()
