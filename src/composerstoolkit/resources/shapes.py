import math

def curve_target(time, length=20, start_value=60, end_value=127, f=math.sin):
    """
    Typically used to generate musical materials that curve upwards or downwards in pitch, accels/decel etc or
    any value that be modulated on a curved plain.
    Calculate the position on a 1/4 of a curve as a function of time, where:
    time - the current time elasped (or horizontal distance / x axis)
    length - the duration of the curve object
    start_value - the origin of the curve (at time = 0)
    end_value - the target peak or trough of the curve. If this is greater than start_value, it will be an ascending
        curve, otherwise will descend
    f - the function of the number of degrees traversed (math.sin or math.cos)
    """
    if start_value < end_value:
        angle = time / length * 90
    else:
        angle = (time / length * 90) + 180
    _sin = f(math.radians(angle))
    target = math.ceil(_sin * (abs(end_value-start_value))) + start_value
    return target