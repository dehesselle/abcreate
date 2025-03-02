import logging
from pathlib import Path
from typing import List

from pydantic_xml import BaseXmlModel, element

from .library import Library

log = logging.getLogger("library")


class Libraries(BaseXmlModel):
    libraries: List[Library] = element(tag="library")

    def install(self, bundle_dir: Path, source_dir: Path):
        for library in self.libraries:
            library.install(bundle_dir, source_dir)
