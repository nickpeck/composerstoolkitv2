import os
import unittest

from mido import MidiFile

from composerstoolkit.core import Graph

class TestSuite(unittest.TestCase):

    def test_can_create_graph_from_midi_file(self):
        filename = os.path.join("tests", "simple_i-iv.mid")
        midi_file = MidiFile(filename)
        graph = Graph.from_midi_track(midi_file.tracks[0])

if __name__ == "__main__":
    unittest.main()