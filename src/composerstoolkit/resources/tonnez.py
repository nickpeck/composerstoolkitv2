from __future__ import annotations
from typing import List, Optional

from ..core.sequence import Event

class Tonnez:
    """Tonnez triad-relations calculator. Is node-based, so can be used as part of a search tree"""
    MAJOR = "maj"
    MINOR = "min"

    def __init__(self, root: Optional[int]=0, third: Optional[int]=4, fifth: Optional[int]=7):
        self.pitch_classes = [root % 12, third % 12, fifth % 12]

    @property
    def root(self):
        return self.pitch_classes[0]

    @property
    def third(self):
        return self.pitch_classes[1]

    @property
    def fifth(self):
        return self.pitch_classes[2]

    @property
    def quality(self):
        if (self.fifth - self.root) % 12 == 7:
            if (self.third - self.root) % 12 == 4:
                return Tonnez.MAJOR
            if (self.third - self.root) % 12 == 3:
                return Tonnez.MINOR
        raise Exception(f"Unexpected chord quality - should be major or minor triad, got {self.pitch_classes}")

    @property
    def p(self) -> Tonnez:
        return Tonnez(
            root=self.root,
            third=self.third - 1 % 12 if self.quality == Tonnez.MAJOR else self.third + 1 % 12,
            fifth=self.fifth)

    @property
    def r(self) -> Tonnez:
        return Tonnez(
            root=self.fifth + 2 % 12 if self.quality == Tonnez.MAJOR else self.third,
            third=self.root if self.quality == Tonnez.MAJOR else self.fifth,
            fifth=self.third if self.quality == Tonnez.MAJOR else self.root - 2 % 12)

    @property
    def l(self) -> Tonnez:
        return Tonnez(
            fifth=self.root - 1 % 12 if self.quality == Tonnez.MAJOR else self.third,
            root=self.third if self.quality == Tonnez.MAJOR else self.fifth + 1 % 12,
            third=self.fifth if self.quality == Tonnez.MAJOR else self.root)

    @property
    def pl(self) -> Tonnez:
        return Tonnez(
            root=self.fifth + 1 % 12,
            third=self.root if self.quality == Tonnez.MAJOR else self.root - 1 % 12,
            fifth=self.third - 1 % 12 if self.quality == Tonnez.MAJOR else self.third)

    @property
    def pr(self) -> Tonnez:
        return Tonnez(
            third=self.fifth if self.quality == Tonnez.MAJOR else self.fifth -1 % 12,
            root=self.third - 1 % 12 if self.quality == Tonnez.MAJOR else self.third,
            fifth=self.root - 2 % 12)

    @property
    def lp(self) -> Tonnez:
        return Tonnez(
            root=self.third if self.quality == Tonnez.MAJOR else self.third + 1 % 12,
            third=self.fifth + 1 % 12 if self.quality == Tonnez.MAJOR else self.fifth,
            fifth=self.root - 1 % 12)

    @property
    def rp(self) -> Tonnez:
        return Tonnez(
            root=self.fifth + 2 % 12,
            third=self.root + 1 % 12 if self.quality == Tonnez.MAJOR else self.root,
            fifth=self.third if self.quality == Tonnez.MAJOR else self.third + 1 % 12)

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

