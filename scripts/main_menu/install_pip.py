import hou
import os
import threading
import subprocess
from pathlib import Path

hou_path = hou.getenv("HFS")
hou_path = str(Path(hou_path).resolve())
python_path = hou_path + "/python37/python.exe"
shell_path = hou_path + "/bin/hcmd.exe"
tmp_path = str(Path(hou.getenv("HOUDINI_TEMP_DIR")).resolve()) + "/get-pip.py"
# print(python_path)
# print(shell_path)
# print(tmp_path)

if os.path.exists(python_path):
    pass
elif os.path.exists(hou_path + "/python27/python.exe"):
    python_path = hou_path + "/python27/python.exe"
else:
    print("cannot find python file!")

print("download pip installation script...")
subprocess.call((shell_path, '/c', r"curl https://bootstrap.pypa.io/get-pip.py -o {}".format(tmp_path)))
print("finish downloading!")

print("install pip...")
subprocess.call((shell_path, '/c', r"hython {}".format(tmp_path)))
print("finish installing pip!")


