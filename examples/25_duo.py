from typing import Callable, Set, List

from composerstoolkit import *
    
NEXUS_SET = {0,1,6}
#NEXUS_SET = {0,2,5}
    
harmony_gate = enforce_shared_pitch_class_set(
            pitch_class_set=NEXUS_SET,
            get_context = lambda: Context.get_context())

##################### Flute #######################
            
intervals1 = [1, 2,5,7,-1, -2,-5,-7]
    
flute = Sequence.from_generator(random_slice(
    Sequence(events=[
        Event(pitches=[], duration=3),
        Event(pitches=[], duration=0.75),
        Event(pitches=[], duration=0.25),
        Event(pitches=[], duration=0.75),
        Event(pitches=[], duration=0.25),
        Event(pitches=[], duration=2),
    ])
)).transform(
    map_to_intervals(intervals=intervals1, starting_pitch=70, random_order=True)
).transform(
    fit_to_range(min_pitch=60, max_pitch=90)
).transform(
    gated(
        condition=cyclic_time_gate(cycle_length=9,on=0,off=4),
        transformer=rhythmic_diminution(factor=3)
    )
).transform(
    harmony_gate
).transform(
    gated(
        condition=cyclic_time_gate(cycle_length=5, on=4, off=5),
        transformer=rest()
    )
)

##################### Harp #######################

intervals2 = [1, -1, 2,4,5,7,10,-2,-4,-5,-7,-10]

harp = Sequence(events=[Event(pitches=[], duration=1)]
).transform(
    loop()
).transform(
    map_to_intervals(intervals=intervals2, starting_pitch=50, random_order=True)
).transform(
    gated(
        condition=cyclic_time_gate(cycle_length=10,on=5,off=10),
        transformer=aggregate(n_voices=5, duration=1)
    )
).transform(
    map_to_pulses(pulse_sequence=Sequence.from_generator(random_slice(
        Sequence(events=[
            Event(pitches=[], duration=3),
            Event(pitches=[], duration=4),
            Event(pitches=[], duration=4),
            Event(pitches=[], duration=3)
        ])
    )))
).transform(
    gated(
        condition=cyclic_time_gate(cycle_length=10,on=0,off=4),
        transformer=rhythmic_diminution(factor=5)
    )
).transform(
    harmony_gate
).transform(
    fit_to_range(min_pitch=40, max_pitch=70)
).transform(
    gated(
        condition=cyclic_time_gate(cycle_length=15, on=5, off=8),
        transformer=rest()
    )
)


mysequencer = Sequencer(bpm=100, playback_rate=1, debug=True)\
    .add_sequence(flute, channel_no=1)\
    .add_sequence(harp, channel_no=2)\

mysequencer.playback()
