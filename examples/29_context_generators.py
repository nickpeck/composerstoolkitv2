from composerstoolkit import *

def my_generator(
    min=40,
    max=80,
    get_context = lambda: Context.get_context()):
    set = {0,2,4,6,7,9,11}
    last_pitch = 60
    while True:
        context = get_context()
        pitches = [p for p,_c in context.sequencer.active_pitches]
        pf = pitchset.to_prime_form(pitches)
        diff = list(set - pf)
        available_notes = sorted(filter(lambda x: (x % 12) in diff, range(min, max)), key=lambda n: abs(last_pitch-n))
        for n in available_notes:
            last_pitch = n

            yield Event(pitches=[n], duration=1)
oboe = Sequence.from_generator(
    my_generator()
).transform(
    map_to_pulses(
        pulse_sequence = Sequence.from_generator(random_slice(
            Sequence.from_generator(collision_pattern(2,3))
        )
    ))
).transform(
    shape_sine(period_beats=20,
    get_context = lambda: Context.get_context())
)


glock = Sequence.from_generator(
    my_generator(min=70, max=90)
).transform(
    map_to_pulses(
        pulse_sequence = Sequence.from_generator(random_slice(
            Sequence.from_generator(collision_pattern(2,3))
        )
    ))
).transform(
    shape_sine(period_beats=20,
    get_context = lambda: Context.get_context())
).transform(
    rhythmic_augmentation(3)
)

strings = Sequence.from_generator(
    chord_cycle(
        scale=scales.chromatic,
        start=Event(pitches=[60,62,65,70,74], duration=16),
        cycle_of=-4,
        max_len=16)).transform(loop())
        
basses = Sequence.from_generator(
    my_generator(min=20, max=50)
).transform(
    map_to_pulses(
        pulse_sequence = Sequence.from_generator(random_slice(
            Sequence.from_generator(collision_pattern(2,3))
        )
    ))
).transform(
    rhythmic_augmentation(10)
)

mysequencer = Context.get_context().new_sequencer(bpm=220, playback_rate=1, debug=True)\
    .add_sequence(glock, channel_no=1)\
    .add_sequence(oboe, channel_no=2)\
    .add_sequence(strings, channel_no=3)\
    .add_sequence(basses, channel_no=4)

mysequencer.playback()
