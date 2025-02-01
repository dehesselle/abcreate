from pydantic_xml import BaseXmlModel, attr


class Binary(BaseXmlModel):
    source_path: str = attr()
    name: str


# class Binary:
#     def __init__(self):
#         self._source_path = Path()
#         self.target_path = Path()

#     @property
#     def source_path(self):
#         return self._source_path

#     @source_path.setter
#     def source_path(self, value: Path):
#         if value.exists:
#             self._source_path = value
#         else:
#             log.error(f"binary does not exist: {value}")

#     def create(self):
#         copy(self.source_path, self.target_path)


# class Binaries:
#     def __init__(self, xml, bundle_dir: Path, source_dir: Path):
#         self.xml = etree.ElementTree(xml[0])
#         self.bundle_dir = bundle_dir
#         self.source_dir = source_dir

#     def main_binary(self):
#         print(type(self.xml))

#         for e in self.xml.getroot():
#             print(type(e))
#             print(e.tag)
#             print(self.xml.getpath(e))
