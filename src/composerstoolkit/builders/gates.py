"""Gates - which are functions used to toggle transformations
on or off depending on the context at the time an event is emitted.
A gate is simply a function that returns a boolean - you can define your
own, although these are ones that are commonly used in algorithmic music.
"""

def time_gate(on=None, off=None):
    """Returns a gate that is True when the current
    beat offset is between on and out beats.
    This is intended for when a transformation is to be applied
    once during the course of a piece.
    If on is None, then it is applied from he start, update
    to out.
    If out is None, then it is applied from on up to
    the end of the piece.
    """
    def _gate(context) -> bool:
        nonlocal on
        nonlocal off
        offset = context.beat_offset
        if off is None and offset >= on:
            return True
        if offset >= on and offset < off:
            return True
        return False
    return _gate

def cyclic_time_gate(cycle_length, on, off):
    """Returns a gate that becomes true in a cyclic pattern.
    Where the period is cycle_length, and the transformation
    should be toggled ON for the period between on & off.
    This is intended for when a transformation is to be applied
    multiple times during the course of a piece.
    """
    if on is None and off is None:
        raise Exception("cyclic_time_gate: need either on and/or off")
    if on > cycle_length:
        raise Exception("cyclic_time_gate: on cannot be > cycle_length")
    if off > cycle_length:
        raise Exception("cyclic_time_gate: off cannot be > cycle_length")
    def _gate(context) -> bool:
        nonlocal cycle_length
        nonlocal on
        nonlocal off
        mod = context.beat_offset % cycle_length
        if mod >= on and mod < off:
            return True
        return False
    return _gate
