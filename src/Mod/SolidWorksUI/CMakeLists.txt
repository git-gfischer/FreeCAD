# SPDX-License-Identifier: LGPL-2.1-or-later

SET(SolidWorksUI_SRCS
    Init.py
    InitGui.py
    swui.py
)

ADD_CUSTOM_TARGET(SolidWorksUI ALL SOURCES ${SolidWorksUI_SRCS})

fc_copy_sources(SolidWorksUI "${CMAKE_BINARY_DIR}/Mod/SolidWorksUI" ${SolidWorksUI_SRCS})

INSTALL(FILES ${SolidWorksUI_SRCS} DESTINATION Mod/SolidWorksUI)
