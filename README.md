# Composers Toolkit (V2)

This package contains a suite of tools and experiments towards the goal of discovering how technology might play a supporting role in assisting and enriching the process of musical composition - (specifically, in terms of what that means to me on an artistic and aesthetic level). As far as possible, they are agnostic with respect to any one given approach, culture, theory, or style, and it is up to the end-user to define the parameters specific to their intended outcome (keys, chords, structures, rows, cycles etc.). It deals with manipulating discrete note events (such as represented by MIDI) rather than pure sound synthesis. Some of the techniques may be familiar to Schillinger composition students, however in many cases I have adopted my own approaches to these transformations.

A brief overview of the features I am working towards:
- Ability to freely declare events, sequences of events and playback containers to which multiple sequences can be added, thus enabling polyphonic playback using a synth library, DAW or external MIDI device. Examples can be saved or loaded in from MIDI files.
- Ability to quickly generate raw materials and permutations thereof (i.e., permutations of a note row, rhythmic cycle, pitches or chords within a given scale or tonal axis).
- Infinite or finite-length sequences of events can be generated using algorithmic techniques. Different transformations and operations can be applied to these sequences. Transformations can be controlled using ‘higher-order’ transformations that enable gating, looping, or batching in response to external logic.
- Ability to perform statistical analysis of an existing work, to extract key musical motives, patterns and sequences using data-mining techniques.
- Different algorithmic processes that provide a complete compositional output, driven by user-defined constraints, or heuristics discovered through analysis of an existing corpus of works.
- Investigation of biologically inspired and deep-learning techniques and how these might be trained using the previously mentioned analytical processes, and then guided using interaction with the end-user.


## Quickstart

~~~
git clone https://github.com/nickpeck/composerstoolkitv2.git
cd composerstoolkitv2
python3 -m venv .
source bin/activate
export PYTHONPATH=${PYTHONPATH}:path_to_src_folder
python examples/1_random_slicing.py
~~~

By default you won't get any sound because it'll be using 'DummyPlayback' (a synth interface that simply logs events).
To use an existing local MIDI interface, or RTP MIDI interface, create a file such as this in your current working directory. 

~~~
# MySynth.py
from composerstoolkit import RTPMidi

class LocalSynth(RTPMidi):

    # change this to the name of your interface
    def __init__(self, get_port = lambda port_names: port_names.index("name of your MIDI interface ...")):
        super().__init__(get_port)
~~~

To get a list of possible interface names, you can run:

~~~
python -c "import rtmidi;print(rtmidi.MidiOut().get_ports())"
~~~

Then, run the following: 
~~~
export DEFAULT_SYNTH=MySynth.LocalSynth
~~~

You can now run the examples and you should get playback on the configured interface.
(n.b. on Windows, it is a known issue that the default WINDOWS_MM api blocks rtmidi calls until each message is sent. This causes
playbac to drift out of sync - try using a different interface or Linux/Mac over a RTP Midi network configuration for the best results).


Practical examples are given in the examples directory.

### Events, Sequences and Sequencers
The basic atomic unit of structure is the Event class. An event holds 0...* pitches that might sound together as a chord or single note.

~~~
from composerstoolkit import *

# pitches is a list of midi pitch numbers (0-127). Duration is a number (ie number of beats).
Event(pitches=[48], duration=1)

# no pitches implies a musical rest
Event(duration=1)

# there are constants for durations,
Event(duration=QUARTER_NOTE)
Event(duration=DOTTED(QUARTER_NOTE) + WHOLE_NOTE)

# The built-in pitchfactory class is very useful if you would rather use letter notation

pf = pitches.PitchFactory()
Event(pitches=[pf("C6")], duration=QUARTER_NOTE)
~~~

Sequences are chains of events, analogous to a single ‘part’ or ‘voice’ in western musical parlance. There are two forms, Sequence is used for sequences of unknown or infinite length. FiniteSequence, however, is used for sequences of a fixed length.

~~~
from composerstoolkit import *

seq = Sequence(
    events=[
        Event(pitches=[48], duration=QUARTER_NOTE),
        Event(pitches=[43], duration=QUARTER_NOTE),
        Event(pitches=[45], duration=QUARTER_NOTE),
        Event(pitches=[41], duration=QUARTER_NOTE)])

