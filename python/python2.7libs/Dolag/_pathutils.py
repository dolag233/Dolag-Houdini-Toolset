import hou


# get the dest path related to src
def getRelativePath(src, dest):
    """
        consider src = /obj/geo/button1 and dest = /obj/geo/file/reload
        and the result should be ../geo/file/reload

        consider src = /obj/geo/subnet1/button1 and dest = /obj/geo/subnet2/file/reload
        and the result should be ../../subnet2/file/reload

        consider src = /obj/geo/file/reload and dest = /obj/geo/button1
        and the result should be ../button1
    """

    # if equal
    if src == dest:
        return './' + src.split('/')[-1]

    src_path_list = src.split('/')
    dest_path_list = dest.split('/')
    dest_parm_name = dest_path_list[-1]

    if len(src_path_list) < 2 and len(dest_path_list) < 2:
        return

    src_path_list.pop()
    dest_path_list.pop()
    res_str = ''
    # invalid input
    if len(src_path_list) == 0 or len(dest_path_list) == 0:
        return

    # discard common prefix
    while True:
        # if run out token
        if len(src_path_list) == 0 or len(dest_path_list) == 0:
            break

        src_top = src_path_list[0]
        dest_top = dest_path_list[0]
        # if not match
        if src_top != dest_top:
            break

        # pop front
        src_path_list.pop(0)
        dest_path_list.pop(0)

    # e.g. src = /obj/geo and dest = /obj/geo/file
    if len(src_path_list) == 0 and len(dest_path_list) > 0:
        dest_path_list.append(dest_parm_name)
        res_str = '/'.join(dest_path_list)

    # e.g. src = /obj/geo/sub1 and dest = /obj/geo/sub2/file
    elif len(src_path_list) > 0 and len(dest_path_list) > 0:
        dest_path_list.append(dest_parm_name)
        res_str = '../' * len(src_path_list) + '/'.join(dest_path_list)

    # e.g. src = /obj/geo/sub/file and dest = /obj/geo/
    else:
        res_str = "../" * len(src_path_list) + dest_parm_name

    return res_str


# increase file name
# e.g. dolag -> dolag_0 | dolag_999 -> dolag_1000
def increaseFileName(file_name, has_suffix=True):
    suffix = ''

    if has_suffix:
        suffix = '.' + str(file_name.split('.')[-1:][0])
        file_name = '.'.join(file_name.split('.')[:-1])

    # get version number
    version_start = 0
    version = getVersionNum(file_name)
    if version is None or len(version) == 0:
        return file_name + '_0' + suffix

    # get reversed version
    version_rev = version[::-1]
    # for "abc123", the version_start is 3
    version_start = len(file_name) - len(version)
    carry = 0
    for i in range(len(version_rev)):
        dig = version_rev[i]
        dig += carry
        if i == 0:
            dig += 1

        if dig >= 10:
            carry = 1
            dig -= 10

        else:
            carry = 0

        version_rev[i] = dig

        if i == len(version_rev) - 1 and carry:
            version_rev.append(1)

    version = version_rev[::-1]
    # convert to digital version
    version = ''.join(list(map(str, version)))
    file_name = file_name[:version_start] + version + suffix
    return file_name


def getVersionNum(filename):
    if not isinstance(filename, str):
        return None

    number = []
    for i in range(len(filename)):
        char = filename[-i - 1]
        if char.isdigit():
            number.append(int(char))

        else:
            if i == 0:
                return None

            break

    number.reverse()
    return number


# get hda library path
# return None if no otl file
def getHdaLibraryPath(hda_name):
    import os

    otl_scan_paths = hou.getenv("HOUDINI_OTLSCAN_PATH").split(';')
    otl_scan_paths += list(map(lambda x: x + "/otls", hou.getenv("HOUDINI_PATH").split(';')))
    otl_scan_paths += [hou.getenv("HFS") + "/houdini/otls"]
    # remove duplication
    otl_scan_paths = list(set(otl_scan_paths))
    hda_path = None
    # find matched hda path
    for path in otl_scan_paths:
        if not os.path.isdir(path):
            continue
        else:
            for f in os.listdir(path):
                file_path = "{0}/{1}".format(path, f)
                if os.path.isfile(file_path):
                    try:
                        if f[:-4] == hda_name:
                            hda_path = file_path
                            break
                    except:
                        continue

    return hda_path

