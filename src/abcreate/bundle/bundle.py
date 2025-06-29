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
from .gtk import GdkPixbuf, Glib, Gir, Gtk3, Gtk4
from .icons import Icons
from .libraries import Libraries
from .locales import Locales
from .plist import Plist
from .resources import Resources
from .symlinks import Symlinks

log = logging.getLogger("bundle")


class Bundle(BaseXmlModel, tag="bundle"):
    executables: Executables
    symlinks: Optional[Symlinks] = element(default=None)
    frameworks: Optional[Frameworks] = element(default=None)
    gdkpixbuf: GdkPixbuf
    gir: Gir
    glib: Glib
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

    def create(self, output_dir: Path, install_prefix: Path):
        bundle_dir = output_dir / Path(
            self.executables.main_executable.target_name
        ).with_suffix(".app")

        if bundle_dir.exists():
            log.debug(f"removing {bundle_dir.as_posix()}")
            rmtree(bundle_dir)

        log.info(f"creating {bundle_dir.as_posix()}")
        bundle_dir.mkdir(parents=True)

        # It's important to install the plist first because others might
        # depend on it. (There is no dependency management.)
        log.info("---       plist ---")
        self.plist.install(bundle_dir, install_prefix)
        log.info("---        glib ---")
        self.glib.install(bundle_dir, install_prefix)
        if self.gtk3:
            log.info("---        gtk3 ---")
            self.gtk3.install(bundle_dir, install_prefix)
        if self.gtk4:
            log.info("---        gtk4 ---")
            self.gtk4.install(bundle_dir, install_prefix)
        log.info("---   gdkpixbuf ---")
        self.gdkpixbuf.install(bundle_dir, install_prefix)
        log.info("---         gir ---")
        self.gir.install(bundle_dir, install_prefix)
        if self.libraries:
            log.info("---   libraries ---")
            self.libraries.install(bundle_dir, install_prefix)
        if self.frameworks:
            log.info("---  frameworks ---")
            self.frameworks.install(bundle_dir, install_prefix)
        log.info("--- executables ---")
        self.executables.install(bundle_dir, install_prefix)
        log.info("---       icons ---")
        self.icons.install(bundle_dir, install_prefix)
        log.info("---     locales ---")
        self.locales.install(bundle_dir, install_prefix)
        log.info("---   resources ---")
        self.resources.install(bundle_dir, install_prefix)
        if self.symlinks:
            log.info("---    symlinks ---")
            self.symlinks.install(bundle_dir)
