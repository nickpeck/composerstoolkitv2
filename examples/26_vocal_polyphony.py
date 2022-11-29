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
           

# alternative to 'fitpitch_range', because that uses 
# octave displacements which are no always natural for
# vocal lines.           
@Transformer
def enforce_pitch_range(seq: Sequence,
    min_pitch, max_pitch):
    for event in seq.events:
        if event.pitches[0] <= max_pitch \
            and event.pitches[0] >= min_pitch:
            yield event

@Transformer
def rest(seq: Sequence):
    for event in seq.events:
        yield event.extend(pitches=[])
    
#NEXUS_SET = {0,1,6}
NEXUS_SET = {0,2,5}
   
   

g = enforce_shared_pitch_class_set(
            pitch_class_set=NEXUS_SET,
            get_context = lambda: mysequencer.context)

            
intervals = [0,2,-2,1,-1,3,-3,4,-4]
rhythms = [
        Event(pitches=[], duration=1),
        Event(pitches=[], duration=1),
        Event(pitches=[], duration=1),
        Event(pitches=[], duration=0.5),
        Event(pitches=[], duration=0.5),
        Event(pitches=[], duration=2),
    ]
            
##################### Tenor #######################
    
tenor = Sequence.from_generator(
    cantus([55,55,58,60,57,60,57,60,60,55])
).transform(
    map_to_pulses(Sequence.from_generator(pulses([1,1,1,3,1,1,1,2,1])))
).transform(
    loop()
).transform(
    rhythmic_augmentation(multiplier=3)
)

##################### Bass #######################

intervals2 = intervals + [5,-5,7,-7]

bass = Sequence.from_generator(random_slice(
    Sequence(events=rhythms)
)).transform(
    map_to_intervals(intervals=intervals2, starting_pitch=55, random_order=True)
).transform(
    enforce_pitch_range(min_pitch=40, max_pitch=60)
).transform(
    g
)

##################### Alto #######################



alto = Sequence.from_generator(random_slice(
    Sequence(events=rhythms)
)).transform(
    map_to_intervals(intervals=intervals, starting_pitch=60, random_order=True)
).transform(
    enforce_pitch_range(min_pitch=55, max_pitch=72)
).transform(
    g
)


##################### Soprano #######################


soprano = Sequence.from_generator(random_slice(
    Sequence(events=rhythms)
)).transform(
    map_to_intervals(intervals=intervals, starting_pitch=70, random_order=True)
).transform(
    enforce_pitch_range(min_pitch=60, max_pitch=77)
).transform(
    g
)

mysequencer = Sequencer(bpm=35, playback_rate=1, debug=True)\
    .add_sequence(tenor, channel_no=3)\
    .add_sequence(alto, offset=5, channel_no=2)\
    .add_sequence(soprano, offset=10, channel_no=1)\
    .add_sequence(bass, offset=15, channel_no=4)\
    .add_transformer(
        gated( # cycle ends on a major or min triad
            condition = cyclic_time_gate(20, 16, 18),
            transformer = enforce_shared_pitch_class_set(
                pitch_class_set={0,4,7},
                get_context = lambda: mysequencer.context
            ),
            get_context = lambda: mysequencer.context
        )
    )\
    .add_transformer( # complete rest every cycle
        gated(
            condition = cyclic_time_gate(20, 18, 20),
            transformer = rest(),
            get_context = lambda: mysequencer.context
        )
    )

    

mysequencer.playback()
