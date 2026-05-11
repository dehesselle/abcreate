# SPDX-FileCopyrightText: 2025 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
import re
from pathlib import Path

from pydantic_xml import BaseXmlModel

from abcreate.bundle.library import Library
from abcreate.bundle.resource import Resource

log = logging.getLogger("gdkpixbuf")


class GdkPixbuf(BaseXmlModel):
    def _install_frameworks(self, bundle_dir: Path, source_dir: Path) -> None:
        # pixbuf loaders: *.so files
        for source_path in Path(
            source_dir / "lib" / "gdk-pixbuf-2.0" / "2.10.0" / "loaders"
        ).glob("*.so"):
            library = Library(source_path=source_path)
            # Why flatten? We need to get rid of the subdirectories as e.g.
            # "2.10.0" in a path does not pass validation when signing.
            library.install(bundle_dir, source_dir, flatten=True)

    def _install_resources(self, bundle_dir: Path, source_dir: Path) -> None:
        target_dir = bundle_dir / "Contents" / "Resources"

        resource = Resource(
            source_path=source_dir
            / "lib"
            / "gdk-pixbuf-2.0"
            / "2.10.0"
            / "loaders.cache",
            target_path=target_dir / "etc" / "loaders.cache",
        )

        def modify_func(text, file) -> None:
            # pixbuf loaders need to be picked up from Frameworks directory
            for line in text.splitlines(keepends=True):
                if match := re.match(r'".+(libpixbufloader.+\.so)"', line):
                    file.write(f'"Frameworks/{match.group(1)}"\n')
                else:
                    file.write(line)

        resource.install(bundle_dir, source_dir, modify_func=modify_func)

    def install(self, bundle_dir: Path, source_dir: Path):
        self._install_frameworks(bundle_dir, source_dir)
        self._install_resources(bundle_dir, source_dir)
