import math
import random

"""
Heuristic functions used to guide random generation
(see composers.solver.random_walk_backtracking_w_heuristics)
"""

def heuristic_sine_shape(axis_pitch=60,amplitude=30,length=16, strength=1):
    # this will try and make the music obey the shape of a single sine wave cycle
    def f(tick, choices, weights):
        angle = (tick+1)/length * 360
        value = math.sin(math.radians(angle))
        target_note = math.ceil(axis_pitch + (value * amplitude))
        for i in range(len(choices)):
            if i < axis_pitch-amplitude or i > axis_pitch+amplitude:
                continue
            note = choices[i]
            compensating_value = 1 - (abs(note-target_note)/amplitude)
            if compensating_value > 0:
                weights[i] = weights[i] + math.pow(compensating_value, strength) * 100
        return weights
    return f
    
def heuristic_trend_upwards(axis=60, strength=1):
    def f(tick, choices, weights):
        for i in range(len(choices)):
            note = choices[i]
            if note > axis:
                weights[i] = weights[i] + strength
        return weights
    return f
    
def heuristic_single_pitch(axis_pitch=60, slope=30, strength=1):
    # this will try and make the music obey the shape of a single axis pitch
    def f(tick, choices, weights):
        for i in range(len(choices)):
            note = choices[i]
            compensating_value = 1 - (abs(note-axis_pitch)/slope)
            if compensating_value > 0:
                weights[i] = weights[i] + math.pow(compensating_value, strength) * 100
        return weights
    return f