import logging
from pathlib import Path
from typing import Optional
from shutil import copy

from pydantic_xml import BaseXmlModel, attr

log = logging.getLogger("binary")


class Binary(BaseXmlModel):
    name: Optional[str] = attr(default=None)
    source_path: str

    @property
    def target_name(self) -> str:
        if self.name:
            return self.name
        else:
            return Path(self.source_path).name

    def install(self, bundle_dir: Path, source_dir: Path):
        target_dir = bundle_dir / "Contents" / "MacOS"
        if not target_dir.exists():
            target_dir.mkdir(parents=True)

        if (source_path := source_dir / self.source_path).exists() or (
            source_path := source_dir / "bin" / self.source_path
        ).exists():
            target_path = target_dir / self.target_name
            log.info(f"copy {source_path} to {target_path}")
            copy(source_path, target_path)
        else:
            log.error(f"cannot locate {self.source_path}")
