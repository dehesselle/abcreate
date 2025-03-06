# SPDX-FileCopyrightText: 2025 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
import argparse
from pathlib import Path
from enum import Enum

from abcreate.bundle import Bundle

try:
    from abcreate._version import version
except ImportError:
    version = "0.0.0"

log = logging.getLogger("main")


class ExitOnCriticalHandler(logging.StreamHandler):
    def emit(self, record):
        if record.levelno == logging.CRITICAL:
            raise SystemExit(1)


class CollectStatisticsHandler(logging.StreamHandler):
    message_counter: dict[int, int] = dict()

    def emit(self, record):
        try:
            CollectStatisticsHandler.message_counter[record.levelno] += 1
        except KeyError:
            CollectStatisticsHandler.message_counter[record.levelno] = 1

    @classmethod
    def has_errors(cls) -> bool:
        return logging.ERROR in cls.message_counter

    @classmethod
    def has_warnings(cls) -> bool:
        return logging.WARNING in cls.message_counter

    @classmethod
    def errors(cls) -> int:
        return cls.message_counter[logging.ERROR] if cls.has_errors() else 0

    @classmethod
    def warnings(cls) -> int:
        return cls.message_counter[logging.WARNING] if cls.has_warnings() else 0


class Command(Enum):
    CREATE = "create"


def setup_logging() -> None:
    file_handler = logging.FileHandler("abcreate.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)-23s | %(name)-14s | %(funcName)-20s | %(levelname)-8s | %(message)s"
        )
    )
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(
        logging.Formatter(
            "%(asctime)-23s [%(name)-8s] [%(funcName)-10s] %(levelname)s: %(message)s"
        )
    )
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[
            file_handler,
            stream_handler,
            CollectStatisticsHandler(),
            ExitOnCriticalHandler(),
        ],
    )


def main() -> None:
    setup_logging()

    parser = argparse.ArgumentParser(description="create an application bundle")
    parser.add_argument("--version", action="version", version=f"abcreate {version}")
    p_commands = parser.add_subparsers(help="available commands", dest="command")

    p_create = p_commands.add_parser(
        Command.CREATE.value, help="create application bundle"
    )
    p_create.add_argument("file")
    p_create.add_argument("-s", "--source_dir", required=True, help="source directory")
    p_create.add_argument("-t", "--target_dir", required=True, help="target directory")

    args = parser.parse_args()

    log.info(f"abcreate {version}")

    if args.command == Command.CREATE.value:
        try:
            xml_doc = Path(args.file).read_text()
            bundle = Bundle.from_xml(xml_doc)
            bundle.create(args.target_dir, args.source_dir)
        except Exception as e:
            log.critical(e)
    else:
        log.error("wrong invocation")
        parser.print_usage()

    log.info(
        "finished with {} warnings and {} errors".format(
            CollectStatisticsHandler.warnings(), CollectStatisticsHandler.errors()
        )
    )

    if CollectStatisticsHandler.has_errors():
        exit(1)
