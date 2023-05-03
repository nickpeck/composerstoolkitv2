"""Example of a very crude midi loop capture and sampler.
'my_sampler' captures a stream of midi note_on events
'loop_toggle' is used to capture these into a buffer and loop playback. The capture toggle is
controller 48 (push button '1' on my controller).
"""
from time import sleep

from composerstoolkit import *

init_midi()

MIDI_CONTROLLER_NAME = "V61"
midi_in = MidiInputBus(midi_device=get_midi_device_id(MIDI_CONTROLLER_NAME))

quantization_period = 0.1

def midi_realtime_input():
    held_pitches = set()
    while True:
        active = set(midi_in.active_notes)
        new_pitches = active.difference(held_pitches)
        released_pitches = held_pitches.difference(active)
        held_pitches = active
        yield Event(pitches=list(new_pitches), meta={"realtime": "note_on"})
        yield Event(pitches=list(released_pitches), meta={"realtime": "note_off"})
        sleep(quantization_period)

def toggle_capture_mode():
    if 48 in midi_in.control_data.keys():
        return midi_in.control_data[48] > 0
    return False

live_seq = Sequence.from_generator(midi_realtime_input(), meta={"realtime": True, "bpm": 60})\
    .transform(loop_capture(toggle=toggle_capture_mode, debug=True))

mysequencer = Context.get_context().new_sequencer(bpm=live_seq.meta["bpm"], debug=False) \
    .add_sequence(live_seq, channel_no=1)

mysequencer.playback()
