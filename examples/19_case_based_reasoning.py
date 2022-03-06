from midiutil.MidiFile import MIDIFile # type: ignore
from mido import MidiFile

from pprint import pprint

from composerstoolkit import *

# graphs = []
# midi_file = MidiFile("case_base\\cello_suites\\cs1-1pre.mid")
# graph = Graph.from_midi_track(midi_file.tracks[1])
# graphs.append(graph)

print("Loading case base")
graphs = []
for file in os.listdir(os.path.join("case_base", "cello_suites")):
    if file.endswith("mid"):
        filename = os.path.join("case_base", "cello_suites", file)
    midi_file = MidiFile(filename)
    graph = Graph.from_midi_track(midi_file.tracks[1])
    graphs.append(graph)

pf = pitches.PitchFactory()

cbr = CBR(case_base=graphs)

seq = FiniteSequence(events=[
    Event(pitches=[pf("G2")], duration=0.125),
    Event(pitches=[pf("A2")], duration=0.125),
    Event(pitches=[pf("B2")], duration=0.125)
])

vector_markov_table = {   (0, 0.125): {   (-9, 0.125): 6,
                    (-8, 0.125): 20,
                    (-7, 0.125): 5,
                    (-4, 0.125): 17,
                    (-2, 0.125): 45,
                    (-1, 0.125): 70,
                    (1, 0.125): 43,
                    (4, 0.125): 23,
                    (7, 0.125): 14,
                    (8, 0.125): 7,
                    (9, 0.125): 25}}
if len(seq.events) < 3:
    print("At least three events required")
    exit(1)

while True:
    print("=============================")
    pprint(vector_markov_table, indent=4)
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

    match_len = i # save this for later
    print("match len is " + str(i))

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
    
    # estimate the most likely candidate based on the markov table
    left = seq.events[-1]
    middle = seq.events[-1]
    pitch_delta_l = middle.pitches[-1] - left.pitches[-1]
    time_delta_l = left.duration
    v_left = (pitch_delta_l, time_delta_l)

    def ranking(cand):
        right = cand.events[-1]
        pitch_delta_r = right.pitches[-1] - middle.pitches[-1]
        time_delta_r = middle.duration
        v_right = (pitch_delta_r, time_delta_r)
        try:
            return vector_markov_table[v_left][v_right]
        except KeyError:
            return 0

    candidates = sorted(candidates, key=lambda c : ranking(c), reverse=True)

    for i,candidate in enumerate(candidates):
        if candidate in dead_paths:
            print("ignoring duplicate")
            continue
        print("---------------------------")
        print("candidate {} of {}".format(i+1, len(candidates)))
        Container(bpm=50, playback_rate=1)\
            .add_sequence(candidate)\
            .playback()
        should_keep = input("Keep? Y/N")
        if should_keep == "y":
            seq = candidate
            #new_graph = seq.to_graph()
            #cbr.case_base.insert(0, new_graph)

            # update the markov model with the victor
            right = candidate.events[-1]
            pitch_delta_r = right.pitches[-1] - middle.pitches[-1]
            time_delta_r = middle.duration
            v_right = (pitch_delta_r, time_delta_r)

            if v_left not in vector_markov_table:
                vector_markov_table[v_left] = {}
            if v_right not in vector_markov_table[v_left]:
                vector_markov_table[v_left][v_right] = 0
            vector_markov_table[v_left][v_right] = vector_markov_table[v_left][v_right] + 1 * match_len
            break
        else:
            dead_paths.append(candidate)


