import dis
import pprint

from composerstoolkit import *

pf = pitches.PitchFactory()

def playback(seq):
    Context.get_context().new_sequencer(bpm=250, playback_rate=1)\
        .add_sequence(seq)\
        .playback()

def present_results(result, transformations):
    print("="*20)
    print("The final resulting sequence is :")
    pprint.pprint(result.events, indent=4)
    print("The resulting pool of transformations is :")
    pprint.pprint(transformations, indent=4)
    playback(result)

def get_feedback(seq) -> bool:
    # user offers Y/N feedback on a candidate.
    # if yes, the parents are weigher higher
    print("-"*20)
    pprint.pprint(seq.events, indent=4)
    playback(seq)
    response = input("Press Y to keep, any key to reject: ")
    return response.strip().upper() == "Y"


pulse = Sequence.from_generator(random_slice(
    Sequence.from_generator(collision_pattern(4,5,9))))

starting_fragment = FiniteSequence(
    events = [
        Event(pitches=[pf("C4")], duration=QUARTER_NOTE),
        Event(pitches=[pf("Gb4")], duration=QUARTER_NOTE),
        Event(pitches=[pf("G4")], duration=QUARTER_NOTE)
    ]
)

# initial 'pool' (transformation, weighting)
starting_transformations = [
        (transpose(3), 0.5),
        (transpose(-4), 0.5),
        (retrograde(n_pitches=3), 0.5),
        (aggregate(n_voices=3), 0.5),
        (monody(), 0.5),
        # (invert(), 0.5),
        (rotate(n_pitches=2), 0.5),
        (map_to_pulses(pulse), 0.5),
        (explode_intervals(2), 0.5)
    ]

evo = Evolutionary(
    transformations=starting_transformations,
    fitness_func=get_feedback)

try:
    result,transformations = evo(starting_fragment)
    present_results(result,transformations)
except Extinction:
    print("The pool became extinct! You should try approving some results early on.")
    exit(0)

while True:
    res = input("Enter y to run, unguided for 10 more generations, any other key to end")

    if res.strip().upper() == "Y":
        evo = Evolutionary(
            transformations=transformations,
            fitness_func=lambda x : True) # unguided

        result,transformations = evo(result, 10)
        present_results(result,transformations)
    else:
        break

transformations = sorted(transformations, key=lambda t: t[1])
pprint.pprint(transformations, indent=4)
best = transformations[-1]
print("The leading transformation is:", best)
