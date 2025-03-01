import logging
from pathlib import Path
from shutil import copytree

from pydantic_xml import BaseXmlModel

log = logging.getLogger("framework")


class Framework(BaseXmlModel):
    source_path: str

    def install(self, bundle_dir: Path, source_dir: Path):
        target_dir = bundle_dir / "Contents" / "Frameworks"

        if not target_dir.exists():
            log.info(f"creating {target_dir}")
            target_dir.mkdir(parents=True)

        if (source_path := source_dir / self.source_path).exists():
            target_path = target_dir / Path(self.source_path).name
            if target_path.exists():
                log.error(f"will not overwrite {target_path}")
            else:
                log.info(f"copy {source_path} to {target_path}")
                copytree(source_path, target_path)
        else:
            log.error(f"cannot locate {self.source_path}")
