import pprint

from composerstoolkit import *

pf = pitches.PitchFactory()

starting_fragment = FiniteSequence(
    events = [
        Event(pitches=[pf("C4")], duration=QUARTER_NOTE),
        Event(pitches=[pf("Gb4")], duration=QUARTER_NOTE),
        Event(pitches=[pf("G4")], duration=QUARTER_NOTE)
    ]
)

# initial 'pool' (transformation, weighting)
starting_transformations = [
    (transpose(1), 0.5),
    (retrograde(n_pitches=3), 0.5),
    (invert(), 0.5),
    (rotate(n_pitches=2), 0.5),
    (explode_intervals(2), 0.5)]

def playback(seq):
    Container(bpm=250, playback_rate=1)\
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
        
pulse_pattern = steady_pulse(0.2, len(result.events))
seq = result |chain| map_to_pulses(pulse_pattern)
container = Container(bpm=160)
container.add_sequence(0, seq)
container.save_as_midi_file("3_human_directed_evolutionary.mid")