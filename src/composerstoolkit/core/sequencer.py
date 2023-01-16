from __future__ import annotations
from dataclasses import dataclass, field
import logging
import importlib
import os
from time import sleep
import signal
import sys
import time
from typing import Any, Dict, List, Optional, Callable, Iterator, Set
from threading import Thread

import itertools
import functools

import abjad
from midiutil.MidiFile import MIDIFile # type: ignore
from mido import MidiTrack, Message # type: ignore
from . synth import DummyPlayback 
from . sequence import Event, FiniteSequence
from .. resources.pitches import PitchFactory

@dataclass
class Context:
    sequencer: Sequencer
    beat_offset: float = 0.0
    time_offset_secs: float = 0.0

class Sequencer(Thread):
    """Provides a context for playing back multiple sequences
    or rendering them out to a MIDI file.
    """
    @staticmethod
    def get_fallback_synth():
        path = os.environ.get("DEFAULT_SYNTH", None)
        if path is None:
            return DummyPlayback()
        last_dot = path.rindex(".")
        class_name = path[last_dot + 1:]
        module_path = path[:last_dot]
        cls = getattr(importlib.import_module(module_path), class_name)
        return cls()

    @staticmethod
    def _init_logger():
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        root.addHandler(handler)
        
    @property
    def context(self) -> Optional[Context]:
        if self._playback_started_ts is None:
            return None
        bpm = self.options["bpm"]
        rate = self.options["playback_rate"]
        time_offset = time.time() - self._playback_started_ts
        beat_offset = time_offset * ((bpm/60) * rate)
        return Context(
            time_offset_secs = time_offset,
            beat_offset = beat_offset,
            sequencer = self
        )
    
    def __init__(self, **kwargs):
        """Optional args:
        synth - a synthesier function (defaults to DummyPlayback)
        bpm - int
        playback_rate - defaults to 1
        """
        super().__init__()
        if "debug" not in kwargs:
            kwargs["debug"] = False
            
        if kwargs["debug"]:
            Sequencer._init_logger()

        if "synth" not in kwargs:
            kwargs["synth"] = Sequencer.get_fallback_synth()

        logging.getLogger().info(f'Using synth {kwargs["synth"]}')

        self.options = {
            "bpm": 120,
            "playback_rate": 1,
            "meter": (4,4)
        }
        
        self.sequences = []
        self.options.update(kwargs)
        self.active_pitches = []
        self.is_playing = False
        self._playback_started_ts = None

    @property
    def voices(self):
        return [seq for (channel_no, offset, seq) in self.sequences]

    def add_sequence(self, seq, **kwargs):
        """Add a sequence to the playback sequencer.
        optional args:
            offset (default 0)
            channel_no (defaults to the next available channel)
        """
        try:
            offset = kwargs["offset"]
        except KeyError:
            offset = 0
        if offset > 0:
            seq = seq.extend(
                events=itertools.chain([Event(duration=offset)], seq.events))
        try:
            channel_no = kwargs["channel_no"]
        except KeyError:
            channel_no = len(self.sequences) + 1
        seq.meta["channel_no"] = channel_no
        self.sequences.append((channel_no, offset, seq))
        return self

    def _play_channel(self, channel_no, offset, seq, synth):
        playback_rate = self.options["playback_rate"]
        bpm = self.options["bpm"]
        time_scale_factor = (1/(bpm/60)) * (1/playback_rate)
        logging.getLogger().info(f"Channel {channel_no} playback starting")
        drift = None
        for event in seq.events:
            if not self.is_playing:
                return
            if self.options["debug"]:
                logging.getLogger().info(f"Channel {channel_no} {event}")
            future_time = time.time() + (event.duration * time_scale_factor)
            if drift is not None:
                future_time = future_time - drift
                drift = None
            for pitch in event.pitches:
                if event.duration != 0:
                    synth.noteon(channel_no, pitch, 60)
                    self.active_pitches.append((pitch, channel_no))
            pause_int = future_time - time.time()
            if pause_int > 0:
                sleep(pause_int)
            else:
                logging.getLogger().debug(f"Channel {channel_no} drift {abs(pause_int)} s")
                drift = abs(pause_int)
            for pitch in event.pitches:
                if event.duration != -1:
                    synth.noteoff(channel_no, pitch)
                    self.active_pitches.remove((pitch, channel_no))
        logging.getLogger().info("Channel {} playback ended".format(channel_no))
        
    def clear_all(self, synth):
        for pitch in range(0,128):
            for channel_no in range(1,17):
                synth.noteoff(channel_no, pitch)
        logging.getLogger().info("...done")
        
    def run(self):
        self.playback()

    def playback(self):
        """Playback all midi channels
        """
        synth = self.options.get("synth", None)
        with synth:
            def signal_handler(_sig, _frame):
                logging.getLogger().info("Stop signal recieved")
                logging.getLogger().info("Sending note off to all pitches")
                self.is_playing = False
                sleep(2)
                self.clear_all(synth)
                print('Bye')
                sys.exit(0)
            signal.signal(signal.SIGINT, signal_handler)
            print('Press Ctrl+C to exit')
            if os.name != 'nt':
                # pylint: disable=no-member
                signal.pause()

            
            channels = []
            self.is_playing = True
            self._playback_started_ts = time.time()
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
                    
    def add_transformer(self, transformer: Callable[[Sequence], Iterator[Event]]) -> Sequencer:
        """Convenience method for applying a transformation function globally to all
        sequences in the Sequencer.
        """
        for i,_seq in enumerate(self.sequences):
            channel_no, offset, seq = self.sequences[i]
            self.sequences[i] = (channel_no, offset, seq.extend(
                events = transformer(seq)))
        return self

    def save_as_midi_file(self, filename):
        """Save the contents of the sequencer as a MIDI file
        """
        midifile = MIDIFile(len(self.sequences))
        midifile.addTempo(0, 0, self.options["bpm"])
        for (channel_no, offset, seq) in self.sequences:
            midifile.addTrackName(channel_no - 1, offset, "Channel {}".format(channel_no))
            count = offset
            for event in seq.events:
                for pitch in event.pitches:
                    try:
                        dynamic = event.meta["dynamic"]
                    except KeyError:
                        dynamic = 100
                    midifile.addNote(channel_no - 1, 0, pitch, count, event.duration, dynamic)
                count = count + event.duration
        with open(filename, 'wb') as outf:
            midifile.writeFile(outf)
        return self

    def show_notation(self):
        pf = PitchFactory(output="abjad")
        staves = []
        for (channel_no, offset, seq) in self.sequences:
            if not isinstance(seq, FiniteSequence):
                raise Exception("Only FiniteSequence(s) are supported for notation output")
            ly_str = []
            for event in seq.events:
                note = "r" # rest
                octave = "'"
                duration = 4/event.duration
                if duration % 1 > 0:
                    raise Exception("Tuplets are not currently supported in Sequencer.show_notation")
                duration = int(duration)
                if len(event.pitches) == 0:
                    # rest
                    ly_str.append("r"+str(duration))
                elif len(event.pitches) == 1:
                    # single note
                    ly_str.append(pf(event.pitches[0])+str(duration))
                else:
                    # multiple notes in a chord
                    ly_str.append("<" + \
                        " ".join([pf(p) for p in event.pitches])\
                        + ">" +str(duration))
            voice = abjad.Voice(" ".join(ly_str), name="Voice " + str(channel_no))
            staff = abjad.Staff([voice], name="Staff " + str(channel_no))
            staves.append(staff)
        score = abjad.Score(staves, name="Score")
        abjad.show(score)
        return self
