from composerstoolkit import *

from composerstoolkit.resources.pulselabyrinth import PulseLabyrinth, ModulationMonad, dim, aug

n = ModulationMonad()
aug2 = ModulationMonad(factor=2, transform=aug)
dim2 = ModulationMonad(factor=2, transform=dim)
plus_aug2 = aug2 + n
aug2_dim2 = aug2 + dim2

transformations = {"n": n, "aug2": aug2, "dim2": dim2, "plus_aug2": plus_aug2, "aug2_dim2": aug2_dim2}

p = PulseLabyrinth(100, **transformations)
print("n", p.n)
print("aug2", p.aug2)
print("dim2", p.dim2)
print("plus_aug2", p.plus_aug2)
print("aug2_dim2", p.aug2_dim2)
routes = p.search_for_route(keep_route=lambda pl: pl.bpm > 400 and pl.bpm < 450, n_routes=5)


DRUM_PITCHES = [42,35,38,59,56]

sequences = [FiniteSequence() for i in range(5)]

for i, operations in enumerate(routes):
    print(operations)
    _pl = PulseLabyrinth(p.bpm, **p.child_nodes)
    for op in operations:
        events = []
        _pl = getattr(_pl, op)
        [events.append(Event(pitches=[DRUM_PITCHES[i]], duration=60/_pl.bpm)) for _i in range(int(_pl.bpm))]
        print(f"    -> {op} {_pl}")
        sequences[i].events = sequences[i].events + events

seq = Sequencer(bpm=60).add_sequences(*sequences)
seq.save_as_midi_file("pulses.midi")
