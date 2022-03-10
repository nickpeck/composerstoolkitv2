from __future__ import annotations
from dataclasses import dataclass, field
import os
from time import sleep
import signal
import sys
from typing import Any, Dict, List, Optional, Callable, Iterator, Set
from threading import Thread

import itertools
import functools

import fluidsynth # type: ignore
from midiutil.MidiFile import MIDIFile # type: ignore
from mido import MidiTrack, Message # type: ignore

class Container:
    """Provides a context for playing back multiple sequences
    or rendering them out to a MIDI file.
    """
    def __init__(self,  **kwargs):
        """Optional args:
        synth - a synthesier function (defaults to fluidsynth)
        bpm - int
        playback_rate - defaults to 1
        """
        if "synth" not in kwargs:
            # intialise a fallback synth
            synth = fluidsynth.Synth()
            synth.start()
            sfid = synth.sfload("Nice-Steinway-v3.8.sf2")
            synth.program_select(0, sfid, 0, 0)
            kwargs["synth"] = synth

        self.options = {
            "bpm": 120,
            "playback_rate": 1,
            "synth": kwargs["synth"],
            "debug": True
        }
        self.sequences = []
        self.options.update(kwargs)

    @property
    def voices(self):
        return [seq for (channel_no, offset, seq) in self.sequences]

    def add_sequence(self, seq, **kwargs):
        """Add a sequence to the playback container.
        optional args:
            offset (default 0)
            channel_no (defaults to the next available channel)
        """
        try:
            offset = kwargs["offset"]
        except KeyError:
            offset = 0
        try:
            channel_no = kwargs["channel_no"]
        except KeyError:
            channel_no = len(self.sequences)
        self.sequences.append((channel_no, offset, seq))
        return self

    def _play_channel(self, channel_no, offset, seq, synth):
        playback_rate = self.options["playback_rate"]
        bpm = self.options["bpm"]
        time_scale_factor = (1/(bpm/60)) * (1/playback_rate)
        print("Channel {} playback starting".format(channel_no))
        sleep(offset)
        for event in seq.events:
            if self.options["debug"]:
                print(event)
            for pitch in event.pitches:
                synth.noteon(0, pitch, 60)
            sleep(event.duration * time_scale_factor)
            for pitch in event.pitches:
                synth.noteoff(0, pitch)
        print("Channel {} playback ended".format(channel_no))

    def playback(self):
        """Playback all midi channels
        """
        def signal_handler(_sig, _frame):
            print('Bye')
            sys.exit(0)
        signal.signal(signal.SIGINT, signal_handler)
        print('Press Ctrl+C to exit')
        if os.name != 'nt':
            # pylint: disable=no-member
            signal.pause()

        synth = self.options["synth"]
        channels = []
        for channel_no, offset, seq in self.sequences:
            player_thread = Thread(
                target=self._play_channel,
                args=(channel_no, offset, seq,synth))
            player_thread.daemon = True
            channels.append(player_thread)
        for player_thread in channels:
            player_thread.start()
        while True:
            running_count = 0
            for player_thread in channels:
                if player_thread.is_alive():
                    running_count = running_count + 1
            if running_count == 0:
                return

    def save_as_midi_file(self, filename):
        """Save the contents of the container as a MIDI file
        """
        midifile = MIDIFile(len(self.sequences))
        midifile.addTempo(0, 0, self.options["bpm"])
        for (channel_no, offset, seq) in self.sequences:
            midifile.addTrackName(channel_no, offset, "Channel {}".format(channel_no))
            count = offset
            for event in seq.events:
                for pitch in event.pitches:
                    try:
                        dynamic = event.meta["dynamic"]
                    except KeyError:
                        dynamic = 100
                    midifile.addNote(channel_no, 0, pitch, count, event.duration, dynamic)
                count = count + event.duration
        with open(filename, 'wb') as outf:
            midifile.writeFile(outf)
        return self
