import logging
from pathlib import Path
from shutil import copy

from pydantic_xml import BaseXmlModel

log = logging.getLogger("library")


class Library(BaseXmlModel):
    source_path: str

    @property
    def target_name(self) -> str:
        return Path(self.source_path).name

    @property
    def is_framework(self) -> bool:
        return ".framework/" in self.source_path

    def install(self, bundle_dir: Path, source_dir: Path):
        target_dir = bundle_dir / "Frameworks"
        if not target_dir.exists():
            log.info(f"creating {target_dir}")
            target_dir.mkdir(parents=True)

        if (source_path := source_dir / self.source_path).exists() or (
            source_path := source_dir / "lib" / self.source_path
        ).exists():
            target_path = target_dir / self.target_name
            if target_path.exists():
                log.error(f"will not overwrite {target_path}")
            else:
                log.info(f"copy {source_path} to {target_path}")
                copy(source_path, target_path)
        else:
            log.error(f"cannot locate {self.source_path}")
