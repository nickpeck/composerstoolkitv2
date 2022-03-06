from collections import Counter
import itertools
from typing import List, Any, Tuple, Set

from prefixspan import PrefixSpan

from ..core import Graph, FiniteSequence, Container, Event, Sequence
from ..builders.transformers import *

def seq_chunked(dataset: List[Any], window: int):
    """Return a list comprising of dataset
    broken down into down into sizes of
    length window.
    """
    chunks = []
    for i in range(0, len(dataset), window):
        chunks.append(dataset[i:i + window])
    return chunks

def common_subsequences(
    dataset: List[Any],
    min_match_len = 3,
    max_match_len = 10) -> List[Tuple[int, List[Any]]]:
    """Catalog common sequential patterns 
    (ie, occuring twice or more) that are of length
    min_match_len to max_match_len that occur within
    list dataset.
    Return a list of (count, subsequence), most
    frequent first.
    """
    results = []

    def _count_occurrences(sublist, parent):
        return sum(parent[i:i+len(sublist)]==\
            sublist for i in range(len(parent)))

    for i1 in range(len(dataset) - max_match_len):
        previous = None
        for i2 in range(min_match_len, max_match_len):
            head = dataset[i1:i1 + i2]
            tail = dataset[i1 + i2:]
            count = _count_occurrences(head, tail)
            if count == 0:
                if previous is not None:
                    head = previous
                    results.append(head)
                    previous = None
                break
            previous = head
        results.append(head)
    results = [list(j) for i, j in itertools.groupby(results)]
    results = [(len(seq), seq[0]) for seq in results]
    results = sorted(results,
        key=lambda m: m[0], reverse=True)
    return results

def hidden_subsequences(
    dataset: List[Any],
    depth=4):
    """
    Catalog frequent hidden sequences within
    dataset. (A wrapper around PrefixSpan).
    Return a list of (count, subsequence), longest
    matches first.
    """
    ps = PrefixSpan(dataset)
    detected = ps.topk(depth)
    detected = sorted(detected, key=lambda x: len(x[1]), reverse=True)
    return detected

def chordal_analysis(seq: FiniteSequence,
    window_size_beats=4,
    chord_lexicon=List[Set],
    start_offset = 0,
    overlap_threshold=1):
    """Break the given seq down into chunks of
    window_size (expressed in beats).
    Analyse the content within to determine the
    most likely chordal background.
    In the case of abmiguity, resort to
    the best voice-leading solution.
    Return a list of transposed chord voicings.
    """
    # segement the source sequence
    # curr_time = start_offset
    # slices = []
    # while curr_time <= seq.duration:
        # slices.append(seq.time_slice(
            # curr_time, curr_time +  window_size_beats))
        # curr_time = curr_time + window_size_beats
    slices = seq_chunked(seq, window_size_beats)
    found_chords = []

    # find candidate pcs that best intersects the pcs of each seq
    for i,slice in enumerate(slices):
        pcs = slice.to_pitch_class_set()
        candidate_chords = []
        for chord in chord_lexicon:
            diff = chord.difference(pcs)

            if len(diff) <= overlap_threshold:
                # provide an arbitary weighting, based on
                # the size of the chord and the degree
                # of abmiguity
                metric = len(chord) - len(diff)
                candidate_chords.append((metric, chord))
        # sorted, most likely first
        candidate_chords = sorted(
            candidate_chords, key=lambda c: c[0], reverse=True)

        if len(candidate_chords) == 0:
            # could not find a match
            candidate_chords = [(0, set())]
        if i == 0:
            found_chords.append(candidate_chords[0][1])
            continue
        # Now select the best candidate based on lowest
        # cost voice-leading
        weighted_options = []

        previous = found_chords[-1]
        cost = 0
        # selects the highest weighted group
        candidate_chords = [list(j) for i, j in
            itertools.groupby(candidate_chords)][0]

        for weighting, chord in candidate_chords:

            cost = Event(list(previous))\
                .movement_cost_to(Event(list(chord)))
            weighted_options.append((cost, chord))
        # the head of the list is the best choice
        found_chords.append(weighted_options[0][1])

    return found_chords
