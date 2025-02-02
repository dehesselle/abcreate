from typing import Optional

from pydantic_xml import BaseXmlModel, attr


class Binary(BaseXmlModel):
    name: Optional[str] = attr(default=None)
    source_path: str
