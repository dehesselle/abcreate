import logging
from pathlib import Path
from shutil import copy

from pydantic_xml import BaseXmlModel
from pydantic import field_validator

from .linkedobject import LinkedObject

log = logging.getLogger("library")


class Library(BaseXmlModel):
    source_path: str

    @field_validator("source_path")
    def ensure_relative_path(cls, value: str) -> str:
        path = Path(value)
        if path.is_absolute():
            return cls.path_relative_to(path, "lib").as_posix()
        return value

    @property
    def target_name(self) -> str:
        return Path(self.source_path).name

    @classmethod
    def path_relative_to(cls, path: Path, part: str) -> Path:
        try:
            index = path.parts.index(part)
            return Path(*list((path.parts[index + 1 :])))
        except ValueError:
            return path

    @property
    def is_framework(self) -> bool:
        return ".framework/" in self.source_path

    def install(self, bundle_dir: Path, source_dir: Path):
        target_dir = bundle_dir / "Contents" / "Frameworks"
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

                    # pull in dependencies
                    lo = LinkedObject(source_path)
                    for path in lo.flattened_dependency_tree(exclude_system=True):
                        library = Library(source_path=path.as_posix())
                        if library.is_framework:
                            # frameworks can only be processed with info from bundle.xml
                            log.info(
                                f"skipping framework library {library.source_path}"
                            )
                        else:
                            library.install(bundle_dir, source_dir)

                    # adjust install names
                    lo = LinkedObject(target_path)
                    loader_path = Path("@loader_path")
                    for _ in range(
                        len(self.path_relative_to(source_path, "lib").parts) - 1
                    ):
                        # take care of nested directory structure
                        loader_path /= ".."
                    lo.change_dependent_install_names(
                        loader_path.as_posix(), target_dir.as_posix()
                    )
            else:
                log.error(f"cannot locate {self.source_path}")
