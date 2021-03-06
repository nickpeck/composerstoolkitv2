import unittest

from composerstoolkit import *

def _build_lexicon(chords: List[Event]):
    lexicon = []
    for chordal_event in chords:
        lexicon = lexicon + [
            chord.to_pitch_class_set() for chord in \
                chord_cycle(scale = scales.chromatic,
            start=chordal_event,
            cycle_of=1,
            voice_lead=False,
            max_len=12)]
    return lexicon

PitchFactory = pitches.PitchFactory
pf = PitchFactory()

class TestChordalAnalysis(unittest.TestCase):

    def test_it_identifies_simple_triad(self):
        lexicon = _build_lexicon(chords=[
            Event(pitches=[0,4,7]),
            Event(pitches=[0,3,7]),
            Event(pitches=[0,3,6])]
        )

        source = FiniteSequence(events=[
            Event([pf("C4")], duration=1),
            Event([pf("E4")], duration=1),
            Event([pf("G4")], duration=1)
        ])
        found_chords = chordal_analysis(
            source,
            chord_lexicon=lexicon)
        assert found_chords == [{0,4,7}]

    def test_it_ignores_a_passing_note(self):
        lexicon = _build_lexicon(chords=[
            Event(pitches=[0,4,7]),
            Event(pitches=[0,3,7]),
            Event(pitches=[0,3,6])]
        )

        source = FiniteSequence(events=[
            Event([pf("C4")], duration=1),
            Event([pf("E4")], duration=1),
            Event([pf("F4")], duration=1),
            Event([pf("G4")], duration=1)
        ])
        found_chords = chordal_analysis(
            source, 
            chord_lexicon=lexicon)
        assert found_chords == [{0,4,7}]

    def test_it_returns_an_empty_set_if_no_match(self):
        lexicon = _build_lexicon(chords=[
            Event(pitches=[0,4,7]),
            Event(pitches=[0,3,7]),
            Event(pitches=[0,3,6])]
        )

        source = FiniteSequence(events=[
            Event([pf("C4")], duration=1),
            Event([pf("Db4")], duration=1)
        ])
        found_chords = chordal_analysis(
            source, 
            chord_lexicon=lexicon)
        assert found_chords == [set()]

    def test_we_can_segment_a_sequence_using_windows(self):
        lexicon = _build_lexicon(chords=[
            Event(pitches=[0,4,7]),
            Event(pitches=[0,3,7]),
            Event(pitches=[0,3,6])]
        )

        source = FiniteSequence(events=[
            Event([pf("C4")], duration=1),
            Event([pf("E4")], duration=1),
            Event([pf("G4")], duration=1),
            Event([pf("C4")], duration=1),
            Event([pf("F4")], duration=1),
            Event([pf("A4")], duration=1)
        ])
        found_chords = chordal_analysis(
            source, 
            window_size_beats=3,
            chord_lexicon=lexicon)
        assert found_chords == [{0,4,7}, {0,5,9}]

    def test_we_can_identify_repeated_chords(self):
        lexicon = _build_lexicon(chords=[
            Event(pitches=[0,4,7]),
            Event(pitches=[0,3,7]),
            Event(pitches=[0,3,6])]
        )

        source = FiniteSequence(events=[
            Event([pf("C4")], duration=1),
            Event([pf("E4")], duration=1),
            Event([pf("G4")], duration=1),
            Event([pf("G4")], duration=1),
            Event([pf("C4")], duration=1),
            Event([pf("E4")], duration=1)
        ])
        found_chords = chordal_analysis(
            source, 
            window_size_beats=3,
            chord_lexicon=lexicon)
        assert found_chords == [{0,4,7}, {0,4,7}]

    def test_larger_matches_are_choosen_when_available(self):
        lexicon = _build_lexicon(chords=[
            Event(pitches=[0,4,7]),
            Event(pitches=[0,3,7]),
            Event(pitches=[0,3,6]),
            Event(pitches=[0,4,7,11])]
        )

        source = FiniteSequence(events=[
            Event([pf("B3")], duration=1),
            Event([pf("C4")], duration=1),
            Event([pf("E4")], duration=1),
            Event([pf("F4")], duration=1),
            Event([pf("G4")], duration=1),
            Event([pf("C4")], duration=1),
            Event([pf("A4")], duration=1)
        ])
        found_chords = chordal_analysis(
            source,
            chord_lexicon=lexicon)
        # C maj 7 is the largest match
        assert found_chords == [{0,4,7,11}]

class TestCommonSubsequences(unittest.TestCase):

    def test_common_subsequences(self):
        dataset = [1,2,3,1,2,3,1,2,3]
        results = common_subsequences(
            dataset = dataset,
            min_match_len = 3,
            max_match_len = 5
        )
        assert results == [
           (3, [1,2,3]),
           (2, [2,3,1]),
           (2, [3,1,2])
        ]

    def test_it_raises_an_exc_if_dataset_too_short(self):
        dataset = [1,2,3,1,2,3,1,2,3]
        with self.assertRaises(Exception) as e:
            results = common_subsequences(
                dataset = dataset,
                min_match_len = 3,
                max_match_len = 10
            )
        assert e.exception.args == \
            ("max_match_len cannot be > len(dataset)",)

class TestHiddenSubsequences(unittest.TestCase):

    def test_hidden_subsequences(self):
        dataset = [[1,0,2,0,3,0,1,0,2,3],
                   [0,1,2,0,3,1,0,2,3]]
        results = hidden_subsequences(
            dataset = dataset,
            depth = 100
        )
        assert [1,2,3,1,2,3] in [r for count,r in results]

class TestStatisticsTools(unittest.TestCase):

    def test_pitch_range(self):
        seq = FiniteSequence(events=[
            Event([pf("B3")], duration=1),
            Event([pf("C4")], duration=1),
            Event([pf("E4")], duration=1),
            Event([pf("F4")], duration=1),
            Event([pf("G4")], duration=1),
            Event([pf("C4")], duration=1),
            Event([pf("A4")], duration=1)
        ])
        lower, upper = pitch_range(seq)
        assert lower == pf("B3")
        assert upper == pf("A4")

    def test_total_durations(self):
        seq = FiniteSequence(events=[
            Event([pf("B3")], duration=1),
            Event([pf("C4")], duration=1),
            Event([pf("E4")], duration=1),
            Event([pf("F4")], duration=1),
            Event([pf("G4")], duration=1),
            Event([pf("C4")], duration=1),
            Event([pf("A4")], duration=1)
        ])
        dur = total_duration(seq)
        assert dur == 7

    def test_duration_classes(self):
        seq = FiniteSequence(events=[
            Event([pf("B3")], duration=1),
            Event([pf("C4")], duration=2),
            Event([pf("E4")], duration=1),
            Event([pf("F4")], duration=1),
            Event([pf("G4")], duration=1),
            Event([pf("C4")], duration=5),
            Event([pf("A4")], duration=9)
        ])
        dcs = duration_classes(seq)
        assert dcs == {1,2,5,9}

if __name__ == "__main__":
    unittest.main()