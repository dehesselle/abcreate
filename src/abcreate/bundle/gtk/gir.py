import logging
from pathlib import Path
from lxml import etree
import subprocess
from tempfile import TemporaryDirectory

from pydantic_xml import BaseXmlModel

from abcreate.bundle.library import Library

log = logging.getLogger("gir")


class Gir(BaseXmlModel):
    dummy: str  # FIXME: this is a workaround

    def install(self, bundle_dir: Path, source_dir: Path):
        target_dir = bundle_dir / "Contents" / "Resources" / "lib" / "girepository-1.0"
        target_dir.mkdir(parents=True, exist_ok=True)

        library = Library(source_path="libgirepository-1.0.1.dylib")
        library.install(bundle_dir, source_dir)

        for source_path in Path(source_dir / "share" / "gir-1.0").glob("*.gir"):
            target_path = target_dir / source_path.with_suffix(".typelib").name
            log.info(f"compiling {target_path}")

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
                        Path("@executable_path/../Frameworks") / Path(library).name
                    ).as_posix()

                with TemporaryDirectory() as temp_dir:
                    gir_file = Path(temp_dir) / source_path.name
                    tree.write(gir_file, pretty_print=True)
                    subprocess.run(
                        [
                            f"{source_dir}/usr/bin/jhb",
                            "run",
                            "g-ir-compiler",
                            "-o",
                            target_path,
                            gir_file,
                        ]
                    )
            except KeyError:
                log.debug(f"no shared-library in {target_path}")
                subprocess.run(
                    [
                        f"{source_dir}/usr/bin/jhb",
                        "run",
                        "g-ir-compiler",
                        "-o",
                        target_path,
                        source_path,
                    ]
                )
