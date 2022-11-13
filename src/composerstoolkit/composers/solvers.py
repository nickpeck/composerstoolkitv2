"""Solvers that generate sequences within a domain
of contraints.
These are not designed for on-the-fly usage.
"""

from decimal import Decimal
import math
import random
from typing import Dict

from composerstoolkit.core import Event, Sequence, FiniteSequence
from composerstoolkit.resources import NOTE_MIN, NOTE_MAX

class DeadEndReached(Exception):
    """Indicates that the solver reached a dead-end
    whilst trying to produce a solution.
    """

class InputViolatesConstraints(Exception):
    """Indicates that the seed given to a solver violates
    the constraints for the finished solution
    """

class AllRoutesExhausted(Exception):
    """Indicates that a solver was unable to produce
    a solution after investigating all recursive
    possibilities under the given condition.
    """

def develop(seed: FiniteSequence, **kwargs) -> Sequence:
    """Grow a sequence from a given 'seed' (motive).
    The process does not operate in realtime, and may well
    raise DeadEndReached if it hits a dead-end
    The process is controlled by the following kwargs:

    min_beats - controls the length of the sequence. It is
    recommended to keep this figure smaller to start with.

    mutators - list of transformers. One will be applied to
    the seed at each stage. These are choosen
    using a weighted random choice. Optionally, you can specify weights
    at the start: eg mutators = [(t1, Decimal(1)), (t2, Decimal('1.5'))...]

    constraints - list of constraints. The entire sequence must pass all
    constraints in order to be deemed valid.

    adjust_weights: If True, adjust the weighting of the mutators at
    each stage, so that mutators that result in passing results are
    weighted up, and vice versa.
    """
    opts = {
        "mutators": [],
        "constraints": [],
        "adjust_weights": True,
        "min_beats": 1
    }
    opts.update(kwargs)
    try:
        weights = [y for (x,y) in opts["mutators"]]
        mutators = [x for (x,y) in opts["mutators"]]
    except TypeError:
        weights = [Decimal(1) for i in range(len(opts["mutators"]))]
        mutators = opts["mutators"]
    result = FiniteSequence(seed.events)
    transformed = result.events
    while sum([evt.duration for evt in result.events]) < opts["min_beats"]:
        is_searching = True
        while is_searching:

            if set(weights) == {0}:
                raise DeadEndReached(
                    "The solver ran into a dead-end. Please try again, or adjust the parameters.")
            _weights = (float(w) for w in weights)
            mutator = random.choices(mutators, _weights)[0]

            transformed = list(mutator(Sequence(transformed)))
            candidate = FiniteSequence(result.events + transformed)

           # test that the whole sequence meets the given constraints
            # cycle until we have a sequence that passes checks
            is_searching = False
            for constraint in opts["constraints"]:
                if not constraint(candidate):
                    is_searching = True
                    break

            if is_searching:
                # adjust weights, negative bias
                if opts["adjust_weights"] and weights[mutators.index(mutator)] > 0:
                    weights[mutators.index(mutator)]\
                        = weights[mutators.index(mutator)] - Decimal('0.1')
                continue

            result = candidate
            # adjust weights, positive bias
            if opts["adjust_weights"] and weights[mutators.index(mutator)] < 1:
                weights[mutators.index(mutator)] = weights[mutators.index(mutator)] + Decimal('0.1')
    return result

