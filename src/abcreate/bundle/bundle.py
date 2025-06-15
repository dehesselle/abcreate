# SPDX-FileCopyrightText: 2025 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
from pathlib import Path
from shutil import rmtree
from typing import Optional

from pydantic import model_validator
from pydantic_xml import BaseXmlModel, element

from .executables import Executables
from .frameworks import Frameworks
from .gtk import GdkPixbuf, Gir, Gtk3, Gtk4
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
    gtk3: Optional[Gtk3] = element(default=None)
    gtk4: Optional[Gtk4] = element(default=None)
    icons: Icons
    libraries: Optional[Libraries] = element(default=None)
    locales: Locales
    plist: Plist
    resources: Resources

    @model_validator(mode="after")
    def ensure_gtk3_gtk4_mutually_exclusive(self):
        if (self.gtk3 and self.gtk4) or (not self.gtk3 and not self.gtk4):
            log.critical("gtk3 and gtk4 are mutually exclusive")
        return self

    def create(self, target_dir: Path, source_dir: Path):
        bundle_dir = target_dir / Path(
            self.executables.main_executable.target_name
        ).with_suffix(".app")

        if bundle_dir.exists():
            log.debug(f"removing {bundle_dir.as_posix()}")
            rmtree(bundle_dir)

        log.info(f"creating {bundle_dir.as_posix()}")
        bundle_dir.mkdir(parents=True)

        # order is on purpose:
        #   - plist first because others will modify it
        #   - libraries
        #   - executables
        #   -  resources
        self.plist.install(bundle_dir, source_dir)
        if self.gtk3:
            self.gtk3.install(bundle_dir, source_dir)
        if self.gtk4:
            self.gtk4.install(bundle_dir, source_dir)
        self.gdkpixbuf.install(bundle_dir, source_dir)
        self.gir.install(bundle_dir, source_dir)
        if self.libraries:
            self.libraries.install(bundle_dir, source_dir)
        if self.frameworks:
            self.frameworks.install(bundle_dir, source_dir)
        self.executables.install(bundle_dir, source_dir)
        self.icons.install(bundle_dir, source_dir)
        self.locales.install(bundle_dir, source_dir)
        self.resources.install(bundle_dir, source_dir)
