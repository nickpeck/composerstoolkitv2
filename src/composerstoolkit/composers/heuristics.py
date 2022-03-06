"""
Heuristic functions used to guide random generation
(see composers.solvers.backtracking_solver)
"""
import math
from typing import Dict

# TODO use decimal types here to avoid floating point errors

def heuristic_sine_shape(axis_pitch=60,amplitude=30,length=16, strength=1):
    # this will try and make the music obey the shape of a single sine wave cycle
    def func(tick, choices, weights) -> Dict[int, float]:
        angle = (tick+1)/length * 360
        value = math.sin(math.radians(angle))
        target_note = math.ceil(axis_pitch + (value * amplitude))
        for i, note in enumerate(choices):
            if i < axis_pitch-amplitude or i > axis_pitch+amplitude:
                continue
            compensating_value = 1 - (abs(note-target_note)/amplitude)
            if compensating_value > 0:
                weights[i] = weights[i] + math.pow(compensating_value, strength) * 100
        return weights
    return func

def heuristic_trend_upwards(axis=60, strength=1):
    def func(_tick, choices, weights) -> Dict[int, float]:
        for i, note in enumerate(choices):
            if note > axis:
                weights[i] = weights[i] + strength
        return weights
    return func

def heuristic_single_pitch(axis_pitch=60, slope=30, strength=1):
    # this will try and make the music obey the shape of a single axis pitch
    def func(_tick, choices, weights) -> Dict[int, float]:
        for i, note in enumerate(choices):
            compensating_value = 1 - (abs(note-axis_pitch)/slope)
            if compensating_value > 0:
                weights[i] = weights[i] + math.pow(compensating_value, strength) * 100
        return weights
    return func
