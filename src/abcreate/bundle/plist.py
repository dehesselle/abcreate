from pathlib import Path
import logging
import importlib.resources
from shutil import copy
from enum import Enum
import plistlib

log = logging.getLogger("plist")


class Plist:
    PLIST_NAME = "Info.plist"

    class Key(Enum):
        CFBUNDLEEXECUTABLE = "CFBundleExecutable"
        CFBUNDLEICONFILE = "CFBundleIconFile"
        CFBUNDLELOCALIZATIONS = "CFBundleLocalizations"

    def __init__(self, bundle_dir: Path):
        self.bundle_dir = bundle_dir

    @property
    def target_path(self) -> Path:
        return self.bundle_dir / "Contents" / self.PLIST_NAME

    def install(self):
        if self.target_path.exists():
            log.debug(f"already installed {self.target_path}")
        else:
            self.target_path.parent.mkdir(parents=True, exist_ok=True)
            with importlib.resources.path("abcreate.bundle", self.PLIST_NAME) as source:
                log.debug(f"creating {self.target_path.as_posix()}")
                copy(source, self.target_path)

    @property
    def is_installed(self) -> bool:
        return self.target_path.exists()

    def _write(self, key: str, value: str):
        if plist := self._read_all():
            plist[key] = value
            with open(self.target_path, "wb") as file:
                plistlib.dump(plist, file)

    def _read_all(self):
        if self.is_installed:
            with open(self.target_path, "rb") as file:
                return plistlib.load(file)
        else:
            log.error(f"{self.PLIST_NAME} hasn't been installed yet")
            return None

    def _read(self, key: str) -> str:
        if plist := self._read_all():
            return plist[key]
        else:
            return str()

    @property
    def CFBundleExecutable(self) -> str:
        return self._read(self.Key.CFBUNDLEEXECUTABLE.value)

    @CFBundleExecutable.setter
    def CFBundleExecutable(self, value):
        self._write(self.Key.CFBUNDLEEXECUTABLE.value, value)

    @property
    def CFBundleIconFile(self) -> str:
        return self._read(self.Key.CFBUNDLEICONFILE.value)

    @CFBundleIconFile.setter
    def CFBundleIconFile(self, value):
        self._write(self.Key.CFBUNDLEICONFILE.value, value)

    @property
    def CFBundleLocalizations(self):
        return self._read(self.Key.CFBUNDLELOCALIZATIONS.value)

    @CFBundleLocalizations.setter
    def CFBundleLocalizations(self, value):
        self._write(self.Key.CFBUNDLELOCALIZATIONS.value, value)
