import itertools
import math

from ..core import CTEvent, CTSequence, CTTransformer

@CTTransformer
def loop(seq, n_times=1):
    if n_times < 0:
        raise ValueError("n_times cannot be less than 0")
    result = []
    for i in range(n_times):
        result = result + seq.events
    return result
    
@CTTransformer
def transpose(seq, interval):
    """Transpose all pitches in the 
    given sequence by a constant interval.
    """
    result = []
    for evt in seq.events:
        result.append(
            CTEvent(
                [p + interval for p in evt.pitches], 
                evt.duration))
    return result
    
@CTTransformer
def retrograde(seq):
    events = seq.events[:]
    events.reverse()
    return events
    
@CTTransformer
def invert(seq, axis_pitch=None):
    if axis_pitch is None:
        axis_pitch = seq.events[0].pitches[0]
    res = []
    for evt in seq.events:
        delta = evt.pitches[0]-axis_pitch
        if delta < 0: # note is below axis
            res.append(CTEvent(axis_pitch-delta, evt.duration))
        elif delta > 0: # note is above axis
            res.append(CTEvent(axis_pitch-delta, evt.duration))
        else: #its the axis, so stays the same
            res.append(CTEvent(evt.pitches[0], evt.duration))
    return res
    
@CTTransformer
def rotate(seq, no_times=1):
    if seq.events == []:
        return []
    rotated = seq.events[:]
    for i in range(no_times):
        rotated = rotated[1:] + [rotated[0]]
    return rotated
    
@CTTransformer
def mutation(seq, threshold=0.5, transformations=[], constraints=[]):
    raise NotImplementedError

@CTTransformer
def aggregate_into_chords(seq, n_voices=4, duration=1):
    # break a linear sequence into a series of evenly-spaced chords
    events = seq.events[:]
    result = []
    for i in range(0, len(events), n_voices):
        sliced = events[i:i + n_voices]
        pitches = list(itertools.chain.from_iterable([e.pitches for e in sliced]))
        result.append(CTEvent(pitches, duration))
    return result
    
# @CTTransformer
# def linear_interpolate(seq, resolution=1):
    # events = seq.events[:]
    # if len(events) is 1:
        # return events
        
    # def _vectors(seq):
        # vectors = []
        # x = seq.events[0]
        # for y in seq.events[1:]:
            # vectors.append(y.pitch-x.pitch)
            # x = y
        # return vectors
        
    ## first item in the seq stays as-is
    # i_events = iter(seq.events)
    # i_vectors = iter(_vectors(seq))
    # result = [next(i_events)]
    
    # pitch = result[0].pitch
    # duration = result[0].duration
    # while True:
        # try:
            # next_event = next(i_events)
            # next_vector = next(i_vectors)
            # pitch_increment = next_vector/resolution
            # dur_increment = duration/resolution
            # for x in range(resolution):
                # result.append(CTEvent(
                    # math.ceil((x * pitch_increment) + pitch),
                    # dur_increment
                # ))
            # pitch = next_event.pitch
            # duration = next_event.duration
        # except StopIteration:
            # break
    # return result
    
@CTTransformer
def explode_intervals(seq, factor, mode="exponential"):
    events = seq.events[:]
    if len(events) is 1:
        return events
    
    def _vectors(seq):
        vectors = []
        x = seq.events[0]
        for y in seq.events[1:]:
            # if any event is a chord, then select the uppermost voice
            vectors.append(y.pitches[0]-x.pitches[0])
            x = y
        return vectors
    
    if mode == "exponential":
        interval_vectors = [(factor * v)for v in _vectors(seq)]
    elif mode == "linear":
        interval_vectors = [(factor + v) for v in _vectors(seq)]
    else:
        raise Exception("unrecognised mode "+ mode)
    
    # first item in the seq stays as-is
    i_events = iter(seq.events)
    i_vectors = iter(interval_vectors)
    result = [next(i_events)]
    # apply the interval_vectors to distort the remaining items
    pitch = result[0].pitches[0] # once again, assuming the top voice of any chord
    while True:
        try:
            next_event = next(i_events)
            next_vector = next(i_vectors)
            pitch = math.ceil(next_vector + pitch)
            result.append(CTEvent(pitch, next_event.duration))
        except StopIteration:
            break
    return result
    
@CTTransformer
def rhythmic_augmentation(seq, multiplier):
    return [CTEvent(e.pitches, multiplier*e.duration) for e in seq.events]
    
@CTTransformer
def rhythmic_diminution(seq, factor):
    return [CTEvent(e.pitches, e.duration/factor) for e in seq.events]
    
@CTTransformer
def map_to_pulses(seq, pulse_sequence):
    iter_pulses = iter(pulse_sequence.events)
    result = []
    for e in seq.events:
        try:
            next_pulse = next(iter_pulses)
            result.append(CTEvent(e.pitches, next_pulse.duration))
        except StopIteration:
            break
            #result.append(CTEvent(e.pitches, 0))
    return result
    
@CTTransformer
def map_to_pitches(seq, pitch_sequence):
    iter_pitches = iter(pitch_sequence.events)
    result = []
    for e in seq.events:
        try:
            next_pitch = next(iter_pitches)
            result.append(CTEvent(next_pitch.pitches[0], e.duration))
        except StopIteration:
            result.append(CTEvent(None, e.duration))
    return result
