import logging
from pathlib import Path
from shutil import copy

from pydantic_xml import BaseXmlModel

from .plist import Plist

log = logging.getLogger("icon")


class Icon(BaseXmlModel):
    source_path: str

    def install(self, bundle_dir: Path, source_dir: Path):
        target_dir = bundle_dir / "Contents" / "Resources"
        target_dir.mkdir(parents=True, exist_ok=True)

        source_path = source_dir / self.source_path
        target_path = target_dir / source_path.name

        if target_path.exists():
            log.error(f"will not overwrite {target_path}")
        else:
            log.info(f"copy {source_path} to {target_path}")
            copy(source_path, target_path)

            plist = Plist(bundle_dir)
            plist.install()
            plist.CFBundleIconFile = target_path.name
