"""Composes a quartet for 4 undefined parts (sop,alto,tenor,bass).
To enforce separatation, each part makes use of a different interval set and repertoire of rhythmic material.
Each part has enforced rest periods of different lengths in order to build a more varied texture.
Uses an additional transformer to enforce adherance to a common pitch set between parts.

Changing this 'NEXUS_SET' radically changes the overall harmonic colour. Try comparing a set
that strongly implies diatonic context (ie a pentatonic fragment) with a more tonally ambiguous one
such as the 2nd Viennese trichord.
"""

from typing import Callable, Set, List

from composerstoolkit import *


@Transformer
def rest(seq: Sequence):
    for event in seq.events:
        yield event.extend(pitches=[])
    
NEXUS_SET = {0,1,6}
#NEXUS_SET = {0,2,5}
    
harmony_gate = enforce_shared_pitch_class_set(
            pitch_class_set=NEXUS_SET,
            get_context = lambda: mysequencer.context)

##################### Tenor #######################
            
intervals1 = [2,5,7,-2,-5,-7]
    
tenor = Sequence.from_generator(random_slice(
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
).transform(
    gated(
        condition=cyclic_time_gate(cycle_length=20, on=8, off=18),
        transformer=rest(),
        get_context=lambda: mysequencer.context
    )
)

##################### Bass #######################

intervals2 = [1,3,4,6,-1,-3,-4,-6]

bass = Sequence.from_generator(random_slice(
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
    harmony_gate
).transform(
    gated(
        condition=cyclic_time_gate(cycle_length=30, on=5, off=13),
        transformer=rest(),
        get_context=lambda: mysequencer.context
    )
)

##################### Alto #######################

intervals3 = [10,11,-10,-11]

alto = Sequence.from_generator(random_slice(
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
    harmony_gate
).transform(
    gated(
        condition=cyclic_time_gate(cycle_length=10, on=5, off=9),
        transformer=rest(),
        get_context=lambda: mysequencer.context
    )
)


##################### Soprano #######################

intervals4 = [0,1,2,3,-1,-2,-3]

soprano = Sequence.from_generator(random_slice(
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
    harmony_gate
).transform(
    gated(
        condition=cyclic_time_gate(cycle_length=15, on=2, off=9),
        transformer=rest(),
        get_context=lambda: mysequencer.context
    )
)

mysequencer = Sequencer(bpm=100, playback_rate=1, debug=True)\
    .add_sequence(tenor, channel_no=3)\
    .add_sequence(bass, offset=5, channel_no=4)\
    .add_sequence(alto, offset=10, channel_no=2)\
    .add_sequence(soprano, offset=15, channel_no=1)

mysequencer.playback()
