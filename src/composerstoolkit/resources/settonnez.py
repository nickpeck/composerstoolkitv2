from __future__ import annotations
from typing import List, Callable, Dict, Set

from .. core.sequence import Event
from . pitchset import transpositions, inversions

class SetTonnez:
    """
    Similar to Tonnez, but not limited to tertiary triadic harmony.
    Shows tranpositions (and inversions) of a given pitch class that are
    linked by n_shared_pitches.
    Is node-based, so can be used as part of a search tree
    """
    def __init__(self, pitch_classes: List[int], n_shared_pitches=0, use_transpositions=True, use_inversions=True,
                 other_transformations: List[Callable[List[int], Dict[str, Set]]] = None):
        self.pitch_classes = pitch_classes
        self.n_shared_pitches = n_shared_pitches
        self.transformations = {}
        if use_transpositions:
            self.transformations.update(transpositions(pitch_classes))
        if use_inversions:
            self.transformations.update(inversions(pitch_classes))
        if other_transformations is None:
            other_transformations = []
        for transformation in other_transformations:
            self.transformations.update(transformation(pitch_classes))


    def child_nodes(self) -> Dict[str, 'SetTonnez']:
        children = {}
        for k, v in self.transformations.items():
            if len(v.intersection(self.pitch_classes)) == self.n_shared_pitches:
                children[k] = SetTonnez(v, self.n_shared_pitches)
        return children

    def __getattr__(self, item):
        return SetTonnez(self.transformations[item], self.n_shared_pitches)

    def __repr__(self):
        return str(self.pitch_classes)

    def __eq__(self, other):
        if isinstance(other, SetTonnez):
            return other.pitch_classes == self.pitch_classes
        if isinstance(other, list):
            return other == self.pitch_classes
        return False

    def as_event(self):
        return Event(pitches=self.pitch_classes)
