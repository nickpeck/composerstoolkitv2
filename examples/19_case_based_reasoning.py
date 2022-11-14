"""Given a sample motive, attempt to extend it, using
the statisically most likely pitch vectors and durations,
based upon analysis of a corpus of works.
"""
from midiutil.MidiFile import MIDIFile # type: ignore
from mido import MidiFile

from pprint import pprint

from composerstoolkit import *

print("Loading case base")

graphs = []
for file in os.listdir(os.path.join("case_base", "cello_suites")):
    if file.endswith("mid"):
        filename = os.path.join("case_base", "cello_suites", file)
    print(filename)
    midi_file = MidiFile(filename)
    for track in midi_file.tracks:
        graph = Graph.from_midi_track(track)
        graphs.append(graph)

print("case base contains ", len(graphs), "sequences")

pf = pitches.PitchFactory()

source = FiniteSequence(events=[
    Event(pitches=[pf("G2"), pf("C2")], duration=0.125),
    Event(pitches=[pf("F#2")], duration=0.125),
    Event(pitches=[pf("G2")], duration=0.25)
])

corpus = Corpus(case_base=graphs)

solver = CaseBasedSolver(source=source,
    corpus = corpus,
    target_duration_beats = 2,
    constraints = [
        constraint_in_set(
            scales.G_major,
            lookback_n_beats=1
            ) | constraint_in_set(
            scales.C_major,
            lookback_n_beats=1),
        constraint_range(minimum=30,maximum=70)
    ])

for solution, rating in iter(solver):
    print("rating", rating)
    Sequencer(bpm=50, playback_rate=1)\
        .add_sequence(solution)\
        .playback()
