from composerstoolkit import *

DRUM_PITCHES = {
    "hh": 42,
    "bd": 35,
    "sn": 38,
    "rd": 59,
    "cb": 56
}

track1 = Sequence.from_generator(
    random_slice(
        Sequence(events=[
            Event(pitches=[DRUM_PITCHES["hh"]], duration=SIXTEENTH_NOTE),
            Event(pitches=[DRUM_PITCHES["bd"]], duration=SIXTEENTH_NOTE),
            Event(pitches=[DRUM_PITCHES["hh"]], duration=SIXTEENTH_NOTE),
            Event(pitches=[DRUM_PITCHES["rd"]], duration=SIXTEENTH_NOTE),
            Event(pitches=[DRUM_PITCHES["bd"]], duration=EIGHTH_NOTE),
            Event(pitches=[DRUM_PITCHES["hh"]], duration=SIXTEENTH_NOTE),
            Event(pitches=[DRUM_PITCHES["bd"]], duration=SIXTEENTH_NOTE),
            Event(pitches=[DRUM_PITCHES["sn"]], duration=EIGHTH_NOTE)
        ])
    )
).transform(loop()).transform(transpose(20)).transform(
    map_to_pulses(
        Sequence.from_generator(collision_pattern(3,5)).transform(loop())
    )
).transform(
    rhythmic_diminution(3)
)
