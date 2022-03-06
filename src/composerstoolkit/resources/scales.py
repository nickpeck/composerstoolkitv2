"""Library functions for defining common scale types
"""
from . import NOTE_MAX

MAJ_SCALE_PITCH_CLASSES = {0,2,4,5,7,9,11}
MEL_MINOR_SCALE_PITCH_CLASSES = {0,2,3,5,7,9,11}
HAR_MINOR_SCALE_PITCH_CLASSES = {0,2,3,5,7,8,11}
HAR_MAJOR_SCALE_PITCH_CLASSES = {0,2,4,5,7,8,11}
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

CHROMATIC_SCALE_PITCH_CLASSES = {*range(0,11)}

C_major = [0] + sorted(filter(lambda x: (x % 12) in \
    MAJ_SCALE_PITCH_CLASSES, range(1, NOTE_MAX)))
Db_major = set(map(lambda x: x+1, C_major))
D_major = set(map(lambda x: x+2, C_major))
Eb_major = set(map(lambda x: x+3, C_major))
E_major = set(map(lambda x: x+4, C_major))
F_major = set(map(lambda x: x+5, C_major))
Gb_major = set(map(lambda x: x+6, C_major))
G_major = set(map(lambda x: x+7, C_major))
Ab_major = set(map(lambda x: x+8, C_major))
A_major = set(map(lambda x: x+9, C_major))
Bb_major = set(map(lambda x: x+10, C_major))
B_major = set(map(lambda x: x+11, C_major))

C_mel_minor = [0] + sorted(filter(lambda x: (x % 12) in \
    MEL_MINOR_SCALE_PITCH_CLASSES, range(1, NOTE_MAX)))
Db_mel_minor = map(lambda x: x+1, C_mel_minor)
D_mel_minor = map(lambda x: x+2, C_mel_minor)
Eb_mel_minor = map(lambda x: x+3, C_mel_minor)
E_mel_minor = map(lambda x: x+4, C_mel_minor)
F_mel_minor = map(lambda x: x+5, C_mel_minor)
Gb_mel_minor = map(lambda x: x+6, C_mel_minor)
G_mel_minor = map(lambda x: x+7, C_mel_minor)
Ab_mel_minor = map(lambda x: x+8, C_mel_minor)
A_mel_minor = map(lambda x: x+9, C_mel_minor)
Bb_mel_minor = map(lambda x: x+10, C_mel_minor)
B_mel_minor = map(lambda x: x+11, C_mel_minor)

C_har_minor = [0] + sorted(filter(lambda x: (x % 12) in \
    HAR_MINOR_SCALE_PITCH_CLASSES , range(1, NOTE_MAX)))
Db_har_minor = map(lambda x: x+1, C_mel_minor)
D_har_minor = map(lambda x: x+2, C_major)
Eb_har_minor = map(lambda x: x+3, C_major)
E_har_minor = map(lambda x: x+4, C_major)
F_har_minor = map(lambda x: x+5, C_major)
Gb_har_minor = map(lambda x: x+6, C_major)
G_har_minor = map(lambda x: x+7, C_major)
Ab_har_minor = map(lambda x: x+8, C_major)
A_har_minor = map(lambda x: x+9, C_major)
Bb_har_minor = map(lambda x: x+10, C_major)
B_har_minor = map(lambda x: x+11, C_major)
