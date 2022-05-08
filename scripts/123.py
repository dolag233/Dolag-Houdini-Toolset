"""
    This file maybe loaded in shell mode
    os.getcwd() will return %HOME%
    __file__ is not defined and cannot do any relative path operation
    so config the PATH in houdini.env
"""
if __name__ == "__main__":
    import os
    import sys

    # set DOLAG_HOUDINI_PATH by the first HOUDINI_PATH containing "DolagHoudiniToolSet"
    # and append DOLAG_HOUDINI_PATH\scripts into the sys.path
    if "HOUDINI_PATH" in os.environ.keys():
        for hou_path in os.environ["HOUDINI_PATH"].split(';'):
            # place the main dir in %SYSTEM_DRIVER%\Users\%USER%\Documents
            # and rename it as "DolagHoudiniToolset" or "Dolag-Houdini_Toolset"
            if "DolagHoudiniToolset".upper() in hou_path.upper() or "Dolag-Houdini-Toolset".upper() in hou_path.upper():
                os.environ["DOLAG_HOUDINI_PATH"] = hou_path
                # python script path
                sys.path.append(hou_path + "\\scripts")
                # custom python snippet path
                sys.path.append(hou_path + "\\python\\include")
                sys.path.append(hou_path + "\\python\\custom")
                """
                # seems not work
                # custom vex snippet path
                if "HOUDINI_VEX_PATH" not in os.environ.keys():
                    os.environ["HOUDINI_VEX_PATH"] = hou_path + "\\vex\\custom;"
                else:
                    os.environ["HOUDINI_VEX_PATH"] = hou_path + "/vex/custom;" + os.environ["HOUDINI_VEX_PATH"]
                """

                break

        if "DolagHoudiniToolset".upper() not in os.environ["DOLAG_HOUDINI_PATH"].upper() and\
                "Dolag-Houdini-Toolset".upper() not in os.environ["DOLAG_HOUDINI_PATH"].upper():
            print("Error: Failed to config Dolag Tools.\nPlease Configure houdini.env")

    else:
        # cannot use hou.ui because of partial initialization
        print("Error: Failed to config Dolag Tools.\nPlease Configure houdini.env")
