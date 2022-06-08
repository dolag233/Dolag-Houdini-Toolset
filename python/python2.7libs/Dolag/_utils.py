"""
    misc utils
"""
from abc import ABCMeta, abstractmethod


# use as meta class
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# subject class of observers
class Subject(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.__obsList = []
        self.__is_changed = False

    # add observer instance
    def addObs(self, obs):
        self.__obsList.append(obs)

    def removeObs(self, obs):
        if obs in self.__obsList:
            self.__obsList.remove(obs)

    def sortObs(self):
        pass

    def getObs(self):
        return self.__obsList

    def setChangedFlag(self, val):
        if isinstance(val, bool):
            self.__is_changed = val

    def notifyObs(self):
        pass


# longest common substring
def lcString(s1, s2):
    m = [[0 for i in range(len(s2) + 1)] for j in range(len(s1) + 1)]
    mmax = 0
    p = 0
    for i in range(len(s1)):
        for j in range(len(s2)):
            if s1[i] == s2[j]:
                m[i + 1][j + 1] = m[i][j] + 1
                if m[i + 1][j + 1] > mmax:
                    mmax = m[i + 1][j + 1]
                    p = i + 1

    first_match = p - mmax
    return s1[p - mmax:p], first_match


# longest common subsequence
def lcSequence(s1, s2):
    matrix = [["" for x in range(len(s2))] for x in range(len(s1))]
    for i in range(len(s1)):
        for j in range(len(s2)):
            if s1[i] == s2[j]:
                if i == 0 or j == 0:
                    matrix[i][j] = s1[i]
                else:
                    matrix[i][j] = matrix[i - 1][j - 1] + s1[i]
            else:
                matrix[i][j] = max(matrix[i - 1][j], matrix[i][j - 1], key=len)

    cs = matrix[-1][-1]

    return cs


def writeClipBoard(text):
    import PySide2
    clipboard = PySide2.QtWidgets.QApplication.clipboard()
    clipboard.clear()
    clipboard.setText(text)


def readClipBoard():
    import PySide2
    clipboard = PySide2.QtWidgets.QApplication.clipboard()
    return clipboard.text()
