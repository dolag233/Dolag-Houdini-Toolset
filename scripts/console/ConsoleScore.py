from abc import abstractmethod, ABCMeta, abstractproperty
from functools import wraps
from Dolag import utils as du


class EvalBase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def eval(self):
        pass


class MatchScoreMethodBase(EvalBase):
    __metaclass__ = ABCMeta

    def __init__(self, search_str, match_str, score_bias, score_grain=0.00001):
        self.search_str = search_str
        self.match_str = match_str
        self.score_bias = score_bias
        self.score_grain = score_grain
        self.__priority = self.initPriority()

    @abstractmethod
    # eval the match score of two str
    def eval(self, ignore_cap=True):
        pass

    @abstractmethod
    # each score method should strip the match string for the next score method
    def getRestStr(self):
        pass

    def getPriority(self):
        return self.__priority

    def setMatchString(self, string):
        self.match_str = string

    @abstractmethod
    def initPriority(self):
        return -1


# longest common substring
def lcString(s1, s2):
    if len(s1) == 0 or len(s2) == 0:
        return '', -1

    m = [[0 for i in range(len(s2) + 1)] for j in range(len(s1) + 1)]
    mmax = 0
    p = -1
    for i in range(len(s1)):
        for j in range(len(s2)):
            if s1[i] == s2[j]:
                m[i + 1][j + 1] = m[i][j] + 1
                if m[i + 1][j + 1] > mmax:
                    mmax = m[i + 1][j + 1]
                    p = i + 1

    first_match = p - mmax
    return s1[p - mmax:p], first_match


class PrefixMatchScore(MatchScoreMethodBase):
    def __init__(self, search_str, match_str):
        super(PrefixMatchScore, self).__init__(search_str, match_str, 3)
        self.lcs = 0
        self.first_match = -1

    def eval(self, ignore_cap=True):
        self.lcs, self.first_match = lcString(self.search_str, self.match_str)
        search_str = self.search_str
        match_str = self.match_str
        score_bias = self.score_bias
        score_grain = self.score_grain
        score = 0
        if ignore_cap:
            search_str.upper()
            match_str.upper()

        lcs, first_match = self.lcs, self.first_match
        if first_match != 0:
            return score

        score += score_bias
        score += score_grain * len(lcs)
        score -= first_match * score_grain
        return score

    def getRestStr(self):
        if self.first_match != 0:
            return self.match_str

        return self.match_str[:len(self.lcs)]

    def initPriority(self):
        return 3


class SubStringMatchScore(MatchScoreMethodBase):
    def __init__(self, search_str, match_str):
        super(SubStringMatchScore, self).__init__(search_str, match_str, 2)
        self.lcs = ''
        self.first_match = -1

    def eval(self, ignore_cap=True):
        self.lcs, self.first_match = lcString(self.search_str, self.match_str)
        search_str = self.search_str
        match_str = self.match_str
        score_bias = self.score_bias
        score_grain = self.score_grain
        score = 0
        if ignore_cap:
            search_str.upper()
            match_str.upper()

        lcs, first_match = self.lcs, self.first_match
        # if just match 1 char, degenerate to lcSequence
        if len(lcs) == 1 or first_match == -1:
            return score

        score += score_bias
        score += score_grain * len(lcs)
        score -= first_match * score_grain
        return score

    def getRestStr(self):
        if self.first_match == -1 or len(self.lcs) == 1:
            return self.match_str

        return self.match_str[self.first_match:self.first_match + len(self.lcs)]

    def initPriority(self):
        return 2


def lcSequence(s1, s2):
    if len(s1) == 0 or len(s2) == 0:
        return ''

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


class SubSequenceMatchScore(MatchScoreMethodBase):
    def __init__(self, search_str, match_str):
        super(SubSequenceMatchScore, self).__init__(search_str, match_str, 1)
        self.lcs = ''
        self.first_match = -1

    def eval(self, ignore_cap=True):
        self.lcs = lcSequence(self.search_str, self.match_str)
        if len(self.lcs) != 0:
            self.first_match = self.match_str.find(self.lcs[0])

        search_str = self.search_str
        match_str = self.match_str
        score_bias = self.score_bias
        score_grain = self.score_grain
        score = 0
        if ignore_cap:
            search_str.upper()
            match_str.upper()

        lcs, first_match = self.lcs, self.first_match
        # match failed
        if len(lcs) == 0 or first_match == -1:
            return score

        score += score_bias
        score += score_grain * (len(lcs) - self.first_match)
        return score

    def getRestStr(self):
        return self.match_str

    def initPriority(self):
        return 1


class MatchScoreStringBase(du.Subject):
    __metaclass__ = ABCMeta

    def __init__(self, search_str, match_str):
        super(MatchScoreStringBase, self).__init__()
        self.match_str = match_str
        self.search_str = search_str
        self.rank_score = 0

    def getRankScore(self):
        return self.rank_score

    def getString(self):
        return self.match_str

    def eval(self):
        max_score = -1
        search_str = self.search_str
        match_str = self.match_str
        parm = (search_str, match_str)
        score_methods = []
        for score_method in self.getObs():
            score_method = score_method(*parm)
            score_methods.append((score_method.getPriority(), score_method))

        # sort it
        score_methods.sort()
        score_methods.reverse()
        score_methods = [pair[-1] for pair in score_methods]

        for score_method in score_methods:
            score_method.setMatchString(match_str)
            score = score_method.eval()
            match_str = score_method.getRestStr()

            max_score = max(max_score, score)

        return max_score, self.getRankScore()


class AliasMatchString(MatchScoreStringBase):
    def __init__(self, search_str, match_str, score_method_tuple=()):
        MatchScoreStringBase.__init__(self, search_str=search_str, match_str=match_str)
        for obs in score_method_tuple:
            # if is a class
            if isinstance(obs, type):
                self.addObs(obs)

        self.rank_score = 0.3


class ItemNameMatchString(MatchScoreStringBase):
    def __init__(self, search_str, match_str, score_method_tuple=()):
        MatchScoreStringBase.__init__(self, search_str=search_str, match_str=match_str)
        for obs in score_method_tuple:
            # if is a class
            if isinstance(obs, type):
                self.addObs(obs)

        self.rank_score = 0.2


class CaptainMatchString(MatchScoreStringBase):
    def __init__(self, search_str, match_str, score_method_tuple=()):
        MatchScoreStringBase.__init__(self, search_str=search_str, match_str=match_str)
        for obs in score_method_tuple:
            # if is a class
            if isinstance(obs, type):
                self.addObs(obs)

        self.rank_score = 0.1


# the final eval class
# observer mode
class EvalSearchStringScore(EvalBase, du.Subject):
    def __init__(self, mstring_tuple=()):
        EvalBase.__init__(self)
        du.Subject.__init__(self)
        self.match_strings = []
        for match_string in mstring_tuple:
            if isinstance(match_string, MatchScoreStringBase):
                self.addObs(match_string)

    def eval(self):
        max_score = (-1, -1)
        for match_string in self.getObs():
            score, rank_score = match_string.eval()
            if score > max_score[0]:
                max_score = (score, rank_score)

        return max_score
