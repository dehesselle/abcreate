# SPDX-FileCopyrightText: 2025 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
from pathlib import Path
from shutil import copy

from pydantic_xml import BaseXmlModel

log = logging.getLogger("icon")


class Icon(BaseXmlModel):
    source_path: Path

    @property
    def is_liquid_glass(self) -> bool:
        return self.source_path.suffix.lower() == ".icon"

    def install(self, bundle_dir: Path, install_prefix: Path):
        if self.is_liquid_glass:
            raise ValueError("Liquid Glass icons cannot be installed individually")

        target_dir = bundle_dir / "Contents" / "Resources"
        target_dir.mkdir(parents=True, exist_ok=True)

        source_path = install_prefix / self.source_path
        target_path = target_dir / source_path.name

        if target_path.exists():
            log.error(f"will not overwrite {target_path}")
        else:
            log.debug(f"copy {source_path} to {target_path}")
            copy(source_path, target_path)
