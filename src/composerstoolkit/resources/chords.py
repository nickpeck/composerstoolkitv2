#from ..builder.permutations import permutate
import math

from .scales import CHROMATIC_SCALE_PITCH_CLASSES

COMMON_TRIAD_PITCH_CLASSES = {
    'maj' : {0, 4, 7},
    'min' : {0, 3, 7},
    'dim' : {0, 3, 6},
    'aug' : {0, 4, 8},
}

COMMON_TRETRAD_PITCH_CLASSES  = {
    'maj6' : {0, 4, 7, 9},
    'min6' : {0, 3, 7, },
    'maj7' : {0, 4, 7, 11},
    'maj7b5' : {0, 4, 6, 11},
    'min7' : {0, 3, 7, 10},
    'dom7' : {0, 4, 7, 10},
    'dom7b5' : {0, 3, 6, 10},
    'dim7' : {0, 3, 6, 9},
}

def to_pitch_class_set(pitches):
    return {*[i % 12 for i in pitches]}
    
def set_compliment(pcs):
    return CHROMATIC_SCALE_PITCH_CLASSES - pcs