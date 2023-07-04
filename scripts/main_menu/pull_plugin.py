import hou
import sys
import shutil
import os
import subprocess

dolag_path = hou.getenv("DOLAG_PATH")
hou_path = hou.getenv("HFS")
if sys.version_info.major == 3:
    from pathlib import Path
    hou_path = str(Path(hou_path).resolve())

shell_path = hou_path + "/bin/hcmd.exe"

print("Start pulling DolagPlugin...")

subprocess.call((shell_path, '/c', r'cd "{}" && git pull -b dev'.format(dolag_path)), stderr=sys.stderr, stdout=sys.stdout, shell=True)

new_json_path = os.path.abspath(dolag_path + "DolagPlugin.json")
json_path = os.path.abspath(dolag_path + "../../packages/DolagPlugin.json")

if os.path.exists(new_json_path):
    shutil.copy(new_json_path, json_path)

print("End pulling!\nAutomatically copied DolagPlugin.json to houdini X.Y/packages for you")



