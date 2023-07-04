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


# copy left part to right when LtoR == 1, vise versa
def mirrorRamp(parm, LtoR):
    parm = dp.getParm(parm)
    if parm is None:
        return

    if not isinstance(parm.parmTemplate(), hou.RampParmTemplate):
        return

    ramp = parm.evalAsRamp()
    values = ramp.values()
    keys = ramp.keys()
    basis = ramp.basis()

    if LtoR:
        # get mid index
        mid_idx = 0
        for i in range(len(keys)):
            if keys[i] >= 0.5:
                break
            mid_idx = i

        new_len = 2 * mid_idx + 2
        new_values = [0 for i in range(new_len)]
        new_keys = [0 for i in range(new_len)]
        new_basis = [0 for i in range(new_len)]

        # mirror values, keys and basis
        for i in range(mid_idx + 1):
            idx = i
            new_keys[idx] = keys[idx]
            new_keys[new_len - 1 - idx] = 1 - keys[idx]
            new_values[idx] = values[idx]
            new_values[new_len - 1 - idx] = values[idx]
            new_basis[idx] = basis[idx]
            new_basis[new_len - 1 - idx] = basis[idx]

        new_ramp = hou.Ramp(tuple(new_basis), tuple(new_keys), tuple(new_values))
        parm.set(new_ramp)

    else:
        # get mid index
        mid_idx = 0
        for i in range(len(keys)):
            idx = len(keys) - 1 - i
            if keys[idx] <= 0.5:
                break
            mid_idx = idx

        new_len = 2 * (len(keys) - mid_idx)
        new_values = [0 for i in range(new_len)]
        new_keys = [0 for i in range(new_len)]
        new_basis = [0 for i in range(new_len)]

        # mirror values, keys and basis
        for i in range(len(keys) - mid_idx):
            idx = i
            new_keys[-idx - 1] = keys[-idx - 1]
            new_keys[idx] = 1 - keys[-idx - 1]
            new_values[-idx - 1] = values[-idx - 1]
            new_values[idx] = values[-idx - 1]
            new_basis[-idx - 1] = basis[-idx - 1]
            new_basis[idx] = basis[-idx - 1]

        new_ramp = hou.Ramp(tuple(new_basis), tuple(new_keys), tuple(new_values))
        parm.set(new_ramp)


def randomizeRamp(parm, amp=0.2):
    import random
    parm = dp.getParm(parm)
    if parm is None:
        return

    if not isinstance(parm.parmTemplate(), hou.RampParmTemplate):
        return

    ramp = parm.evalAsRamp()
    values = ramp.values()
    keys = ramp.keys()
    basis = ramp.basis()

    len_keys = len(keys)

    new_values = [0 for i in range(len_keys)]
    new_keys = keys
    new_basis = basis

    # add a little salts
    for i in range(len_keys):
        idx = i
        new_values[idx] = values[idx] + ((random.random() - 0.5) * 2) * amp

    new_ramp = hou.Ramp(tuple(new_basis), tuple(new_keys), tuple(new_values))
    parm.set(new_ramp)


def subdivideRamp(parm, level=1):
    import random
    parm = dp.getParm(parm)
    if parm is None:
        return

    if not isinstance(parm.parmTemplate(), hou.RampParmTemplate):
        return

    ramp = parm.evalAsRamp()
    values = ramp.values()
    keys = ramp.keys()
    basis = ramp.basis()

    len_keys = len(keys)
    if len_keys <= 1:
        return

    subdivision = level + 1
    unit = 1 / subdivision
    len_new = subdivision * (len_keys - 1) + 1
    new_values = [0 for i in range(len_new)]
    new_keys = [0 for i in range(len_new)]
    new_basis = [0 for i in range(len_new)]

    # add a little salts
    for i in range(len_keys):
        idx = i
        new_idx = idx * subdivision
        if idx != (len_keys - 1):
            for j in range(subdivision):
                ji = j + 1
                new_values[new_idx + j + 1] = values[idx] * (1 - ji * unit) + values[idx + 1] * ji * unit
                new_keys[new_idx + j + 1] = keys[idx] * (1 - ji * unit) + keys[idx + 1] * ji * unit
                if (j - 1) > (subdivision + 2) / 2:
                    new_basis[new_idx + j + 1] = basis[idx + 1]
                else:
                    new_basis[new_idx + j + 1] = basis[idx]

        new_values[new_idx] = values[idx]
        new_keys[new_idx] = keys[idx]
        new_basis[new_idx] = basis[idx]

    new_ramp = hou.Ramp(tuple(new_basis), tuple(new_keys), tuple(new_values))
    parm.set(new_ramp)


def smoothRamp(parm, iter=1):
    import random
    parm = dp.getParm(parm)
    if parm is None:
        return

    if not isinstance(parm.parmTemplate(), hou.RampParmTemplate):
        return

    ramp = parm.evalAsRamp()
    values = ramp.values()
    keys = ramp.keys()
    basis = ramp.basis()

    len_keys = len(keys)

    new_values = [0 for i in range(len_keys)]
    new_keys = keys
    new_basis = basis

    weight = [0.041666667, 0.0833333333, 0.16666667, 0.41666666667, 0.16666667, 0.0833333333, 0.041666667]
    len_weight = len(weight)
    half_len_weight = (len_weight + 1) / 2
    def getValue(idx):
        idx = int(idx)
        if idx < 0:
            return values[0]

        elif idx > (len_keys - 1):
            return values[-1]

        else:
            return values[idx]

    for j in range(iter):
        # add a little salts
        for i in range(len_keys):
            idx = i
            for j in range(len_weight):
                sample_idx = idx + (j - (half_len_weight - 1))
                new_values[idx] += getValue(sample_idx) * weight[j]

        values = new_values

    new_ramp = hou.Ramp(tuple(new_basis), tuple(new_keys), tuple(new_values))
    parm.set(new_ramp)

