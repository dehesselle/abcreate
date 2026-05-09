# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import logging
from enum import Enum
from pathlib import Path

from abcreate.bundle import Bundle
from abcreate.util.version import VERSION

log = logging.getLogger("main")


class Command(Enum):
    CREATE = "create"


def create_app(args: argparse.Namespace) -> None:
    log.info(f"abcreate {VERSION}")
    xml_doc = args.file.read_text()
    bundle = Bundle.from_xml(xml_doc)
    bundle.create(args.output_dir, args.install_prefix)


def setup_cli(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--version", action="version", version=f"abcreate {VERSION}")
    commands = parser.add_subparsers(help="available commands", dest="command")

    create_command = commands.add_parser(
        Command.CREATE.value, help="create application bundle"
    )
    create_command.add_argument("file", type=Path, help="XML configuration file")
    create_command.add_argument(
        "-i",
        "--install_prefix",
        type=Path,
        required=True,
        help="install prefix of the application",
    )
    create_command.add_argument(
        "-o",
        "--output_dir",
        type=Path,
        required=True,
        help="directory to create the .app bundle in",
    )
    create_command.set_defaults(func=create_app)
