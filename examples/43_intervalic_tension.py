""" This is used to grade chords of a given size (cardinality) by intervalic tension in a post-tonal context
using personal criteria.
- min 2nds are classed as 'sharp dissonances'
- major 2nds are classed as mild 'dissonances'
- maj and min 3rds are soft consonances (I rate min 3rds slightly dissonant)
- tritone is generally considered a dissonance
4ths and must be determined based upon context - if a min 2nd is present, it is more open, but more restless
otherwise.
Given that we are using the Forte sets as input, this doesn't really take timbre, register or spacing into account.
Typically, the sharp/mild dissonances tend to become somewhat milder when inverted and spread > greater than an
octave.
"""
from pprint import pprint
from functools import cmp_to_key
from composerstoolkit import *

chord_dict = pitchset.ForteSet.as_dict()

cardinality = 3

chord_names = filter(lambda name: isinstance(name, str) and name.startswith(f"{cardinality}-"), chord_dict.keys())
chords = [chord_dict[name] for name in chord_names]

def intervalic_tension(chord):
    # this is a subjective weighting applied to each interval in the set's vector (see above)
    multiplier = (4, 3, 1, 0, 0, 3)
    score = []
    for i in range(6):
        score.append(multiplier[i] * chord.vector[i])
    if chord.vector[4] > 0:
        # 4th and another sharp dissonance, 4th is more open
        if chord.vector[0] > 0:
            score.append(0)
        else:
            # otherwise, 4th behaves as a dissonance
            score.append(2)
    return sum(score)

def compare_intervalic_tension(chord1, chord2):
    chord1_tension = intervalic_tension(chord1)
    chord2_tension = intervalic_tension(chord2)
    return chord1_tension - chord2_tension

chords = sorted(chords, key=cmp_to_key(compare_intervalic_tension))

pprint(chords, indent=4)
s = FiniteSequence(events=[c.as_event(transposition=70).extend(duration=1) for c in chords])
Sequencer(bpm=60, dump_midi=True).add_sequence(s).show_notation()