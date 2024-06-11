"""Use a brute-force search to determine some routes between two triads using the transformations in the Tonnez"""

import logging
from composerstoolkit import *

start = tonnez.Tonnez(0,4,7) # Cmajor
target = tonnez.Tonnez(6,10,1) # Gb major
n_routes = 5


def play_route(route):
    print("ROUTE ", "->".join(route))
    events = [start.as_event().extend(duration=1)]
    for r in route:
        events.append(getattr(start, r).as_event().extend(duration=1))
    events.append(target.as_event().extend(duration=1))
    Sequencer(log_level=logging.WARNING, bpm=60)\
        .add_sequence(
            Sequence(events)
            .transform(transpose(12 * 5))
            .bake(len(events))) \
        .show_notation() \
        .playback()

explored_routes = []
transformations = ["p", "l", "r", "pl", "pr", "lp", "rp"]
current_paths = [([t], getattr(start, t)) for t in transformations]
solutions = 0

while solutions < n_routes:
    candidate_routes = []
    for route, node in current_paths:
        if solutions > n_routes - 1:
            break
        if route in explored_routes:
            continue
        if target == node:
            play_route(route)
            explored_routes.append(route)
            solutions = solutions + 1
            continue
        candidate_routes = candidate_routes + [(route + [t], getattr(node, t)) for t in transformations]
        explored_routes.append(route)

    current_paths = current_paths + candidate_routes

