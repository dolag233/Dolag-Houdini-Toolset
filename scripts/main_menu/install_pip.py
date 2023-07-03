import hou
import sys
import subprocess

hou_path = hou.getenv("HFS")
tmp_path = hou.getenv("HOUDINI_TEMP_DIR") + "/get-pip.py"
if sys.version_info.major == 3:
    from pathlib import Path
    hou_path = str(Path(hou_path).resolve())
    tmp_path = str(Path(hou.getenv("HOUDINI_TEMP_DIR")).resolve()) + "/get-pip.py"
shell_path = hou_path + "/bin/hcmd.exe"

print("download pip installation script...")

if sys.version_info.major == 3:
    subprocess.call((shell_path, '/c', r"curl https://bootstrap.pypa.io/get-pip.py -o {}".format(tmp_path)), stderr=sys.stderr, stdout=sys.stdout, shell=True)
elif sys.version_info.major == 2:
    subprocess.call((shell_path, '/c', r"curl https://bootstrap.pypa.io/pip/2.7/get-pip.py -o {}".format(tmp_path)), stderr=sys.stderr, stdout=sys.stdout, shell=True)

print("finish downloading!")

print("install pip...")
subprocess.call((shell_path, '/c', r"hython {}".format(tmp_path)), stderr=sys.stderr, stdout=sys.stdout, shell=True)
print("finish installing pip!")


