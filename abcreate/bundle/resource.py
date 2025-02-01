from typing import Optional

from pydantic_xml import BaseXmlModel, attr


class Resource(BaseXmlModel):
    target_dir: Optional[str] = attr(default=None)
    name: str
