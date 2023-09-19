import os
import shutil
from error.error_report import displayError

def travelDir(dir):
    if not os.path.isdir(dir):
        return

    items = os.listdir(dir)
    for item in items:
        item_path = os.path.join(dir, item)
        if os.path.isfile(item_path):
            if item.split(".")[-1] == "pyc":
                os.remove(item_path)
                continue

        elif os.path.isdir(item_path):
            if item == "__pycache__":
                shutil.rmtree(item_path)

            travelDir(item_path)


dolag_path = hou.getenv("DOLAG_PATH")
try:
    travelDir(dolag_path)
    hou.ui.setStatusMessage("Clear all py cache!")
except:
    displayError("Encounter errors when clearing py cache")



