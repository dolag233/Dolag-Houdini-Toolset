"""
    config some items for DolagPlugin
    @NOTE: This file is run in top-level
    so cannot do any relative path operation
    solving by configuring the sys.path
"""
if __name__ == "__main__":
    import os
    import sys

    # DOLAG_HOUDINI_PATH will be create by DolagPlugin.json
    # and append some our python load dir into the sys.path
    if "DOLAG_HOUDINI_PATH" in os.environ.keys():
        dolag_path = os.environ["DOLAG_HOUDINI_PATH"]
        # python script path
        sys.path.append(dolag_path + "\\scripts")
        # custom python snippet path
        sys.path.append(dolag_path + "\\python\\python2.7libs")
        sys.path.append(dolag_path + "\\python\\custom")
        sys.path.append(dolag_path + "\\python")
        sys.path.append(dolag_path)
        # env DOLAG_PYTHON_LIB path
        for pylib_path in os.environ["DOLAG_PYTHON_LIB"]:
            if pylib_path not in sys.path:
                sys.path.append(pylib_path)

    else:
        # cannot use hou.ui because of partial initialization
        print("Error: Failed to config Dolag Tools.\nPlease Configure $HOUDINI_USER_PREF/packages/DolagPlugin.json")
