import sys


def getPythonPath():
    import hou
    import os

    hou_path = hou.getenv("HFS")
    if sys.version_info.major == 3:
        from pathlib import Path
        hou_path = str(Path(hou_path).resolve())

    python_path_prefix = hou_path
    python_path = None
    # check python 3.x
    for i in range(7, 30):
        python_path = python_path_prefix + "/python3" + str(i) + "/python.exe"
        if not os.path.exists(python_path):
            python_path = None
            continue

        else:
            break

    # check python 2.7
    if not python_path:
        if os.path.exists(hou_path + "/python27/python.exe"):
            python_path = hou_path + "/python27/python.exe"

    return python_path

def pipInstall(module_name, version = ""):
    import subprocess

    python_path = getPythonPath()
    if not python_path:
        print("cannot find python!")

    if version == "" or version is None:
        print("start install {}".format(module_name))
        subprocess.call((python_path, '-m', 'pip', 'install', r"{}".format(module_name)), stderr=sys.stderr, stdout=sys.stdout, shell=True)
    else:
        print("start install {}=={}".format(module_name, version))
        subprocess.call((python_path, '-m', 'pip', 'install', r"{}=={}".format(module_name, version)), stderr=sys.stderr, stdout=sys.stdout, shell=True)

    print("finish downloading!")

def pipUninstall(module_name):
    import subprocess

    python_path = getPythonPath()
    if not python_path:
        print("cannot find python!")

    print("start install {}}".format(module_name))
    subprocess.call((python_path, '-m', 'pip', 'uninstall', module_name), stderr=sys.stderr, stdout=sys.stdout, shell=True)
    print("finish downloading!")


