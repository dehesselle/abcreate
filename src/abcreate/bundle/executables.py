import logging
from pathlib import Path
from typing import List

from pydantic_xml import BaseXmlModel, element

from .executable import Executable
from .plist import Plist

log = logging.getLogger("executable")


class Executables(BaseXmlModel):
    executables: List[Executable] = element(tag="executable")

    @property
    def main_executable(self) -> Executable:
        try:
            return self.executables[0]
        except IndexError:
            log.critical("no executables specified")
            return None

    def install(self, bundle_dir: Path, source_dir: Path):
        for executable in self.executables:
            executable.install(bundle_dir, source_dir)

        Plist(bundle_dir).install()
        Plist(bundle_dir).CFBundleExecutable = self.main_executable.target_name