fin_seq = FiniteSequence(
    events=[
        Event(pitches=[48], duration=QUARTER_NOTE),
        Event(pitches=[43], duration=QUARTER_NOTE),
        Event(pitches=[45], duration=QUARTER_NOTE),
        Event(pitches=[41], duration=QUARTER_NOTE)])

# you can covert from one to another:
seq.bake() # evalutes the whole sequence - be careful you are not trying to evaluate an infinate sequence!

# and vice-versa
fin_seq.to_sequence()
~~~

Implementation-wise, the difference is that Sequences makes use of lazy-evaluated sequences (generators), and are useful for live applications & algorithmic music generation. FiniteSequence does not, and is useful for operations where we need to perform list-style operations upon it, for example:

~~~
# it behaves like a list:
fin_seq[0]
... FiniteSequence(events=[Event(pitches=[48], duration=QUARTER_NOTE)])

fin_seq.time_slice(0, 2)
... FiniteSequence(events=[Event(pitches=[48], duration=QUARTER_NOTE), Event(pitches=[43], duration=QUARTER_NOTE)])
~~~

### Sequencers
Sequencers are analogous to a MIDI sequencer, and allow us to cue multiple sequences together for playback on a given engine. By default, we use composerstoolkit.core.synth.DummyPlayback (which just logs the noteon/noteoff events), but we could save to MIDI, send to a MIDI device, or write our own playback engine that implements composerstoolkit.core.synth.Playback

~~~
Context.get_context().new_sequencer(bpm=240, playback_rate=1)\
    .add_sequence(seq)\
    .add_sequence(fin_seq, offset=10)\
    .playback()
~~~

If you want to define a synth engine to be used globally, then set the environment variable DEFAULT_SYNTH to the python import path of your synth class. eg to import class Synth from module MySynth:

~~~
$export DEFAULT_SYNTH=MySynth.Synth
~~~

If you have Lilypond installed on your system, you can generate basic notation output from your container. (Note, only FiniteSequences are supported and the system does not currently handle tuplet durations).

~~~
Context.get_context().new_sequencer(bpm=240, playback_rate=1)\
    .add_sequence(fin_seq)\
    .show_notation()
~~~

### Generators
In Schillinger-parlance, generators are use to produce sequences using simple algorithmic techniques. The following generates a ‘resultant’ scale using the intervals derived form the collision pattern of repeating intervals 3,4,9:

~~~
artificial_scale = Sequence.from_generator(
    resultant_pitches(counters=[3,4,9], start_at=40))
~~~

Of course, a strength that the computer provides is pseudo-random choices and generators. Here is a built in generator that spits out random length slices from a short sequence:
~~~
seq_upper = Sequence.from_generator(random_slice(
    Sequence(events=[
        Event(duration=QUARTER_NOTE),
        Event(duration=HALF_NOTE),
        Event(duration=DOTTED(HALF_NOTE)),
        Event(duration=WHOLE_NOTE),
    ])
))
~~~

### Transformations

We can chain together multiple transformational operations onto a sequence. Skillful application of multiple transformations can be very effect towards creating more complex, engaging forms from simple, repetitive source material:

~~~
melody = Sequence.from_generator(
    axis_melody(
        axis_pitch = pf("C6"),
        scale = scales.C_mel_minor,
        max_steps = 14,
        direction="contract"
)).transform(map_to_pulses(
     Sequence.from_generator(collision_pattern(4,5)).transform(loop())
)).transform(fit_to_range(
    min_pitch = pf("G5"),
    max_pitch = pf("C7")
)).transform(rhythmic_augmentation(
    multiplier = 2
)).transform(loop(
))
~~~

In addition, there are several 'higher-order' transformations that control the application of different transformations.
~~~
# 'gated' transformer uses user-defined logic to control the application of a transformer
# 'batch' allows us to apply multiple transformations at once (some of which my be additional 'higher-order' transformations).

def my_gate1(context):
    return context.beat_offset % 5 == 0

seq = Sequence(events=[
        Event(pitches=[60], duration=QUARTER_NOTE),
    ]).transform(loop())\
    .transform(
        gated(
            rhythmic_augmentation(2),
            my_gate2))\
    .transform(
        gated(
            batch([
                transpose(12),
                rhythmic_diminution(0.5)])
          , my_gate2))
~~~

This creates interesting potential for evolving musicial material that changes state according to external input, or logic.

### Next Steps

See the examples folder for more advanced applications, in particular 'Solvers' (which compose according to a given set of constraints or heuristics), and tools for performing analytical and inferential work on existing material.
