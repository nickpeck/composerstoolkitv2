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
chunked = seq_chunked(sequence.pitches, 16)

hidden_pitch_patterns = hidden_subsequences(chunked, 100)

# library of basic triads through all keys
maj_triads_pcs = [chord.to_pitch_class_set() for chord in chord_cycle(scale = scales.chromatic,
    start=Event(pitches=[0,4,7]),
    cycle_of=1,
    voice_lead=False,
    max_len=12)]

min_triads_pcs = [chord.to_pitch_class_set() for chord in chord_cycle(scale = scales.chromatic,
    start=Event(pitches=[0,3,7]),
    cycle_of=1,
    voice_lead=False,
    max_len=12)]

dom_7th_pcs = [chord.to_pitch_class_set() for chord in chord_cycle(scale = scales.chromatic,
    start=Event(pitches=[0,4,7,10]),
    cycle_of=1,
    voice_lead=False,
    max_len=12)]

dom_min_7th_pcs = [chord.to_pitch_class_set() for chord in chord_cycle(scale = scales.chromatic,
    start=Event(pitches=[0,3,7,10]),
    cycle_of=1,
    voice_lead=False,
    max_len=12)]

maj_7th_pcs = [chord.to_pitch_class_set() for chord in chord_cycle(scale = scales.chromatic,
    start=Event(pitches=[0,4,7,11]),
    cycle_of=1,
    voice_lead=False,
    max_len=12)]

dim_7th_pcs = [chord.to_pitch_class_set() for chord in chord_cycle(scale = scales.chromatic,
    start=Event(pitches=[0,3,6,9]),
    cycle_of=1,
    voice_lead=False,
    max_len=3)]

chord_lexicon = maj_triads_pcs + min_triads_pcs + maj_7th_pcs + dom_7th_pcs + dom_min_7th_pcs + maj_7th_pcs + dim_7th_pcs

found_chords = chordal_analysis(sequence, 0, chord_lexicon, start_offset=0.125)

found_chords = [Event(list(pitches), 2.125) for pitches in found_chords]
found_chords = Sequence(found_chords).transform(
    transpose(12 * 4)
)

Container(bpm=50, playback_rate=1)\
    .add_sequence(found_chords)\
    .add_sequence(sequence)\
    .playback()

exit(0)

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


