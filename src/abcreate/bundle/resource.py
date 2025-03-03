# SPDX-FileCopyrightText: 2025 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
from pathlib import Path
from typing import Optional
from shutil import copy, copytree

from pydantic_xml import BaseXmlModel, attr

log = logging.getLogger("resource")


class Resource(BaseXmlModel):
    target_path: Optional[str] = attr(default=None)
    chmod: Optional[str] = attr(default=None)
    source_path: str

    @classmethod
    def path_relative_to(cls, path: Path, part: str) -> str:
        try:
            index = path.parts.index(part)
            return "/".join(path.parts[index:])
        except ValueError:
            return path

    def install(self, bundle_dir: Path, source_dir: Path):
        target_dir = bundle_dir / "Contents" / "Resources"

        for source_path in (source_dir / Path(self.source_path).parent).glob(
            Path(self.source_path).name
        ):
            if source_path.exists():
                if self.target_path:
                    target_path = target_dir / self.target_path
                else:
                    # source_path
                    #     a fully expanded path from self.source_path
                    # self.source_path
                    #     a path relative to source_dir, can contain globs
                    #
                    # Example:                   +----------------------------------+
                    #                            |                                  |
                    #                            v                                  |
                    #   self.source_path   =   share/glib-2.0/*.txt                 |
                    #   source_path        =   /some/path/share/glib-2.0/foo.txt    |
                    #                                       ^                       |
                    #                                       |                       |
                    #                                       +-----------------------+
                    #                           This is where we cut off source_path.
                    target_path = target_dir / self.path_relative_to(
                        source_path, Path(self.source_path).parts[0]
                    )
                if target_path.exists():
                    log.debug(f"will not overwrite {target_path}")
                else:
                    if not target_path.parent.exists():
                        # for subdirectories
                        target_path.parent.mkdir(parents=True)

                    log.debug(f"copy {source_path} to {target_path}")
                    if source_path.is_dir():
                        copytree(source_path, target_path, symlinks=True)
                    else:
                        copy(source_path, target_path)
                        if self.chmod:
                            target_path.chmod(int(self.chmod, 8))
            else:
                log.error(f"cannot locate {self.source_path}")
