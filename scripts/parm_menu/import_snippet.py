import hou
import os
from os import environ as env
import re
from error.error_report import displayError


def __getVexFilenames(path):
    if not os.path.isdir(path):
        return [], []

    lists = os.listdir(path)
    filenames = []
    for i in lists:
        i = path + '\\' + i
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
    suffix = ("vfl", "h", "vex")
    if not isinstance(vex_path, str) or vex_path.split('.')[-1] not in suffix:
        return [], None

    if not os.path.isfile(vex_path):
        return [], None

    func_names = []
    with open(vex_path, 'r') as f:
        f.seek(0, 0)
        content = f.read()
        # @TODO parser

        # discard comment
        pattern_comment = re.compile(r"/\*.*\*/|//[^\n]*", re.M | re.S)
        content = pattern_comment.sub('', content)
        # discard string
        pattern_string = re.compile(r"'.'|\".+\"")
        content = pattern_string.sub('', content)
        # match function signature
        pattern_func = re.compile(r"{0}void{1}|{0}int{1}|{0}vector[24]?{1}|{0}float{1}|{0}string{1}|{0}int\[\]{1}|{0}matrix[23]?{1}".format(r"function[\s\n]+", r"[\s\n]+\w+[\s\n]*"), re.M)
        func_sigs = pattern_func.findall(content)
        # match token
        pattern_token = re.compile(r"\w+")
        for func_sig in func_sigs:
            tokens = pattern_token.findall(func_sig)
            # append func name
            func_names.append(tokens[-1])

    return func_names, vex_path.split('\\')[-1]


def searchVexList():
    vex_funcs = {}
    houdini_paths = env["HOUDINI_PATH"].split(';')
    for houdini_path in houdini_paths:
        vfl_path_root = houdini_path + "\\vex"
        vfl_path_include = houdini_path + "\\vex\\include"
        vfl_path_custom = houdini_path + "\\vex\\custom"
        vex_files = list()

        vex_files += __getVexFilenames(vfl_path_root)
        vex_files += __getVexFilenames(vfl_path_include)
        vex_files += __getVexFilenames(vfl_path_custom)

        for vex_file in vex_files:
            func_names, file_name = __getVexFunc(vex_file)
            if file_name is not None and len(func_names) != 0:
                vex_funcs[file_name] = func_names

    print(vex_funcs)
