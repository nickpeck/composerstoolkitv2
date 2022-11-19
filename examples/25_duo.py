from typing import Callable, Set, List

from composerstoolkit import *
    
@Transformer
def enforce_shared_pitch_class_set(seq: Sequence,
    pitch_class_set: Set[int],
    get_context: Callable[[], Context]):
    for event in seq.events:
        pitches = event.pitches
        sequencer = get_context().sequencer
        other_pitches = [p for p,_c in sequencer.active_pitches]
        all_pitches = pitches + other_pitches
        aggregate = set()
        for e1 in all_pitches:
            for e2 in all_pitches:
                if e1 == e2:
                    continue
                aggregate.add(abs(e2-e1) % 12)
        if aggregate.issubset(pitch_class_set):
            yield event

@Transformer
def rest(seq: Sequence):
    for event in seq.events:
        yield event.extend(pitches=[])
    
NEXUS_SET = {0,1,6}
#NEXUS_SET = {0,2,5}
    
g = enforce_shared_pitch_class_set(
            pitch_class_set=NEXUS_SET,
            get_context = lambda: mysequencer.context)

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
        transformer=rhythmic_diminution(factor=3),
        get_context=lambda: mysequencer.context
    )
).transform(
    g
).transform(
    gated(
        condition=cyclic_time_gate(cycle_length=5, on=4, off=5),
        transformer=rest(),
        get_context=lambda: mysequencer.context
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
        transformer=aggregate(n_voices=5, duration=1),
        get_context=lambda: mysequencer.context
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
        transformer=rhythmic_diminution(factor=5),
        get_context=lambda: mysequencer.context
    )
).transform(
    g
).transform(
    fit_to_range(min_pitch=40, max_pitch=70)
).transform(
    gated(
        condition=cyclic_time_gate(cycle_length=15, on=5, off=8),
        transformer=rest(),
        get_context=lambda: mysequencer.context
    )
)


mysequencer = Sequencer(bpm=100, playback_rate=1, debug=True)\
    .add_sequence(flute, channel_no=1)\
    .add_sequence(harp, channel_no=2)\

mysequencer.playback()
