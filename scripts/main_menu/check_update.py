from __future__ import print_function, division

import os
import sys
import json
import zipfile
import tempfile
import shutil
import subprocess
import webbrowser

try:
    # Py3
    from urllib.request import urlopen, Request
except Exception:
    # Py2
    from urllib2 import urlopen, Request

try:
    import ssl
    _SSL_CTX = ssl._create_unverified_context()
except Exception:
    _SSL_CTX = None

try:
    import hou
except Exception:
    hou = None

from _utils.qt_compat_layer import QtCore, QtGui, QtG, exec_dialog


def _plugin_root():
    # Prefer environment variables configured by DolagPlugin.json
    env_keys = ['DOLAG_HOUDINI_PATH', 'DOLAG_PATH']
    for k in env_keys:
        p = os.environ.get(k)
        if p:
            try:
                if hou and hasattr(hou, 'expandString'):
                    p = hou.expandString(p)
            except Exception:
                pass
            return os.path.abspath(p)

    # Fallback to file location when __file__ is available
    try:
        if '__file__' in globals():
            here = os.path.abspath(os.path.dirname(__file__))
            return os.path.abspath(os.path.join(here, '..', '..'))
    except Exception:
        pass

    # Last resort: walk up from CWD until manifest.json is found
    cwd = os.getcwd()
    probe = cwd
    for _ in range(6):
        if os.path.isfile(os.path.join(probe, 'manifest.json')):
            return probe
        parent = os.path.dirname(probe)
        if parent == probe:
            break
        probe = parent
    return cwd

def _get_houdini_user_dir():
    """Get Houdini user documents directory like C:/Users/username/Documents/houdini19.5"""
    try:
        if hou and hasattr(hou, 'houdiniPath'):
            # Get from Houdini's internal path
            paths = hou.houdiniPath()
            for p in paths:
                if 'Documents' in p and 'houdini' in p:
                    # Extract base houdini user dir (remove any subdirs)
                    parts = p.split(os.sep)
                    for i, part in enumerate(parts):
                        if part.startswith('houdini') and any(c.isdigit() for c in part):
                            return os.sep.join(parts[:i+1])
    except Exception:
        pass
    
    # Fallback: current plugin root's parent should be houdini user dir
    root = _plugin_root()
    parent = os.path.dirname(root)
    if os.path.basename(parent).startswith('houdini'):
        return parent
    return root


def _read_manifest():
    mf = os.path.join(_plugin_root(), 'manifest.json')
    try:
        with open(mf, 'r') as f:
            return json.load(f)
    except Exception:
        return {
            'name': 'DolagPlugin',
            'version': '0.0.0',
            'github_repo': 'https://github.com/dolag233/Dolag-Houdini-Toolset'
        }


def _parse_repo(url):
    # expect https://github.com/{owner}/{repo}
    try:
        parts = url.strip('/').split('/')
        owner, repo = parts[-2], parts[-1]
        if repo.endswith('.git'):
            repo = repo[:-4]
        return owner, repo
    except Exception:
        return 'dolag233', 'Dolag-Houdini-Toolset'


def _http_get(url, timeout=8):
    try:
        headers = {'User-Agent': 'Dolag-Updater'}
        req = Request(url, headers=headers)
        if _SSL_CTX is not None:
            resp = urlopen(req, context=_SSL_CTX, timeout=timeout)
        else:
            resp = urlopen(req, timeout=timeout)
        data = resp.read()
        return data
    except Exception:
        return None


def _find_git():
    # shutil.which not in Py2
    paths = os.environ.get('PATH', '').split(os.pathsep)
    candidates = ['git', 'git.exe']
    for p in paths:
        for exe in candidates:
            full = os.path.join(p, exe)
            if os.path.isfile(full):
                return full
    # common Windows install path
    extra = [
        r'C:\Program Files\Git\bin\git.exe',
        r'C:\Program Files\Git\cmd\git.exe',
    ]
    for full in extra:
        if os.path.isfile(full):
            return full
    return None


