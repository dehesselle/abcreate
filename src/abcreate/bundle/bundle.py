import logging
from typing import List
from pathlib import Path
from shutil import rmtree

from pydantic_xml import BaseXmlModel, element, wrapped

from .executable import Executable
from .framework import Framework
from .gtk import Gir
from .icon import Icon
from .library import Library
from .locale import Locale
from .plist import Plist
from .resource import Resource
from abcreate.configuration import configuration as config

log = logging.getLogger("bundle")


class Bundle(BaseXmlModel, tag="bundle"):
    executables: List[Executable] = wrapped(
        "executables", element(tag="executable", default_factory=list)
    )
    frameworks: List[Framework] = wrapped(
        "frameworks", element(tag="framework", default_factory=list)
    )
    gir: Gir
    icon: Icon
    libraries: List[Library] = wrapped(
        "libraries", element(tag="library", default_factory=list)
    )
    locales: List[Locale] = wrapped(
        "locales", element(tag="locale", default_factory=list)
    )
    resources: List[Resource] = wrapped(
        "resources", element(tag="resource", default_factory=list)
    )

    def _check(self):
        if not self.executables.count:
            log.critical("no main executable")

    def create(self, target_dir: str, source_dir: str):
        self._check()
        main_executable = self.executables[0]
        bundle_dir = target_dir / Path(main_executable.target_name).with_suffix(
            ".app.tmp"
        )

        if bundle_dir.exists():
            log.info(f"removing {bundle_dir.as_posix()}")
            rmtree(bundle_dir)

        log.info(f"creating {bundle_dir.as_posix()}")
        bundle_dir.mkdir(parents=True)

        Plist(bundle_dir).install()
        Plist(bundle_dir).CFBundleExecutable = main_executable.target_name

        source_dir = Path(source_dir)

        for executable in self.executables:
            executable.install(bundle_dir, source_dir)

        for framework in self.frameworks:
            framework.install(bundle_dir, source_dir)

        self.gir.install(bundle_dir, source_dir)

        for library in self.libraries:
            library.install(bundle_dir, source_dir)

        for locale in self.locales:
            locale.install(bundle_dir, source_dir)

        for resource in self.resources:
            resource.install(bundle_dir, source_dir)
