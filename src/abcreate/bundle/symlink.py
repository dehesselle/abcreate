# SPDX-FileCopyrightText: 2025 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
import os
from pathlib import Path

from pydantic_xml import BaseXmlModel

log = logging.getLogger("symlink")


class Symlink(BaseXmlModel):
    name: str

    def install(self, bundle_dir: Path):
        target_dir = bundle_dir / "Contents" / "MacOS"

        source_path = Path(self.name)
        target_path = target_dir / source_path.name

        if target_path.exists():
            log.debug(f"will not overwrite {target_path}")
        else:
            log.debug(f"symlinking {source_path} to {target_path}")
            target_path.parent.mkdir(parents=True, exist_ok=True)
            os.symlink(src=source_path, dst=target_path)
