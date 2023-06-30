def pipInstall(module_name: str, version: str = ""):
    import hou
    import os
    import threading
    import subprocess
    from pathlib import Path

    hou_path = hou.getenv("HFS")
    hou_path = str(Path(hou_path).resolve())
    python_path = hou_path + "/python37/python.exe"

    if os.path.exists(python_path):
        pass
    elif os.path.exists(hou_path + "/python27/python.exe"):
        python_path = hou_path + "/python27/python.exe"
    else:
        print("cannot find python!")

    if version == "" or version is None:
        print("start install {}".format(module_name))
        subprocess.call((python_path, '-m', r"pip install {}".format(module_name)))
    else:
        print("start install {}=={}".format(module_name, version))
        subprocess.call((python_path, '-m', r"pip install {}=={}".format(module_name, version)))

    print("finish downloading!")

def pipUninstall(module_name: str):
    import hou
    import os
    import threading
    import subprocess
    from pathlib import Path

    hou_path = hou.getenv("HFS")
    hou_path = str(Path(hou_path).resolve())
    python_path = hou_path + "/python37/python.exe"

    if os.path.exists(python_path):
        pass
    elif os.path.exists(hou_path + "/python27/python.exe"):
        python_path = hou_path + "/python27/python.exe"
    else:
        print("cannot find python!")

    print("start install {}}".format(module_name))
    subprocess.call((python_path, '-m', r"pip uninstall {}".format(module_name)))
    print("finish downloading!")


