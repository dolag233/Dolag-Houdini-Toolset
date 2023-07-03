import sys


def pipInstall(module_name, version = ""):
    import hou
    import os
    import threading
    import subprocess

    hou_path = hou.getenv("HFS")
    if sys.version_info.major == 3:
        from pathlib import Path
        hou_path = str(Path(hou_path).resolve())

    python_path = hou_path + "/python37/python.exe"

    if not os.path.exists(python_path):
        python_path = hou_path + "/python27/python.exe"
    if not os.path.exists(python_path):
        print("cannot find python!")
        return

    if version == "" or version is None:
        print("start install {}".format(module_name))
        subprocess.call((python_path, '-m', 'pip', 'install', r"{}".format(module_name)), stderr=sys.stderr, stdout=sys.stdout, shell=True)
    else:
        print("start install {}=={}".format(module_name, version))
        subprocess.call((python_path, '-m', 'pip', 'install', r"{}=={}".format(module_name, version)), stderr=sys.stderr, stdout=sys.stdout, shell=True)

    print("finish downloading!")

def pipUninstall(module_name):
    import hou
    import os
    import threading
    import subprocess

    hou_path = hou.getenv("HFS")
    if sys.version_info.major == 3:
        from pathlib import Path
        hou_path = str(Path(hou_path).resolve())

    python_path = hou_path + "/python37/python.exe"

    if not os.path.exists(python_path):
        python_path = hou_path + "/python27/python.exe"
    if not os.path.exists(python_path):
        print("cannot find python!")
        return

    print("start install {}}".format(module_name))
    subprocess.call((python_path, '-m', 'pip', 'uninstall', module_name), stderr=sys.stderr, stdout=sys.stdout, shell=True)
    print("finish downloading!")


