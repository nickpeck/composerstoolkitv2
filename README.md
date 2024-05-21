# Composers Toolkit (V2)

This package contains a suite of tools and experiments towards discovering how technology might play a supporting role in assisting and enriching the process of musical composition - (specifically, in terms of what that means to me on an artistic and aesthetic level). The use of partially algorithmic processes alongside freely composed material is nothing new, and examples abound in the historical and contemporary musical traditions of both East and West.

It deals with manipulating discrete note and controller events (as represented by MIDI) rather than pure sound synthesis and is intended to serve as the back-end for external sound synthesis via MIDI, or generating MIDI output that can then be imported into external score notation software. It does not currently use live or stored digital sound data (ie WAV) as in input source. It is possible to use thee tools manipulate sound modification parameters as part of the musical structure (using controller events). Some of the techniques may be familiar to Schillinger practitioners or users of Max/OpenMusic/Ableton, however in many cases I have adopted my own approaches to these transformations. I enjoy to taking 'longer road' of developing my own tools and building a more personal connection with the results.

This project is primarily geared towards serving the needs of my own shifting artistic and research goals, rather than something I would want to promote for general consumption. Composition is for me, usually a solitary pursuite, and code is being used as 'craft' that serves a purpose (not an art in itself). With that in mind, occasionally best technical practices may have been overlooked in order to serve the chaotic and sometimes exploratory whims of artistic inspiration.

The ordered experiments in the 'examples' folder serve as a document of the approaches and ideas I have investigated. Some of the outputs of this have found their way into my actual music-making - often interwoven with, or serving as the initial seed for material that I have then developed using more traditional means.

As far as possible, it is agnostic with respect to any one given approach, culture, theory, or style, popular or art-music and it is up to the end-user to define the parameters specific to their intended outcome (keys, chords, structures, rows, cycles etc.). However, given the current scope of MIDI, it is currently limited to the Western 12-EDO pitch system.

Broadly speaking, the techniques I have use so far fall into these categories:
- Generating real-time or ahead-of-time music, using randomized or predetermined transformations of various input materials. These transformations might be toggled or modulated as a function of time, or of the real time 'context' (i.e. which notes are actually being sounded at the present time).
- Ability to capture live MIDI input, either for control purposes, or as a source of musical material that might be stored and manipulated.
- Using basic machine-learning techniques such as tree-search, evolutionary or constraint logic programming techniques to compose music according a predetermined set of criteria.
- Generating a corpus of material (ie all possibilities of a given chord/scale relationship or musical pattern) or temporal structures that might serve as reference material for a future composition.
- Analyzing an existing corpus of works for specific musical patterns, structures or statistical data that might then serve to drive further composition.

## Package structure:
- analysis: Tools for analyzing an existing corpus of music.
- builders: Tools for creating music using algorithmic processes. Specifically 'generators' which create musical materials and 'transformers' which modify them. The framework allows for lazy (real-time) evaluation.
- composers: Tools for generating music using machine learning techniques.
- core: Basic framework for organizing music into events, sequences of events, sequencers (which group multiple sequences), creating rudimentary notation, MIDI files and the scheduler (which enables real-time playback via any MIDI interfaces or external synths). It should be possible to create an interface to any sound synthesis engine that supports note on/off and cc-style data.
- resources: convenience methods and definitions of common western musical patterns (scales, durations, chords, pitches).

## Quickstart

~~~
git clone https://github.com/nickpeck/composerstoolkitv2.git
cd composerstoolkitv2
python3 -m venv .
source bin/activate
pip install -r requirements.txt
python setup.py develop
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
playback to drift out of sync - try using a different interface or Linux/Mac over a RTP Midi network configuration for the best results).


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

Implementation-wise, the difference is that Sequences makes use of lazy-evaluation (generators), and are useful for live applications & algorithmic music generation. FiniteSequence does not, and is useful for operations where we need to perform list-style operations upon it, for example:

~~~
# it behaves like a list:
fin_seq[0]
... FiniteSequence(events=[Event(pitches=[48], duration=QUARTER_NOTE)])

fin_seq.time_slice(0, 2)
... FiniteSequence(events=[Event(pitches=[48], duration=QUARTER_NOTE), Event(pitches=[43], duration=QUARTER_NOTE)])
~~~

### Sequencer
The Sequencer is analogous to a MIDI sequencer, and allow us to cue multiple sequences together for playback on a given engine. By default, we use composerstoolkit.core.synth.DummyPlayback (which just logs the noteon/noteoff events), but we could save to MIDI, send to a MIDI device, or write our own playback engine that implements composerstoolkit.core.synth.Playback

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

If you have Lilypond installed on your system, you can generate rough-and-ready notation output from your container. (Note, only FiniteSequences are supported and the system does not currently handle tuplet durations).

~~~
Context.get_context().new_sequencer(bpm=240, playback_rate=1)\
    .add_sequence(fin_seq)\
    .show_notation()
~~~

You can, alternatively export to midi and import into a DAW/notation software of your choice.

~~~
Context.get_context().new_sequencer(bpm=240, playback_rate=1)\
    .add_sequence(fin_seq)\
    .save_as_midi_file("output.midi")
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

A sequence can be used is various ways to drive the input of another sequence, leading to complex 'signal-chains' that feed into each other.

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
