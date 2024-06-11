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

    def test_pitch_lilypond_output(self):
        pitch = PitchFactory(output="abjad")
        assert pitch(69) == "a'"
        assert pitch(70) == "as'"
        assert pitch(127) == "g''''''"
        assert pitch(0) == "c,,,,"

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

class PitchClassSetTests(unittest.TestCase):

    def test_to_prime_form_empty_set(self):
        assert pitchset.to_prime_form(set()) == set()
    
    def test_to_prime_form_single_item(self):
        assert pitchset.to_prime_form({5}) == {0}

    def test_to_prime_form(self):
        assert pitchset.to_prime_form({0,4,6,7}) == {0,1,3,7}
        assert pitchset.to_prime_form({7,4,6,0}) == {0,1,3,7}
        assert pitchset.to_prime_form({2,6,8,9}) == {0,1,3,7}
        assert pitchset.to_prime_form({8,6,2,9}) == {0,1,3,7}
        assert pitchset.to_prime_form({60,62,63,68}) == {0,1,3,7}        
        assert pitchset.to_prime_form({0,1}) == {0,1}
        assert pitchset.to_prime_form({0,1,3,5,7}) == {0,1,3,5,7}
        assert pitchset.to_prime_form({0,1,3,5,7,10}) == {0,2,3,5,7,9}
        
    def test_to_prime_form_from_list(self):
        assert pitchset.to_prime_form([0,4,6,7]) == {0,1,3,7}

    def test_get_missing(self):
        assert list(pitchset.complete_set(pitches={0,1}, target_pcs={0,1,3,5,6,8,10})) == [{3,5,6,8,10}]
        assert list(pitchset.complete_set(pitches={3,4}, target_pcs={0,1,2,3})) == [{5,6}, {1,2}]
        assert list(pitchset.complete_set(pitches={0,5}, target_pcs={0, 1, 3, 5, 7, 8, 10}))\
            == [{1, 3, 7, 8, 10}, {1, 3, 6, 8, 10}, {2, 4, 7, 9, 11}]

class ForteSetTests(unittest.TestCase):
    def test_can_lookup_by_name(self):
        f_set = pitchset.ForteSet.as_dict()["4-z15"]
        assert f_set.prime == (0,1,4,6)

    def test_can_lookup_by_prime(self):
        f_set = pitchset.ForteSet.as_dict()[(0,1,4,6)]
        assert f_set.name == "4-z15"

    def test_can_lookup_by_vector(self):
        f_sets = pitchset.ForteSet.as_dict()[(1, 1, 1, 1, 1, 1)]
        assert len(f_sets) == 2

    def test_has_cardinality(self):
        f_set = pitchset.ForteSet.as_dict()["4-z15"]
        assert f_set.cardinality == 4

    # can now use the forte list to cross-check our helper functions:
    def test_to_interval_vectors(self):
        all_sets = pitchset.ForteSet.as_dict()
        for _,i in all_sets.items():
            if isinstance(i, list):
                continue
            assert pitchset.to_interval_vectors(i.prime) == list(i.vector)

    def test_to_prime_form(self):
        all_sets = pitchset.ForteSet.as_dict()
        for _,i in all_sets.items():
            if isinstance(i, list):
                continue
            # each of these should be identical
            assert pitchset.to_prime_form(i.prime) == set(i.prime)


class TonnezTests(unittest.TestCase):

    def test_p_transformation(self):
        t = tonnez.Tonnez()
        assert t.p.pitch_classes == [0,3,7] # Cminor

    def test_r_transformation(self):
        t = tonnez.Tonnez()
        assert t.r.pitch_classes == [9,0,4] # Aminor

    def test_l_transformation(self):
        t = tonnez.Tonnez()
        assert t.l.pitch_classes == [4,7,11] # Eminor

    def test_pl_transformation(self):
        t = tonnez.Tonnez()
        assert t.pl.pitch_classes == [8,0,3] # Ab maj

    def test_pr_transformation(self):
        t = tonnez.Tonnez()
        assert t.pr.pitch_classes == [3,7,10] # Eb maj

    def test_lp_transformation(self):
        t = tonnez.Tonnez()
        assert t.lp.pitch_classes == [4,8,11] # E maj

    def test_rp_transformation(self):
        t = tonnez.Tonnez()
        assert t.rp.pitch_classes == [9,1,4] # A maj

    def test_child_nodes(self):
        t = tonnez.Tonnez()
        children = t.child_nodes()
        assert t.p in children
        assert t.r in children
        assert t.l in children
        assert t.pl in children
        assert t.pr in children
        assert t.lp in children
        assert t.rp in children

    def test_equality(self):
        assert tonnez.Tonnez(0,4,7) == tonnez.Tonnez(0,4,7)
        assert tonnez.Tonnez(0, 4, 7) == [0, 4, 7]
        assert tonnez.Tonnez(0, 4, 7) != tonnez.Tonnez(7, 0, 4)
        assert tonnez.Tonnez(0, 4, 7) != {0, 4, 7}



if __name__ == "__main__":
    unittest.main()