def _version_tuple(v):
    if not v:
        return (0, 0, 0)
    v = str(v).strip()
    if v.startswith('v'):
        v = v[1:]
    parts = []
    for s in v.split('.'):
        try:
            parts.append(int(s))
        except Exception:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def _latest_tag(owner, repo):
    # Use RSS feed only (no API rate limit, no auth needed)
    rss_url = 'https://github.com/{}/{}/releases.atom'.format(owner, repo)
    try:
        data = _http_get(rss_url, timeout=5)
        if data:
            content = data.decode('utf-8')
            import re
            # RSS format: first <title> is feed title, next <title> in <entry> is version
            # Look for pattern: <entry>....<title>VERSION</title>
            entry_pattern = r'<entry>.*?<title>([^<]+)</title>'
            match = re.search(entry_pattern, content, re.DOTALL)
            if match:
                version = match.group(1).strip()
                # Basic sanity check: should look like a version (contains digit)
                if any(c.isdigit() for c in version):
                    return version
    except Exception:
        pass
    return None


def _download_zip(owner, repo, tag, dest_zip):
    # Source archive URL
    url = 'https://github.com/{}/{}/archive/refs/tags/{}.zip'.format(owner, repo, tag)
    data = _http_get(url)
    if not data:
        return False, 'Download failed'
    try:
        with open(dest_zip, 'wb') as f:
            f.write(data)
        return True, dest_zip
    except Exception as e:
        return False, str(e)


def _iter_files(root, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = set()
    for base, dirs, files in os.walk(root):
        # prune
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.endswith('__pycache__')]
        for f in files:
            yield os.path.join(base, f)


def _copy_tree(src_root, dst_root, on_step=None):
    # exclude user_data to keep user prefs
    exclude_dirs = {'user_data', '.git'}
    all_files = list(_iter_files(src_root, exclude_dirs))
    total = len(all_files)
    done = 0
    for f in all_files:
        rel = os.path.relpath(f, src_root)
        target = os.path.join(dst_root, rel)
        td = os.path.dirname(target)
        if not os.path.isdir(td):
            try:
                os.makedirs(td)
            except Exception:
                pass
        try:
            shutil.copy2(f, target)
        except Exception:
            # best-effort copy; skip locked files
            try:
                shutil.copy(f, target)
            except Exception:
                pass
        done += 1
        if on_step is not None:
            on_step(done, total)


def _check_latest_sync():
    """Synchronously check latest version - no threading"""
    mf = _read_manifest()
    owner, repo = _parse_repo(mf.get('github_repo', ''))
    latest = _latest_tag(owner, repo)
    if latest:
        return latest, ''
    else:
        return '', 'Unable to fetch latest version'





class UpdateDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(UpdateDialog, self).__init__(parent)
        self.setWindowTitle('Dolag Updater')
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self._latest = None
        self._setup_ui()
        self._check_latest()

    def _setup_ui(self):
        lay = QtGui.QVBoxLayout(self)

        mf = _read_manifest()
        owner, repo = _parse_repo(mf.get('github_repo', ''))
        self.repo_url = 'https://github.com/{}/{}'.format(owner, repo)

        form = QtGui.QFormLayout()
        self.lb_current = QtGui.QLabel(str(mf.get('version', '0.0.0')))
        self.lb_latest = QtGui.QLabel('checking...')
        self.lb_latest.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        form.addRow('Current Version:', self.lb_current)
        form.addRow('Latest Version:', self.lb_latest)
        lay.addLayout(form)

        self.progress = QtGui.QProgressBar()
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.progress.setVisible(False)  # Hidden by default
        lay.addWidget(self.progress)

        btns = QtGui.QHBoxLayout()
        self.btn_check = QtGui.QPushButton('Re-check')
        self.btn_zip = QtGui.QPushButton('Update')
        btns.addWidget(self.btn_check)
        btns.addWidget(self.btn_zip)
        if _find_git():
            self.btn_git = QtGui.QPushButton('Update via Git')
            btns.addWidget(self.btn_git)
        lay.addLayout(btns)

        self.btn_check.clicked.connect(self._check_latest)
        self.btn_zip.clicked.connect(self._do_zip_update)
        if _find_git():
            self.btn_git.clicked.connect(self._do_git_update)

        self.setMinimumWidth(420)
        # Light style polish for better look in Houdini dark theme
        self.setStyleSheet('''
        QDialog { background:#2b2b2b; }
        QLabel { color:#dddddd; }
        QLabel.update-available { color:#4CAF50; font-weight:bold; }
        QProgressBar { background:#3a3a3a; height:12px; border:1px solid #4a4a4a; }
        QProgressBar::chunk { background:#2e7dd1; }
        QPushButton { padding:4px 10px; }
        ''')

    def _check_latest(self):
        self.lb_latest.setText('checking...')
        # Force UI update
        if hasattr(QtCore.QCoreApplication, 'processEvents'):
            QtCore.QCoreApplication.processEvents()
        
        # Synchronous check - no threading
        latest, error = _check_latest_sync()
        
        if latest:
            self._latest = latest
            # compare
            current_text = self.lb_current.text()
            cur = _version_tuple(current_text)
            lat = _version_tuple(latest)
            if lat > cur:
                self.lb_latest.setText(latest + '  (update available)')
                self.lb_latest.setProperty('class', 'update-available')
                self.lb_latest.style().unpolish(self.lb_latest)
                self.lb_latest.style().polish(self.lb_latest)
            else:
                self.lb_latest.setText(latest + '  (up to date)')
                self.lb_latest.setProperty('class', '')
                self.lb_latest.style().unpolish(self.lb_latest)
                self.lb_latest.style().polish(self.lb_latest)
        else:
            self._latest = None
            self.lb_latest.setText('N/A ({})'.format(error))

    def _do_zip_update(self):
        tag = self._latest
        if not tag:
            QtGui.QMessageBox.warning(self, 'Update', 'Latest version not available.')
            return
        
        # Show progress and start download
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.progress.setValue(0)
        if hasattr(QtCore.QCoreApplication, 'processEvents'):
            QtCore.QCoreApplication.processEvents()
        
        try:
            mf = _read_manifest()
            owner, repo = _parse_repo(mf.get('github_repo', ''))
            tmp = tempfile.mkdtemp(prefix='dolag_update_')
            zf_path = os.path.join(tmp, 'src.zip')
            
            ok, msg = _download_zip(owner, repo, tag, zf_path)
            if not ok:
                shutil.rmtree(tmp, ignore_errors=True)
                self.progress.setVisible(False)
                QtGui.QMessageBox.warning(self, 'Update', 'Download failed: {}'.format(msg))
                return
            
            with zipfile.ZipFile(zf_path, 'r') as zf:
                zf.extractall(tmp)
            
            # Find extracted folder (should be 'Dolag-Houdini-Toolset-{tag}')
            src_root = None
            for name in os.listdir(tmp):
                p = os.path.join(tmp, name)
                if os.path.isdir(p) and name.lower().startswith(repo.lower() + '-'):
                    src_root = p
                    break
            
            if src_root is None:
                shutil.rmtree(tmp, ignore_errors=True)
                self.progress.setVisible(False)
                QtGui.QMessageBox.warning(self, 'Update', 'Invalid zip structure')
                return
            
            # Install following README instructions:
            # 1. Extract to correct DolagPlugin folder
            # 2. Copy DolagPlugin.json to packages folder
            houdini_user_dir = _get_houdini_user_dir()
            dolag_plugin_dir = os.path.join(houdini_user_dir, 'DolagPlugin')
            packages_dir = os.path.join(houdini_user_dir, 'packages')
            
            # Ensure packages directory exists
            if not os.path.exists(packages_dir):
                os.makedirs(packages_dir)
            
            # Copy extracted content to DolagPlugin folder
            _copy_tree(src_root, dolag_plugin_dir)
            
            # Copy DolagPlugin.json to packages folder
            json_src = os.path.join(dolag_plugin_dir, 'DolagPlugin.json')
            json_dst = os.path.join(packages_dir, 'DolagPlugin.json')
            if os.path.exists(json_src):
                shutil.copy2(json_src, json_dst)
            
            shutil.rmtree(tmp, ignore_errors=True)
            
            self.progress.setRange(0, 1)
            self.progress.setValue(1)
            QtGui.QMessageBox.information(self, 'Update', 
                'Update completed successfully!\n\n'
                'Files installed to: {}\n'
                'Package config: {}\n\n'
                'Please restart Houdini to take effect.'.format(dolag_plugin_dir, json_dst))
            
        except Exception as e:
            self.progress.setVisible(False)
            QtGui.QMessageBox.warning(self, 'Update', 'Update failed: {}'.format(str(e)))

    def _do_git_update(self):
        tag = self._latest
        if not tag:
            QtGui.QMessageBox.warning(self, 'Update', 'Latest version not available.')
            return
        
        git = _find_git()
        if not git:
            QtGui.QMessageBox.warning(self, 'Update', 'Git not found')
            return
        
        # Show progress and start git clone
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.progress.setValue(0)
        if hasattr(QtCore.QCoreApplication, 'processEvents'):
            QtCore.QCoreApplication.processEvents()
        
        try:
            mf = _read_manifest()
            repo_url = mf.get('github_repo', '')
            
            # Install following README instructions using Git
            houdini_user_dir = _get_houdini_user_dir()
            dolag_plugin_dir = os.path.join(houdini_user_dir, 'DolagPlugin')
            packages_dir = os.path.join(houdini_user_dir, 'packages')
            
            # Ensure packages directory exists
            if not os.path.exists(packages_dir):
                os.makedirs(packages_dir)
            
            # Remove existing DolagPlugin directory if it exists
            if os.path.exists(dolag_plugin_dir):
                shutil.rmtree(dolag_plugin_dir)
            
            # Clone directly to DolagPlugin folder
            cmd = [git, 'clone', '--depth', '1', '--branch', tag, repo_url, dolag_plugin_dir]
            subprocess.check_call(cmd)
            
            # Copy DolagPlugin.json to packages folder
            json_src = os.path.join(dolag_plugin_dir, 'DolagPlugin.json')
            json_dst = os.path.join(packages_dir, 'DolagPlugin.json')
            if os.path.exists(json_src):
                shutil.copy2(json_src, json_dst)
            
            self.progress.setRange(0, 1)
            self.progress.setValue(1)
            QtGui.QMessageBox.information(self, 'Update', 
                'Update completed successfully!\n\n'
                'Files installed to: {}\n'
                'Package config: {}\n\n'
                'Please restart Houdini to take effect.'.format(dolag_plugin_dir, json_dst))
            
        except Exception as e:
            self.progress.setVisible(False)
            QtGui.QMessageBox.warning(self, 'Update', 'Update failed: {}'.format(str(e)))

    def closeEvent(self, ev):
        # Simple close without thread management
        self.done(0)


def open_updater():
    dlg = UpdateDialog()
    # Use same exec method as other dialogs
    (getattr(dlg, 'exec', None) or getattr(dlg, 'exec_', None))()


def _report_error(prefix, e):
    try:
        import traceback
        tb = traceback.format_exc()
        msg = '{}: {}\n\n{}'.format(prefix, e, tb)
        if hou and hasattr(hou, 'ui'):
            hou.ui.displayMessage(msg)
        else:
            print(msg)
    except Exception:
        pass


# When invoked via Houdini menu (scriptPath), execute immediately
try:
    open_updater()
except Exception as _e:
    _report_error('Failed to open updater', _e)


if __name__ == '__main__':
    # allow running standalone for quick test
    from _utils.qt_compat_layer import qapplication_instance
    app = qapplication_instance('dolag_updater')
    try:
        open_updater()
    except Exception as _e:
        _report_error('Failed to open updater', _e)

