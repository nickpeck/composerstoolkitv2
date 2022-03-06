from pprint import pprint

from midiutil.MidiFile import MIDIFile # type: ignore
from mido import MidiFile

from composerstoolkit import *

print("Loading case base")

filename = os.path.join("case_base", "cello_suites", "cs1-1pre.mid")
midi_file = MidiFile(filename)
graph = Graph.from_midi_track(midi_file.tracks[1])
full_piece = FiniteSequence.from_graph(graph)
# we divide into chunks (say, 4 beats) 
sequences = FiniteSequence.from_graph(graph)

common_vectors = common_subsequences(sequences.to_vectors())
common_rhythms = common_subsequences(sequences.durations)

for i, vectors in common_vectors:
    print("===============================", i)
    cur_pitch = 60
    events = []
    for v in vectors:
        events.append(Event([cur_pitch], v[1]))
        cur_pitch = cur_pitch + v[0]
    seq = FiniteSequence(events)
    Container(bpm=50, playback_rate=1)\
        .add_sequence(seq)\
        .playback()
