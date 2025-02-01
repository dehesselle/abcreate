from pathlib import Path
import logging
import re
from enum import Enum
import os

log = logging.getLogger("config")


class Configuration:
    class Source:
        def __init__(self):
            _prefix_path = Path()

        @property
        def prefix_path(self) -> Path:
            if self._prefix_path is None:
                return Path()
            else:
                return self.prefix_path

        @prefix_path.setter
        def prefix_path(self, value):
            _prefix_path = Path(value)

    source: Source

    def resolve_path(self, path: str) -> Path:
        def render_template(text: str) -> str:
            class Pattern(str, Enum):
                ENVIRONMENT_VARIABLE = r".*\${env:(\w+)}"

            if match := re.match(Pattern.ENVIRONMENT_VARIABLE, path):
                return re.sub(
                    Pattern.ENVIRONMENT_VARIABLE, os.getenv(match.group(1)), path
                )
            else:
                return text

        def is_relative(path: str) -> bool:
            return path[0] != "/"

        path = render_template(path)
        if is_relative(path):
            return (self.prefix_path / path).absolute()
        else:
            return Path(path).absolute()


configuration = Configuration()
