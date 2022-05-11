"""
    edit env json
"""
import subprocess
import os
from error.error_report import displayError

pref_dir = os.environ["HOUDINI_USER_PREF_DIR"]
ENV_JSON_PATH = pref_dir + r"/packages/DolagPlugin.json"
if os.path.isfile(ENV_JSON_PATH):
    if "Windows" == os.environ["HOUDINI_OS"]:
        subprocess.call(["notepad", ENV_JSON_PATH])
    else:
        subprocess.call(["nano", ENV_JSON_PATH])

else:
    displayError("env_json")

