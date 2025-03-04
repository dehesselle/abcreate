# SPDX-FileCopyrightText: 2025 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
from pathlib import Path
import re

from pydantic_xml import BaseXmlModel

from abcreate.bundle.library import Library

log = logging.getLogger("gtk")


class Gtk3(BaseXmlModel):
    @classmethod
    def path_relative_to(cls, path: Path, part: str) -> str:
        try:
            index = path.parts.index(part)
            return "/".join(path.parts[index + 1 :])
        except ValueError:
            return path

    def install(self, bundle_dir: Path, source_dir: Path):
        target_dir = bundle_dir / "Contents" / "Frameworks"

        library = Library(source_path="libgtk-3.0.dylib")
        library.install(bundle_dir, source_dir)

        for source_path in Path(
            source_dir / "lib" / "gtk-3.0" / "3.0.0" / "immodules"
        ).glob("*.so"):
            library = Library(source_path=source_path.as_posix())
            # Why flatten? We need to get rid of the subdirectories as e.g.
            # "3.0.0" in a path does not pass validation when signing.
            library.install(bundle_dir, source_dir, flatten=True)

        for source_path in Path(
            source_dir / "lib" / "gtk-3.0" / "3.0.0" / "printbackends"
        ).glob("*.so"):
            library = Library(source_path=source_path.as_posix())
            # Why flatten? We need to get rid of the subdirectories as e.g.
            # "3.0.0" in a path does not pass validation when signing.
            library.install(bundle_dir, source_dir, flatten=True)

        target_dir = bundle_dir / "Contents" / "Resources"
        source_path = Path(source_dir / "lib" / "gtk-3.0" / "3.0.0" / "immodules.cache")
        immodules_cache = source_path.read_text()
        # Since we're breaking up the original structure, best place for
        # loaders.cache is etc as it is a configuration file after all.
        target_path = target_dir / "etc" / "immodules.cache"
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "wt") as file:
            for line in immodules_cache.splitlines(keepends=True):
                if match := re.match('".+(im-.+\.so)"', line):
                    file.write(f'"@executable_path/../Frameworks/{match.group(1)}"\n')
                else:
                    file.write(line)
