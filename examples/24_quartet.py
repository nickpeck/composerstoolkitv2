from typing import Callable, Set, List

from composerstoolkit import *
    
@Transformer
def enforce_shared_pitches(seq: Sequence,
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
            #print(all_pitches, aggregate)
            yield event
 
            
'''g = gated(
        enforce_shared_pitches(
            pitch_class_set={0,2,5,6},
            get_context = lambda: mysequencer.context),
        cyclic_time_gate(4,3,4),
        get_context = lambda: mysequencer.context
    )'''
    
g = enforce_shared_pitches(
            pitch_class_set={0,1,2,6},
            get_context = lambda: mysequencer.context)


intervals1 = [2,5,7,-2,-5,-7]
    
voice1 = Sequence.from_generator(random_slice(
    Sequence(events=[
        Event(pitches=[], duration=3),
        Event(pitches=[], duration=0.75),
        Event(pitches=[], duration=0.25),
        Event(pitches=[], duration=0.75),
        Event(pitches=[], duration=0.25),
        Event(pitches=[], duration=2),
    ])
)).transform(
    map_to_intervals(intervals=intervals1, starting_pitch=60, random_order=True)
).transform(
    fit_to_range(min_pitch=40, max_pitch=70)
)

intervals2 = [1,3,4,6,-1,-3,-4,-6]

voice2 = Sequence.from_generator(random_slice(
    Sequence(events=[
        Event(pitches=[], duration=1.0/3.0),
        Event(pitches=[], duration=1.0/3.0),
        Event(pitches=[], duration=1.0/3.0),
        Event(pitches=[], duration=3)
    ])
)).transform(
    map_to_intervals(intervals=intervals2, starting_pitch=50, random_order=True)
).transform(
    fit_to_range(min_pitch=30, max_pitch=60)
).transform(
    g
)

intervals3 = [10,11,-10,-11]

voice3 = Sequence.from_generator(random_slice(
    Sequence(events=[
        Event(pitches=[], duration=1),
        Event(pitches=[], duration=1),
        Event(pitches=[], duration=1),
        Event(pitches=[], duration=1)
    ])
)).transform(
    map_to_intervals(intervals=intervals3, starting_pitch=60, random_order=True)
).transform(
    fit_to_range(min_pitch=50, max_pitch=80)
).transform(
    g
)


intervals4 = [0,1,2,3,-1,-2,-3]

voice4 = Sequence.from_generator(random_slice(
    Sequence(events=[
        Event(pitches=[], duration=1.0/5.0),
        Event(pitches=[], duration=1.0/5.0),
        Event(pitches=[], duration=1.0/5.0),
        Event(pitches=[], duration=1.0/5.0),
        Event(pitches=[], duration=1.0/5.0),
        Event(pitches=[], duration=1.0/5.0),
        Event(pitches=[], duration=1)
    ])
)).transform(
    map_to_intervals(intervals=intervals3, starting_pitch=70, random_order=True)
).transform(
    fit_to_range(min_pitch=65, max_pitch=100)
).transform(
    g
)

mysequencer = Sequencer(bpm=100, playback_rate=1, debug=True)\
    .add_sequence(voice1, channel_no=3)\
    .add_sequence(voice2, offset=5, channel_no=4)\
    .add_sequence(voice3, offset=10, channel_no=2)\
    .add_sequence(voice4, offset=15, channel_no=1)

mysequencer.playback()