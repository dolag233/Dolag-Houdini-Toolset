import hou

_error_msg =\
    {
        "config": "Error: Failed to config Dolag Tools",
        "filename": "Error: Illegal file name",
        "code": "Error: Wrong code type",
    }

def displayError(error_key):
    # print error message via hou.ui.displayMessage
    error_msg = error_key
    # if error_key not in the error dict, then print error_key
    if error_key in _error_msg.keys():
        error_msg = _error_msg[error_key]

    hou.ui.displayMessage(error_msg)