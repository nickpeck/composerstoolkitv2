import logging
from typing import Tuple, Iterator, List, Callable
from threading import Lock, Thread
from time import sleep
from queue import PriorityQueue

from  . synth import Playback

class Scheduler(Thread):

    def __init__(self, buffer_secs=1, queue_size=100):
        super().__init__()
        self.is_running = True
        self._lock = Lock()
        self._events = PriorityQueue(maxsize=queue_size)
        self.lock_timeout = 1
        self.observers = []
        self.buffer_secs = buffer_secs
        self.active_pitches = []

        def _iter():
            def f() -> Iterator[Tuple[int, Tuple]]:
                next_slot, event = self._events.get()
                return next_slot, event
            return f
        self._it = _iter()

    def subscribe(self, observer: Playback):
        self.observers.append(observer)

    def add_event(self, offset_secs: float, event: Tuple):
        self._events.put((offset_secs, event))
        logging.getLogger().debug(f"Scheduler queued event {event} at time {offset_secs}")

    def run(self):
        self._main_event_loop()

    def _main_event_loop(self):
        sleep(self.buffer_secs)
        logging.getLogger().info("Scheduler starting main event loop.")
        time_elapsed = 0
        while self.is_running:
            logging.getLogger().debug(f"Main event loop, at time {time_elapsed}")
            time_pos, event = self._it()
            if time_pos < time_elapsed:
                logging.getLogger().info(f"Scheduler latency {abs(time_pos - time_elapsed)}")
            if time_pos > time_elapsed:
                wait_time = time_pos - time_elapsed
                logging.getLogger().debug(f"Scheduler event loop sleeping for {wait_time} secs")
                sleep(wait_time)
                time_elapsed = time_pos
            self.on_event(event)
        logging.getLogger().info("Scheduler exited main event loop.")


    def on_event(self, event):
        logging.getLogger().debug(f"Scheduler pushing to event observers {event}")
        for observer in self.observers:
            if event[0] == "note_on":
                _, channel_no, pitch, velocity = event
                self.active_pitches.append((pitch, channel_no))
                observer.noteon(channel_no, pitch, velocity)
            elif event[0] == "note_off":
                _, channel_no, pitch = event
                observer.noteoff(channel_no, pitch)
                self.active_pitches.remove((pitch, channel_no))
            elif event[0] == "cc":
                _, channel_no, cc, value = event
                observer.control_change(channel_no, cc, value)
