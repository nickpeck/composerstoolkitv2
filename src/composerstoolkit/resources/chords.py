"""Library of common chord types
"""
import re
from typing import Iterator, Set

from .scales import CHROMATIC_SCALE_PITCH_CLASSES
from ..core import Event

class ChordBuilder:
    """Helper class for constructing stock chord voicings
    from jazz/pop chord notation.

    usage:
    cb = ChordBuilder()
    cb("Cmaj7")
    ... Event(pitches=[0,4,7,11], duration=0)
    """
    notes = {
        "C" : 0,
        "D" : 2,
        "E" : 4,
        "F" : 5,
        "G" : 7,
        "A" : 9,
        "B" : 11
    }

    def __init__(self, octave=0):
        """Constructor for the chord builder.
        octave - the octave the root of the chord
        should be placed in.
        """
        self.schema = re.compile(
            "^([A-G])(maj|min|minmaj|dim|sus|aug)?([1-9]*)"\
            +"(aug[1-9]*|b[1-9]*|#[1-9]*)?"\
            +"(aug[1-9]*|b[1-9]*|#[1-9]*)?"\
            +"(\/[A-G])?$",
            flags=re.DOTALL|re.MULTILINE|re.IGNORECASE)
        self.octave = octave

    def __call__(self, *args):
        """Return a zero-length event,
        or None if the chord name cannot be parsed.
        """
        name = args[0]
        name = name.replace(" ", "")

        match = self.schema.match(name)
        if match is None:
            return None
        groups = match.groups()

        root = groups[0]
        base_quality = groups[1]
        first_ext = groups[2]
        second_ext = groups[3]
        third_ext = groups[4]
        slash_root = groups[5]

        pitches = []
        root_pitch = ChordBuilder.notes[root]
        root_pitch = root_pitch + (12 * self.octave)
        pitches.append(root_pitch)

        # todo refactor this mess!
        if base_quality is None:
            pitches.append(root_pitch+ 4) # maj3
            pitches.append(root_pitch+ 7) # 5th
        if base_quality is not None:
            if base_quality == "min":
                pitches.append(root_pitch+ 3) # min3
                pitches.append(root_pitch+ 7) # 5th
            if base_quality == "maj":
                pitches.append(root_pitch+ 4) # 3rd
                pitches.append(root_pitch+ 7) # 5th
            if base_quality == "dim":
                pitches.append(root_pitch+ 3) # min3
                pitches.append(root_pitch+ 6) # 5th
            if base_quality == "sus":
                pitches.append(root_pitch+ 5) # 4th
                pitches.append(root_pitch+ 7) # 5th
            if base_quality == "aug":
                pitches.append(root_pitch+ 4) # maj3th
                pitches.append(root_pitch+ 8) # aug5th
        if first_ext is not None:
            if first_ext == "6":
                pitches.append(root_pitch+ 8)
            if first_ext in ["7", "9", "11", "13"]:
                # determine the 7th
                if base_quality in ["min", "sus", "aug"]:
                    pitches.append(root_pitch+ 10) # b 7th
                if base_quality is None:
                    pitches.append(root_pitch+ 10) # b 7th
                if base_quality == "dim":
                    pitches.append(root_pitch+ 9)
                if base_quality in ["minmaj", "maj"]:
                    pitches.append(root_pitch+ 11) # ^7th
            if first_ext == "9":
                pitches.append(root_pitch+ 14) # 9th
            if first_ext == "11":
                pitches.append(root_pitch+ 14) # 11th
                pitches.append(root_pitch+ 17) # 11th
            if first_ext == "13":
                pitches.append(root_pitch+ 14) # 9th
                pitches.append(root_pitch+ 21) # 13th
                if base_quality == "min":
                    pitches.append(root_pitch+ 17)
            if second_ext is not None:
                if second_ext.startswith("b"):
                    digit = int(second_ext.split("b")[1])
                    if digit == 5:
                        pitches.append(root_pitch+ 6) # b5th
                        # the perfect 5th is usually removed in this case
                        pitches.remove(root_pitch + 7)
                    if digit == 6:
                        pitches.append(root_pitch+ 8) # b6 aeolean
                        # the perfect 5th is usually removed in this case
                        pitches.remove(root_pitch + 7)
                    if digit == 9:
                        pitches.append(root_pitch+ 13) # b9th
                        if (root_pitch + 14) in pitches:
                            pitches.remove(root_pitch + 14)
                    if digit == 13:
                        pitches.append(root_pitch+ 20) # b13th
                if second_ext.startswith("#"):
                    digit = int(second_ext.split("#")[1])
                    if digit == 9:
                        pitches.append(root_pitch+ 15) # #9th
                    if digit == 11:
                        pitches.append(root_pitch+ 18) # b11th
            if third_ext is not None:
                if third_ext.startswith("b"):
                    digit = int(third_ext.split("b")[1])
                    if digit == 5:
                        pitches.append(root_pitch+ 6) # b5th
                        # the perfect 5th is usually removed in this case
                        pitches.remove(root_pitch + 7)
                    if digit == 6:
                        pitches.append(root_pitch+ 8) # b6 aeolean
                        # the perfect 5th is usually removed in this case
                        pitches.remove(root_pitch + 7)
                    if digit == 9:
                        pitches.append(root_pitch+ 13) # b9th
                        if (root_pitch + 14) in pitches:
                            pitches.remove(root_pitch + 14)
                    if digit == 13:
                        pitches.append(root_pitch+ 20) # b13th
                if third_ext.startswith("#"):
                    digit = int(third_ext.split("#")[1])
                    if digit == 9:
                        pitches.append(root_pitch+ 15) # #9th
                    if digit == 11:
                        pitches.append(root_pitch+ 18) # b11th
            if slash_root is not None:
                slash_root = slash_root.split("/")[1]
                pitches = [pitch + 12 for pitch in pitches]
                root = ChordBuilder.notes[slash_root]
                pitches.append(root)
        pitches = sorted(pitches)
        return Event(pitches)

def set_compliment(pcs: Set[int]):
    """Return the chromatic set compliment
    (ie the notes missing from the given set to
    provide a full chromatic series).
    """
    return CHROMATIC_SCALE_PITCH_CLASSES - pcs
