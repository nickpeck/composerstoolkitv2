import logging

import midiutil
from time import time

from . synth import Playback

class MidiCapture(Playback):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.bpm = kwargs.get("bpm", 120)
        self.playback_rate = kwargs.get("playback_rate", 1)
        self.active_pitches = {}
        self.time_started = None
        self.note_events = []
        self.cc_events = []
        self.channels = set()

    def _time_to_beats(self, time):
        return (time * (self.bpm / 60)) * self.playback_rate

    def noteon(self, channel: int, pitch: int, velocity: int):
        self.active_pitches[(pitch, channel)] = time(), velocity

    def noteoff(self, channel: int, pitch: int):
        self.channels.add(channel)
        cur_time = time()
        try:
            note_started_time, volume = self.active_pitches[(pitch, channel)]
        except KeyError:
            logging.getLogger().error(f"MidiCapture error - no stored pitch event: {(pitch, channel)}")
            return
        duration = self._time_to_beats(cur_time - note_started_time)
        time_offset = self._time_to_beats(cur_time - self.time_started)
        event = (channel - 1, 0, pitch, time_offset, duration, volume)
        self.note_events.append(event)

    def control_change(self, channel: int, cc: int, value: int):
        time_offset = self._time_to_beats(cur_time - self.time_started)
        event = (channel - 1, 0, time_offset, cc, value)
        self.cc_events.append(event)

    def _write_midi(self):
        filename = str(int(time())) + ".midi"
        logging.getLogger().info(f"writing midi data to file")
        channels = sorted(list(self.channels))
        midifile = midiutil.MIDIFile(
            channels[-1],
            deinterleave=False)  # https://github.com/MarkCWirt/MIDIUtil/issues/24
        midifile.addTempo(0, 0, self.bpm)
        i = 1
        for channel_no in channels:
            while i <= channel_no:
                midifile.addTrackName(i - 1, 0, "Channel {}".format(i))
                i = i + 1
        for track, channel, pitch, offset, duration, volume in self.note_events:
            midifile.addNote(track=track, channel=channel, pitch=pitch, time=offset, duration=duration, volume=volume)
        for track, channel, offset, controller_number, parameter in self.cc_events:
            midifile.addControllerEvent(track=track, channel=channel,
                                        time=offset, controller_number=controller_number, parameter=parameter)
        with open(filename, 'wb') as outf:
            midifile.writeFile(outf)
        logging.getLogger().info(f"dumped MIDI output to {filename}")

    def __enter__(self):
        self.time_started = time()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._write_midi()
