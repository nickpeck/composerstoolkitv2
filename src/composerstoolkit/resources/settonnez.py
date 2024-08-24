from __future__ import annotations
from typing import List, Callable

from . pitchset import transpositions, inversions

class SetTonnez:
    def __init__(self, pitch_classes: List[int], n_shared_pitches=0):
        self.pitch_classes = pitch_classes
        self.n_shared_pitches = n_shared_pitches
        self.transformations = transpositions(pitch_classes)
        self.transformations.update(inversions(pitch_classes))

    def child_nodes(self) -> 'SetTonnez':
        children = []
        for k, v in self.transformations.items():
            if len(v.intersection(self.pitch_classes)) == self.n_shared_pitches:
                children.append(v)
        return children

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
