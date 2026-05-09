# SPDX-FileCopyrightText: 2025 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
from pathlib import Path
from typing import List

from pydantic_xml import BaseXmlModel, element

from .errors import BundleValidationError
from .icon import Icon
from .plist import Plist

log = logging.getLogger("icon")


class Icons(BaseXmlModel):
    icons: List[Icon] = element(tag="icon")

    @property
    def main_icon(self) -> Icon:
        try:
            return self.icons[0]
        except IndexError:
            raise BundleValidationError("no icons specified")

    def install(self, bundle_dir: Path, install_prefix: Path):
        for icon in self.icons:
            icon.install(bundle_dir, install_prefix)

        Plist().CFBundleIconFile = Path(self.main_icon.source_path).name
