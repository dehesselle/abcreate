from pydantic_xml import BaseXmlModel


class Icon(BaseXmlModel):
    source_path: str
