# SPDX-FileCopyrightText: 2025 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
from pathlib import Path
from typing import Optional
from shutil import copy

from pydantic_xml import BaseXmlModel, attr

from abcreate.util import LinkedObject
from .library import Library

log = logging.getLogger("executable")


class Executable(BaseXmlModel):
    name: Optional[str] = attr(default=None)
    source_path: str

    @property
    def target_name(self) -> str:
        if self.name:
            return self.name
        else:
            return Path(self.source_path).name

    def install(self, bundle_dir: Path, source_dir: Path):
        target_dir = bundle_dir / "Contents" / "MacOS"
        if not target_dir.exists():
            target_dir.mkdir(parents=True)

        if (source_path := source_dir / "bin" / self.source_path).exists():
            target_path = target_dir / self.target_name
            if target_path.exists():
                log.error(f"will not overwrite {target_path}")
            else:
                log.debug(f"copy {source_path} to {target_path}")
                copy(source_path, target_path)

                # pull in dependencies
                lo = LinkedObject(source_path)
                for path in lo.flattened_dependency_tree(exclude_system=True):
                    library = Library(source_path=path.as_posix())
                    if library.is_framework:
                        # frameworks are taken care of separately
                        log.debug(
                            f"intentionally skipping framework library {library.source_path}"
                        )
                        pass
                    else:
                        library.install(bundle_dir, source_dir)

                # adjust install names: top level...
                frameworks_dir = bundle_dir / "Contents" / "Frameworks"
                lo = LinkedObject(target_path)
                lo.change_dependent_install_names(
                    "@executable_path/../Frameworks",
                    frameworks_dir.as_posix(),
                )
                # ...and one nesting level
                for sub_dir in filter(Path.is_dir, frameworks_dir.iterdir()):
                    lo.change_dependent_install_names(
                        f"@executable_path/../Frameworks/{sub_dir.name}",
                        sub_dir.as_posix(),
                    )
        else:
            log.error(f"cannot locate {self.source_path}")
