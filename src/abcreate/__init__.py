# SPDX-FileCopyrightText: 2025 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import logging
from pathlib import Path

from abcreate.bundle.errors import BundleValidationError
from abcreate.util.cli import setup_cli
from abcreate.util.log import logstats, setup_logging

log = logging.getLogger("main")


def main() -> None:
    parser = argparse.ArgumentParser(description="create an application bundle")
    setup_cli(parser)
    args = parser.parse_args()
    setup_logging(Path("abcreate.log"))

    try:
        args.func(args)
    except AttributeError:
        parser.print_usage()
        exit(1)
    except BundleValidationError as e:
        log.critical(e)
        exit(2)

    log.info(f"finished with {logstats.warnings} warnings and {logstats.errors} errors")

    if logstats.errors:
        exit(1)
