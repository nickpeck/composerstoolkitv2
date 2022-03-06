from pprint import pprint

from midiutil.MidiFile import MIDIFile # type: ignore
from mido import MidiFile

from composerstoolkit import *

print("Loading case base")
sequences = []
for file in os.listdir(os.path.join("case_base", "cello_suites")):
    if file.endswith("mid"):
        filename = os.path.join("case_base", "cello_suites", file)
    midi_file = MidiFile(filename)
    graph = Graph.from_midi_track(midi_file.tracks[1])
    sequences.append(FiniteSequence.from_graph(graph))


print("common intervalic sequences")
pprint(frequent_intervallic(sequences, 30), indent=4)

print("common rhythmic sequences")
pprint(frequent_rhythms(sequences, 30), indent=4)

print("common vectors are")
pprint(frequent_vectors(sequences, 30), indent=4)

#Todo try this with a single sequence, but cut into bars?

