#coding=utf-8
"""
    open documentation file
"""
import os
from error.error_report import displayError

DOC_NAME = "文档模板"
if "DOLAG_HOUDINI_PATH" in os.environ.keys():
    dolag_path = os.environ["DOLAG_HOUDINI_PATH"]
    doc_path = dolag_path + '/doc/{0}.html'.format(DOC_NAME)
    if os.path.isfile(doc_path):
        os.startfile(doc_path)

    else:
        displayError("doc")

else:
    displayError("doc")
