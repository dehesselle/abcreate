# SPDX-FileCopyrightText: 2025 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
from pathlib import Path
from typing import List

from pydantic_xml import BaseXmlModel, element

from .symlink import Symlink

log = logging.getLogger("symlink")


class Symlinks(BaseXmlModel):
    symlinks: List[Symlink] = element(tag="symlink")

    def install(self, bundle_dir: Path):
        for symlink in self.symlinks:
            symlink.install(bundle_dir)
