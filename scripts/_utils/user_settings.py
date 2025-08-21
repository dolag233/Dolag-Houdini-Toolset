"""Lightweight user settings persistence.

Cross-platform JSON store under user config directory.

Windows: %APPDATA%/Dolag/Houdini-Toolset
macOS:   ~/Library/Application Support/Dolag/Houdini-Toolset
Linux:   ~/.config/Dolag/Houdini-Toolset
"""

from __future__ import division

import os
import io
import sys
import json
import threading


def _base_dir():
    # Windows
    appdata = os.environ.get('APPDATA')
    if appdata:
        return os.path.join(appdata, 'Dolag', 'Houdini-Toolset')
    # macOS
    if sys.platform == 'darwin':
        return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'Dolag', 'Houdini-Toolset')
    # Linux/others
    return os.path.join(os.path.expanduser('~'), '.config', 'Dolag', 'Houdini-Toolset')


class UserSettings(object):
    def __init__(self, filename='settings.json'):
        self._dir = _base_dir()
        self._path = os.path.join(self._dir, filename)
        self._data = {}
        self._lock = threading.Lock()
        self._loaded = False

    @property
    def path(self):
        return self._path

    def _ensure_dir(self):
        try:
            if not os.path.exists(self._dir):
                os.makedirs(self._dir)
        except Exception:
            pass

    def load(self):
        with self._lock:
            if self._loaded:
                return self
            self._loaded = True
            try:
                if os.path.exists(self._path):
                    with io.open(self._path, 'r', encoding='utf-8', errors='ignore') as f:
                        self._data = json.load(f) or {}
            except Exception:
                self._data = {}
        return self

    def save(self):
        with self._lock:
            self._ensure_dir()
            try:
                with io.open(self._path, 'w', encoding='utf-8') as f:
                    json.dump(self._data or {}, f, indent=2)
            except Exception:
                pass
        return self

    # ---- section helpers ----
    def get_section(self, name, default=None):
        self.load()
        val = self._data.get(name)
        if val is None:
            return {} if default is None else default
        return val

    def set_section(self, name, mapping):
        self.load()
        with self._lock:
            self._data[name] = dict(mapping or {})
        self.save()
        return True

    def get(self, section, key, default=None):
        sec = self.get_section(section, {})
        return sec.get(key, default)

    def set(self, section, key, value):
        self.load()
        with self._lock:
            sec = self._data.setdefault(section, {})
            sec[key] = value
        self.save()
        return True

    def update(self, section, mapping):
        self.load()
        with self._lock:
            sec = self._data.setdefault(section, {})
            sec.update(mapping or {})
        self.save()
        return True

    # ---- raw helpers (store any JSON-serializable value at top-level key) ----
    def get_raw(self, key, default=None):
        self.load()
        return self._data.get(key, default)

    def set_raw(self, key, value):
        self.load()
        with self._lock:
            self._data[key] = value
        self.save()
        return True


# Global singleton for convenience
settings = UserSettings().load()


