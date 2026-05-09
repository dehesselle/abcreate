# SPDX-FileCopyrightText: 2025 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import logging
from enum import Enum
from pathlib import Path

from abcreate.bundle import Bundle
from abcreate.util.log import logstats, setup_logging
from abcreate.util.version import VERSION

log = logging.getLogger("main")


class Command(Enum):
    CREATE = "create"


def main() -> None:
    parser = argparse.ArgumentParser(description="create an application bundle")
    parser.add_argument("--version", action="version", version=f"abcreate {VERSION}")
    p_commands = parser.add_subparsers(help="available commands", dest="command")

    p_create = p_commands.add_parser(
        Command.CREATE.value, help="create application bundle"
    )
    p_create.add_argument("file", type=Path, help="XML configuration file")
    p_create.add_argument(
        "-i",
        "--install_prefix",
        type=Path,
        required=True,
        help="install prefix of the application",
    )
    p_create.add_argument(
        "-o",
        "--output_dir",
        type=Path,
        required=True,
        help="directory to create the .app bundle in",
    )

    args = parser.parse_args()

    if args.command == Command.CREATE.value:
        setup_logging(Path("abcreate.log"))
        log.info(f"abcreate {VERSION}")

        try:
            xml_doc = args.file.read_text()
            bundle = Bundle.from_xml(xml_doc)
        except Exception as e:
            log.critical(e)
        else:
            bundle.create(args.output_dir, args.install_prefix)

    else:
        parser.print_usage()

    log.info(f"finished with {logstats.warnings} warnings and {logstats.errors} errors")

    if logstats.errors:
        exit(1)
