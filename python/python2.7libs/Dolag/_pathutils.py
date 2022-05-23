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


# get hda library path
# return None if no otl file
def getHdaLibraryPath(hda_name):
    import os

    otl_scan_paths = hou.getenv("HOUDINI_OTLSCAN_PATH").split(';')
    otl_scan_paths += list(map(lambda x: x + "/otls", hou.getenv("HOUDINI_PATH").split(';')))
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

