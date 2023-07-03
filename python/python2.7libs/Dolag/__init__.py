"""
    Access submodule by:
    import Dolag
    Dolag.path
    Dolag.path.getRelativePath(src, dest)
"""

# different import behavior between python2 and python3
import platform
if platform.python_version_tuple()[0] == '2':
    import _pathutils as path
    import _nodeutils as node
    import _parmutils as parm
    import _utils as utils

elif platform.python_version_tuple()[0] == '3':
    from . import _pathutils as path
    from . import _nodeutils as node
    from . import _parmutils as parm
    from . import _utils as utils
