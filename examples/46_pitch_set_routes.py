"""
Similar to example 44, but searches for a route through a series of chords derived
from a single pitch set linked by a number of shared common tones.
"""

from composerstoolkit import *

source_set = {0,1,4}
transpositions = pitchset.transpositions(source_set)

start = settonnez.SetTonnez(transpositions["p0"], n_shared_pitches=1)
target = settonnez.SetTonnez(transpositions["p6"])
n_routes = 5

def play_route(route):
    print("ROUTE ", "->".join(route))
    events = [start.as_event().extend(duration=1)]
    current_node = start
    for r in route:
        current_node = getattr(current_node, r)
        events.append(current_node.as_event().extend(duration=1))
    Sequencer(log_level=logging.WARNING, bpm=60)\
        .add_sequence(
            Sequence(events)
            .transform(transpose(12 * 5))
            .bake(len(events))) \
        .show_notation() \
        .playback()


explored_routes = []
current_paths = [([k], v) for k, v in start.child_nodes().items()]
solutions = []

while len(solutions) < n_routes:
    candidate_routes = []
    for route, node in current_paths:
        if len(solutions) > n_routes - 1:
            break
        if route in explored_routes:
            continue
        if target == node:
            solutions.append(route)
            explored_routes.append(route)
            continue
        current_paths = current_paths + [(route + [k], v) for k, v in node.child_nodes().items()]
        explored_routes.append(route)

    current_paths = current_paths + candidate_routes

for route in solutions:
    play_route(route)