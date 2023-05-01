"""
Use the built-in init_reloader() to enable hot reloading of python files.
Assumes:
    file is adjacent to this main file (no recursive dirs)
    file defines a Sequence with the same name as the module

(try updating the definition of track1 in track1.py).
Provides an interesting POC as to how to improve the on-the-fly workflow.
"""

from composerstoolkit import *

from track1 import track1

init_reloader()

mysequencer = Sequencer(bpm=120, debug=True)\
    .add_sequence(track1)
    
mysequencer.playback()
