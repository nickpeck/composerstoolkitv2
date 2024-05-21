from typing import Callable, Set, List

from composerstoolkit import *
    

# alternative to 'fitpitch_range', because that uses 
# octave displacements which are not always natural for
# vocal lines.           
@Transformer
def enforce_pitch_range(seq: Sequence,
    min_pitch, max_pitch):
    n_events = 0
    for event in seq.events:
        if not Context.get_context().sequencer.scheduler.is_running:
            yield event
        if event.pitches[0] <= max_pitch \
            and event.pitches[0] >= min_pitch:
            yield event
        else:
            n_events = n_events + 1
            if n_events >= 100:
                yield event.extend(pitches=[])
                n_events = 0

@Transformer
def rest(seq: Sequence):
    for event in seq.events:
        yield event.extend(pitches=[])
    
#NEXUS_SET = {0,1,6}
NEXUS_SET = {0,2,4,5,7,9,11}
   
   

harmony_gate = enforce_shared_pitch_class_set(
            pitch_class_set=NEXUS_SET,
            get_context = lambda: Context.get_context())

            
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
    harmony_gate
)

##################### Alto #######################



alto = Sequence.from_generator(random_slice(
    Sequence(events=rhythms)
)).transform(
    map_to_intervals(intervals=intervals, starting_pitch=60, random_order=True)
).transform(
    enforce_pitch_range(min_pitch=55, max_pitch=72)
).transform(
    harmony_gate
)


##################### Soprano #######################


soprano = Sequence.from_generator(random_slice(
    Sequence(events=rhythms)
)).transform(
    map_to_intervals(intervals=intervals, starting_pitch=70, random_order=True)
).transform(
    enforce_pitch_range(min_pitch=60, max_pitch=77)
).transform(
    harmony_gate
)

mysequencer = Context.get_context().new_sequencer(bpm=35, playback_rate=1, jit=True, debug=True)\
    .add_sequence(tenor, track_no=3)\
    .add_sequence(alto, track_no=2)\
    .add_sequence(soprano, track_no=1)\
    .add_sequence(bass, track_no=4)\
    .add_transformer(
        gated( # cycle ends on a major or min triad
            condition = cyclic_time_gate(20, 16, 18),
            transformer = enforce_shared_pitch_class_set(
                pitch_class_set={0,4,7},
                get_context = lambda: Context.get_context()
            )
        )
    )\
    .add_transformer( # complete rest every cycle
        gated(
            condition = cyclic_time_gate(20, 18, 20),
            transformer = rest()
        )
    )

    

mysequencer.playback()
