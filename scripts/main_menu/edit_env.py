"""
    edit env json
"""
import subprocess
import os
from error.error_report import displayError

pref_dir = os.environ["HOUDINI_USER_PREF_DIR"]
ENV_JSON_PATH = pref_dir + r"/packages/DolagPlugin.json"
if os.path.isfile(ENV_JSON_PATH):
    os.startfile(ENV_JSON_PATH)

else:
    displayError("env_json")

