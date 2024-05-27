from __future__ import annotations
import os
from contextlib import ExitStack
from dataclasses import dataclass
from typing import Optional, List
import logging
import importlib
import itertools
import time
import sys

import abjad
from midiutil import MIDIFile

from . sequence import Sequence, FiniteSequence, Event
from . scheduler import Scheduler
from . synth import Playback, DummyPlayback
from . pitch_tracker import PitchTracker
from . midicapture import MidiCapture
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
        if self.sequencer.scheduler.playback_started_ts is None:
            return 0
        return self.sequencer.scheduler.time_elapsed * ((self.bpm / 60) * self.rate)

    @staticmethod
    def get_context(*args, **kwargs):
        if Context._context is None:
            Context._context = Context(*args, **kwargs)
        return Context._context

    def new_sequencer(self, *args, **kwargs) -> Sequencer:
        self.sequencer = Sequencer(*args, **kwargs)
        return self.sequencer


class Sequencer:
    """
    Used to group multiple sequences together as tracks. They can then be used to compose a midi file, produce
    musical notation, or inform real-time playback.
    """
    def __init__(self, **kwargs):
        """Optional args:
        synth - a synthesier function (defaults to DummyPlayback - no sound)
        bpm - int
        playback_rate - defaults to 1
        log_level - (int) logging level (ie logging.DEBUG, logging.INFO)
        queue_size - int (default 100). Scheduler queue size. Limits the number of events that can be submitted to the
         scheduler ahead of time, capping memory usage. Might need to be higher for extreme polyphony - which would
         result in Queue.Full exceptions being raised in the scheduler.
        jit - (default False). enable just in time evaluation (required if the composition uses the
            context.active_pitches data to inform pitch selections). Default is ahead-of-time evaluation.
        dump_midi - (default False) used to collect and dump midi to a timestamped file when the process is terminated.
            This is used for recording infinate duration real-time generative music
            (where save_as_midi_file() cannot be used), or just to store samples for future use.
            Compared to save_as_midi_file, notes may not be perfectly in sync if the sequencer has latency.
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
            "queue_size": 100,
            "jit": False
        }

        self.options.update(kwargs)
        self._init_logger()
        self.sequences = []
        self.active_pitches = PitchTracker()
        self.scheduler = Scheduler(
            queue_size=self.options["queue_size"],
            time_scale_factor=self.time_scale_factor,
            pitch_tracker=self.active_pitches,
            jit=self.options["jit"])
        self.scheduler.daemon = True
        self.scheduler.subscribe(self.options["synth"])
        logging.getLogger().debug(f'Using synth {self.options["synth"]}')

    @property
    def time_scale_factor(self) -> float:
        playback_rate = self.options["playback_rate"]
        bpm = self.options["bpm"]
        time_scale_factor = (1 / (bpm / 60)) * (1 / playback_rate)
        return time_scale_factor

    @property
    def voices(self) -> List[Sequence]:
        return [seq for (track_no, offset, seq) in self.sequences]

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
            track_no (defaults to the next available track)
        """
        try:
            offset = kwargs["offset"]
        except KeyError:
            offset = 0
        if offset > 0:
            seq = seq.extend(
                events=itertools.chain([Event(duration=offset)], seq.events))
        try:
            track_no = kwargs["track_no"]
        except KeyError:
            track_no = len(self.sequences) + 1
        if track_no <= 0:
            raise Exception("add_sequence() track_no should be 1 or greater")
        seq.meta["track_no"] = track_no
        self.sequences.append((track_no, offset, seq))
        return self

    def add_sequences(self, *sequences):
        """Helper method to add multiple sequences at once"""
        for sequence in sequences:
            self.add_sequence(sequence)
        return self

    def playback(self, to_midi=False):
        """Commence playback.
        This will schedule each event for playback using your active synth.
        This is either defined as env variable DEFAULT_SYNTH, or using constructor arg 'synth'.
        Playback will terminate once each sequence runs out of events, or is terminated (ie via CTRL-C)"""
        ctx_managers = [self.options["synth"], self.active_pitches]
        if self.options["dump_midi"]:
            mc = MidiCapture(bpm=self.options["bpm"], playback_rate=self.options["playback_rate"])
            ctx_managers.append(mc)
            self.scheduler.subscribe(mc)
        with ExitStack() as stack:
            for mgr in ctx_managers:
                stack.enter_context(mgr)
            try:
                self._do_playback_loop()
            except KeyboardInterrupt:
                logging.getLogger().info(f"Keyboard interupt received")
                self.scheduler.is_running = False
                self.scheduler.join(0.1)

    def _do_playback_loop(self):
        n_active_tracks = len(self.sequences)
        logging.getLogger().info(f"Sequencer starting playback")
        for track_no, _, seq in self.sequences:
            # enqueue each sound event. The playback thread will wait until the scheduled event time
            self.scheduler.enqueue(track_no= track_no, sequence=seq)
        self.scheduler.start()
        it = iter(self.scheduler)
        while n_active_tracks > 0:
            # as events are performed, the playback thread will yield when it is time to evaluate the next
            # item for each track
            try:
                track_no, seq, offset_secs = next(it)
            except StopIteration:
                break
            # re-enqueue the seq. Evaluation happens on this thread (the main thread).
            if not self.scheduler.enqueue(track_no=track_no, sequence=seq, offset_secs=offset_secs):
                n_active_tracks = n_active_tracks - 1
        logging.getLogger().info("Waiting for scheduler to finish playback")
        while self.scheduler.has_events:
            time.sleep(1)
        logging.getLogger().info("Playback complete")

    def add_transformer(self, transformer: Callable[[Sequence], Iterator[Event]]) -> Sequencer:
        """Convenience method for applying a transformation function globally to all
        sequences in the Sequencer.
        """
        for i, _seq in enumerate(self.sequences):
            track_no, offset, seq = self.sequences[i]
            self.sequences[i] = (track_no, offset, seq.extend(
                events=transformer(seq)))
        return self

    def show_notation(self):
        """
        Create a crude musical notation for debug purposes.
        Requires lilypond to be installed.
        Only FiniteSequences can be turned into notation - otherwise an Exception will be raised.
        """
        pf = PitchFactory(output="abjad")
        staves = []
        for (track_no, offset, seq) in self.sequences:
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
            voice = abjad.Voice(" ".join(ly_str), name="Voice " + str(track_no))
            staff = abjad.Staff([voice], name="Staff " + str(track_no))
            staves.append(staff)
        score = abjad.Score(staves, name="Score")
        abjad.show(score)
        return self

    def save_as_midi_file(self, filename):
        """Save the contents of the sequencer as a MIDI file
        Only FiniteSequences can be written - otherwise an Exception will be raised.
        """
        midifile = MIDIFile(len(self.sequences), deinterleave=False)
        midifile.addTempo(0, 0, self.options["bpm"])
        for (track_no, offset, seq) in self.sequences:
            if not isinstance(seq, FiniteSequence):
                raise Exception("Only FiniteSequence(s) are supported for midi file output")
            midifile.addTrackName(track_no - 1, offset, "Track {}".format(track_no))
            count = offset
            for event in seq.events:
                for cc, value in event.meta.get("cc", []):
                    midifile.addControllerEvent(track_no - 1, 0, count, cc, value)
                for pitch in event.pitches:
                    try:
                        dynamic = event.meta["dynamic"]
                    except KeyError:
                        dynamic = 100
                    midifile.addNote(track_no - 1, 0, pitch, count, event.duration, dynamic)
                count = count + event.duration
        with open(filename, 'wb') as outf:
            midifile.writeFile(outf)
        return self
