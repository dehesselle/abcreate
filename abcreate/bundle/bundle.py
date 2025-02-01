import logging
from typing import List

from pydantic_xml import BaseXmlModel, element, wrapped

from .binary import Binary
from .library import Library
from .resource import Resource
from .icon import Icon

log = logging.getLogger("bundle")


class Bundle(BaseXmlModel, tag="bundle"):
    binaries: List[Binary] = wrapped(
        "binaries", element(tag="binary", default_factory=list)
    )
    libraries: List[Library] = wrapped(
        "libraries", element(tag="library", default_factory=list)
    )
    resources: List[Resource] = wrapped(
        "resources", element(tag="resource", default_factory=list)
    )
    icon: Icon


# class Bundle:
#     def __init__(self, tree: etree.Element, source_dir: str):
#         self.tree = tree
#         self.components = "foobar"
#         self.source_dir = source_dir

#     def check_configuration(self):
#         for element in self.xml:
#             try:
#                 module_name = f"abcreate.components.{element.tag}"
#                 module = import_module(module_name)
#                 _class = getattr(module, module_name.capitalize())
#                 log.debug(f"module found: {element.tag}")
#             except ModuleNotFoundError as e:
#                 log.error(f"bundle will be broken, no module to handle '{element.tag}'")

#     def create(self, target_dir: Path):
#         # tree = self.xml.xpath("/bundle/binaries/binary")
#         tree = self.tree.xpath("/bundle/binaries")
#         print("oof", type(tree))
#         binaries = Binaries(
#             tree, "/Users/rene/.local/tmp/bundle", "/Users/rene/.local/tmp"
#         )
#         binaries.main_binary()
