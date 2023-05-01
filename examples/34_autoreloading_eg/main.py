import sys
import time
import logging
import os

from importlib import reload

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from composerstoolkit import *

from track1 import track1

print(sys.modules['track1'])

init_reloader()

mysequencer = Sequencer(bpm=120, debug=True)\
    .add_sequence(track1)
    
mysequencer.playback()
