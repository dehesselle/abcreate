# SPDX-FileCopyrightText: 2025 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
from pathlib import Path
from typing import List, Optional

from pydantic_xml import BaseXmlModel, element

from .errors import BundleValidationError
from .executable import Executable
from .plist import Plist
from .symlink import Symlink

log = logging.getLogger("executable")


class Executables(BaseXmlModel):
    executables: List[Executable] = element(tag="executable")
    symlinks: Optional[List[Symlink]] = element(tag="symlink", default=list())

    @property
    def main_executable(self) -> Executable:
        try:
            return self.executables[0]
        except IndexError:
            raise BundleValidationError("no executables specified")

    def install(self, bundle_dir: Path, install_prefix: Path):
        for executable in self.executables:
            executable.install(bundle_dir, install_prefix)

        Plist().CFBundleExecutable = self.main_executable.target_name

        for symlink in self.symlinks:
            symlink.install(bundle_dir)
