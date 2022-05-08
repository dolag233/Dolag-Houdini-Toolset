import hou
import os
from os import environ as env
import re
from error.error_report import displayError


def __getVexFilenames(path):
    if not os.path.isdir(path):
        return []

    lists = os.listdir(path)
    filenames = []
    for i in lists:
        if not os.path.isfile(i):
            continue

        suffix = ("vfl", "h", "vex")
        if i.split('.')[-1] in suffix:
            filenames.append(i)

    return filenames


def __getPythonFilenames(path):
    if not os.path.isdir(path):
        return []

    lists = os.listdir(path)
    filenames = []
    for i in lists:
        if not os.path.isfile(i):
            continue

        suffix = ("py", )
        if i.split('.')[-1] in suffix:
            filenames.append(i)

    return filenames


def __getVexFunc(vex_path):
    if not os.path.isfile(vex_path):
        return []

    with open(vex_path, 'r') as f:
        f.seek(0, 0)
        content = f.read()
        re_pattern = r"function\s+(void|int|vector[|2|4]|float|string|int\[\]|matrix[|2|3]|)\s+\S+"


def searchVexList():
    houdini_paths = env["HOUDINI_PATH"].split(';')
    for houdini_path in houdini_paths:
        vfl_path_root = houdini_path + "\\vex"
        vfl_path_include = houdini_path + "\\vex\\include"
        vex_files = list()

        vex_files.append(__getVexFilenames(vfl_path_root))
        vex_files.append(__getVexFilenames(vfl_path_include))

