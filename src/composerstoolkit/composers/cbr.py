from typing import List, Tuple, Optional

from composerstoolkit.core import Event, Graph, Sequence, FiniteSequence, Constraint

class Corpus:
    """Allows us to store and query information
    based on a collection of normalised musical examples
    """
    def __init__(self,
        case_base: List[Graph]):
        self.case_base = case_base

    def _search_graph(self, graph, vectors):
        paths = []
        arr = graph.to_vector_indexed_array()
        route_found = False

        for vector in vectors:
            route_found = False

            if vector not in arr:
                return []
            new_paths = arr[vector]

            if paths == []:
                paths = new_paths
                continue
            for path in paths:
                for new_path in new_paths:
                    if path[-1] == new_path[0]:
                        path.append(new_path[-1])
                        route_found = True
            if not route_found:
                return []
        return paths

    def find_matches(self, vectors = List[Tuple[int, int]]):
        """Return all matches of the given list of vectors
        from the corpus
        """
        paths = []
        for graph in self.case_base:
            paths = paths + self._search_graph(graph, vectors)
        return paths

class CaseBasedSolver:
    """Brute-force solver that attempts to grow a sequence of notes
    based on the statistically most likely routes in a
    given corpus of material. Constraints can be used
    to shape the resulting solutions.

    At each stage, the solver is looking for the longest
    possible match in the corpus, resulting in material
    that is more likely to exhibit a more distinct
    shape and structure.

    The instance is iterable, yielding solutions along
    with their confidence rating.
    """
    def __init__(self,
        source: FiniteSequence,
        corpus: Corpus,
        target_duration_beats: int,
        constraints: Optional[List[Constraint]] = None):

        self.source = source
        self.corpus = corpus
        self.target_duration_beats = target_duration_beats
        if constraints  is None:
            constraints = []
        self.constraints = constraints
        self.paths_explored = []

    def __iter__(self):
        return self

    def __next__(self) -> Tuple[FiniteSequence, int]:
        # make a copy of the source seq
        seq = FiniteSequence(events=self.source.events[:])

        confidence_score = 0 # TODO

        while seq.duration <= self.target_duration_beats:
            # find instances in the corpus that match the shape of our source
            vectors = seq.to_vectors()
            intervals = [i for (i,p) in vectors]
            matches = []
            matches = self.corpus.find_matches(vectors)
            while len(matches) == 0:
                # if we can't match the full melody, try and match
                # progressivly shorter sections from the end
                vectors = vectors[1:]
                if len(vectors) == 0:
                    raise StopIteration("Could not find a longer match for vectors", self.corpus.find_matches(vectors))
                matches = self.corpus.find_matches(vectors)

            # data structure is a dict of pitch delta : List[durations]
            options = {i:[] for i in range(-127,127)}
            # expand the last edge of each match, to find the possible
            # destinations from that point
            for match in matches:
                last_e = match[-1]
                for vertex in last_e.vertices:
                    pitch_delta = vertex.pitch - last_e.pitch
                    time_delta = last_e.end_time - last_e.start_time
                    if time_delta != 0:
                        options[pitch_delta].append(time_delta)

            # pitch options is a list of possible vectors, sorted by the 
            # most frequent first
            options = [(k,v) for k,v in options.items()]
            options = sorted(options, key=lambda o: len(o[1]), reverse=True)
            n_options = len(options)
            # iterate over pitch options, to find the best fi
            # that matches our critera, but has not been used before
            found_next = False
            i = n_options
            while found_next == False:
                if options == []:
                    # this route is a dead end. Chop the last events
                    # off and backtrack
                    self.paths_explored.append(FiniteSequence(seq.events[:]))
                    seq.events.pop()
                    break

                if options[0][1] == []:
                    # this option is never visited in the corpus, ignore
                    options.remove(options[0])
                    i = i - 1
                    continue

                seq.events.append(
                    Event([seq.events[-1].pitches[-1] + options[0][0]],
                        max(options[0][1], key=options[0][1].count)))
                if seq in self.paths_explored:
                    seq.events.pop()
                    options.remove(options[0])
                    continue

                # check against constraints
                passed_const_check = True
                for constraint in self.constraints:
                    if not constraint(seq):
                        passed_const_check = False
                        break
                if not passed_const_check:
                    # this option does not work
                    # remove it from this round
                    seq.events.pop()
                    options.remove(options[0])
                    continue
                found_next = True

        self.paths_explored.append(seq)
        return (seq, confidence_score)