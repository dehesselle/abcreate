from pydantic_xml import BaseXmlModel


class Icon(BaseXmlModel):
    path: str
