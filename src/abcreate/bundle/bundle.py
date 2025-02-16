import logging
from typing import List
from pathlib import Path
from shutil import rmtree, copy

from pydantic_xml import BaseXmlModel, element, wrapped

from .binary import Binary
from .library import Library
from .resource import Resource
from .icon import Icon
from .plist import Plist
from abcreate.configuration import configuration as config

log = logging.getLogger("bundle")


class Bundle(BaseXmlModel, tag="bundle"):
    binaries: List[Binary] = wrapped(
        "binaries", element(tag="binary", default_factory=list)
    )
    libraries: List[Library] = wrapped(
        "libraries", element(tag="library", default_factory=list)
    )
    resources: List[Resource] = wrapped(
        "resources", element(tag="resource", default_factory=list)
    )
    icon: Icon

    def _check(self):
        if not self.binaries.count:
            log.critical("no main binary")

    def create(self, target_dir: str):
        self._check()
        main_binary = self.binaries[0]
        if main_binary.name:
            bundle_dir = target_dir / Path(main_binary.name).with_suffix(".app.tmp")
        else:
            bundle_dir = target_dir / Path(
                Path(main_binary.source_path).name
            ).with_suffix(".app.tmp")

        if bundle_dir.exists():
            log.info(f"removing {bundle_dir.as_posix()}")
            rmtree(bundle_dir)

        log.info(f"creating {bundle_dir.as_posix()}")
        bundle_dir.mkdir(parents=True)

        Plist(bundle_dir).install()
        Plist(bundle_dir).CFBundleExecutable = "foo"
