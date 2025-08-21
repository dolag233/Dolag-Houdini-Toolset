"""VS Code opener utilities with language-aware defaults and optional linter.

Usage examples:
  from _utils.open_vex_in_vsc import open_in_vscode
  new_py = open_in_vscode(py_text, language='python', wait=True)
  new_vex = open_in_vscode(vex_text, language='vex', wait=True)
"""

from __future__ import division

import os
import io
import sys
import json
import time
import shutil
import tempfile
import subprocess


# ---------------- internal helpers ----------------

def _ensure_text(text):
    if text is None:
        return ''
    if isinstance(text, bytes):
        try:
            return text.decode('utf-8', 'ignore')
        except Exception:
            return text.decode(errors='ignore')
    return str(text)


def _ext_for_language(language):
    lang = (language or '').lower()
    if lang in ('py', 'python'):
        return '.py'
    if lang in ('vex', 'vfl'):
        return '.vfl'
    if lang == 'json':
        return '.json'
    if lang in ('txt', 'text'):
        return '.txt'
    return '.txt'


def _find_code_cli():
    # Allow override by env var
    override = os.getenv('VSCODE_CLI') or os.getenv('VSCODE_PATH')
    if override and os.path.exists(override):
        return override
    # PATH
    for name in ('code', 'code.cmd', 'code.exe', 'Code.exe'):
        p = shutil.which(name)
        if p:
            return p
    # Typical Windows installs
    local = os.getenv('LOCALAPPDATA') or ''
    candidates = [
        os.path.join(local, 'Programs', 'Microsoft VS Code', 'bin', 'code.cmd'),
        os.path.join(local, 'Programs', 'Microsoft VS Code', 'Code.exe'),
        os.path.join(local, 'Programs', 'Microsoft VS Code Insiders', 'bin', 'code-insiders.cmd'),
        os.path.join(local, 'Programs', 'Microsoft VS Code Insiders', 'Code - Insiders.exe'),
    ]
    for p in candidates:
        if p and os.path.exists(p):
            return p
    for root in filter(None, [os.getenv('ProgramFiles'), os.getenv('ProgramW6432')]):
        for p in (
            os.path.join(root, 'Microsoft VS Code', 'bin', 'code.cmd'),
            os.path.join(root, 'Microsoft VS Code', 'Code.exe'),
        ):
            if os.path.exists(p):
                return p
    return shutil.which('code')


def _write_text(path, text):
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent)
    with io.open(path, 'w', encoding='utf-8') as f:
        f.write(_ensure_text(text))


def _prepare_workspace(language):
    """Create a temp workspace with language-specific settings (linters, association)."""
    ws_dir = os.path.join(tempfile.gettempdir(), 'dolag_vscode_workspace')
    vs_dir = os.path.join(ws_dir, '.vscode')
    try:
        if not os.path.exists(vs_dir):
            os.makedirs(vs_dir)
    except Exception:
        pass
    settings = {}
    # existing settings
    try:
        s_path = os.path.join(vs_dir, 'settings.json')
        if os.path.exists(s_path):
            with io.open(s_path, 'r', encoding='utf-8', errors='ignore') as f:
                settings = json.load(f)
    except Exception:
        settings = {}

    lang = (language or '').lower()
    if lang in ('python', 'py'):
        # Enable Python linting if extension exists; harmless otherwise
        settings.update({
            'python.linting.enabled': True,
            'python.linting.pylintEnabled': True,
            'python.linting.flake8Enabled': False,
            'python.analysis.typeCheckingMode': 'basic',
        })
    elif lang in ('vex', 'vfl'):
        # Ensure .vfl recognized as vex for syntax; linter depends on user extension
        fa = settings.get('files.associations', {})
        fa.update({'*.vfl': 'vex'})
        settings['files.associations'] = fa

    # write back
    try:
        with io.open(os.path.join(vs_dir, 'settings.json'), 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
    except Exception:
        pass
    return ws_dir


def _launch_vscode(file_path, workspace_dir, wait=True, reuse_window=True):
    cli = _find_code_cli() or 'code'
    args = []
    if reuse_window:
        args.append('--reuse-window')
    if wait:
        args.append('--wait')
    # open workspace folder to apply settings, and the file to edit
    args.append(workspace_dir)
    args.append(file_path)

    if sys.platform.startswith('win') and cli.lower().endswith(('.cmd', '.bat')):
        # .cmd requires shell
        cmdline = ' '.join(['"{0}"'.format(cli)] + ['"{0}"'.format(a) for a in args])
        return subprocess.call(cmdline, shell=True)
    else:
        return subprocess.call([cli] + args)


# ---------------- public API ----------------

def openInVscode(text, language='txt', wait=True):
    """Open text in VS Code with language-aware defaults; optionally block and return edited text.

    - language: 'python' | 'vex' | 'json' | 'txt' ... (affects file extension and workspace settings)
    - wait: True to block until VS Code closes the file and return edited content
    """
    text = _ensure_text(text)
    ext = _ext_for_language(language)
    ws_dir = _prepare_workspace(language)
    tmp_file = os.path.join(ws_dir, 'scratch_{0}{1}'.format(int(time.time() * 1000), ext))
    _write_text(tmp_file, text)

    _launch_vscode(tmp_file, ws_dir, wait=wait)

    if wait:
        try:
            with io.open(tmp_file, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return text
    return None


# --------------- heuristics for parm detection ---------------

def guess_language_from_parm(parm):
    """Guess code language from a hou.Parm using label/name/node type.

    Heuristics priority:
      1) parm.description().label() contains 'vex' / 'python'
      2) parm.parmTemplate().label() fallback
      3) parm.name() in common names: snippet/vex*/python/script
      4) node type name contains 'wrangle' -> vex, contains 'python' -> python
      5) default: 'txt'
    """
    try:
        import hou  # type: ignore
    except Exception:
        hou = None

    def _label_of(p):
        try:
            return (p.description().label() or '').lower()
        except Exception:
            try:
                return (p.parmTemplate().label() or '').lower()
            except Exception:
                return ''

    try:
        label = _label_of(parm)
        name = ''
        try:
            name = (parm.name() or '').lower()
        except Exception:
            pass
        ntype = ''
        try:
            n = parm.node()
            ntype = (n.type().name() if n is not None else '')
            ntype = ntype.lower() if ntype else ''
        except Exception:
            pass

        if 'vex' in label:
            return 'vex'
        if 'python' in label:
            return 'python'
        if name in ('snippet', 'vexsnippet', 'vex_snippet') or name.startswith('vex'):
            return 'vex'
        if name in ('python', 'pyscript', 'script'):
            return 'python'
        if 'wrangle' in ntype:
            return 'vex'
        if 'python' in ntype:
            return 'python'
    except Exception:
        pass
    return 'txt'


def openParmInVscode(parm, wait=True, write_back=True):
    """Open a hou.Parm in VS Code with guessed language; optionally write back on close."""
    try:
        lang = guess_language_from_parm(parm)
        try:
            text = parm.unexpandedString()
        except Exception:
            text = parm.eval() if hasattr(parm, 'eval') else ''
        edited = openInVscode(text, language=lang, wait=wait)
        if write_back and edited is not None:
            try:
                parm.set(edited)
            except Exception:
                pass
        return edited
    except Exception:
        return None

 
