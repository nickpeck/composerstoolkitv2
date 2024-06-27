"""Randomly sort a set of modes and move a voicing through
the resulting sequence of tonalities, maintaining best voice leading
via a lexicon of acceptable chord voicings.
"""
from decimal import Decimal
import random

from composerstoolkit import *
from composerstoolkit.resources import scales, pitches

pf = pitches.PitchFactory()

# arbitary selection of scales
modes = [set(m) for m in [
    scales.mode("D", scales.MAJOR),
    scales.mode("E", scales.HAR_MINOR),
    scales.mode("C", scales.MEL_MINOR),
    scales.mode("B", scales.MAJOR),
    scales.mode("Bb", scales.HAR_MINOR)
]]

spacing = 3

# library of 5-note quartal voicings from each scale
chord_lexicon = list(chords_from_scale(scales.mode("D", scales.MAJOR), n_voices=5, spacing=spacing))\
    + list(chords_from_scale(scales.mode("E", scales.HAR_MINOR), n_voices=5, spacing=spacing))\
    + list(chords_from_scale(scales.mode("B", scales.MAJOR), n_voices=5, spacing=spacing))\
    + list(chords_from_scale(scales.mode("C", scales.MEL_MINOR), n_voices=5, spacing=spacing))\
    + list(chords_from_scale(scales.mode("Bb", scales.HAR_MINOR), n_voices=5, spacing=spacing))

random.shuffle(modes)

# Starting event, a typical quartal voicing using notes drawn from c major
start = Event([
    pf("D3"),
    pf("G4"),
    pf("C4"),
    pf("F4"),
    pf("A4")],
    duration=WHOLE_NOTE)

progression = Sequence.from_generator(
    select_chords(
        event=start,
        scales=Permutations(starting_list=modes).flatten(),
        chord_lexicon=chord_lexicon)
).transform(fit_to_range(
    min_pitch = pf("C3"),
    max_pitch = pf("C9")
))

Context.get_context().new_sequencer(bpm=300, playback_rate=1)\
    .add_sequence(progression)\
    .playback()
