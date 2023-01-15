"""
Illustrates using live MIDI input events to transform a generative piece of music (just a simple ostinato).
There are two gates:
- E2 toggles on a gate that quantizes the tonality to E major
- Ab2 toggles on a gate that quantizes the tonality to Ab major

Altering the position of the pitch wheel transposes the music +/- of the neutral position.
Altering the position of the 1st control wheel (20 on my controller) reduces the duration of the events
"""

from composerstoolkit import *

pf = pitches.PitchFactory()
init_midi()

MIDI_CONTROLLER_NAME = "V61"

midi_in = MidiInputBus(midi_device = get_midi_device_id(MIDI_CONTROLLER_NAME))

def my_gate1(context):
    return 40 in midi_in.active_notes

def my_gate2(context):
    return 44 in midi_in.active_notes

@Transformer
def my_pitch_transformer(seq: Sequence):
    for event in seq.events:
        pitch_wheel_pos = 64
        try:
            pitch_wheel_pos = midi_in.control_data[0]
        except KeyError:
            pass
        pitch_delta = pitch_wheel_pos - 64
        yield event.extend(pitches = [p + pitch_delta for p in event.pitches])

@Transformer
def my_duration_transformer(seq: Sequence):
    for event in seq.events:
        wheel1_pos = 1
        try:
            wheel1_pos = midi_in.control_data[20] + 1
        except KeyError:
            pass
        duration = event.duration * ( 1/(wheel1_pos/128)/10)
        yield event.extend(duration=duration)

ostinato = Sequence(events=[
    Event(pitches=[pf("C6")], duration=EIGHTH_NOTE),
    Event(pitches=[pf("D6")], duration=EIGHTH_NOTE),
    Event(pitches=[pf("E6")], duration=EIGHTH_NOTE),
    Event(pitches=[pf("G6")], duration=EIGHTH_NOTE),
    Event(pitches=[pf("A6")], duration=EIGHTH_NOTE),
]).transform(
    loop()
).transform(
    my_pitch_transformer()
)
    
mysequencer = Sequencer(bpm=80, debug=False)\
    .add_sequence(ostinato, channel_no=1)\
    .add_transformer(gated(
        modal_quantize(scales.E_major),
        my_gate1,
        lambda: mysequencer.context))\
    .add_transformer(gated(
        modal_quantize(scales.Ab_major),
        my_gate2,
        lambda: mysequencer.context))\
    .add_transformer(
        my_duration_transformer()
    )

mysequencer.playback()
