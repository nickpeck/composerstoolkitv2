"""Library functions for defining common scale types
"""
from . import NOTE_MAX
from . pitches import PITCH_CLASSES

MAJOR = IONIAN = IONIAN_MODE_PITCH_CLASSES = MAJ_SCALE_PITCH_CLASSES = {0,2,4,5,7,9,11}
MEL_MINOR = MEL_MINOR_SCALE_PITCH_CLASSES = {0,2,3,5,7,9,11}
HAR_MINOR = HAR_MINOR_SCALE_PITCH_CLASSES = {0,2,3,5,7,8,11}
HAR_MAJOR = HAR_MAJOR_SCALE_PITCH_CLASSES = {0,2,4,5,7,8,11}
# Church Modes
DORIAN = DORIAN_MODE_PITCH_CLASSES = {0,2,3,5,7,9,10}
PHYGIAN = PHYGIAN_MODE_PITCH_CLASSES = {0,1,3,5,7,8,10}
LYDIAN = LYDIAN_MODE_PITCH_CLASSES = {0,2,4,6,7,9,11}
MIXOLYDIAN = _MODE_PITCH_CLASSES = {0,2,4,5,7,9,10}
AEOLIAN = AEOLIAN_MODE_PITCH_CLASSES = {0,2,3,5,7,8,10}
LOCRIAN = LOCRIAN_MODE_PITCH_CLASSES = {0,1,3,5,6,8,10}
# these are Messiaen's modes of limited transposition
MODE_1_PITCH_CLASSES = {0,2,4,6,8,10}
MODE_2_PITCH_CLASSES = {0,1,3,4,6,7,9,10}
MODE_3_PITCH_CLASSES = {0,2,3,4,6,7,8,10,11}
MODE_4_PITCH_CLASSES = {0,1,2,5,6,7,8,11}
MODE_5_PITCH_CLASSES = {0,1,5,6,7,11}
MODE_6_PITCH_CLASSES = {0,2,4,5,6,8,10,11}
MODE_7_PITCH_CLASSES = {0,1,2,3,5,6,7,8,9,11}
# aliases for the above
WHOLE_TONE_SCALE_PITCH_CLASSES = MODE_1_PITCH_CLASSES
OCTATONIC_SCALE_PITCH_CLASSES = MODE_2_PITCH_CLASSES
DIMINISHED_SCALE_PITCH_CLASSES = MODE_2_PITCH_CLASSES

CHROMATIC = CHROMATIC_SCALE_PITCH_CLASSES = {*range(0,11)}

# TODO refactor these to use the mode() function below rather than duplicating (need to update examples too)

chromatic = {*range(0, NOTE_MAX)}

def mode(root="C", mode=DORIAN):
    transposition = PITCH_CLASSES[root.upper()]
    c_mode = [0] + sorted(filter(lambda x: (x % 12) in \
        mode , range(1, NOTE_MAX)))
    return set(map(lambda x: x+transposition, c_mode))
