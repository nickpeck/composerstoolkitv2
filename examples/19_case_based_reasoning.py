from midiutil.MidiFile import MIDIFile # type: ignore
from mido import MidiFile

from pprint import pprint

from composerstoolkit import *

graphs = []
for file in os.listdir("tests"):
    if file.startswith("chor"):
        filename = os.path.join("tests", file)
    midi_file = MidiFile(filename)
    graph = Graph.from_midi_track(midi_file.tracks[0])
    graphs.append(graph)

pf = pitches.PitchFactory()

cbr = CBR(case_base=graphs)

seq = FiniteSequence(events=[
    Event(pitches=[pf("C5")], duration=1),
    Event(pitches=[pf("C5")], duration=1),
    Event(pitches=[pf("D5")], duration=1),
    Event(pitches=[pf("E5")], duration=1.5),
    Event(pitches=[pf("F5")], duration=0.5),
    Event(pitches=[pf("G5")], duration=1),
])

while True:
    matches = []
    dead_paths = []
    i = len(seq.events)
    while len(matches) == 0:
        vectors = seq[-i:].to_vectors()
        matches = cbr.find_matches(vectors)
        i = i - 1
        if i == 0:
            dead_paths.append(seq)
            print("backtracking...")
            seq = seq[:-1]
            i = len(seq.events)
            if i == 0:
                raise Exception("could not find a match")

    # expand all possible candidate paths by one
    candidates = []
    for match in matches:
        last_e = match[-1]
        for vertex in last_e.vertices:
            pitch_delta = vertex.pitch - last_e.pitch
            time_delta = last_e.end_time - last_e.start_time
            if time_delta != 0:
                candidate = FiniteSequence(seq.events + [Event(
                    [seq.events[-1].pitches[-1] + pitch_delta],
                    time_delta
                )])
                if candidate not in dead_paths:
                    candidates.append(candidate)

    # fitness function
    print("assessing {} candidates".format(len(candidates)))
    prev_note = candidate.events[-2]
    for candidate in candidates:
        
        Container(bpm=120, playback_rate=1)\
            .add_sequence(candidate)\
            .playback()
        should_keep = input("Keep? Y/N")
        if should_keep == "y":
            seq = candidate
            break


