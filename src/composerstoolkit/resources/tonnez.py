from __future__ import annotations
from typing import List, Optional

from ..core.sequence import Event

class Tonnez:
    """Tonnez triad-relations calculator. Is node-based, so can be used as part of a search tree"""

    def __init__(self, root: Optional[int]=0, third: Optional[int]=4, fifth: Optional[int]=7):
        self.pitch_classes = [root % 12, third % 12, fifth % 12]

    @property
    def p(self) -> Tonnez:
        return Tonnez(
            root=self.pitch_classes[0],
            third=self.pitch_classes[1] - 1 % 12,
            fifth=self.pitch_classes[2])

    @property
    def r(self) -> Tonnez:
        return Tonnez(
            root=self.pitch_classes[2] + 2 % 12,
            third=self.pitch_classes[0],
            fifth=self.pitch_classes[1])

    @property
    def l(self) -> Tonnez:
        return Tonnez(
            fifth=self.pitch_classes[0] - 1 % 12,
            root=self.pitch_classes[1],
            third=self.pitch_classes[2])

    @property
    def pl(self) -> Tonnez:
        return Tonnez(
            root=self.pitch_classes[2] + 1 % 12,
            third=self.pitch_classes[0],
            fifth=self.pitch_classes[1] - 1 % 12)

    @property
    def pr(self) -> Tonnez:
        return Tonnez(
            third=self.pitch_classes[2],
            root=self.pitch_classes[1] - 1 % 12,
            fifth=self.pitch_classes[0] - 2 % 12)

    @property
    def lp(self) -> Tonnez:
        return Tonnez(
            root=self.pitch_classes[1],
            third=self.pitch_classes[2] + 1 % 12,
            fifth=self.pitch_classes[0] -1 % 12)

    @property
    def rp(self) -> Tonnez:
        return Tonnez(
            root=self.pitch_classes[2] + 2 % 12,
            third=self.pitch_classes[0] + 1 % 12,
            fifth=self.pitch_classes[1])

    def child_nodes(self) -> List[Tonnez]:
        return [self.p, self.r, self.l, self.pl, self.pr, self.lp, self.rp]

    def __repr__(self):
        return str(self.pitch_classes)

    def __eq__(self, other):
        if isinstance(other, Tonnez):
            return other.pitch_classes == self.pitch_classes
        if isinstance(other, list):
            return other == self.pitch_classes
        return False

    def as_event(self):
        return Event(pitches=self.pitch_classes)

