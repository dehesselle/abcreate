# SPDX-FileCopyrightText: 2025 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
import argparse
from pathlib import Path
from enum import Enum

import os

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
            self.message_counter[record.levelno] += 1
        except KeyError:
            self.message_counter[record.levelno] = 1

    @classmethod
    def has_errors(cls) -> bool:
        return logging.ERROR in cls.message_counter


class Command(Enum):
    CREATE = "create"


def main() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-23s|%(name)-10s|%(levelname)-8s|%(message)s",
        handlers=[
            logging.FileHandler("abcreate.log"),
            logging.StreamHandler(),
            CollectStatisticsHandler(),
            ExitOnCriticalHandler(),
        ],
    )
    log.debug(f"abcreate {version}")

    parser = argparse.ArgumentParser(description="create an application bundle")
    parser.add_argument("--version", action="version", version=f"abcreate {version}")
    p_commands = parser.add_subparsers(help="available commands", dest="command")

    p_create = p_commands.add_parser(
        Command.CREATE.value, help="create application bundle"
    )
    p_create.add_argument("file")
    p_create.add_argument("-s", "--source_dir", required=True, help="source directory")
    p_create.add_argument("-t", "--target_dir", required=False, help="target directory")

    args = parser.parse_args()

    if args.command == Command.CREATE.value:
        try:
            xml_doc = Path(args.file).read_text()
            bundle = Bundle.from_xml(xml_doc)

            if args.target_dir:
                bundle.create(args.target_dir, args.source_dir)
            else:
                bundle.create(os.getcwd(), args.source_dir)
        except Exception as e:
            log.critical(e.msg)
    else:
        log.error("wrong invocation")
        parser.print_usage()

    log.debug("end log")

    if CollectStatisticsHandler.has_errors():
        exit(1)
