import logging
from typing import Tuple, Iterator, List, Callable
from threading import Thread
from time import sleep, time
from queue import PriorityQueue, Queue, Empty
from typing import Union
import traceback

from . synth import Playback
from . sequence import Sequence, FiniteSequence, Event
from . pitch_tracker import PitchTracker

class Scheduler(Thread):
    """
    Maintains a single thread for scheduling playback of sound events across multiple tracks.
    It can be run in two evaluation modes:
     - ahead of time (default) - the next note for each track is calculated and enqeued on the
     main thread. This means that the scheduler is soley responsible for playback.
     - just in time (jit=True), this is used where transformers are being used that rely upon the
     realtime context (ie active pitches), and requires musical events to be evaluted on the playback thread.
     The scheduler will try to compensate for latency, but might result in glitches if the tempo/density is too rapid.
    Usage:
        The evaluation thread (sequencer) should call Scheduler.enqueue(track_no, seq) for each seq.
        the schedular object is an iterator, which yields (track_no, seq, offset) each time we are
        ready to evaluate the next item for each track
    """

    def __init__(self, queue_size=0, time_scale_factor=1, jit=False, pitch_tracker=PitchTracker()):
        super().__init__()
        self.is_running = True
        # playback queue
        self._pq = PriorityQueue(maxsize=queue_size)
        # eval queue
        self._eq = Queue()
        self.observers = [pitch_tracker]
        self.playback_started_ts = None
        self.time_scale_factor = time_scale_factor
        self.time_elapsed = 0
        self.jit = jit

    @property
    def has_events(self):
        return self._pq.qsize() > 0 and self.is_running

    def subscribe(self, observer: Playback):
        self.observers.append(observer)

    def __iter__(self):
        """Returns an iterator that yields track_no, seq, offset each time we are ready to
        evaluate the next item from each track"""
        def f():
            if self.jit:
                return []
            while True:
                offset, work_item = self._eq.get()
                track_no, seq = work_item
                yield track_no, seq, offset
        return f()

    def _get_next_event(self, seq: Union[Sequence, FiniteSequence]) -> Event:
        try:
            if isinstance(seq, Sequence):
                event = next(seq.events)
            elif isinstance(seq, FiniteSequence):
                event = seq.events.pop()
            else:
                logging.getLogger().error(f"{seq} is not a Sequence or FiniteSequence")
                return None
            return event
        except (StopIteration, IndexError) as e:
            return None

    def enqueue(self, track_no: int, sequence: Sequence, offset_secs=0) -> bool:
        """
        Grab the next event off the sequence and enqueue it for playback if it is in the future.
        If a noteon/cc event needs to be actioned immediately, route it directly to the observers.
        return True if enqueued, False if no more events.
        Queue.Full might be raised  - in which case you need to set a higher queue_size in the constructor
        """
        event = self._get_next_event(sequence)
        if event is None:
            logging.getLogger().info(f"Scheduler playback for track {track_no} has ended")
            return False
        logging.getLogger().info(f"Scheduler track {track_no} new event {event} at {offset_secs}")
        future_time = offset_secs + (event.duration * self.time_scale_factor)
        for cc, value in event.meta.get("cc", []):
            if self.time_elapsed >= offset_secs:
                # if an event needs to happen immediately, bypass the queue
                self._on_event(("cc", track_no, cc, value))
                continue
            self._pq.put_nowait((offset_secs, ("cc", track_no, cc, value)))
        for pitch in event.pitches:
            volume = event.meta.get("volume", 60)
            if event.meta.get("realtime", None) != "note_off":
                if self.time_elapsed >= offset_secs or event.meta.get("realtime", None) == "note_on":
                    # if an event needs to happen immediately, bypass the queue
                    self._on_event(("note_on", track_no, pitch, volume))
                else:
                    self._pq.put_nowait((offset_secs, ("note_on", track_no, pitch, volume)))
            if event.meta.get("realtime", None) != "note_on":
                if event.meta.get("realtime", None) == "note_off":
                    self._on_event(("note_off", track_no, pitch))
                else:
                    self._pq.put_nowait((future_time, ("note_off", track_no, pitch)))
        self._pq.put_nowait((future_time, ("eval", track_no, sequence)))
        logging.getLogger().debug(f"Scheduler queued event {event} at time {offset_secs}")
        return True

    def run(self):
        try:
            self._main_event_loop()
        except:
            traceback.print_exc()
            self.is_running = False

    def _main_event_loop(self):
        """Pull chronological items off the playback queue, and wait until their
        scheduled time before sending them to the playback observers"""
        logging.getLogger().info("Scheduler starting main event loop.")
        self.playback_started_ts = time()
        self.time_elapsed = 0
        while self.is_running:
            cur_time = time()
            try:
                time_pos, event = self._pq.get_nowait()
            except Empty:
                continue
            logging.getLogger().debug(f"Main event loop, at time {self.time_elapsed}")
            latency = (cur_time-self.playback_started_ts) - self.time_elapsed
            if latency > 0:
                logging.getLogger().info(f"Scheduler latency {abs(latency)}")
            if event[0] == "eval" and not self.jit:
                # "eval" items are used to signal back to pull the next event for each track
                _, track_no, seq = event
                # if jit==False, evaluation tasks are queued for execution on the main thread
                self._eq.put((time_pos, (track_no, seq)))
                continue
            if time_pos > self.time_elapsed:
                wait_time = (time_pos - self.time_elapsed) - latency
                logging.getLogger().debug(f"Scheduler event loop sleeping for {wait_time} secs")
                if wait_time > 0:
                    sleep(wait_time) # block until event is ready to be actioned
                self.time_elapsed = time_pos
            if event[0] == "eval" and self.jit:
                # in JIT mode, next-note-evaluation happens on the scheduler thread
                # This is important if transformations need access to the context, but may
                # result in glitches if the scheduler cannot keep up
                _, track_no, seq = event
                self.enqueue(track_no, seq, time_pos)
                continue
            self._on_event(event)
        self.is_running = False
        logging.getLogger().info("Scheduler exited main event loop.")


    def _on_event(self, event):
        logging.getLogger().debug(f"Scheduler pushing to event observers {event}")
        for observer in self.observers:
            if event[0] == "note_on":
                _, track_no, pitch, velocity = event
                observer.noteon(track_no, pitch, velocity)
            elif event[0] == "note_off":
                _, track_no, pitch = event
                observer.noteoff(track_no, pitch)
            elif event[0] == "cc":
                _, track_no, cc, value = event
                observer.control_change(track_no, cc, value)
