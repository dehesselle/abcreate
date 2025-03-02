# SPDX-FileCopyrightText: 2025 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
from pathlib import Path
from typing import List

from pydantic_xml import BaseXmlModel, element

from .framework import Framework

log = logging.getLogger("framework")


class Frameworks(BaseXmlModel):
    frameworks: List[Framework] = element(tag="framework")

    def install(self, bundle_dir: Path, source_dir: Path):
        for framework in self.frameworks:
            framework.install(bundle_dir, source_dir)
