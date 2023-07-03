import sys

if sys.version_info.major == 2:
    '''
        python2 do not have builtin enum module
        so just imply with int
        use "if SnippetType.end > snippet_type >= 0:" to check if snippet_type belong to SnippetType
    '''
    class SnippetType(object):
        vex = 0
        python = 1
        end = 2

    # type of vex
    class VexType(object):
        h = 0
        vfl = 1
        end = 2

elif sys.version_info.major == 3:
    from enum import Enum, auto

    # type of snippet
    class SnippetType(Enum):
        vex = 0
        python = auto()
        end = auto()

        def __le__(self, b):
            if isinstance(b, int):
                return self.value <= b

            return self.value <= b.value

        def __lt__(self, b):
            if isinstance(b, int):
                return self.value < b

            return self.value < b.value

        def __ge__(self, b):
            if isinstance(b, int):
                return self.value >= b

            return self.value >= b.value

        def __gt__(self, b):
            if isinstance(b, int):
                return self.value > b

            return self.value > b.value

    # type of vex
    class VexType(Enum):
        h = 0
        vfl = auto()
        end = auto()

        def __le__(self, b):
            if isinstance(b, int):
                return self.value <= b

            return self.value <= b.value

        def __lt__(self, b):
            if isinstance(b, int):
                return self.value < b

            return self.value < b.value

        def __ge__(self, b):
            if isinstance(b, int):
                return self.value >= b

            return self.value >= b.value

        def __gt__(self, b):
            if isinstance(b, int):
                return self.value > b

            return self.value > b.value

