import logging
from pathlib import Path
from shutil import copy

from pydantic_xml import BaseXmlModel

from .linkedobject import LinkedObject

log = logging.getLogger("library")


class Library(BaseXmlModel):
    source_path: str

    @property
    def target_name(self) -> str:
        return Path(self.source_path).name

    @classmethod
    def path_relative_to(cls, path: Path, part: str) -> str:
        try:
            index = path.parts.index(part)
            return "/".join(path.parts[index + 1 :])
        except ValueError:
            return path

    @property
    def is_framework(self) -> bool:
        return ".framework/" in self.source_path

    def install(self, bundle_dir: Path, source_dir: Path):
        target_dir = bundle_dir / "Frameworks"
        if not target_dir.exists():
            log.info(f"creating {target_dir}")
            target_dir.mkdir(parents=True)

        for source_path in (source_dir / "lib" / Path(self.source_path).parent).glob(
            Path(self.source_path).name
        ):
            if source_path.exists():
                target_path = target_dir / self.path_relative_to(source_path, "lib")
                if target_path.exists():
                    log.debug(f"will not overwrite {target_path}")
                else:
                    if not target_path.parent.exists():
                        # for subdirectories in the libraries directory
                        target_path.parent.mkdir(parents=True)

                    log.info(f"copy {source_path} to {target_path}")
                    copy(source_path, target_path)

                    lo = LinkedObject(source_path)
                    for path in lo.flattened_dependency_tree(exclude_system=True):
                        library = Library(source_path=path.as_posix())
                        if library.is_framework:
                            # frameworks can only be processed with info from bundle.xml
                            log.info(
                                f"skipping framework library {library.source_path}"
                            )
                            pass
                        else:
                            library.install(bundle_dir, source_dir)
            else:
                log.error(f"cannot locate {self.source_path}")
