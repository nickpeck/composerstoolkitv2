from composerstoolkit import *

def pulse_pattern():
    while True:
        for i in [3,2]:
            yield i

t_voice_pcs = [0,4,9] # minor triad

sop_melody = list(reversed([i + (12 * 7) for i in scales.MAJ_SCALE_PITCH_CLASSES]))

soprano = Sequence(events=[Event([p], 0) for p in sop_melody]).transform(
    loop(9)
).transform(
    map_to_pulses(Sequence.from_generator(pulses(pulse_pattern())))
).transform(
    tintinnabulation(t_voice_pcs=t_voice_pcs, position="below")
)

alto_melody = list(reversed([i + (12 * 5) for i in scales.MAJ_SCALE_PITCH_CLASSES]))

alto = Sequence(events=[Event([p], 0) for p in alto_melody]).transform(
    loop(6)
).transform(
    map_to_pulses(Sequence.from_generator(pulses(pulse_pattern())))
).transform(
    tintinnabulation(t_voice_pcs=t_voice_pcs, position="below")
).transform(
    rhythmic_augmentation(multiplier=3)
)

tenor_melody = list(reversed([i + (12 * 3) for i in scales.MAJ_SCALE_PITCH_CLASSES]))

tenor = Sequence(events=[Event([p], 0) for p in tenor_melody]).transform(
    loop(3)
).transform(
    map_to_pulses(Sequence.from_generator(pulses(pulse_pattern())))
).transform(
    tintinnabulation(t_voice_pcs=t_voice_pcs, position="below")
).transform(
    rhythmic_augmentation(multiplier=6)
)

mysequencer = Context.get_context().new_sequencer(bpm=140, playback_rate=1, debug=True) \
    .add_sequence(tenor.bake(), channel_no=3, offset=9) \
    .add_sequence(alto.bake(), channel_no=2, offset=3) \
    .add_sequence(soprano.bake(), channel_no=1)

mysequencer.save_as_midi_file("tintinnabulation.midi")