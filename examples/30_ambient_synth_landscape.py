from composerstoolkit import *

pf = pitches.PitchFactory()

drone_c = Sequence(events=[
    Event([pf("C2")], duration=WHOLE_NOTE * 5),
]).transform(
    loop()
)

drone_g = Sequence(events=[
    Event([pf("G2")], duration=WHOLE_NOTE * 3),
]).transform(
    loop()
)


def my_gate1(context):
    return context.beat_offset % 15 != 0
    
def my_gate2(context):
    return context.beat_offset % 15 < 7
    
@Transformer
def silence(seq: Sequence) -> Iterator[Event]:
    for event in seq.events:
        yield Event(pitches=[], duration=event.duration)

chords = Sequence.from_generator(
    chord_cycle(
        scale=scales.C_major,
        start=Event(pitches=[pf("C4"), pf("E4"), pf("G4"), pf("B4"), pf("D5")], duration=1),
        cycle_of=-3)
).transform(
    loop()
).transform(
    map_to_pulses(
        Sequence.from_generator(collision_pattern(3,5)).transform(loop())
    )
).transform(
    rhythmic_augmentation(multiplier=15)
)

spectral_melody = Sequence.from_generator(
    axis_melody(
        axis_pitch = pf("G6"),
        scale = scales.D_major,
        max_steps = 20,
        direction="contract"
)).transform(
    modal_quantize(scale=scales.C_major)
).transform(
    map_to_pulses(
        Sequence.from_generator(collision_pattern(3,5)).transform(loop())
    )
).transform(
    rhythmic_augmentation(multiplier=15)
)

ostinato = Sequence.from_generator(random_slice(
    Sequence(events=[
        Event(pitches=[pf("C6")], duration=EIGHTH_NOTE),
        Event(pitches=[pf("D6")], duration=EIGHTH_NOTE),
        Event(pitches=[pf("E6")], duration=EIGHTH_NOTE),
        Event(pitches=[pf("G6")], duration=EIGHTH_NOTE),
        Event(pitches=[pf("A6")], duration=EIGHTH_NOTE),
    ])
)).transform(
    loop()
)

mysequencer = Sequencer(bpm=80, debug=True)\
    .add_sequence(drone_c, channel_no=1)\
    .add_sequence(drone_g, offset=30, channel_no=2)\
    .add_sequence(chords, offset=5, channel_no=2)\
    .add_sequence(spectral_melody, offset=15, channel_no=3)\
    .add_sequence(ostinato, offset=80, channel_no=4)\
    .add_transformer(gated(
        modal_quantize(scales.E_major),
        cyclic_time_gate(300,100,200),
        lambda: mysequencer.context))\
    .add_transformer(gated(
        modal_quantize(scales.Ab_major),
        cyclic_time_gate(300,200,300),
        get_context = lambda: mysequencer.context))

mysequencer.playback()
