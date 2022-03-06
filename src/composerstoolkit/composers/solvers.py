from decimal import Decimal
import itertools
import math
import random

from time import sleep

from composerstoolkit.core import (Event, Sequence, FixedSequence, Context, Constraint)
from composerstoolkit.builders.generators import cantus
from composerstoolkit.resources import NOTE_MIN, NOTE_MAX

class DeadEndException(Exception):
    """Indicates that the solver reached a dead-end
    whilst trying to produce a solution.
    """

class InputViolatesConstraintsException(Exception):
    """Indicates that the seed given to a solver violates
    the constraints for the finished solution
    """

class AllRoutesExhaustedException(Exception):
    """Indicates that a solver was unable to produce
    a solution after investigating all recursive
    possibilities under the given condition.
    """

def grow_seed(seed: FixedSequence, **kwargs) -> Sequence:
    """Grow a sequence from a given 'seed' (motive).
    The process does not operate in realtime, and may well
    raise DeadEndException if it hits a dead-end
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
    except:
        weights = [Decimal(1) for i in range(len(opts["mutators"]))]
        mutators = opts["mutators"]
    result = FixedSequence(seed.events)
    transformed = result.events
    while sum([evt.duration for evt in result.events]) < opts["min_beats"]:
        is_searching = True
        while is_searching:

            if set(weights) == {0}:
                raise DeadEndException("The solver ran into a dead-end.")
            _weights = (float(w) for w in weights)
            mutator = random.choices(mutators, _weights)[0]

            transformed = list(mutator(Sequence(transformed)))
            candidate = FixedSequence(result.events + transformed)

           # test that the whole sequence meets the given constraints
            # cycle until we have a sequence that passes checks
            is_searching = False
            for c in opts["constraints"]:
                if not c(candidate):
                    is_searching = True
                    break

            if is_searching:
                # adjust weights, negative bias
                if opts["adjust_weights"] and weights[mutators.index(mutator)] > 0:
                    weights[mutators.index(mutator)] = weights[mutators.index(mutator)] - Decimal('0.1')
                continue

            result = candidate
            # adjust weights, positive bias
            if opts["adjust_weights"] and weights[mutators.index(mutator)] < 1:
                weights[mutators.index(mutator)] = weights[mutators.index(mutator)] + Decimal('0.1')
    return result

def grow_cantus_backtracking(starting_event: Event,
        constraints: List[Constraint],
        n_events=64) -> FixedSequence:
    """Extend a given pitch sequence  by up to n_events, using
    an unweighted random selection process and backtracking solver.

    seed - CTEvent (starting pitch)
    n_events - how long to make the target sequence
    constraints - a list of constraints that should be satisfied at each stage. If the 
        transformation fails to meet the constraints, it will be rejected and the solver
        will backtrack to select a new path. 'Dead' paths are tracked and rejected.
        Each constraint recieves a tuple of (note, seq, tick), where tick is the number
        of the event.
    
    returns: CTSequence or UnsatisfiableException if a solution that satisfies the
        constraints cannot be found.
        
    """
    tick = 0
    seq = FixedSequence([starting_event])
    if n_events == 1:
        return FixedSequence(seq)
    results = set()
    for constraint in constraints:
        results.update([constraint(seq)])
    if results != {True}:
        raise InputViolatesConstraintsException("Unable to solve!")
    choices = list(range(NOTE_MIN, NOTE_MAX))
    dead_paths = []
    while tick < n_events-1:
        # lets use a very basic random choice to begin with and see how far we go
        try:
            note = Event([random.choice(choices)])

        except IndexError:
            # this was thrown because we ran out of choices (we have reached a dead-end)
            # back track
            dead_paths.append(seq[:])
            seq = seq[:-1]
            tick = tick -1
            choices = list(range(NOTE_MIN, NOTE_MAX))
            if tick == 0:
                raise UnsatisfiableException("Unable to solve!")
                break
            else:
                continue

        context = FixedSequence(seq.events[:])
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
