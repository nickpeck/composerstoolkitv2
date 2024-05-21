"""
Some intefaces for different playback engines.
"""

from abc import ABC
import logging
import time

class Playback(ABC):
    def noteon(self, track: int, pitch: int, velocity: int):
        raise NotImplementedError("noteon")
        
    def noteoff(self, track: int, pitch: int):
        raise NotImplementedError("noteoff")

    def control_change(self, track: int, cc: int, value: int):
        raise NotImplementedError("control_change")
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

class DummyPlayback(Playback):
    """
    Just logs the noteon/noteoff event
    """
    def noteon(self, track: int, pitch: int, velocity: int):
        logging.getLogger().info(f"NOTE ON track:{track} pitch:{pitch} velocity:{velocity}")
        
    def noteoff(self, track: int, pitch: int):
        logging.getLogger().info(f"NOTE OFF track:{track} pitch:{pitch}")

    def control_change(self, track: int, cc: int, value: int):
        logging.getLogger().info(f"NOTE OFF track:{track} cc:{cc} value:{value}")

class RTPMidi(Playback):
    """
    Wrapper for network MIDI playback using rtmidi
    (package python-rtmidi)
    """

    def __init__(self, get_port=lambda all_ports: 0):
        """
        get_port - function to return the index of the desired
        rtpmidi port, given a list of available port names
        """
        import rtmidi
        self.midiout = rtmidi.MidiOut()
        available_ports = self.midiout.get_ports()
        self.port_no = get_port(available_ports)
        self._is_active = False
    
    def noteon(self, track: int, pitch: int, velocity: int):
        from rtmidi.midiconstants import NOTE_ON
        status = NOTE_ON | (track - 1)  # bit-wise OR of NOTE_ON and channel (zero-based)
        if self._is_active:
            self.midiout.send_message([status, pitch, velocity])
        
    def noteoff(self, track: int, pitch: int):
        from rtmidi.midiconstants import NOTE_OFF
        status = NOTE_OFF | (track - 1)
        if self._is_active:
            self.midiout.send_message([status, pitch, 0])

    def control_change(self, track: int , cc: int, value: int):
        from rtmidi.midiconstants import CONTROL_CHANGE
        status = CONTROL_CHANGE | (track - 1)
        if self._is_active:
            self.midiout.send_message([status, cc, value])
        
    def __enter__(self):
        self.midiout.open_port(self.port_no)
        self._is_active = True
        logging.getLogger().debug("Opened connection to RTPMidi port")
        return self
        
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.midiout.close_port()
        time.sleep(0.1)
        self._is_active = False
        del self.midiout
        logging.getLogger().debug("Closed connection to RTPMidi port")

class FluidsynthPlayback(Playback):
    """
    Wrapper for fluidsynth
    """

    def __init__(self, sf_file: str):
        import fluidsynth
        self.synth = fluidsynth.Synth()
        self.sf_file = sf_file
        
    def noteon(self, track: int, pitch: int, velocity: int):
        self.synth.noteon(track, pitch, velocity)
        
    def noteoff(self, track: int, pitch: int):
        self.synth.noteoff(track, pitch)
        
    def __enter__(self):
        self.synth.start()
        sfid = self.synth.sfload(self.sf_file)
        self.synth.program_select(0, sfid, 0, 0)
        logging.getLogger().debug("Load fluidsynth using soundfont {self.sf_file}")
        return self
        
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.synth.delete()
        logging.getLogger().debug(f"Closing fluidsynth")
