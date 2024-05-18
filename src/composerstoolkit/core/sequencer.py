from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional
import logging
import importlib
import itertools
import time
import sys

import abjad

from . sequence import Sequence, FiniteSequence, Event
from . scheduler import Scheduler
from . synth import Playback, DummyPlayback
from .. resources.pitches import PitchFactory


@dataclass
class Context:
    sequencer: Optional[Sequencer] = None
    _context: Optional[ClassVar['Context']] = None

    @property
    def bpm(self) -> float:
        return self.sequencer.options["bpm"]

    @property
    def rate(self) -> float:
        return self.sequencer.options["playback_rate"]

    @property
    def time_offset(self) -> float:
        if self.sequencer is None:
            return 0
        if self.sequencer.scheduler.playback_started_ts is None:
            return 0
        return time.time() - self.sequencer.scheduler.playback_started_ts

    @property
    def beat_offset(self) -> float:
        if self.sequencer is None:
            return 0
        return self.time_offset * ((self.bpm / 60) * self.rate)

    @staticmethod
    def get_context(*args, **kwargs):
        if Context._context is None:
            Context._context = Context(*args, **kwargs)
        return Context._context

    def new_sequencer(self, *args, **kwargs) -> Sequencer:
        self.sequencer = Sequencer(*args, **kwargs)
        return self.sequencer


class Sequencer:
    def __init__(self, **kwargs):
        """Optional args:
        synth - a synthesier function (defaults to DummyPlayback)
        bpm - int
        playback_rate - defaults to 1
        """
        super().__init__()

        if "synth" not in kwargs:
            kwargs["synth"] = Sequencer.get_default_synth()

        self.options = {
            "bpm": 120,
            "playback_rate": 1,
            "meter": (4, 4),
            "dump_midi": False,
            "log_level": logging.INFO,
            "buffer_secs": 0,
            "queue_size": 100,
            "window_size": 4
        }

        self.options.update(kwargs)
        self._init_logger()
        self.sequences = []
        self.scheduler = Scheduler(
            buffer_secs=self.options["buffer_secs"],
            queue_size=self.options["queue_size"])
        self.scheduler.daemon = True
        self.scheduler.subscribe(self.options["synth"])
        logging.getLogger().info(f'Using synth {self.options["synth"]}')

    @property
    def time_scale_factor(self):
        playback_rate = self.options["playback_rate"]
        bpm = self.options["bpm"]
        time_scale_factor = (1 / (bpm / 60)) * (1 / playback_rate)
        return time_scale_factor

    def _init_logger(self):
        root = logging.getLogger()
        root.setLevel(self.options["log_level"])
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(self.options["log_level"])
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        root.addHandler(handler)

    @staticmethod
    def get_default_synth() -> Playback:
        path = os.environ.get("DEFAULT_SYNTH", None)
        if path is None:
            return DummyPlayback()
        last_dot = path.rindex(".")
        class_name = path[last_dot + 1:]
        module_path = path[:last_dot]
        cls = getattr(importlib.import_module(module_path), class_name)
        return cls()


    def add_sequence(self, seq: Sequence, **kwargs):
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

    def add_sequences(self, *sequences):
        for sequence in sequences:
            self.add_sequence(sequence)
        return self

    def playback(self, to_midi=False):
        try:
            self._do_playback()
        except KeyboardInterrupt:
            logging.getLogger().info(f"Keyboard interupt received")
            self.scheduler.is_running = False
            self.scheduler.join(1)


    def _do_playback(self):
        logging.getLogger().info(f"Sequencer starting playback")
        channel_positions = {}
        self.scheduler.start()
        active_channels = len(self.sequences)
        window_size = self.options["window_size"]
        window = (0, window_size)
        with self.options["synth"]:
            while active_channels > 0:
                start, end = window
                for channel_no, _, seq in self.sequences:
                    try:
                        count = channel_positions[channel_no]
                    except KeyError:
                        channel_positions[channel_no] = 0
                        count = 0
                    while count >= start and count <= end:
                        try:
                            if isinstance(seq, Sequence):
                                event = next(seq.events)
                            elif isinstance(seq, FiniteSequence):
                                event = seq.events.pop()
                        except (StopIteration, IndexError):
                            active_channels = active_channels - 1
                            logging.getLogger().info(f"Channel {channel_no} playback has completed")
                            break
                        logging.getLogger().info(f"Channel {channel_no} event {event}")
                        future_time = count + (event.duration * self.time_scale_factor)
                        self.scheduler.add_event(count, channel_no, event.extend(duration=event.duration * self.time_scale_factor))
                        count = future_time
                    channel_positions[channel_no] = future_time
                window = (start + window_size, end + window_size)
            logging.getLogger().info("All channels have completed. Waiting for scheduler to finish playback")
            while self.scheduler.has_events:
                time.sleep(1)
            logging.getLogger().info("Playback complete")

    def add_transformer(self, transformer: Callable[[Sequence], Iterator[Event]]) -> Sequencer:
        """Convenience method for applying a transformation function globally to all
        sequences in the Sequencer.
        """
        for i, _seq in enumerate(self.sequences):
            channel_no, offset, seq = self.sequences[i]
            self.sequences[i] = (channel_no, offset, seq.extend(
                events=transformer(seq)))
        return self

    def show_notation(self):
        pf = PitchFactory(output="abjad")
        staves = []
        for (channel_no, offset, seq) in self.sequences:
            if not isinstance(seq, FiniteSequence):
                raise Exception("Only FiniteSequence(s) are supported for notation output")
            ly_str = []
            for event in seq.events:
                note = "r"  # rest
                octave = "'"
                duration = 4 / event.duration
                if duration % 1 > 0:
                    raise Exception("Tuplets are not currently supported in Sequencer.show_notation")
                duration = int(duration)
                if len(event.pitches) == 0:
                    # rest
                    ly_str.append("r" + str(duration))
                elif len(event.pitches) == 1:
                    # single note
                    ly_str.append(pf(event.pitches[0]) + str(duration))
                else:
                    # multiple notes in a chord
                    ly_str.append("<" + \
                                  " ".join([pf(p) for p in event.pitches]) \
                                  + ">" + str(duration))
            voice = abjad.Voice(" ".join(ly_str), name="Voice " + str(channel_no))
            staff = abjad.Staff([voice], name="Staff " + str(channel_no))
            staves.append(staff)
        score = abjad.Score(staves, name="Score")
        abjad.show(score)
        return self

    def save_as_midi_file(self, filename):
        """Save the contents of the sequencer as a MIDI file
        """
        midifile = MIDIFile(len(self.sequences), deinterleave=False)
        midifile.addTempo(0, 0, self.options["bpm"])
        for (channel_no, offset, seq) in self.sequences:
            if not isinstance(seq, FiniteSequence):
                raise Exception("Only FiniteSequence(s) are supported for midi file output")
            midifile.addTrackName(channel_no - 1, offset, "Channel {}".format(channel_no))
            count = offset
            for event in seq.events:
                for cc, value in event.meta.get("cc", []):
                    midifile.addControllerEvent(channel_no - 1, 0, count, cc, value)
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
