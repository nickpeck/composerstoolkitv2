"""
Illustration of 'tapping' into an existing sequence at given points and using this to generate new sequences.
Might be useful for some complex generative synthesis
"""

from composerstoolkit import *

pf = pitches.PitchFactory()

pitch_seq = [pf("C4"), pf("C4"), pf("Eb4"), pf("F4"), pf("G4"), pf("Ab4"), pf("Bb4"), pf("C5")]
pitch_seq = pitch_seq + list(reversed(pitch_seq))

def pitch_generator(duration=1):
    i = 0
    while True:
        for p in pitch_seq:
            yield Event([p], duration)
            i = i + 1
            if i > 100:
                return

seq2 = Sequence()
seq3 = Sequence()
seq1 = Sequence(events=pitch_generator())\
    .feed_into(seq2).\
    transform(rhythmic_augmentation(multiplier=3)).\
    transform(tintinnabulation(t_voice_pcs=[0,3,7]))
seq2 = seq2.feed_into(seq3)\
    .transform(tintinnabulation(t_voice_pcs=[0,3,7]))\
    .transform(transpose(-12))
seq3 = seq3.transform(rhythmic_augmentation(multiplier=9))\
    .transform(transpose(-12))

sequencer = Sequencer(bpm=80, debug=True).add_sequences(seq1, seq2, seq3)
sequencer.save_as_midi_file("sample.midi")
