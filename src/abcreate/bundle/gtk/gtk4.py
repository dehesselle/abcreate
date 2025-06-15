# SPDX-FileCopyrightText: 2025 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
from pathlib import Path

from pydantic_xml import BaseXmlModel

from abcreate.bundle.library import Library

log = logging.getLogger("gtk")


class Gtk4(BaseXmlModel):
    def install(self, bundle_dir: Path, source_dir: Path):
        target_dir = bundle_dir / "Contents" / "Frameworks"

        library = Library(source_path="libgtk-4.1.dylib")
        library.install(bundle_dir, source_dir)

        for source_path in Path(
            source_dir / "lib" / "gtk-4.0" / "4.0.0" / "printbackends"
        ).glob("*.so"):
            library = Library(source_path=source_path.as_posix())
            # Why flatten? We need to get rid of the subdirectories as e.g.
            # "4.0.0" in a path does not pass validation when signing.
            library.install(bundle_dir, source_dir, flatten=True)
