"""
Some intefaces for different playback engines.
"""

from abc import ABC
import logging

class Playback(ABC):
    def noteon(self, channel: int, pitch: int, velocity: int):
        raise NotImplementedError("noteon")
        
    def noteoff(self, channel: int, pitch: int):
        raise NotImplementedError("noteoff")
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

class DummyPlayback(Playback):
    """
    Just logs the noteon/noteoff event
    """
    def noteon(self, channel: int, pitch: int, velocity: int):
        logging.getLogger().info(f"NOTE ON channel:{channel} pitch:{pitch} velocity:{velocity}")
        
    def noteoff(self, channel: int, pitch: int):
        logging.getLogger().info(f"NOTE OFF channel:{channel} pitch:{pitch}")

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
    
    def noteon(self, channel: int, pitch: int, velocity: int):
        from rtmidi.midiconstants import NOTE_ON
        status = NOTE_ON | (channel - 1)  # bit-wise OR of NOTE_ON and channel (zero-based)
        self.midiout.send_message([status, pitch, velocity])
        
    def noteoff(self, channel: int, pitch: int):
        from rtmidi.midiconstants import NOTE_OFF
        status = NOTE_OFF | (channel - 1)
        self.midiout.send_message([NOTE_OFF, pitch, 0])
        
    def __enter__(self):
        self.midiout.open_port(self.port_no)
        logging.getLogger().debug("Opened connection to RTPMidi port")
        return self
        
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.midiout.close_port()
        logging.getLogger().debug("Closed connection to RTPMidi port")

class FluidsynthPlayback(Playback):
    """
    Wrapper for fluidsynth
    """

    def __init__(self, sf_file: str):
        import fluidsynth
        self.synth = fluidsynth.Synth()
        self.sf_file = sf_file
        
    def noteon(self, channel: int, pitch: int, velocity: int):
        self.synth.noteon(channel, pitch, velocity)
        
    def noteoff(self, channel: int, pitch: int):
        self.synth.noteoff(channel, pitch)
        
    def __enter__(self):
        self.synth.start()
        sfid = self.synth.sfload(self.sf_file)
        self.synth.program_select(0, sfid, 0, 0)
        logging.getLogger().debug("Load fluidsynth using soundfont {self.sf_file}")
        return self
        
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.synth.delete()
        logging.getLogger().debug(f"Closing fluidsynth")
