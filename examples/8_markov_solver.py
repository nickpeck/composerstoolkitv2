"""Extract a markov table of note motions from Bach's chorale
no1. Then use this to compose a new harmonisation under Bach's
existing melody.
"""
import os
from midiutil.MidiFile import MIDIFile # type: ignore
from mido import MidiFile

from composerstoolkit import *
from composerstoolkit.resources import scales

filename = os.path.join("tests", "chor001.MID")
midi_file = MidiFile(filename)
graph = Graph.from_midi_track(midi_file.tracks[0])

voice1 = FiniteSequence(events=[
    Event(pitches=[67], duration=QUARTER_NOTE),
    Event(pitches=[67], duration=HALF_NOTE),
    Event(pitches=[74], duration=QUARTER_NOTE),
    Event(pitches=[71], duration=DOTTED(QUARTER_NOTE)),
    Event(pitches=[69], duration=EIGHTH_NOTE),
    Event(pitches=[67], duration=QUARTER_NOTE),
    Event(pitches=[67], duration=DOTTED(QUARTER_NOTE)),
    Event(pitches=[69], duration=EIGHTH_NOTE),
    Event(pitches=[71], duration=QUARTER_NOTE),
    Event(pitches=[69], duration=HALF_NOTE),
])

I_IV_V_in_G = [{0,4,7}, {2,7,11}, {2,6,9}]

voice2 = backtracking_markov_solver(
        Event(pitches=[62], duration=QUARTER_NOTE),
       graph.to_markov_table(),
    constraints=[
        constraint_in_set(scales.G_major),
        constraint_no_voice_crossing(voice1),
        constraint_no_leaps_more_than(4),

        constraint_no_consecutives({0,5,7}, voice1),
        constraint_use_chords(I_IV_V_in_G, [voice1])
        ],
    heuristics=[],
    n_events=12,
)

voice2 = Sequence(voice2.events).transform(tie_repeated()).bake()

voice3 = backtracking_markov_solver(
        Event(pitches=[59], duration=QUARTER_NOTE),
       graph.to_markov_table(),
    constraints=[
        constraint_in_set(scales.G_major),
        constraint_no_voice_crossing(voice2),
        constraint_no_leaps_more_than(4),

        constraint_no_consecutives({0,5,7}, voice1),
        constraint_no_consecutives({0,5,7}, voice2),
        constraint_use_chords(I_IV_V_in_G, [voice1, voice2])
        ],
    heuristics=[],
    n_events=12,
)

voice3 = Sequence(voice3.events).transform(tie_repeated()).bake()

voice4 = backtracking_markov_solver(
        Event(pitches=[55], duration=QUARTER_NOTE),
       graph.to_markov_table(),
    constraints=[
        constraint_in_set(scales.G_major),
        constraint_no_voice_crossing(voice3),
        constraint_no_leaps_more_than(12),

        constraint_no_consecutives({0,5,7}, voice1),
        constraint_no_consecutives({0,5,7}, voice2),
        constraint_no_consecutives({0,5,7}, voice3),
        constraint_use_chords(I_IV_V_in_G, [voice1, voice2, voice3])
        ],
    heuristics=[],
    n_events=12,
)

voice4 = Sequence(voice4.events).transform(tie_repeated()).bake()

Context.get_context().new_sequencer(bpm=60, playback_rate=1)\
    .add_sequence(voice1)\
    .add_sequence(voice2)\
    .add_sequence(voice3)\
    .add_sequence(voice4)\
    .playback()
