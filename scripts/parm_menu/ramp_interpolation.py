#coding=utf-8
"""
    set the interpolation type of ramp parameter
"""
import hou
from Dolag import parm as dp


# input "base" is the interpolate type in hou.rampBasis
def setRampInterpolation(parm, base):
    parm = dp.getParm(parm)
    if parm is None:
        return

    if not isinstance(parm.parmTemplate(), hou.RampParmTemplate):
        return

    ramp = parm.evalAsRamp()
    values = ramp.values()
    keys = ramp.keys()
    basis = tuple([base for i in keys])

    new_ramp = hou.Ramp(basis, keys, values)
    parm.set(new_ramp)
