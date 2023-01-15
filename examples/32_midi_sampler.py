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

sample_length = 4 # length is in beats, so set a sequencer BPM of 60 to avoid confusion
quantization_period = 0.2

def my_sampler():
    # TODO this is a bit crude, as we aren't capturing the durations properly
    # but just to illustrate the concept for future refinement
    held_pitches = set()
    while True:
        released_pitches = set(midi_in.active_notes) - held_pitches
        held_pitches = set(midi_in.active_notes)
        yield Event(pitches=list(released_pitches), duration=quantization_period)
        sleep(quantization_period)

def toggle_capture_mode():
    if 48 in midi_in.control_data.keys():
        return midi_in.control_data[48] > 0
    return False

live_seq = Sequence.from_generator(my_sampler())\
    .transform(loop_capture(toggle=toggle_capture_mode, debug=True))

mysequencer = Sequencer(bpm=60, debug=True) \
    .add_sequence(live_seq, channel_no=1)

mysequencer.playback()
