import logging
import os
from threading import Thread

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg
import pygame.midi

def init_midi():
    pg.init()
    pg.fastevent.init()
    pygame.midi.init()

def enummerate_devices(mode="input"):
    """
    Return a enumerated list of (interf, name, input, output, opened) for each MIDI device.
    (The enumeration id is the device id, to be passed back to pygame to interact with the device)
    """
    results = []
    for i in range(pygame.midi.get_count()):
        (interf, name, input, output, opened) = pygame.midi.get_device_info(i)
        if mode == "input" and input or mode == "output" and output:
            results.append((i, (interf, name, input, output, opened)))
    return results

class MidiListener(Thread):
    def __init__(self, input_id, **kwargs):
        """
        Midi Listener
        Parameters input_id - the numeric index of the device (see enummerate_devices)
        kwargs: can be used to define handler functions for any of the following:
            note_on, note_off, control_change
        """
        super().__init__()
        self.input_dev = pygame.midi.Input(input_id)
        self.handlers = {k: lambda e: None for k in [
            "note_on",
            "note_off",
            "control_change"
        ]}
        self.handlers.update(kwargs)

    def _publish_event(self, e):
        if e.status == 144:
            self.handlers["note_on"](e)
        elif e.status == 128:
            self.handlers["note_off"](e)
        else:
            self.handlers["control_change"](e)

    def _poll_for_events(self):
        event_post = pg.fastevent.post
        midi_events = self.input_dev.read(10)
        # convert them into pygame events.
        midi_evs = pygame.midi.midis2events(midi_events, self.input_dev.device_id)
        [self._publish_event(e) for e in midi_evs]

        for m_e in midi_evs:
            event_post(m_e)

    def run(self):
        going = True
        event_get = pg.fastevent.get
        while going:
            events = event_get()
            for e in events:
                if e.type in [pg.QUIT]:
                    going = False
                if e.type in [pg.KEYDOWN]:
                    going = False

            if self.input_dev.poll():
                self._poll_for_events()

class MidiInputBus:
    """
    Transforms the stream of events from a midi input device into a form that can
    be used by multiple gates or transformers.
    The bus has two properties, active_notes and control_data, which can be queried to determine
    the current state of the midi input device.
    """
    def __init__(self, midi_device):
        self.active_notes = []
        self.control_data = {}
        listener = MidiListener(
            midi_device,
            note_on=self._on_note_on,
            note_off=self._on_note_off,
            control_change=self._on_control_change)
        listener.setDaemon(True)
        listener.start()

    def _on_note_on(self, e):
        self.active_notes.append(e.data1)

    def _on_note_off(self, e):
        self.active_notes.remove(e.data1)

    def _on_control_change(self, e):
        self.control_data[e.data1] = e.data2

def get_midi_device_id(midi_device_name):
    init_midi()
    device = None
    if midi_device_name is None:
        device = pygame.midi.get_default_input_id()
    else:
        for i, info in enummerate_devices():
            (interf, name, input, output, opened) = info
            if name.decode() == midi_device_name:
                device = i
        if device is None:
            raise Exception(f"No device named {midi_device_name}")
    return device
