# SPDX-FileCopyrightText: 2025 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
import shlex
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional

from lxml import etree
from pydantic_xml import BaseXmlModel, attr

from abcreate.bundle.library import Library

log = logging.getLogger("gir")


class Gir(BaseXmlModel):
    lib_dir: Optional[str] = attr(default="@executable_path/../Frameworks")
    command: Optional[str] = attr(default="g-ir-compiler")

    def _compile(self, source_path: Path, target_path: Path):
        log.debug(f"compiling {target_path}")
        try:
            subprocess.run(
                [
                    *shlex.split(self.command),
                    "-o",
                    target_path,
                    source_path,
                ]
            ).check_returncode()
        except FileNotFoundError:
            log.error(f"command not found: {self.command}")
        except subprocess.CalledProcessError as e:
            log.error(f"typelib compilation failed\n{e}")

    def _install_frameworks(self, bundle_dir: Path, source_dir: Path) -> None:
        library = Library(source_path=Path("libgirepository-1.0.1.dylib"))
        library.install(bundle_dir, source_dir)

    def _install_resources(self, bundle_dir: Path, source_dir: Path) -> None:
        target_dir = bundle_dir / "Contents" / "Resources" / "lib" / "girepository-1.0"
        target_dir.mkdir(parents=True, exist_ok=True)

        for source_path in Path(source_dir / "share" / "gir-1.0").glob("*.gir"):
            target_path = target_dir / source_path.with_suffix(".typelib").name

            tree = etree.parse(source_path)
            nsmap = {
                "core": "http://www.gtk.org/introspection/core/1.0",
                "c": "http://www.gtk.org/introspection/c/1.0",
                "glib": "http://www.gtk.org/introspection/glib/1.0",
            }
            try:
                element = tree.xpath(
                    "//core:repository/core:namespace", namespaces=nsmap
                )[0]
                libraries = element.attrib["shared-library"].split(",")
                element.attrib["shared-library"] = ""

                for library in libraries:
                    if len(element.attrib["shared-library"]):
                        element.attrib["shared-library"] += ","
                    element.attrib["shared-library"] += (
                        Path(self.lib_dir) / Path(library).name
                    ).as_posix()

                with TemporaryDirectory() as temp_dir:
                    gir_file = Path(temp_dir) / source_path.name
                    tree.write(gir_file, pretty_print=True)
                    self._compile(gir_file, target_path)
            except KeyError:
                log.debug(f"no shared-library in {target_path}")
                self._compile(source_path, target_path)

    def install(self, bundle_dir: Path, source_dir: Path):
        self._install_frameworks(bundle_dir, source_dir)
        self._install_resources(bundle_dir, source_dir)
