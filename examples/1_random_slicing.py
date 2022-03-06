from composerstoolkit.core import Event, Sequence, Container
from composerstoolkit.builders.generators import random_slice
from composerstoolkit.builders.transformers import loop
from composerstoolkit.builders.permutators import Permutations

ostinato = Sequence(events=Permutations([
            Event(pitches=[48], duration=1),
            Event(pitches=[43], duration=1),
            Event(pitches=[45], duration=1),
            Event(pitches=[41], duration=1)]).flatten()
        ).transform(loop(10))

seq_upper = Sequence.from_generator(random_slice(
    Sequence(events=[
        Event(pitches=[60], duration=1),
        Event(pitches=[62], duration=2),
        Event(pitches=[64], duration=3),
        Event(pitches=[59], duration=4),
    ]),
    None
))

Container(bpm=3000, playback_rate=1)\
    .add_sequence(seq_upper)\
    .add_sequence(ostinato)\
    .playback()
