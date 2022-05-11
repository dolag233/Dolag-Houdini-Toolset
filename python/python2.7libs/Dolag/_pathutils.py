# get the dest path related to src
def getRelativePath(src, dest):
    """

        consider src = /obj/geo/button1 and dest = /obj/geo/file/reload
        and the result should be ../geo/file/reload

        consider src = /obj/geo/subnet1/button1 and dest = /obj/geo/subnet2/file/reload
        and the result should be ../../subnet2/file/reload
    """

    # if equal
    if src == dest:
        return '.'
    src_path_list = src.split('/')
    dest_path_list = dest.split('/')
    if len(src_path_list) < 2 and len(dest_path_list) < 2:
        return

    src_parent = src_path_list[-2]
    res_str = ''
    # invalid input
    if len(src_path_list) == 0 or len(dest_path_list) == 0:
        return

    # discard common prefix
    while True:
        src_top = src_path_list[0]
        dest_top = dest_path_list[0]
        # if not match
        if src_top != dest_top:
            break
        # if run out token
        if len(src_path_list) == 1 or len(dest_path_list) == 1:
            break
        # pop front
        src_path_list.pop(0)
        dest_path_list.pop(0)

    # parent statement count
    parent_count = len(src_path_list)
    res_str = "../" * parent_count
    # @NOTE .. for /obj/geo/subnet/button is interpreter as /obj/geo
    dest_path_list.insert(0, src_parent)
    res_str += '/'.join(dest_path_list)
    return res_str
