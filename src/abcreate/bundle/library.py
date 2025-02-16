from pydantic_xml import BaseXmlModel


class Library(BaseXmlModel):
    source_path: str
