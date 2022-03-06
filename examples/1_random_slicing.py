from composerstoolkit.core import Event, Sequence, Container
from composerstoolkit.builders.generators import random_slice
from composerstoolkit.builders.transformers import loop

ostinato = Sequence(events=[
    Event(pitches=[48], duration=1),
    Event(pitches=[43], duration=1),
    Event(pitches=[45], duration=1),
    Event(pitches=[41], duration=1),
]).transform(loop(10))

seq_upper = Sequence.from_generator(random_slice(
    Sequence(events=[
        Event(pitches=[60], duration=0.5),
        Event(pitches=[62], duration=0.75),
        Event(pitches=[64], duration=1),
        Event(pitches=[59], duration=0.25),
    ]),
    None,
    40
))

Container(bpm=300)\
    .add_sequence(seq_upper)\
    .add_sequence(ostinato)\
    .playback()