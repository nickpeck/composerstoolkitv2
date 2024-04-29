#!/usr/bin/env/python

import sys, os
import pathlib

directory = input("Please enter the path to the project: ")
parts = []

not_ready = True
while not_ready:
    part_name = input("enter the name of an instumental part or n/N to continue: ").strip()
    if part_name.lower() == "n":
        not_ready = False
        break
    if not part_name.isidentifier():
        print(f"Invalid module name {part_name}")
        continue
    parts.append(str(part_name))

print(f"Directory: {directory} with parts {','.join(parts)}")
is_ok = input("Is this correct? y/n? ").strip()
if is_ok.lower() != "y":
    exit()

p = pathlib.Path(directory)
p.mkdir(parents=True, exist_ok=True)

for part in parts:
    with open(os.path.join(directory, f"{part}.py"), "w+") as mod:
        mod.write(f"""
from composerstoolkit import *

{part} = Sequence()""")

part_imports = "".join([f"from {part} import {part}\n" for part in parts])

sequencer_init = ["sequencer = Sequencer(bpm=120, debug=True)"]

for part in parts:
    sequencer_init.append(f"\\\n    .add_sequence({part})")

sequencer_init = ''.join(sequencer_init)

with open(os.path.join(directory, "main.py"), "w+") as main:
    main.write(f"""
from composerstoolkit import *
{part_imports}

init_reloader()

{sequencer_init}
    
sequencer.playback()""")

print("Done!")
print(f"run: python {directory}\main.py to start")