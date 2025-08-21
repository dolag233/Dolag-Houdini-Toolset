"""
    config some items for DolagPlugin
    @NOTE: This file is run in top-level
    Add necessary paths but avoid adding common module names like 'utils'
"""
if __name__ == "__main__":
    import os
    import sys

    # DOLAG_HOUDINI_PATH will be create by DolagPlugin.json
    if "DOLAG_HOUDINI_PATH" in os.environ.keys():
        dolag_path = os.environ["DOLAG_HOUDINI_PATH"]
        
        # Add the plugin root path
        if dolag_path not in sys.path:
            sys.path.insert(0, dolag_path)
            
        # Add scripts path but rename modules to avoid conflicts
        scripts_path = dolag_path + "\\scripts"
        if scripts_path not in sys.path:
            sys.path.insert(0, scripts_path)
            
        # Add python paths
        sys.path.insert(0, dolag_path + "\\python\\python2.7libs")
        sys.path.insert(0, dolag_path + "\\python\\custom")
        sys.path.insert(0, dolag_path + "\\python")
        
        # env DOLAG_PYTHON_LIB path
        if "DOLAG_PYTHON_LIB" in os.environ.keys():
            for pylib_path in os.environ["DOLAG_PYTHON_LIB"]:
                if pylib_path not in sys.path:
                    sys.path.insert(0, pylib_path)

    else:
        # cannot use hou.ui because of partial initialization
        print("Error: Failed to config Dolag Tools.\nPlease Configure $HOUDINI_USER_PREF/packages/DolagPlugin.json")
