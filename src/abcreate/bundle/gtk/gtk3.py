import logging
from pathlib import Path
import re

from pydantic_xml import BaseXmlModel

from abcreate.bundle.library import Library

log = logging.getLogger("gtk")


class Gtk3(BaseXmlModel):
    dummy: str  # FIXME: this is a workaround

    @classmethod
    def path_relative_to(cls, path: Path, part: str) -> str:
        try:
            index = path.parts.index(part)
            return "/".join(path.parts[index + 1 :])
        except ValueError:
            return path

    def install(self, bundle_dir: Path, source_dir: Path):
        target_dir = bundle_dir / "Contents" / "Frameworks"

        library = Library(source_path="libgtk-3.0.dylib")
        library.install(bundle_dir, source_dir)

        for source_path in Path(
            source_dir / "lib" / "gtk-3.0" / "3.0.0" / "immodules"
        ).glob("*.so"):
            library = Library(source_path=source_path.as_posix())
            library.install(bundle_dir, source_dir)

        for source_path in Path(
            source_dir / "lib" / "gtk-3.0" / "3.0.0" / "printbackends"
        ).glob("*.so"):
            library = Library(source_path=source_path.as_posix())
            library.install(bundle_dir, source_dir)

        source_path = Path(source_dir / "lib" / "gtk-3.0" / "3.0.0" / "immodules.cache")
        immodules_cache = source_path.read_text()
        target_path = target_dir / self.path_relative_to(source_path, "lib")

        with open(target_path, "wt") as file:
            for line in immodules_cache.splitlines(keepends=True):
                if match := re.match('".+(im-.+\.so)"', line):
                    file.write(
                        f'"@executable_path/../Frameworks/gtk-3.0/3.0.0/immodules/{match.group(1)}"\n'
                    )
                else:
                    file.write(line)
