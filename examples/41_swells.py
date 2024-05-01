"""
Creates an ambient texture of three sustained chordal pads and uses param modulation to fade and pan them
in different phases.
"""

from composerstoolkit import *

cb = chords.ChordBuilder()

duration_secs = 3600

def set_volume_cc(event, value):
    event.meta["cc"] = [(7, int(value))]

def set_pan_cc(event, value):
    event.meta["cc"].append((10, int(value)))

def create_pad(chord, period, starting_deg):
    # each pad is a sustained note event followed by 'rest' events on each sec, to which we will map changing cc values.
    chord = cb(chord)
    chord.meta["cc"] = [(64,127)]
    pad = Sequence(events=[chord]) + Sequence(events=[Event([], 1)]).transform(loop(duration_secs))
    pad = pad.transform(transpose(12*4))\
        .transform(
            cyclic_modulation(
                period = period,
                starting_deg = starting_deg,
                modulator = set_volume_cc
            )
        )\
        .transform(
        cyclic_modulation(
            period=period * 1.5, # to add variety, pan is slightly out of phase with volume
            starting_deg=starting_deg,
            modulator=set_pan_cc
        )
    )
    return pad

# use of 3 closely related chords creates ambiguous shifting modal tonality
pad1 = create_pad("Emin13", period=60, starting_deg=270).transform(transpose(12))
pad2 = create_pad("Cmaj9", period=80, starting_deg=0)
pad3 = create_pad("Fmaj9/A", period=100, starting_deg=180).transform(transpose(-12))

sequencer = Sequencer(bpm=50, debug=True, dump_midi=True).add_sequences(pad1, pad2, pad3)
#sequencer.playback()
sequencer.save_as_midi_file("ambient.midi")