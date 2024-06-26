from composerstoolkit import *

pf = pitches.PitchFactory()

# sample probability matrix - choose notes from a chord
# middle tones are statistically more likely
pad = Sequence.from_generator(probability_matrix(choices=[
    (pf("C2"), 0.1),
    (pf("Bb1"), 0.1),
    (pf("F4"), 0.8),
    (pf("Bb4"), 0.8),
    (pf("A7"), 0.2),
    (pf("D7"), 0.2)],
    window=1,
    monody=True
)).transform(
    map_to_pulses(Sequence.from_generator(collision_pattern(4,7)))
).transform( # sustains each node
    update_meta(cc=[(64,127)])
)

sequencer = Sequencer(bpm=90, debug=True, dump_midi=True).add_sequence(pad)
sequencer.playback()