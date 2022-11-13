"""
Takes a steady stream of middle C s and illustrates how to
create a more varied texture by higher order transformations.

'Gates' allow us to control when a transformation is applied,
using a controller function.

'Batches' allow us to group multiple transformations.

Both of these act as transformers in themselves, so can be
chained ad infinitum.

uses 'keyboard' (pip install keyboard)
"""
import keyboard
from composerstoolkit import *

class MyListener:
    def __init__(self):
        # .keyboard.is_pressed blocks in this context so have to implement this the long way
        self.a_pressed = False
        self.b_pressed = False
        keyboard.add_hotkey('a', lambda: self.toggle_a(True))
        keyboard.on_release_key('a', lambda x: self.toggle_a(False))
        keyboard.add_hotkey('b', lambda: self.toggle_b(True))
        keyboard.on_release_key('b', lambda x: self.toggle_b(False))
        keyboard.add_hotkey('a+b', lambda: self.toggle_a(True) and self.toggle_b(True))
        keyboard.add_hotkey('b+a', lambda: self.toggle_a(True) and self.toggle_b(True))
        
    def toggle_a(self, v):
        self.a_pressed = v
        
    def toggle_b(self, v):
        self.b_pressed = v

listener = MyListener()


def my_gate1(context):
    return listener.a_pressed   
    # or the gate can be triggered by the musical context:
    #return context.beat_offset % 5 == 0

def my_gate2(context):
    return listener.b_pressed

seq = Sequence(events=[
        Event(pitches=[60], duration=QUARTER_NOTE),
    ]).transform(loop())\
    .transform(
        gated(
            rhythmic_augmentation(2),
            my_gate1))\
    .transform(
        gated(
            batch([
                transpose(12),
                rhythmic_diminution(0.5)])
          , my_gate2))

Container(bpm=240, playback_rate=1)\
    .add_sequence(seq)\
    .playback()
