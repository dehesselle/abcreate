# SPDX-FileCopyrightText: 2025 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
import re
from pathlib import Path

from pydantic_xml import BaseXmlModel

from abcreate.bundle.library import Library
from abcreate.bundle.locale import Locale
from abcreate.bundle.resource import Resource

from .gdkpixbuf import GdkPixbuf
from .glib import Glib

log = logging.getLogger("gtk")


class Gtk3(BaseXmlModel):
    def _install_frameworks(self, bundle_dir: Path, source_dir: Path):
        library = Library(source_path=Path("libgtk-3.0.dylib"))
        library.install(bundle_dir, source_dir)

        for source_path in Path(
            source_dir / "lib" / "gtk-3.0" / "3.0.0" / "immodules"
        ).glob("*.so"):
            library = Library(source_path=source_path)
            # Why flatten? We need to get rid of the subdirectories as e.g.
            # "3.0.0" in a path does not pass validation when signing.
            library.install(bundle_dir, source_dir, flatten=True)

        for source_path in Path(
            source_dir / "lib" / "gtk-3.0" / "3.0.0" / "printbackends"
        ).glob("*.so"):
            library = Library(source_path=source_path)
            # Why flatten? We need to get rid of the subdirectories as e.g.
            # "3.0.0" in a path does not pass validation when signing.
            library.install(bundle_dir, source_dir, flatten=True)

    def _install_locales(self, bundle_dir: Path, source_dir: Path) -> None:
        locale = Locale(name="gtk30.mo")
        locale.install(bundle_dir, source_dir)

    def _install_resources(self, bundle_dir: Path, source_dir: Path):
        target_dir = bundle_dir / "Contents" / "Resources"

        resource = Resource(
            source_path=source_dir / "lib" / "gtk-3.0" / "3.0.0" / "immodules.cache",
            target_path=target_dir / "etc" / "immodules.cache",
        )

        def modify_func(text, file) -> None:
            for line in text.splitlines(keepends=True):
                if match := re.match(r'".+(im-.+\.so)"', line):
                    # TODO: this probably needs to be @rpath in cases where an app calls a bundled
                    # Python that needs to be able reach these
                    file.write(f'"@executable_path/../Frameworks/{match.group(1)}"\n')
                else:
                    file.write(line)

        resource.install(bundle_dir, source_dir, modify_func=modify_func)

        resource = Resource(source_path=Path("share/gtk-3.0"))
        resource.install(bundle_dir, source_dir)

    def install(self, bundle_dir: Path, source_dir: Path):
        glib = Glib()
        glib.install(bundle_dir, source_dir)
        gdkpixbuf = GdkPixbuf()
        gdkpixbuf.install(bundle_dir, source_dir)
        self._install_frameworks(bundle_dir, source_dir)
        self._install_locales(bundle_dir, source_dir)
        self._install_resources(bundle_dir, source_dir)
