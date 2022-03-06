from typing import List, Tuple

from composerstoolkit.core import Graph, Sequence

class CBR:
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
        paths = []
        for graph in self.case_base:
            paths = paths + self._search_graph(graph, vectors)
        return paths
