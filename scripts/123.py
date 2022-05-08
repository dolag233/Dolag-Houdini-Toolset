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
            # and rename it as "DolagHoudiniToolSet" or "Dolag-Houdini_Toolset"
            if "DolagHoudiniToolSet" in hou_path.split() or "Dolag-Houdini_Toolset" in hou_path.split():
                os.environ["DOLAG_HOUDINI_PATH"] = hou_path
                # python script path
                sys.path.append(hou_path + "\\scripts")
                # custom python snippet path
                sys.path.append(hou_path + "\\python\\include")
                break

            else:
                hou.ui.displayMessage("Error: Failed to config Dolag Tools.\nPlease Configure houdini.env")

        print("Dolag houdini path : " + os.environ["DOLAG_HOUDINI_PATH"])

    else:
        hou.ui.displayMessage("Error: Failed to config Dolag Tools.\nPlease Configure houdini.env")