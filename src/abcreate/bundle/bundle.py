# SPDX-FileCopyrightText: 2025 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
from pathlib import Path
from shutil import rmtree
from typing import Optional

from pydantic_xml import BaseXmlModel, element

from .executables import Executables
from .frameworks import Frameworks
from .gtk import GdkPixbuf, Gir, Gtk3
from .icons import Icons
from .libraries import Libraries
from .locales import Locales
from .plist import Plist
from .resources import Resources

log = logging.getLogger("bundle")


class Bundle(BaseXmlModel, tag="bundle"):
    executables: Executables
    frameworks: Optional[Frameworks] = element(default=None)
    gdkpixbuf: GdkPixbuf
    gir: Gir
    gtk3: Gtk3
    icons: Icons
    libraries: Libraries
    locales: Locales
    plist: Plist
    resources: Resources

    def create(self, target_dir: str, source_dir: str):
        bundle_dir = target_dir / Path(
            self.executables.main_executable.target_name
        ).with_suffix(".app")

        if bundle_dir.exists():
            log.debug(f"removing {bundle_dir.as_posix()}")
            rmtree(bundle_dir)

        log.info(f"creating {bundle_dir.as_posix()}")
        bundle_dir.mkdir(parents=True)

        source_dir = Path(source_dir)

        # order is on purpose:
        #   - plist first because others will modify it
        #   - libraries
        #   - executables
        #   -  resources
        self.plist.install(bundle_dir, source_dir)
        self.gtk3.install(bundle_dir, source_dir)
        self.gdkpixbuf.install(bundle_dir, source_dir)
        self.gir.install(bundle_dir, source_dir)
        self.libraries.install(bundle_dir, source_dir)
        if self.frameworks:
            self.frameworks.install(bundle_dir, source_dir)
        self.executables.install(bundle_dir, source_dir)
        self.icons.install(bundle_dir, source_dir)
        self.locales.install(bundle_dir, source_dir)
        self.resources.install(bundle_dir, source_dir)
