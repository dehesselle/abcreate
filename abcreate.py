#!/usr/bin/env python3

import logging
import argparse
from pathlib import Path
from enum import Enum

import os

from abcreate.bundle import Bundle
from abcreate.configuration import configuration as config

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


class Command(str, Enum):
    CREATE = "create"


def main():
    parser = argparse.ArgumentParser(description="create an application bundle")
    p_commands = parser.add_subparsers(help="available commands", dest="command")

    p_create = p_commands.add_parser(Command.CREATE, help="create application bundle")
    p_create.add_argument("file")
    p_create.add_argument("-s", "--source_dir", required=True, help="source directory")
    p_create.add_argument("-t", "--target_dir", required=False, help="target directory")

    args = parser.parse_args()

    if args.command == Command.CREATE:
        try:
            xml_doc = Path(args.file).read_text()
            bundle = Bundle.from_xml(xml_doc)

            for b in bundle.binaries:
                print(b.name)

            if args.target_dir:
                pass
            else:
                pass
                # os.getcwd()

        except Exception as e:
            log.critical(e.msg)
    else:
        parser.print_usage()


if __name__ == "__main__":
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

    log.info("begin")

    print(config.resolve_path("${env:HOME}/hanse"))
    # main()
    log.info("end")

    try:
        if CollectStatisticsHandler.message_counter[logging.ERROR] > 0:
            exit(1)
    except KeyError:
        pass
