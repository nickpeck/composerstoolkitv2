"""Extract a markov table of note motions from Bach's chorale
no1. Then use this to compose a new harmonisation under Bach's
existing melody.
"""
import os
from midiutil.MidiFile import MIDIFile # type: ignore
from mido import MidiFile

from composerstoolkit import *
from composerstoolkit.resources import scales, pitches

filename = os.path.join("tests", "chor001.MID")
midi_file = MidiFile(filename)
graph = Graph.from_midi_track(midi_file.tracks[0])
table = graph.to_markov_table()

pf = pitches.PitchFactory()

melody = Sequence.from_generator(using_markov_table(
    Event(pitches=[pf("G4")], duration=1),
    table
)).transform(
    modal_quantize(scales.G_major)
)

Container(bpm=150, playback_rate=1)\
    .add_sequence(melody)\
    .playback()
