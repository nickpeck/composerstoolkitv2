"""Explores modifying a sequence by random paramter mutation,
as well as building symetrical_scales out of a resultant pattern.
"""

from composerstoolkit import *
from composerstoolkit.resources import scales

symetrical_scale = [e.pitches[-1] for e in resultant_pitches(
    counters=[5,6],
    start_at=60)]

symetrical_scale_span = symetrical_scale[-1] - symetrical_scale[0]

def mutate_pitch(event, value):
    return Event([value], event.duration)

def mutation_duration(event, value):
    return Event(event.pitches, value)

even_pulse = Sequence.from_generator(
    pulses([QUARTER_NOTE]))\
    .transform(loop())

melody = Sequence.from_generator(
    cantus(symetrical_scale)
).transform(
    map_to_pulses(even_pulse)
).transform(
    loop()
).transform(
    random_mutation(
        key_function = mutate_pitch,
        choices = symetrical_scale,
        threshold =0.8)
).transform(
    random_mutation(
        key_function = mutation_duration,
        choices = [0.5, 1],
        threshold =0.3)
)

chords = Sequence.from_generator(chords_from_scale(
    symetrical_scale,
    spacing=4,
    n_voices=5,
    allow_inversions=False
)).transform(map_to_pulses(
     Sequence.from_generator(pulses([WHOLE_NOTE])).transform(loop())
)).transform(
    transpose(-symetrical_scale_span)
).transform(
    loop()
).transform(
    random_mutation(
        key_function = mutation_duration,
        choices = [1,2,3,4],
        threshold = 0.0))

Context.get_context().new_sequencer(bpm=150, playback_rate=1)\
    .add_sequence(melody)\
    .add_sequence(chords)\
    .playback()
