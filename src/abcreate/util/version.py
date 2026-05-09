# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

try:
    from ._version import version as VERSION
except ImportError:
    VERSION = "0.0.0"
