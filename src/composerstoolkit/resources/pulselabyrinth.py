from __future__ import annotations
from typing import List, Callable, Dict
from functools import partial, reduce
from operator import add, sub, mul, truediv


aug = lambda monad, n: n * (1 / monad.factor)
dim = lambda monad, n: n * ( 1 / (1 / monad.factor))


class ModulationMonad:
    """Monadic constructor for metric modulation operations.
    ie augment by 2x, diminution by 3x
    Can be combined to form compound operations: ie augment by 2x and add original duration
    """
    def __init__(self, factor=1, transform = lambda m, n: n * m.factor):
        """
        factor - how much to scale by
        transform - the operation (typically aug or dim)
        """
        self.factor = factor
        self.transform = transform

    def _compound(self, other: ModulationMonad, op) -> ModulationMonad:
        def compound_transformation(monad, n):
            return reduce(op, [self.transform(self, n), other.transform(other, n)])
        return ModulationMonad(transform=compound_transformation)

    def __add__(self, other: ModulationMonad):
        return self._compound(other, add)

    def __sub__(self, other: ModulationMonad):
        return self._compound(other, sub)

    def __mul__(self, other: ModulationMonad):
        return self._compound(other, mul)

    def __div__(self, other: ModulationMonad):
        return self._compound(other, truediv)

    def __call__(self, pl: PulseLabyrinth):
        return PulseLabyrinth(bpm=self.transform(self, pl.bpm), **pl.child_nodes)


class PulseLabyrinth:
    """Represents a labyrinth tree of pulses that can be obtained
    from apply a set of operations to a tempo"""
    def __init__(self, bpm, **transformations: Dict[str, Callable]):
        self.bpm = bpm
        self.child_nodes = {
            "aug2": ModulationMonad(factor=2, transform=aug),
            "dim2": ModulationMonad(factor=2, transform=dim)
        }
        if transformations != {}:
            self.child_nodes = {n: c for n,c in transformations.items()}

    def __getattr__(self, item):
        return self.child_nodes[item](self)

    def __repr__(self):
        return f"<tempo={self.bpm}bpm>"

    def __eq__(self, other):
        if isinstance(other, PulseLabyrinth):
            return other.bpm == self.bpm
        if isinstance(other, list):
            return other == self.bpm
        return False

    def search_for_route(self, keep_route: Callable[[PulseLabyrinth], bool], n_routes: int):
        """Search for a route through the labyrinth, where keep_route returns true for
        a destination node"""
        explored_routes = []
        current_paths = [([k], getattr(self, k)) for k in self.child_nodes.keys()]
        solutions = []

        while len(solutions) < n_routes:
            candidate_routes = []
            for route, node in current_paths:
                if len(solutions) > n_routes - 1:
                    break
                if route in explored_routes:
                    continue
                if keep_route(node):
                    solutions.append(route)
                    explored_routes.append(route)
                    continue
                current_paths = current_paths + [(route + [k], getattr(node, k)) for k in self.child_nodes.keys()]
                explored_routes.append(route)

            current_paths = current_paths + candidate_routes
        return solutions
