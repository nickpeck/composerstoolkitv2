"""Convenience class for specifying pitches
Returns a callable that allows for
translation to between name, MIDI pitch number, and frequency.

Usage:
pitch = PitchFactory()
pitch("A4")
... 69

pitch = PitchFactory(output="name")
pitch(69)
... "A4"

pitch = PitchFactory(output="hz")
pitch(69)
... 440.00
"""
import math
import re

class PitchFactory:
    notes = {
        "C" : 0,
        "D" : 2,
        "E" : 4,
        "F" : 5,
        "G" : 7,
        "A" : 9,
        "B" : 11
    }

    def __init__(self, **kwargs):
        """Constructor for PitchFactory
        summary of optional kwargs:
        output - either midi_no, hz or name (default midi_no)
        a4_freq - base frequency to which A4 is tuned
        schema - the note naming schema, defaults to '{name}{octave}'
        to_freq - function that converts the midi note number to a freq,
        defaults to equal temperament.
        """
        self.opts = {
            "output": "midi_no", # midi_no, hz, lilypond or name
            "a4_freq": 440,
            "schema": re.compile("^([A-G])([#b]?)([+-]?[0-9])$"),
            "to_freq": self._midi_no_to_hz
        }
        self.opts.update(kwargs)

    def _midi_no_to_hz(self, i: int):
        a4_freq = self.opts["a4_freq"]
        freq_float = a4_freq * math.pow(2, (i - 69) / 12.0)
        return round(freq_float, 2)

    def _midi_no_to_name(self, i: int):
        octave = int(i / 12) - 1
        if self.opts["output"] == "lilypond":
            if i >= 60:
                octave = "'" * (round((i-60) /  12))
            else:
                octave = "," * (round((60-i) /  12))
        remainder = i % 12
        _notes = {pitch: name for name, pitch in self.__class__.notes.items()}
        accidental = ""
        try:
            note = _notes[remainder]
        except KeyError:
            note = _notes[remainder - 1]
            if self.opts["output"] == "lilypond":
                accidental = "s"
            else:
                accidental = "#"
        if self.opts["output"] == "lilypond":
            note = note.lower()
        return "{}{}{}".format(note,accidental,octave)

    def _name_to_midi_no(self, name: str):
        match = self.opts["schema"].match(name)
        if match is None:
            raise NameError(
                "'{}' is not a recognised pitch".format(name))
        note, accidental, octave = match.groups()
        # nb midi octaves begin at -1
        octave = int(octave) + 1
        note = self.__class__.notes[note.upper()]
        if accidental is not None:
            if accidental == "#":
                note = note + 1
            elif accidental == "b":
                note = note -1
        midi_note_no = (octave * 12) + note
        return midi_note_no

    def __call__(self, *args):
        arg = args[0]
        if isinstance(arg, str):
            midi_note_no = self._name_to_midi_no(arg)
        elif isinstance(arg, int):
            midi_note_no = arg
        else:
            raise TypeError(
                "arg[0] should be a str or int, got: {}".format(type(name)))
        if self.opts["output"] == "midi_no":
            return midi_note_no
        if self.opts["output"] == "hz":
            return self.opts["to_freq"](midi_note_no)
        if self.opts["output"] in ["name", "lilypond"]:
            return self._midi_no_to_name(midi_note_no)
