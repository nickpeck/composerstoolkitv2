import logging
from typing import Tuple, Iterator, List, Callable
from threading import Lock, Thread
from time import sleep

from  . synth import Playback

class Scheduler(Thread):

    def __init__(self, buffer_secs=1):
        super().__init__()
        self.is_running = True
        self._lock = Lock()
        self._events = {}
        self.lock_timeout = 1
        self.observers = []
        self.buffer_secs = buffer_secs

        def _iter():
            offset = 0
            def f() -> Iterator[Tuple[int, Tuple]]:
                self._lock.acquire(timeout=self.lock_timeout)
                if self._events == {}:
                    raise StopIteration
                next_slot = list(filter(lambda t: t >= offset, self._events.keys()))[0]
                item = self._events[next_slot].pop(0)
                if self._events[next_slot] == []:
                    del self._events[next_slot]
                self._lock.release()
                return next_slot, item
            return f
        self._it = _iter()

    def subscribe(self, observer: Playback):
        self.observers.append(observer)

    def add_event(self, offset_secs: float, event: Tuple):
        self._lock.acquire(timeout=self.lock_timeout)
        try:
            self._events[offset_secs].append(event)
        except KeyError:
            self._events[offset_secs] = [event]
        finally:
            self._lock.release()

    def run(self):
        self._main_event_loop()

    def _main_event_loop(self):
        sleep(self.buffer_secs)
        logging.getLogger().debug("Scheduler starting main event loop.")
        time_elapsed = 0
        while self.is_running:
            try:
                time, next_event = self._it()
            except StopIteration:
                logging.getLogger().debug("Scheduler no more events.")
                return
            wait_time = time - time_elapsed
            logging.getLogger().debug(f"Scheduler event loop sleeping for {wait_time} secs")
            if wait_time >= 0:
                sleep(wait_time)
            else:
                logging.getLogger().debug(f"Scheduler latency : {wait_time} secs")
            self.on_event(next_event)
            time_elapsed = time_elapsed + wait_time

    def on_event(self, event):
        logging.getLogger().debug(f"Scheduler pushing to event observers {event}")
        for observer in self.observers:
            if event[0] == "note_on":
                _, channel_no, pitch, velocity = event
                observer.noteon(channel_no, pitch, velocity)
            if event[0] == "note_off":
                _, channel_no, pitch = event
                observer.noteoff(channel_no, pitch)
            if event[0] == "cc":
                _, channel_no, cc, value = event
                observer.control_change(channel_no, cc, value)
