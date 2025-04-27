# SPDX-FileCopyrightText: 2025 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from enum import Enum
from pathlib import Path
from typing import List
import subprocess
import shlex
import re
import logging

log = logging.getLogger("linkedobj")


class LinkedObject:
    class SystemLinkPath(Enum):
        SYSTEM = "/System"
        USR = "/usr"

    class RelativeLinkPath(Enum):
        EXECUTABLE_PATH = "@executable_path"
        LOADER_PATH = "@loader_path"
        RPATH = "@rpath"

    def __init__(self, path: Path):
        self.path = path

    @classmethod
    def is_relative_path(
        cls, path: Path, linkpath_type: RelativeLinkPath = None
    ) -> bool:
        if linkpath_type:
            return path.parts[0] == linkpath_type
        else:
            return (
                path.parts[0] in [item.value for item in cls.RelativeLinkPath]
                or not path.parent.name
            )

    @classmethod
    def is_system_path(cls, path: Path) -> bool:
        # Why 0:2? the leading slash counts as part
        return "".join(path.parts[0:2]) in [item.value for item in cls.SystemLinkPath]

    @classmethod
    def is_framework(cls, path: Path) -> bool:
        return ".framework/" in path.as_posix()

    def _make_absolute(self, path: Path) -> Path:
        if LinkedObject.is_relative_path(path) and not LinkedObject.is_framework(path):
            # TODO: This is an oversimplifaction. Best case, the first rpath
            # is correct...
            if (
                LinkedObject.is_relative_path(path, self.RelativeLinkPath.RPATH)
                and self.rpath
            ):
                return self.rpath / path.name
            else:
                # ...and this is just guesswork.
                if self.path.parent.name == "bin":
                    return self.path.parent.parent / "lib" / path.name
                else:
                    return self.path.parent / path.name
        else:
            return path

    def _otool(self, args: str) -> list:
        try:
            sp = subprocess.run(
                shlex.split(f"/usr/bin/otool {args} {self.path}"),
                capture_output=True,
                encoding="utf-8",
            )
            sp.check_returncode()
            return sp.stdout.splitlines()
        except subprocess.CalledProcessError:
            log.error(f"otool {args} failed for {self.path}")
            return list()

    def _install_name_tool(self, args: str) -> list:
        try:
            sp = subprocess.run(
                shlex.split(f"/usr/bin/install_name_tool {args} {self.path}"),
                capture_output=True,
                encoding="utf-8",
            )
            sp.check_returncode()
            return sp.stdout.splitlines()
        except subprocess.CalledProcessError:
            log.error(f"install_name_tool {args} failed for {self.path}")
            return list()

    @property
    def install_name(self) -> str:
        result = self._otool("-D")
        return result[1] if len(result) == 2 else ""

    @install_name.setter
    def install_name(self, install_name: str):
        self._install_name_tool(f"-id {install_name}")

    @property
    def rpath(self) -> list:
        result = list()
        line_iter = iter(self._otool("-l"))
        for line in line_iter:
            if re.match("\s+cmd LC_RPATH", line):
                next(line_iter)
                if match := re.match("\s+path (.+) \(offset.+", next(line_iter)):
                    result.append(match.group(1))
        return result

    def add_rpath(self, rpath: str):
        self._install_name_tool(f"-add_rpath {rpath}")

    def change_one_dependant_install_name(self, install_name: str):
        if libs := [l for l in self.depends_on() if Path(install_name).name in l]:
            self._install_name_tool(f"-change {libs[0]} {install_name}")

    def change_dependent_install_names(self, install_name: str, lib_dir: str):
        libs_in_lib_dir = [
            l for l in Path(lib_dir).glob("*.dylib") if not l.is_symlink()
        ]

        for lib in self.depends_on():
            if Path(lib).name in [Path(l).name for l in libs_in_lib_dir]:
                self._install_name_tool(
                    f"-change {lib} {Path(install_name)/Path(lib).name}"
                )

    def clear_rpath(self):
        for rpath in self.rpath:
            self._install_name_tool(f"-delete_rpath {rpath}")

    def depends_on(self, exclude_system: bool = False) -> List[Path]:
        result = list()

        if LinkedObject.is_framework(self.path):
            log.debug(f"skipping {self.path}")
        else:
            skip_lines = 2 if self.install_name else 1
            for line in self._otool("-L")[skip_lines:]:
                # This matches only dylibs:
                # match = re.match("\t(.+\.dylib)", line)
                # This will match everything:
                if match := re.match("\t(.+) \(compatibility", line):
                    library = Path(match.group(1))
                    if exclude_system:
                        if not LinkedObject.is_system_path(library):
                            result.append(library)
                    else:
                        result.append(library)
        return result

    def flattened_dependency_tree(
        self, exclude_system: bool = False, _dependencies=list()
    ) -> List[Path]:
        for library in self.depends_on(exclude_system):
            library = self._make_absolute(library)
            if library not in _dependencies:
                _dependencies.append(library)
                [
                    _dependencies.append(l)
                    for l in LinkedObject(library).flattened_dependency_tree(
                        exclude_system, _dependencies
                    )
                    if l not in _dependencies
                ]
        return _dependencies
