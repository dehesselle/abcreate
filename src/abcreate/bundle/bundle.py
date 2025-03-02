import logging
from typing import List
from pathlib import Path
from shutil import rmtree

from pydantic_xml import BaseXmlModel, element, wrapped

from .executables import Executables
from .frameworks import Frameworks
from .gtk import GdkPixbuf, Gir, Gtk3
from .icon import Icon
from .libraries import Libraries
from .locales import Locales
from .plist import Plist
from .resource import Resource
from abcreate.configuration import configuration as config

log = logging.getLogger("bundle")


class Bundle(BaseXmlModel, tag="bundle"):
    executables: Executables
    frameworks: Frameworks
    gdkpixbuf: GdkPixbuf
    gir: Gir
    gtk3: Gtk3
    icon: Icon
    libraries: Libraries
    locales: Locales
    resources: List[Resource] = wrapped(
        "resources", element(tag="resource", default_factory=list)
    )

    def create(self, target_dir: str, source_dir: str):
        bundle_dir = target_dir / Path(
            self.executables.main_executable.target_name
        ).with_suffix(".app.tmp")

        if bundle_dir.exists():
            log.info(f"removing {bundle_dir.as_posix()}")
            rmtree(bundle_dir)

        log.info(f"creating {bundle_dir.as_posix()}")
        bundle_dir.mkdir(parents=True)

        source_dir = Path(source_dir)

        self.executables.install(bundle_dir, source_dir)
        self.frameworks.install(bundle_dir, source_dir)
        self.gdkpixbuf.install(bundle_dir, source_dir)
        self.gir.install(bundle_dir, source_dir)
        self.gtk3.install(bundle_dir, source_dir)
        self.libraries.install(bundle_dir, source_dir)
        self.locales.install(bundle_dir, source_dir)

        for resource in self.resources:
            resource.install(bundle_dir, source_dir)
