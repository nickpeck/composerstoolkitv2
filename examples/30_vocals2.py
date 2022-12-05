from composerstoolkit import *

def my_generator(
    min=40,
    max=80,
    get_context =  lambda : mysequencer.context):
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

sop = Sequence.from_generator(
    my_generator()
).transform(
    map_to_pulses(
        pulse_sequence = Sequence.from_generator(random_slice(
            Sequence.from_generator(collision_pattern(2,3))
        )
    ))
).transform(
    shape_sine(period_beats=20,
    get_context = lambda: mysequencer.context)
)


alto = Sequence.from_generator(
    my_generator()
).transform(
    map_to_pulses(
        pulse_sequence = Sequence.from_generator(random_slice(
            Sequence.from_generator(collision_pattern(2,3))
        )
    ))
).transform(
    shape_sine(period_beats=20,
    get_context = lambda: mysequencer.context)
)

tenor = Sequence.from_generator(
    my_generator(min=50,max=65)
).transform(
    map_to_pulses(
        pulse_sequence = Sequence.from_generator(random_slice(
            Sequence.from_generator(collision_pattern(2,3))
        )
    ))
).transform(
    shape_sine(period_beats=20,
    get_context = lambda: mysequencer.context)
)
        
basses = Sequence.from_generator(
    my_generator(min=35, max=50)
).transform(
    map_to_pulses(
        pulse_sequence = Sequence.from_generator(random_slice(
            Sequence.from_generator(collision_pattern(2,3))
        )
    ))
).transform(
    rhythmic_augmentation(3)
)

mysequencer = Sequencer(bpm=55, playback_rate=1, debug=True)\
    .add_sequence(sop, channel_no=1)\
    .add_sequence(alto, channel_no=2)\
    .add_sequence(tenor, channel_no=3)\
    .add_sequence(basses, channel_no=4)

mysequencer.playback()
