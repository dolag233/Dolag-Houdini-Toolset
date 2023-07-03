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

print("add tuna mirror")

subprocess.call((shell_path, '/c', r"hython -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple"), stderr=sys.stderr, stdout=sys.stdout, shell=True)

print("finish!")