"""
    save project file Incrementally
    in the File menu
"""
from hou import hipFile as hf


def saveIncrease():
    name = hf.basename()
    file_name = ''
    suffix = ''

    # strip suffix
    if ".hip" == name[-4:]:
        suffix = ".hip"
        file_name = name.replace(".hip", '')
    elif ".hipnc" == name[-6:]:
        # if is hip non-commercial
        suffix = ".hipnc"
        file_name = name.replace(".hipnc", '')
    else:
        return

    # get version number
    file_name_rev = file_name[::-1]
    version = []
    version_start = 0
    for c in file_name_rev:
        if '9' >= c >= '0':
            version.append(int(c))
            version_start += 1
        else:
            break

    # for "abc123", the version_start is 3
    version_start = len(file_name) - version_start

    if len(version) > 0:
        # get reversed version
        version = version[::-1]
        carry = [0 for i in range(len(version) + 1)]
        for i in range(len(version)):
            dig = version[i]
            dig += 1 if i == 0 else 0
            # if carry
            dig_sum = dig + carry[i]
            if dig_sum >= 10:
                version[i] = dig_sum % 10
                carry[i + 1] = 1
            # else not carry
            else:
                version[i] = dig_sum

        # if version == something like 999999
        if carry[-1] == 1:
            version.append(1)
        version.reverse()

    else:
        version = [0]

    # convert to digital version
    version = ''.join(list(map(str, version)))
    file_name = HIP = hou.getenv("HIP") + '/' + file_name[:version_start] + version + suffix
    try:
        hf.save(file_name)
        hou.ui.setStatusMessage("Save file as {0}".format(file_name))
    except Exception:
        hou.ui.setStatusMessage("Save Failed")


saveIncrease()
