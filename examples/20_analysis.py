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
sequence = FiniteSequence.from_graph(graph)

common_vectors = common_subsequences(sequence.to_vectors())
common_rhythms = common_subsequences(sequence.durations)

def seq_chunked(seq: FiniteSequence, n: int):
    chunks = []
    for i in range(0, len(seq), n):
        chunks.append(seq[i:i + n])
    return chunks

chunked = seq_chunked(sequence.pitches, 16)
hidden_pitch_patterns = hidden_subsequences(chunked, 100)

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


