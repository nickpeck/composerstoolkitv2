import unittest

from composerstoolkit import *

PitchFactory = pitches.PitchFactory

class TestPitchFactory(unittest.TestCase):
    def test_pitch_factory_returns_midi_pitch_nos_from_note_names(self):
        pitch = PitchFactory()
        assert pitch("A4") == 69
        assert pitch("A#4") == 70
        assert pitch("Bb4") == 70
        assert pitch("G9") == 127
        assert pitch("C-1") == 0

    def test_pitch_factory_can_return_frequencies(self):
        pitch = PitchFactory(output="hz")
        assert pitch("A4") == 440
        assert pitch("A#4") == 466.16
        assert pitch("Bb4") == 466.16
        assert pitch("G9") == 12543.85
        assert pitch("C-1") == 8.18

    def test_pitch_factory_can_convert_midi_nos_to_names(self):
        pitch = PitchFactory(output="name")
        assert pitch(69) == "A4"
        assert pitch(70) == "A#4"
        assert pitch(127) == "G9"
        assert pitch(0) == "C-1"

ChordBuilder = chords.ChordBuilder

class TestChordBuilder(unittest.TestCase):
    def test_major_triad(self):
        cb = ChordBuilder()
        assert cb("C").pitches == [0,4,7]

    def test_can_specify_the_octave(self):
        cb = ChordBuilder(octave=5)
        assert cb("C").pitches == [60,64,67]

    def test_major_triad(self):
        cb = ChordBuilder()
        assert cb("Csus").pitches == [0,5,7]

    def test_min_triad(self):
        cb = ChordBuilder()
        assert cb("Cmin").pitches == [0,3,7]

    def test_dim_triad(self):
        cb = ChordBuilder()
        assert cb("Cdim").pitches == [0,3,6]

    def test_aug_triad(self):
        cb = ChordBuilder()
        assert cb("Caug").pitches == [0,4,8]

    def test_added_6th_chord(self):
        cb = ChordBuilder()
        assert cb("C6").pitches == [0,4,7,8]

    def test_7th_chords(self):
        cb = ChordBuilder()
        assert cb("C7").pitches == [0,4,7,10]
        assert cb("Cmin7").pitches == [0,3,7,10]
        assert cb("Cmaj7").pitches == [0,4,7,11]
        assert cb("Cmin7b5").pitches == [0,3,6,10]
        assert cb("Cdim7").pitches == [0,3,6,9]

    def test_9th_chords(self):
        cb = ChordBuilder()
        assert cb("C9").pitches == [0,4,7,10,14]
        assert cb("Cmin9").pitches == [0,3,7,10,14]
        assert cb("Cmaj9").pitches == [0,4,7,11,14]
        assert cb("Cmin9b5").pitches == [0,3,6,10,14]
        assert cb("C7b9").pitches == [0,4,7,10,13]

    def test_11th_chords(self):
        cb = ChordBuilder()
        assert cb("C11").pitches == [0,4,7,10,14,17]
        assert cb("Csus11").pitches == [0,5,7,10,14,17]
        assert cb("Cmin11").pitches == [0,3,7,10,14,17]
        assert cb("Cmaj9#11").pitches == [0,4,7,11,14,18]
        assert cb("Cmin11b5").pitches == [0,3,6,10,14,17]

    def test_13th_chords(self):
        cb = ChordBuilder()
        assert cb("C13").pitches == [0,4,7,10,14,21]
        assert cb("Csus13").pitches == [0,5,7,10,14,21]
        assert cb("Cmin13").pitches == [0,3,7,10,14,17,21]

    def test_alterations(self):
        cb = ChordBuilder()
        assert cb("C13b9").pitches == [0,4,7,10,13,21]
        assert cb("C7#9").pitches == [0,4,7,10,15]
        assert cb("C13b9#11").pitches == [0,4,7,10,13,18,21]
        assert cb("C7b9b13").pitches == [0,4,7,10,13,20]
        assert cb("C7#9b13").pitches == [0,4,7,10,15,20]
        assert cb("Csus7b9").pitches == [0,5,7,10,13]

    def test_slash_notation(self):
        cb = ChordBuilder()
        assert cb("C/G").pitches == [7,12,16,19]

if __name__ == "__main__":
    unittest.main()
