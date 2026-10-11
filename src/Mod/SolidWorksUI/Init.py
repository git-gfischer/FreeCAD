# SPDX-License-Identifier: LGPL-2.1-or-later
# SolidWorks-style shell. The widgets are installed from InitGui.py.

import FreeCAD


def _quiet_theme():
    # This FreeCAD build cannot evaluate the bare words in FreeCAD Dark.yaml
    # ("white", "images_classic"). Loading FreeCAD.qss then prints
    # StylesheetIconsColor / IconsLocationFolderName errors. The shell paints
    # its own dark theme, so those stylesheets are not needed.
    window = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/MainWindow")
    window.SetString("StyleSheet", "")
    window.SetString("OverlayActiveStyleSheet", "")


_quiet_theme()
