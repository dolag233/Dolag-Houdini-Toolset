from abc import abstractmethod, ABCMeta


class EvalBase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def eval(self):
        pass


class MatchScoreBase(EvalBase):
    __metaclass__ = ABCMeta

    def __init__(self, search_str, match_str, score_bias, score_grain=0.00001):
        self.search_str = search_str
        self.match_str = match_str
        self.score_bias = score_bias
        self.score_grain = score_grain

    @abstractmethod
    # eval the match score of two str
    def eval(self, ignore_cap=True):
        pass

    @abstractmethod
    # each score method should strip the match string for the next score method
    def getRestStr(self):
        pass


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


class PrefixMatchScore(MatchScoreBase):
    def __init__(self, search_str, match_str):
        super(PrefixMatchScore, self).__init__(search_str, match_str, 3)
        self.lcs, self.first_match = lcString(search_str, match_str)

    def eval(self, ignore_cap=True):
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
        return score

    def getRestStr(self):
        if self.first_match != 0:
            return self.match_str

        return self.match_str[:len(self.lcs)]


class SubStringMatchScore(MatchScoreBase):
    def __init__(self, search_str, match_str):
        super(SubStringMatchScore, self).__init__(search_str, match_str, 2)
        self.lcs, self.first_match = lcString(search_str, match_str)

    def eval(self, ignore_cap=True):
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
        return score

    def getRestStr(self):
        if self.first_match == -1 or len(self.lcs) == 1:
            return self.match_str

        return self.match_str[self.first_match:self.first_match + len(self.lcs)]


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


class SubSequenceMatchScore(MatchScoreBase):
    def __init__(self, search_str, match_str):
        super(SubSequenceMatchScore, self).__init__(search_str, match_str, 1)
        self.lcs = lcSequence(search_str, match_str)
        self.first_match = -1
        if len(self.lcs) != 0:
            self.first_match = match_str.find(self.lcs[0])

    def eval(self, ignore_cap=True):
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
        if len(lcs) == 0 or first_match == -1:
            return score

        score += score_bias
        score += score_grain * (len(lcs) + self.first_match)
        return score

    def getRestStr(self):
        return self.match_str


class MatchStringBase(object):
    __metaclass__ = ABCMeta

    def __init__(self, string):
        self.string = string
        self.rank_score = 0

    def getRankScore(self):
        return self.rank_score

    def getString(self):
        return self.string


class AliasMatchString(MatchStringBase):
    def __init__(self, string):
        super(AliasMatchString, self).__init__(string=string)
        self.rank_score = 0.3


class ItemNameMatchString(MatchStringBase):
    def __init__(self, string):
        super(ItemNameMatchString, self).__init__(string=string)
        self.rank_score = 0.2


class CaptainMatchString(MatchStringBase):
    def __init__(self, string):
        super(CaptainMatchString, self).__init__(string=string)
        self.rank_score = 0.1


# @TODO divide this workflow
def evalScore(search_str, match_str):
    score = 0
    cur_match_str = match_str.getString()

    # eval with the order of prefix->substring->subsequence
    pms = PrefixMatchScore(search_str, cur_match_str)
    score += pms.eval()
    cur_match_str = pms.getRestStr()

    sstrs = SubStringMatchScore(search_str, cur_match_str)
    score += sstrs.eval()
    cur_match_str = sstrs.getRestStr()

    sseqs = SubSequenceMatchScore(search_str, cur_match_str)
    score += sseqs.eval()

    rank_score = match_str.getRankScore()
    return score, rank_score


# the final eval class
class EvalScore(EvalBase):
    def __init__(self, search_str, match_string_tuple):
        self.search_str = search_str
        self.match_strings = []
        for match_string in match_string_tuple:
            if isinstance(match_string, MatchStringBase):
                self.match_strings.append(match_string)

    def eval(self):
        max_score = [-1, -1]
        for match_string in self.match_strings:
            score, rank_score = evalScore(self.search_str, match_string)
            if score > max_score[0] or (score == max_score[0] and rank_score > max_score[1]):
                max_score = [score, rank_score]

        return tuple(max_score)
