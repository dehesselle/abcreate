# SPDX-FileCopyrightText: 2025 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
from pathlib import Path
import subprocess
from typing import List

from pydantic_xml import BaseXmlModel, element

from .icon import Icon
from .plist import Plist

log = logging.getLogger("icon")


class Icons(BaseXmlModel):
    icons: List[Icon] = element(tag="icon")

    @property
    def main_icon(self) -> Icon:
        try:
            return self.icons[0]
        except IndexError:
            log.critical("no icons specified")
            return None

    def install(self, bundle_dir: Path, install_prefix: Path):
        main_icon = self.main_icon
        generate_legacy_icon = True
        liquid_glass_icons = []

        for icon in self.icons:
            if icon.is_liquid_glass:
                liquid_glass_icons.append(icon.source_path)
            else:
                icon.install(bundle_dir, install_prefix)
                if main_icon.is_liquid_glass and not icon.is_liquid_glass and Path(main_icon.source_path).stem == Path(icon.source_path).stem:
                    # If there is a legacy icon with the same name as the main Liquid Glass icon,
                    # it will be used on legacy OS versions.
                    generate_legacy_icon = False

        main_icon_name = Path(main_icon.source_path).stem
        Plist().CFBundleIconFile = main_icon_name

        if main_icon.is_liquid_glass:
            # Because the main icon will be stored in an asset catalog, CFBundleIconName should be
            # set in addition to CFBundleIconFile.
            Plist().CFBundleIconName = main_icon_name

            self._install_liquid_glass_icons(
                bundle_dir,
                liquid_glass_icons,
                main_icon_name,
                generate_legacy_icon
            )
        elif liquid_glass_icons:
            log.error(
                f"not installing the Liquid Glass icon(s) {[str(path) for path in liquid_glass_icons]} "
                "because the main (first) icon is a legacy (*.icns) icon. To use a Liquid Glass "
                "icon as your main icon, specify it before all the other icons."
            )

    def _install_liquid_glass_icons(
        self,
        bundle_dir: Path,
        liquid_glass_icons: List[Icon],
        main_icon_name: str,
        generate_legacy_icon: bool
    ):
        # Liquid Glass icons are installed as part of an Assets.car file, called an asset catalog.

        target_dir = bundle_dir / "Contents" / "Resources"
        target_dir.mkdir(parents=True, exist_ok=True)

        try:
            subprocess.run(
                [
                    # actool is the command used to create asset catalogs.
                    "actool",

                    # All the Liquid Glass icons to be included in the asset catalog.
                    *liquid_glass_icons,

                    # Compile an asset catalog.
                    "--compile",

                    # actool will save two files to this directory: Assets.car, containing
                    # the Liquid Glass icon, and, if applicable, a generated legacy icon (*.icns).
                    # actool will only ever generate a fallback legacy icon for the main icon,
                    # even if you include more than one Liquid Glass icon.
                    target_dir,

                    # This is the main icon for the app.
                    "--app-icon", main_icon_name,

                    # If set to YES, an *.icns file will be created for backwards compatibility.
                    "--enable-icon-stack-fallback-generation", "YES" if generate_legacy_icon else "NO",

                    # It is possible to include more than one Liquid Glass app icon in one app,
                    # though it appears only the main one will actually be used.
                    "--include-all-app-icons",

                    # actool generates a partial Info.plist file containing the CFBundleIconFile
                    # and CFBundleIconName keys. We don’t need this file, but if we don’t provide
                    # a path for it, actool throws an error.
                    "--output-partial-info-plist", "/dev/null",

                    # macOS 26.0 Tahoe is the first version of macOS to support Liquid Glass icons.
                    "--platform", "macosx",
                    "--minimum-deployment-target", "26.0",

                    "--output-format", "human-readable-text",
                    "--errors",
                ]
            ).check_returncode()
        except FileNotFoundError:
            log.error(f"actool not found. It is included with the macOS SDK.")
        except subprocess.CalledProcessError as e:
            log.error(f"Liquid Glass icon asset catalog compilation failed\n{e}")
