# SPDX-FileCopyrightText: 2025 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
from pathlib import Path
from shutil import copy

from pydantic_xml import BaseXmlModel

log = logging.getLogger("locale")


class Locale(BaseXmlModel):
    name: str

    @classmethod
    def path_relative_to(cls, path: Path, part: str) -> str:
        try:
            index = path.parts.index(part)
            return "/".join(path.parts[index + 1 :])
        except ValueError:
            return path

    def install(self, bundle_dir: Path, source_dir: Path):
        target_dir = bundle_dir / "Contents" / "Resources" / "share" / "locale"

        for source_path in Path(source_dir / "share" / "locale").rglob(self.name):
            target_path = target_dir / self.path_relative_to(source_path, "locale")
            if target_path.exists():
                log.debug(f"will not overwrite {target_path}")
            else:
                log.debug(f"copy {source_path} to {target_path}")
                target_path.parent.mkdir(parents=True, exist_ok=True)
                copy(source_path, target_path)
