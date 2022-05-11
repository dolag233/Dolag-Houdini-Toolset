"""
    open plugin folder
"""
import os
from error.error_report import displayError

if "DOLAG_HOUDINI_PATH" in os.environ.keys():
    dolag_path = os.environ["DOLAG_HOUDINI_PATH"]
    if os.path.isdir(dolag_path):
        os.startfile(dolag_path)

    else:
        displayError("Error: error when open plugin folder")

else:
    displayError("Error: error when open plugin folder")