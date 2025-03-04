# SPDX-FileCopyrightText: 2025 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
from pathlib import Path
from typing import List

from pydantic_xml import BaseXmlModel, element

from .executable import Executable
from .plist import Plist

log = logging.getLogger("executable")


class Executables(BaseXmlModel):
    executables: List[Executable] = element(tag="executable")

    @property
    def main_executable(self) -> Executable:
        try:
            return self.executables[0]
        except IndexError:
            log.critical("no executables specified")
            return None

    def install(self, bundle_dir: Path, source_dir: Path):
        for executable in self.executables:
            executable.install(bundle_dir, source_dir)

        Plist(source_path=None).CFBundleExecutable = self.main_executable.target_name
