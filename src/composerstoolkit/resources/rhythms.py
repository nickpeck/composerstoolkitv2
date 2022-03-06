"""Library constants for specifying relative note values.
"""
WHOLE_NOTE = 4
HALF_NOTE = 2
QUARTER_NOTE = 1
EIGHTH_NOTE = 0.5
SIXTEENTH_NOTE = 0.25
DOTTED = lambda x : x + (x/2)
TIED = lambda *x : sum(x)
TICKS_PER_BEAT = 960