def backtracking_markov_solver(
        starting_event: Event,
        table: Dict[int, Dict[int, int]],
        **kwargs) -> FiniteSequence:
    """Compose a melodic sequence based upon the
    domain and constraints given.

    starting_event: Event dictate the starting pitch.
    All subsequent events will be of similar duration.

    constraints - list of constraint functions
    (see composerstoolkit.composers.constraints)

    heuristics - list of heuristics (weight maps)
    that can be used to provide a rough shape to the line
    (see composerstoolkit.composers.heuristics)

    n_events - the number of notes of the desired target
    sequence. (Default 1)
    """
    opts = {
        "constraints": [],
        "heuristics": [],
        "n_events": 1
    }
    opts.update(kwargs)
    constraints = opts["constraints"]
    heuristics = opts["heuristics"]
    n_events = opts["n_events"]

    tick = 0
    seq = FiniteSequence([starting_event])

    if n_events == 1:
        return FiniteSequence(seq)


    for constraint in constraints:
        if not constraint(seq):
            raise InputViolatesConstraints("Unable to solve!")

    dead_paths = []
    choices = list(range(12))
    previous_note = seq.events[-1].pitches[-1]
    previous_note_pc = previous_note % 12
    weights = list(table[previous_note_pc].values())
    while tick < n_events-1:

        try:

            pitch = random.choices(choices, weights)[0]
            original_8va = math.floor(previous_note / 12)
            _pitch = (original_8va * 12) + pitch
            if abs(_pitch - previous_note) > 12:
                _pitch = _pitch - 12
            note = Event([_pitch], starting_event.duration)

        except IndexError:
            # this was thrown because we ran out of choices (we have reached a dead-end)
            dead_paths.append(seq[:])
            seq = seq[:-1]
            tick = tick -1
            previous_note = seq.events[-1].pitches[-1]
            previous_note_pc = previous_note % 12
            weights = list(table[previous_note_pc].values())
            choices = list(range(12))
            # choices = list(range(NOTE_MIN, NOTE_MAX))
            if tick == 0:
                raise AllRoutesExhausted("Unable to solve!")
            continue
        context = FiniteSequence(seq.events[:])
        context.events.append(note)

        results = {True}
        for constraint in constraints:
            results.update([constraint(context)])
        candidate = seq[:]
        candidate.events.append(note)

        if results == {True} and candidate not in dead_paths:
            seq.events.append(note)
            tick = tick + 1
            choices = list(range(12))
            previous_note = _pitch
            previous_note_pc = previous_note % 12
            weights = list(table[previous_note_pc].values())
            # choices = list(range(NOTE_MIN, NOTE_MAX))
        else:
            #this choice was bad, so we must exclude it
            i = choices.index(pitch)
            del weights[i]
            del choices[i]
    return seq

def backtracking_solver(
        starting_event: Event,
        **kwargs) -> FiniteSequence:
    """Compose a melodic sequence based upon the
    domain and constraints given.

    starting_event: Event dictate the starting pitch.
    All subsequent events will be of similar duration.

    constraints - list of constraint functions
    (see composerstoolkit.composers.constraints)

    heuristics - list of heuristics (weight maps)
    that can be used to provide a rough shape to the line
    (see composerstoolkit.composers.heuristics)

    n_events - the number of notes of the desired target
    sequence. (Default 1)
    """
    opts = {
        "constraints": [],
        "heuristics": [],
        "n_events": 1
    }
    opts.update(kwargs)
    constraints = opts["constraints"]
    heuristics = opts["heuristics"]
    n_events = opts["n_events"]

    tick = 0
    seq = FiniteSequence([starting_event])
    use_weights = len(heuristics) > 0

    if n_events == 1:
        return FiniteSequence(seq)

    results = set()
    for constraint in constraints:
        results.update([constraint(seq)])
    if results != {True}:
        raise InputViolatesConstraints("Unable to solve!")

    choices = list(range(NOTE_MIN, NOTE_MAX))
    dead_paths = []
    while tick < n_events-1:

        if use_weights:
            weights= [1.0 for i in range(len(choices))]
            for heuristic in heuristics:
                weights = heuristic(tick, choices, weights)

        try:
            if use_weights:
                note = Event([random.choices(choices, weights)[0]], starting_event.duration)
            else:
                note = Event([random.choice(choices)], starting_event.duration)
        except IndexError:
            # this was thrown because we ran out of choices (we have reached a dead-end)
            dead_paths.append(seq[:])
            seq = seq[:-1]
            tick = tick -1
            choices = list(range(NOTE_MIN, NOTE_MAX))
            if tick == 0:
                raise AllRoutesExhausted("Unable to solve!")
            continue
        context = FiniteSequence(seq.events[:])
        context.events.append(note)

        results = set()
        for constraint in constraints:
            results.update([constraint(context)])
        candidate = seq[:]
        candidate.events.append(note)
        if results == {True} and candidate not in dead_paths:
            seq.events.append(note)
            tick = tick + 1
            choices = list(range(NOTE_MIN, NOTE_MAX))
        else:
            #this choice was bad, so we must exclude it
            choices.remove(note.pitches[-1])
    return seq
