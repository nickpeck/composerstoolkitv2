from pprint import pprint

from midiutil.MidiFile import MIDIFile # type: ignore
from mido import MidiFile

from composerstoolkit import *

print("Loading case base")

filename = os.path.join("case_base", "cello_suites", "cs1-2all.mid")
midi_file = MidiFile(filename)
graph = Graph.from_midi_track(midi_file.tracks[1])
full_piece = FiniteSequence.from_graph(graph)

# we divide into chunks (say, 4 beats) 
sequence = FiniteSequence.from_graph(graph)

common_vectors = common_subsequences(sequence.to_vectors())
common_rhythms = common_subsequences(sequence.durations)

def chunked(dataset: List[Any], window: int):
    """Return a list comprising of dataset
    broken down into down into sizes of
    length window.
    """
    chunks = []
    for i in range(0, len(dataset), window):
        chunks.append(dataset[i:i + window])
    return chunks

chunked = chunked(sequence.pitches, 16)

hidden_pitch_patterns = hidden_subsequences(chunked, 100)

def build_chord_lexicon(chords: List[Event]):
    lexicon = []
    for chordal_event in chords:
        lexicon = lexicon + [
            chord.to_pitch_class_set() for chord in \
                chord_cycle(scale = scales.chromatic,
            start=chordal_event,
            cycle_of=1,
            voice_lead=False,
            max_len=12)]
    return lexicon

chord_lexicon = build_chord_lexicon(chords=[
    Event(pitches=[0,4,7]),
    Event(pitches=[0,3,7]),
    Event(pitches=[0,4,7,10]),
    Event(pitches=[0,3,7,10]),
    Event(pitches=[0,4,7,11]),
    Event(pitches=[0,3,6,9])]
)

found_chords = chordal_analysis(sequence,chord_lexicon=chord_lexicon,window_size_beats=2)

found_chords = [Event(list(pitches), 2) for pitches in found_chords]
found_chords = Sequence(found_chords).transform(
    transpose(12 * 5)
).bake()

common_chords = common_subsequences([e.pitches for e in found_chords.events])
for count, progression in common_chords:
    seq = FiniteSequence([Event(sorted(chord), 2) for chord in progression])
    Sequencer(bpm=50, playback_rate=1)\
        .add_sequence(seq)\
        .playback()


