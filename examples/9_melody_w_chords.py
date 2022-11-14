"""Use a generator to assemble a progression of diatonic seventh
chords about the cycle of fiths, and then develop a lead line
from a fragment that fits against these chords.
"""
from composerstoolkit import *
from composerstoolkit.resources import scales

chords = Sequence.from_generator(
    chord_cycle(
        scale=scales.C_major,
        start=Event(pitches=[60,64,67,71], duration=WHOLE_NOTE),
        cycle_of=-4,
        max_len=16)).bake()

@Constraint
def constraint_use_chord_tone_on_first_beat(
    sequence: FiniteSequence) -> bool:
    for i,event in enumerate(sequence.events):
        if i % 4 != 0:
            continue
        chord_pcs = chords.event_at(i).to_pitch_class_set()
        if event.pitches[-1] % 12 not in chord_pcs:
            return False
    return True

melody = develop(
    FiniteSequence(events=[
        Event(pitches=[72], duration=QUARTER_NOTE),
        Event(pitches=[74], duration=QUARTER_NOTE),
        Event(pitches=[76], duration=QUARTER_NOTE)]),
    mutators=[
        transpose_diatonic(1, scales.C_major),
        invert(),
        retrograde(3)],
    constraints=[
        constraint_in_set(scales.C_major),
        constraint_no_leaps_more_than(4),
        constraint_use_chord_tone_on_first_beat()],
    min_beats=16
)

melody = Sequence(melody.events).transform(tie_repeated()).bake()

Sequencer(bpm=60, playback_rate=1)\
    .add_sequence(melody[:16])\
    .add_sequence(chords)\
    .playback()
