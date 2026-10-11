# SPDX-License-Identifier: LGPL-2.1-or-later
"""SolidWorks command manager on top of FreeCAD commands.

Button order follows the SolidWorks part-modeling ribbon. Each button calls
the FreeCAD command that performs that step. Profile features leave sketch
edit first, the same handoff SolidWorks makes between Sketch and Features.
"""

import os

# label uses a newline where the ribbon shows two lines.
TABS = [
    {
        "id": "Features",
        "label": "Features",
        "buttons": [
            {"label": "Extruded\nBoss/Base", "kind": "feature", "cmd": "PartDesign_Pad", "profile": True, "icon": "extrude"},
            {"label": "Extruded\nCut", "kind": "feature", "cmd": "PartDesign_Pocket", "profile": True, "icon": "cut"},
            {"label": "Revolved\nBoss/Base", "kind": "feature", "cmd": "PartDesign_Revolution", "profile": True, "icon": "revolve"},
            {"label": "Revolved\nCut", "kind": "feature", "cmd": "PartDesign_Groove", "profile": True, "icon": "groove"},
            {"label": "Swept\nBoss/Base", "kind": "feature", "cmd": "PartDesign_AdditivePipe", "profile": True, "icon": "sweep"},
            {"label": "Lofted\nBoss/Base", "kind": "feature", "cmd": "PartDesign_AdditiveLoft", "profile": True, "icon": "loft"},
            {
                "label": "Boundary\nBoss/Base",
                "kind": "feature",
                "cmd": "PartDesign_AdditiveLoft",
                "profile": True,
                "icon": "boundary",
                "note": "FreeCAD has no boundary boss. This opens Loft, which needs two or more profiles.",
            },
            {"sep": True},
            {"label": "Swept\nCut", "kind": "feature", "cmd": "PartDesign_SubtractivePipe", "profile": True, "icon": "sweepcut"},
            {"label": "Lofted\nCut", "kind": "feature", "cmd": "PartDesign_SubtractiveLoft", "profile": True, "icon": "loftcut"},
            {"sep": True},
            {"label": "Fillet", "kind": "feature", "cmd": "PartDesign_Fillet", "icon": "fillet"},
            {"label": "Chamfer", "kind": "feature", "cmd": "PartDesign_Chamfer", "icon": "chamfer"},
            {"label": "Draft", "kind": "feature", "cmd": "PartDesign_Draft", "icon": "draft"},
            {"label": "Shell", "kind": "feature", "cmd": "PartDesign_Thickness", "icon": "shell"},
            {
                "label": "Rib",
                "kind": "feature",
                "cmd": "PartDesign_Pad",
                "profile": True,
                "icon": "rib",
                "note": "FreeCAD has no rib feature. Draw the rib profile, then extrude it.",
            },
            {
                "label": "Wrap",
                "kind": "feature",
                "cmd": "PartDesign_AdditivePipe",
                "profile": True,
                "icon": "wrap",
                "note": "FreeCAD has no wrap feature. This opens Sweep.",
            },
            {"label": "Hole\nWizard", "kind": "feature", "cmd": "PartDesign_Hole", "icon": "hole"},
            {"label": "Intersect", "kind": "feature", "cmd": "PartDesign_Boolean", "icon": "intersect"},
            {"sep": True},
            {"label": "Linear\nPattern", "kind": "feature", "cmd": "PartDesign_LinearPattern", "icon": "linear"},
            {"label": "Circular\nPattern", "kind": "feature", "cmd": "PartDesign_PolarPattern", "icon": "polar"},
            {"label": "Mirror", "kind": "feature", "cmd": "PartDesign_Mirrored", "icon": "mirror"},
        ],
    },
    {
        "id": "Sketch",
        "label": "Sketch",
        "buttons": [
            {"label": "Sketch", "kind": "newsketch", "icon": "sketch"},
            {"label": "Smart\nDimension", "kind": "sketch", "cmd": "Sketcher_Dimension", "fallback": "Sketcher_ConstrainDistance", "icon": "dim"},
            {"label": "Line", "kind": "sketch", "cmd": "Sketcher_CreateLine", "icon": "line"},
            {"label": "Centerline", "kind": "sketch", "cmd": "Sketcher_ToggleConstruction", "icon": "centerline"},
            {"label": "Corner\nRectangle", "kind": "sketch", "cmd": "Sketcher_CreateRectangle", "icon": "rect"},
            {"label": "Circle", "kind": "sketch", "cmd": "Sketcher_CreateCircle", "icon": "circle"},
            {"label": "Centerpoint\nArc", "kind": "sketch", "cmd": "Sketcher_CreateArc", "icon": "arc"},
            {"label": "3 Point\nArc", "kind": "sketch", "cmd": "Sketcher_Create3PointArc", "icon": "arc3"},
            {"label": "Slot", "kind": "sketch", "cmd": "Sketcher_CreateSlot", "icon": "slot"},
            {"label": "Polygon", "kind": "sketch", "cmd": "Sketcher_CreateHexagon", "icon": "polygon"},
            {"label": "Spline", "kind": "sketch", "cmd": "Sketcher_CreateBSpline", "icon": "spline"},
            {"label": "Point", "kind": "sketch", "cmd": "Sketcher_CreatePoint", "icon": "point"},
            {"sep": True},
            {"label": "Trim\nEntities", "kind": "sketch", "cmd": "Sketcher_Trimming", "icon": "trim"},
            {"label": "Offset\nEntities", "kind": "sketch", "cmd": "Sketcher_Offset", "icon": "offset"},
            {"label": "Convert\nEntities", "kind": "sketch", "cmd": "Sketcher_Projection", "fallback": "Sketcher_CompExternal", "icon": "project"},
            {"label": "Mirror\nEntities", "kind": "sketch", "cmd": "Sketcher_MirrorSketch", "icon": "mirror"},
            {"label": "Linear Sketch\nPattern", "kind": "sketch", "cmd": "Sketcher_RectangularArray", "icon": "linear"},
            {"label": "Sketch\nFillet", "kind": "sketch", "cmd": "Sketcher_CreateFillet", "icon": "fillet"},
            {"sep": True},
            {"label": "Coincident", "kind": "sketch", "cmd": "Sketcher_ConstrainCoincidentUnified", "fallback": "Sketcher_ConstrainCoincident", "icon": "coincident"},
            {"label": "Horizontal", "kind": "sketch", "cmd": "Sketcher_ConstrainHorizontal", "icon": "horizontal"},
            {"label": "Vertical", "kind": "sketch", "cmd": "Sketcher_ConstrainVertical", "icon": "vertical"},
            {"label": "Parallel", "kind": "sketch", "cmd": "Sketcher_ConstrainParallel", "icon": "parallel"},
            {"label": "Perpendicular", "kind": "sketch", "cmd": "Sketcher_ConstrainPerpendicular", "icon": "perpendicular"},
            {"label": "Tangent", "kind": "sketch", "cmd": "Sketcher_ConstrainTangent", "icon": "tangent"},
            {"label": "Equal", "kind": "sketch", "cmd": "Sketcher_ConstrainEqual", "icon": "equal"},
            {"sep": True},
            {"label": "Exit\nSketch", "kind": "exitsketch", "icon": "exit"},
        ],
    },
    {
        "id": "Surfaces",
        "label": "Surfaces",
        "buttons": [
            {"label": "Extruded\nSurface", "kind": "command", "cmd": "Part_Extrude", "wb": "PartWorkbench", "icon": "extrude"},
            {"label": "Revolved\nSurface", "kind": "command", "cmd": "Part_Revolve", "wb": "PartWorkbench", "icon": "revolve"},
            {"label": "Swept\nSurface", "kind": "command", "cmd": "Part_Sweep", "wb": "PartWorkbench", "icon": "sweep"},
            {"label": "Lofted\nSurface", "kind": "command", "cmd": "Part_Loft", "wb": "PartWorkbench", "icon": "loft"},
            {"label": "Boundary\nSurface", "kind": "command", "cmd": "Surface_GeomFillSurface", "wb": "SurfaceWorkbench", "icon": "boundary"},
            {"label": "Filled\nSurface", "kind": "command", "cmd": "Surface_Filling", "wb": "SurfaceWorkbench", "icon": "fill"},
            {"label": "Ruled\nSurface", "kind": "command", "cmd": "Part_RuledSurface", "wb": "PartWorkbench", "icon": "loft"},
            {"label": "Offset\nSurface", "kind": "command", "cmd": "Part_Offset", "wb": "PartWorkbench", "icon": "offset"},
            {"label": "Extend\nSurface", "kind": "command", "cmd": "Surface_ExtendFace", "wb": "SurfaceWorkbench", "icon": "extend"},
            {"label": "Trim\nSurface", "kind": "command", "cmd": "Surface_Cut", "wb": "SurfaceWorkbench", "icon": "trim"},
            {
                "label": "Knit\nSurface",
                "kind": "command",
                "cmd": "Part_Compound",
                "wb": "PartWorkbench",
                "icon": "knit",
                "note": "FreeCAD groups faces with a compound. Fuse the solids if you need one body.",
            },
        ],
    },
    {
        "id": "SheetMetal",
        "label": "Sheet Metal",
        "buttons": [
            {"label": "Base\nFlange", "kind": "try", "cmd": "SheetMetal_AddBase", "fallback": "PartDesign_Pad", "wb": "SheetMetalWorkbench", "fallback_wb": "PartDesignWorkbench", "profile": True, "icon": "flange", "note": "SheetMetal addon is not loaded. Using Extrude for the base flange."},
            {"label": "Edge\nFlange", "kind": "try", "cmd": "SheetMetal_AddWall", "fallback": "PartDesign_Pad", "wb": "SheetMetalWorkbench", "fallback_wb": "PartDesignWorkbench", "profile": True, "icon": "flange", "note": "SheetMetal addon is not loaded. Using Extrude."},
            {"label": "Miter\nFlange", "kind": "try", "cmd": "SheetMetal_AddMiter", "fallback": "PartDesign_Pad", "wb": "SheetMetalWorkbench", "fallback_wb": "PartDesignWorkbench", "icon": "flange", "note": "SheetMetal addon is not loaded. Using Extrude."},
            {"label": "Hem", "kind": "try", "cmd": "SheetMetal_AddHem", "fallback": "PartDesign_Thickness", "wb": "SheetMetalWorkbench", "fallback_wb": "PartDesignWorkbench", "icon": "hem", "note": "SheetMetal addon is not loaded. Using Shell."},
            {"label": "Jog", "kind": "try", "cmd": "SheetMetal_AddJog", "fallback": "PartDesign_Pad", "wb": "SheetMetalWorkbench", "fallback_wb": "PartDesignWorkbench", "icon": "jog", "note": "SheetMetal addon is not loaded. Using Extrude."},
            {"label": "Sketched\nBend", "kind": "try", "cmd": "SheetMetal_AddBend", "fallback": "PartDesign_Pad", "wb": "SheetMetalWorkbench", "fallback_wb": "PartDesignWorkbench", "icon": "bend", "note": "SheetMetal addon is not loaded. Using Extrude."},
            {"label": "Unfold", "kind": "try", "cmd": "SheetMetal_Unfold", "wb": "SheetMetalWorkbench", "icon": "unfold", "note": "Unfold needs the SheetMetal addon."},
            {"label": "Fold", "kind": "try", "cmd": "SheetMetal_Fold", "wb": "SheetMetalWorkbench", "icon": "fold", "note": "Fold needs the SheetMetal addon."},
            {"label": "Flatten", "kind": "try", "cmd": "SheetMetal_Unfold", "wb": "SheetMetalWorkbench", "icon": "unfold", "note": "Flatten needs the SheetMetal addon."},
            {"label": "Corner\nRelief", "kind": "try", "cmd": "SheetMetal_AddCornerRelief", "fallback": "PartDesign_Fillet", "wb": "SheetMetalWorkbench", "fallback_wb": "PartDesignWorkbench", "icon": "fillet", "note": "SheetMetal addon is not loaded. Using Fillet."},
        ],
    },
    {
        "id": "Mold",
        "label": "Mold",
        "buttons": [
            {"label": "Draft\nAnalysis", "kind": "command", "cmd": "PartDesign_Draft", "wb": "PartDesignWorkbench", "icon": "draft", "note": "This is a draft feature, not a mold draft-analysis plot."},
            {"label": "Undercut\nDetection", "kind": "command", "cmd": "Part_CheckGeometry", "wb": "PartWorkbench", "icon": "check"},
            {"label": "Parting\nLine", "kind": "command", "cmd": "Part_SectionCut", "wb": "PartWorkbench", "icon": "section"},
            {"label": "Parting\nSurface", "kind": "command", "cmd": "Surface_Filling", "wb": "SurfaceWorkbench", "icon": "fill"},
            {"label": "Shut-off\nSurfaces", "kind": "command", "cmd": "Surface_Filling", "wb": "SurfaceWorkbench", "icon": "fill"},
            {"label": "Tooling\nSplit", "kind": "command", "cmd": "Part_SliceApart", "wb": "PartWorkbench", "icon": "split"},
            {"label": "Core", "kind": "feature", "cmd": "PartDesign_Pocket", "profile": True, "icon": "cut"},
            {"label": "Cavity", "kind": "command", "cmd": "PartDesign_Boolean", "wb": "PartDesignWorkbench", "icon": "intersect"},
            {"label": "Move\nFace", "kind": "command", "cmd": "Part_Offset", "wb": "PartWorkbench", "icon": "offset", "note": "FreeCAD offset is the closest move-face."},
            {"label": "Delete\nFace", "kind": "command", "cmd": "PartDesign_Defeaturing", "wb": "PartDesignWorkbench", "icon": "delete"},
            {"label": "Scale", "kind": "command", "cmd": "PartDesign_Scaled", "wb": "PartDesignWorkbench", "icon": "scale"},
        ],
    },
    {
        "id": "Direct",
        "label": "Direct Editing",
        "buttons": [
            {"label": "Move\nFace", "kind": "command", "cmd": "Part_Offset", "wb": "PartWorkbench", "icon": "offset", "note": "FreeCAD offset is the closest move-face."},
            {"label": "Delete\nFace", "kind": "command", "cmd": "PartDesign_Defeaturing", "wb": "PartDesignWorkbench", "icon": "delete"},
            {"label": "Move/Copy", "kind": "command", "cmd": "Draft_Move", "wb": "DraftWorkbench", "icon": "move"},
            {"label": "Rotate", "kind": "command", "cmd": "Draft_Rotate", "wb": "DraftWorkbench", "icon": "rotate"},
            {"label": "Copy\nBody", "kind": "command", "cmd": "PartDesign_Clone", "wb": "PartDesignWorkbench", "icon": "copy"},
            {"label": "Combine", "kind": "command", "cmd": "PartDesign_Boolean", "wb": "PartDesignWorkbench", "icon": "intersect"},
            {"label": "Intersect", "kind": "command", "cmd": "Part_Common", "wb": "PartWorkbench", "icon": "intersect"},
            {"label": "Split", "kind": "command", "cmd": "Part_SliceApart", "wb": "PartWorkbench", "icon": "split"},
            {"label": "Offset\nSurface", "kind": "command", "cmd": "Part_Offset", "wb": "PartWorkbench", "icon": "offset"},
        ],
    },
    {
        "id": "Evaluate",
        "label": "Evaluate",
        "buttons": [
            {"label": "Measure", "kind": "command", "cmd": "Std_Measure", "icon": "measure"},
            {"label": "Mass\nProperties", "kind": "command", "cmd": "Std_MassProperties", "icon": "mass"},
            {"label": "Section\nView", "kind": "command", "cmd": "Part_SectionCut", "wb": "PartWorkbench", "icon": "section"},
            {"label": "Check", "kind": "command", "cmd": "Part_CheckGeometry", "wb": "PartWorkbench", "icon": "check"},
            {"label": "Interference\nDetection", "kind": "command", "cmd": "Part_Common", "wb": "PartWorkbench", "icon": "intersect", "note": "The common solid is the overlap of the selected shapes."},
            {"label": "Deviation\nAnalysis", "kind": "command", "cmd": "Part_CheckGeometry", "wb": "PartWorkbench", "icon": "check"},
        ],
    },
    {
        "id": "Addins",
        "label": "SOLIDWORKS Add-ins",
        "buttons": [
            {"label": "Part\nDesign", "kind": "workbench", "wb": "PartDesignWorkbench", "icon": "extrude"},
            {"label": "Part", "kind": "workbench", "wb": "PartWorkbench", "icon": "box"},
            {"label": "Sketcher", "kind": "workbench", "wb": "SketcherWorkbench", "icon": "sketch"},
            {"label": "Draft", "kind": "workbench", "wb": "DraftWorkbench", "icon": "line"},
            {"label": "Assembly", "kind": "workbench", "wb": "AssemblyWorkbench", "icon": "intersect"},
            {"label": "Drawing", "kind": "command", "cmd": "TechDraw_PageDefault", "wb": "TechDrawWorkbench", "icon": "drawing"},
            {"label": "Simulation", "kind": "workbench", "wb": "FemWorkbench", "icon": "mesh"},
            {"label": "CAM", "kind": "workbench", "wb": "CAMWorkbench", "icon": "cam"},
            {"label": "Spreadsheet", "kind": "workbench", "wb": "SpreadsheetWorkbench", "icon": "table"},
            {"label": "Mesh", "kind": "workbench", "wb": "MeshWorkbench", "icon": "mesh"},
            {"label": "Surface", "kind": "workbench", "wb": "SurfaceWorkbench", "icon": "boundary"},
        ],
    },
]

FEATURE_LABELS = {
    "PartDesign::Pad": "Boss-Extrude",
    "PartDesign::Pocket": "Cut-Extrude",
    "PartDesign::Revolution": "Boss-Revolve",
    "PartDesign::Groove": "Cut-Revolve",
    "PartDesign::AdditivePipe": "Boss-Sweep",
    "PartDesign::SubtractivePipe": "Cut-Sweep",
    "PartDesign::AdditiveLoft": "Boss-Loft",
    "PartDesign::SubtractiveLoft": "Cut-Loft",
    "PartDesign::Fillet": "Fillet",
    "PartDesign::Chamfer": "Chamfer",
    "PartDesign::Thickness": "Shell",
    "PartDesign::Draft": "Draft",
    "PartDesign::Mirrored": "Mirror",
    "PartDesign::LinearPattern": "LPattern",
    "PartDesign::PolarPattern": "CirPattern",
    "PartDesign::Hole": "Hole",
    "PartDesign::Boolean": "Combine",
    "Sketcher::SketchObject": "Sketch",
}

PLANES = {
    "XY_Plane": "Top Plane",
    "XZ_Plane": "Front Plane",
    "YZ_Plane": "Right Plane",
}

_KINDS = {"feature", "sketch", "command", "try", "newsketch", "exitsketch", "workbench"}
_NEED_CMD = {"feature", "sketch", "command", "try"}
_NEED_WB = {"workbench"}

_state = {"editing": False, "relabel": False, "mgr": None, "ticks": 0}


def button_id(tab_id, spec):
    plain = spec["label"].replace("\n", " ")
    slug = "".join(ch if ch.isalnum() else "_" for ch in plain)
    return "SWbtn_%s_%s" % (tab_id, slug)


def validate():
    assert [tab["label"] for tab in TABS] == [
        "Features",
        "Sketch",
        "Surfaces",
        "Sheet Metal",
        "Mold",
        "Direct Editing",
        "Evaluate",
        "SOLIDWORKS Add-ins",
    ]
    seen = set()
    required = {
        "Features": {"Extruded Boss/Base", "Extruded Cut", "Revolved Boss/Base", "Mirror"},
        "Sketch": {"Sketch", "Line", "Smart Dimension", "Exit Sketch"},
    }
    found = {tab["id"]: set() for tab in TABS}
    for tab in TABS:
        assert tab["id"] and tab["label"]
        for spec in tab["buttons"]:
            if spec.get("sep"):
                continue
            assert spec.get("label"), spec
            assert spec["kind"] in _KINDS, spec
            if spec["kind"] in _NEED_CMD:
                assert spec.get("cmd"), spec
            if spec["kind"] in _NEED_WB:
                assert spec.get("wb"), spec
            oid = button_id(tab["id"], spec)
            assert oid not in seen, oid
            seen.add(oid)
            found[tab["id"]].add(spec["label"].replace("\n", " "))
    for tab_id, names in required.items():
        missing = names - found[tab_id]
        assert not missing, missing
    return len(seen)


def _pack(red, green, blue):
    return (red << 24) | (green << 16) | (blue << 8)


if __name__ == "__main__":
    print("swui selfcheck ok", validate())
    raise SystemExit(0)

import FreeCAD
import FreeCADGui

try:
    from PySide import QtCore, QtGui, QtWidgets
except ImportError:
    from PySide6 import QtCore, QtGui, QtWidgets


def _tip(spec):
    lines = [spec["label"].replace("\n", " ")]
    if spec.get("cmd"):
        lines.append("FreeCAD: " + spec["cmd"])
    if spec.get("fallback"):
        lines.append("Fallback: " + spec["fallback"])
    if spec.get("note"):
        lines.append(spec["note"])
    return "\n".join(lines)


def paint_icon(kind):
    pm = QtGui.QPixmap(32, 32)
    pm.fill(QtCore.Qt.transparent)
    painter = QtGui.QPainter(pm)
    painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
    ink = QtGui.QColor("#3c4650")
    painter.setPen(QtGui.QPen(ink, 1.2))
    gold, red, blue = "#d89a16", "#c62828", "#1565c0"

    def slab(accent, arrow):
        painter.setPen(QtGui.QPen(ink, 1.1))
        top = QtGui.QPolygonF(
            [
                QtCore.QPointF(7, 12),
                QtCore.QPointF(18, 7),
                QtCore.QPointF(27, 12),
                QtCore.QPointF(16, 17),
            ]
        )
        right = QtGui.QPolygonF(
            [
                QtCore.QPointF(18, 7),
                QtCore.QPointF(27, 12),
                QtCore.QPointF(27, 22),
                QtCore.QPointF(18, 17),
            ]
        )
        left = QtGui.QPolygonF(
            [
                QtCore.QPointF(7, 12),
                QtCore.QPointF(16, 17),
                QtCore.QPointF(16, 27),
                QtCore.QPointF(7, 22),
            ]
        )
        painter.setBrush(QtGui.QColor("#d5dbe1"))
        painter.drawPolygon(top)
        painter.setBrush(QtGui.QColor("#b7c0c8"))
        painter.drawPolygon(right)
        painter.setBrush(QtGui.QColor("#9aa6b0"))
        painter.drawPolygon(left)
        color = QtGui.QColor(accent)
        painter.setPen(QtGui.QPen(color, 1.7))
        painter.setBrush(color)
        if arrow == "up":
            painter.drawLine(QtCore.QPointF(16, 16), QtCore.QPointF(16, 5))
            painter.drawPolygon(
                QtGui.QPolygonF(
                    [QtCore.QPointF(16, 2), QtCore.QPointF(12, 7), QtCore.QPointF(20, 7)]
                )
            )
        elif arrow == "down":
            painter.drawLine(QtCore.QPointF(22, 14), QtCore.QPointF(22, 26))
            painter.drawPolygon(
                QtGui.QPolygonF(
                    [QtCore.QPointF(22, 29), QtCore.QPointF(18, 24), QtCore.QPointF(26, 24)]
                )
            )
        elif arrow == "spin":
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.drawArc(4, 2, 18, 12, 40 * 16, 220 * 16)

    def stroke():
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(QtGui.QPen(ink, 1.6))

    if kind in ("extrude", "flange", "rib"):
        slab(gold, "up")
    elif kind in ("cut", "sweepcut", "loftcut"):
        slab(red, "down")
    elif kind == "revolve":
        slab(blue, "spin")
    elif kind == "groove":
        slab(red, "spin")
    elif kind in ("sweep", "wrap"):
        slab(gold, "up")
        stroke()
        painter.drawArc(18, 14, 12, 12, 0, 180 * 16)
    elif kind in ("loft", "boundary", "fill", "knit"):
        slab(blue if kind != "loft" else gold, None)
    elif kind == "fillet":
        stroke()
        painter.drawArc(6, 6, 20, 20, 0, 90 * 16)
        painter.drawLine(QtCore.QPointF(6, 16), QtCore.QPointF(6, 26))
        painter.drawLine(QtCore.QPointF(16, 6), QtCore.QPointF(26, 6))
    elif kind == "chamfer":
        stroke()
        painter.drawLine(QtCore.QPointF(6, 24), QtCore.QPointF(14, 8))
        painter.drawLine(QtCore.QPointF(14, 8), QtCore.QPointF(26, 8))
    elif kind == "draft":
        slab(blue, None)
    elif kind == "shell":
        stroke()
        painter.drawRect(QtCore.QRectF(8, 8, 16, 16))
        painter.drawRect(QtCore.QRectF(12, 12, 8, 8))
    elif kind == "hole":
        slab("#607d8b", None)
        painter.setBrush(QtGui.QColor("#eceff1"))
        painter.drawEllipse(QtCore.QPointF(16, 14), 3.5, 2.2)
    elif kind in ("intersect", "copy"):
        stroke()
        painter.drawEllipse(QtCore.QRectF(6, 8, 12, 12))
        painter.drawEllipse(QtCore.QRectF(14, 12, 12, 12))
    elif kind == "linear":
        stroke()
        for x in (6, 14, 22):
            painter.drawRect(QtCore.QRectF(x, 10, 6, 12))
    elif kind == "polar":
        stroke()
        painter.drawEllipse(QtCore.QRectF(12, 12, 8, 8))
        for pt in ((8, 8), (20, 8), (8, 20), (20, 20)):
            painter.drawEllipse(QtCore.QPointF(*pt), 2.2, 2.2)
    elif kind == "mirror":
        stroke()
        painter.drawLine(QtCore.QPointF(16, 4), QtCore.QPointF(16, 28))
        painter.drawRect(QtCore.QRectF(6, 10, 7, 12))
        painter.drawRect(QtCore.QRectF(19, 10, 7, 12))
    elif kind in ("line", "centerline"):
        stroke()
        if kind == "centerline":
            painter.setPen(QtGui.QPen(ink, 1.4, QtCore.Qt.DashLine))
        painter.drawLine(QtCore.QPointF(6, 24), QtCore.QPointF(26, 8))
    elif kind == "rect":
        stroke()
        painter.drawRect(QtCore.QRectF(7, 8, 18, 16))
    elif kind == "circle":
        stroke()
        painter.drawEllipse(QtCore.QRectF(7, 7, 18, 18))
    elif kind in ("arc", "arc3"):
        stroke()
        painter.drawArc(6, 8, 20, 16, 20 * 16, 160 * 16)
    elif kind == "slot":
        stroke()
        painter.drawRoundedRect(QtCore.QRectF(6, 10, 20, 12), 6, 6)
    elif kind == "polygon":
        stroke()
        painter.drawPolygon(
            QtGui.QPolygonF(
                [
                    QtCore.QPointF(16, 5),
                    QtCore.QPointF(26, 12),
                    QtCore.QPointF(22, 25),
                    QtCore.QPointF(10, 25),
                    QtCore.QPointF(6, 12),
                ]
            )
        )
    elif kind == "spline":
        stroke()
        path = QtGui.QPainterPath(QtCore.QPointF(4, 22))
        path.cubicTo(10, 4, 18, 28, 28, 10)
        painter.drawPath(path)
    elif kind == "point":
        painter.setBrush(ink)
        painter.drawEllipse(QtCore.QPointF(16, 16), 2.4, 2.4)
    elif kind == "dim":
        stroke()
        painter.drawLine(QtCore.QPointF(6, 22), QtCore.QPointF(26, 22))
        painter.drawLine(QtCore.QPointF(6, 18), QtCore.QPointF(6, 26))
        painter.drawLine(QtCore.QPointF(26, 18), QtCore.QPointF(26, 26))
    elif kind == "trim":
        stroke()
        painter.drawLine(QtCore.QPointF(6, 24), QtCore.QPointF(26, 8))
        painter.setPen(QtGui.QPen(QtGui.QColor(red), 1.8))
        painter.drawLine(QtCore.QPointF(12, 8), QtCore.QPointF(22, 20))
    elif kind in ("offset", "extend"):
        stroke()
        painter.drawRect(QtCore.QRectF(8, 10, 12, 12))
        painter.setPen(QtGui.QPen(QtGui.QColor(blue), 1.4, QtCore.Qt.DashLine))
        painter.drawRect(QtCore.QRectF(12, 6, 12, 12))
    elif kind == "project":
        stroke()
        painter.drawLine(QtCore.QPointF(6, 8), QtCore.QPointF(22, 8))
        painter.setPen(QtGui.QPen(QtGui.QColor(blue), 1.5))
        painter.drawLine(QtCore.QPointF(8, 16), QtCore.QPointF(24, 16))
    elif kind == "sketch":
        stroke()
        painter.drawRect(QtCore.QRectF(6, 8, 16, 14))
        painter.drawLine(QtCore.QPointF(18, 18), QtCore.QPointF(26, 26))
    elif kind == "exit":
        stroke()
        painter.drawRect(QtCore.QRectF(6, 8, 14, 16))
        painter.setPen(QtGui.QPen(QtGui.QColor(gold), 1.8))
        painter.drawLine(QtCore.QPointF(16, 16), QtCore.QPointF(27, 16))
        painter.drawLine(QtCore.QPointF(23, 12), QtCore.QPointF(27, 16))
        painter.drawLine(QtCore.QPointF(23, 20), QtCore.QPointF(27, 16))
    elif kind in ("horizontal", "vertical", "parallel", "perpendicular", "tangent", "equal", "coincident"):
        stroke()
        if kind == "vertical":
            painter.drawLine(QtCore.QPointF(16, 6), QtCore.QPointF(16, 26))
        elif kind == "perpendicular":
            painter.drawLine(QtCore.QPointF(8, 24), QtCore.QPointF(24, 8))
            painter.drawLine(QtCore.QPointF(14, 8), QtCore.QPointF(24, 8))
            painter.drawLine(QtCore.QPointF(24, 8), QtCore.QPointF(24, 18))
        elif kind == "coincident":
            painter.setBrush(ink)
            painter.drawEllipse(QtCore.QPointF(16, 16), 3, 3)
        else:
            painter.drawLine(QtCore.QPointF(6, 20), QtCore.QPointF(26, 12))
            if kind == "parallel":
                painter.drawLine(QtCore.QPointF(6, 25), QtCore.QPointF(26, 17))
    elif kind == "measure":
        stroke()
        painter.drawLine(QtCore.QPointF(8, 24), QtCore.QPointF(24, 8))
    elif kind == "mass":
        slab(blue, None)
    elif kind == "section":
        slab(red, None)
        painter.setPen(QtGui.QPen(QtGui.QColor(red), 1.6))
        painter.drawLine(QtCore.QPointF(4, 20), QtCore.QPointF(28, 10))
    elif kind == "check":
        painter.setPen(QtGui.QPen(QtGui.QColor("#2e7d32"), 2.2))
        painter.drawLine(QtCore.QPointF(8, 16), QtCore.QPointF(14, 23))
        painter.drawLine(QtCore.QPointF(14, 23), QtCore.QPointF(25, 9))
    elif kind == "split":
        slab(blue, None)
        painter.setPen(QtGui.QPen(QtGui.QColor(red), 1.5))
        painter.drawLine(QtCore.QPointF(16, 4), QtCore.QPointF(16, 28))
    elif kind == "delete":
        stroke()
        painter.drawLine(QtCore.QPointF(8, 8), QtCore.QPointF(24, 24))
        painter.drawLine(QtCore.QPointF(24, 8), QtCore.QPointF(8, 24))
    elif kind == "move":
        stroke()
        painter.drawLine(QtCore.QPointF(6, 16), QtCore.QPointF(26, 16))
        painter.drawLine(QtCore.QPointF(20, 10), QtCore.QPointF(26, 16))
        painter.drawLine(QtCore.QPointF(20, 22), QtCore.QPointF(26, 16))
    elif kind == "rotate":
        stroke()
        painter.setPen(QtGui.QPen(QtGui.QColor(blue), 1.6))
        painter.drawArc(6, 6, 18, 18, 30 * 16, 260 * 16)
    elif kind == "scale":
        stroke()
        painter.drawRect(QtCore.QRectF(8, 12, 8, 8))
        painter.drawRect(QtCore.QRectF(14, 8, 12, 12))
    elif kind in ("hem", "jog", "bend", "fold", "unfold"):
        stroke()
        painter.drawLine(QtCore.QPointF(6, 20), QtCore.QPointF(14, 20))
        painter.drawLine(QtCore.QPointF(14, 20), QtCore.QPointF(20, 10))
        painter.drawLine(QtCore.QPointF(20, 10), QtCore.QPointF(27, 10))
    elif kind == "drawing":
        stroke()
        painter.drawRect(QtCore.QRectF(8, 5, 16, 22))
        painter.drawLine(QtCore.QPointF(11, 12), QtCore.QPointF(21, 12))
        painter.drawLine(QtCore.QPointF(11, 17), QtCore.QPointF(21, 17))
    elif kind == "cam":
        stroke()
        painter.drawEllipse(QtCore.QRectF(8, 8, 16, 16))
        painter.drawLine(QtCore.QPointF(16, 8), QtCore.QPointF(16, 24))
    elif kind == "table":
        stroke()
        painter.drawRect(QtCore.QRectF(6, 7, 20, 18))
        painter.drawLine(QtCore.QPointF(6, 13), QtCore.QPointF(26, 13))
        painter.drawLine(QtCore.QPointF(14, 7), QtCore.QPointF(14, 25))
    elif kind == "mesh":
        stroke()
        painter.drawLine(QtCore.QPointF(16, 6), QtCore.QPointF(26, 24))
        painter.drawLine(QtCore.QPointF(26, 24), QtCore.QPointF(6, 24))
        painter.drawLine(QtCore.QPointF(6, 24), QtCore.QPointF(16, 6))
    else:
        slab(blue, None)
    painter.end()
    return QtGui.QIcon(pm)


class SWButton(QtWidgets.QFrame):
    def __init__(self, tab_id, spec):
        super().__init__()
        self.spec = spec
        self.plain = spec["label"].replace("\n", " ")
        self.setObjectName(button_id(tab_id, spec))
        self.setFixedSize(76, 72)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setToolTip(_tip(spec))
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(2, 3, 2, 2)
        layout.setSpacing(1)
        icon = QtWidgets.QLabel()
        icon.setPixmap(paint_icon(spec.get("icon", "box")).pixmap(28, 28))
        icon.setAlignment(QtCore.Qt.AlignCenter)
        icon.setStyleSheet("background: transparent; border: none;")
        text = QtWidgets.QLabel(spec["label"].replace("\n", "<br>"))
        text.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        text.setTextFormat(QtCore.Qt.RichText)
        text.setStyleSheet("background: transparent; border: none; color: #e8e8e8; font-size: 10px;")
        layout.addWidget(icon)
        layout.addWidget(text)
        self._idle()

    def _idle(self):
        self.setStyleSheet("background: transparent; border: 1px solid transparent; border-radius: 2px;")

    def enterEvent(self, event):
        self.setStyleSheet("background: #d6ebf9; border: 1px solid #7eb4ea; border-radius: 2px;")
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._idle()
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.rect().contains(event.pos()):
            dispatch(self.spec)
        super().mouseReleaseEvent(event)


class CommandManager(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("SWCommandManagerHost")
        self._buttons = {}
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        header = QtWidgets.QHBoxLayout()
        header.setContentsMargins(8, 0, 8, 0)
        self.tabs = QtWidgets.QTabBar()
        self.tabs.setDocumentMode(True)
        self.tabs.setExpanding(False)
        self.tabs.setDrawBase(False)
        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText("Search Commands")
        self.search.setClearButtonEnabled(True)
        self.search.setFixedWidth(210)
        header.addWidget(self.tabs, 1)
        header.addWidget(self.search, 0)
        root.addLayout(header)
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll.setWidgetResizable(False)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll.setFixedHeight(84)
        self.scroll.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        root.addWidget(self.scroll)
        # One stack. QScrollArea.setWidget() deletes the previous widget.
        self.stack = QtWidgets.QStackedWidget()
        self.scroll.setWidget(self.stack)
        self._pages = {}
        for index, tab in enumerate(TABS):
            self.tabs.addTab(tab["label"])
            self.tabs.setTabData(index, tab["id"])
            page = QtWidgets.QWidget()
            row = QtWidgets.QHBoxLayout(page)
            row.setContentsMargins(6, 2, 6, 2)
            row.setSpacing(2)
            buttons = []
            for spec in tab["buttons"]:
                if spec.get("sep"):
                    line = QtWidgets.QFrame()
                    line.setFrameShape(QtWidgets.QFrame.VLine)
                    line.setFixedSize(8, 64)
                    line.setStyleSheet("color: #555555;")
                    row.addWidget(line)
                    continue
                button = SWButton(tab["id"], spec)
                row.addWidget(button)
                buttons.append(button)
            row.addStretch(1)
            self._buttons[tab["id"]] = buttons
            self._pages[tab["id"]] = page
            self.stack.addWidget(page)
        self.tabs.currentChanged.connect(self._show_index)
        self.search.textChanged.connect(self._filter)
        self.setStyleSheet(
            "QTabBar::tab { background: #2b2b2b; color: #c8c8c8; padding: 6px 14px;"
            " border: none; border-top: 3px solid transparent; font-size: 12px; }"
            "QTabBar::tab:selected { background: #1e1e1e; color: #4da3ff; font-weight: 600;"
            " border-top: 3px solid #4da3ff; }"
            "QTabBar::tab:hover { background: #333333; }"
            "QLineEdit { border: 1px solid #555555; border-radius: 2px; padding: 3px 8px;"
            " background: #1e1e1e; color: #e8e8e8; }"
            "QScrollArea, QStackedWidget { background: #1e1e1e; }"
        )
        self._show_index(0)

    def current_id(self):
        return self.tabs.tabData(self.tabs.currentIndex())

    def show_tab(self, tab_id):
        for index in range(self.tabs.count()):
            if self.tabs.tabData(index) == tab_id:
                self.tabs.setCurrentIndex(index)
                return

    def _show_index(self, index):
        self.stack.setCurrentIndex(index)
        page = self.stack.currentWidget()
        page.adjustSize()
        hint = page.sizeHint()
        self.stack.setMinimumSize(hint)
        self.stack.resize(hint)
        self._filter(self.search.text())

    def _filter(self, text):
        query = (text or "").strip().lower()
        first = None
        for index, tab in enumerate(TABS):
            visible = 0
            for button in self._buttons[tab["id"]]:
                show = (not query) or (query in button.plain.lower())
                button.setVisible(show)
                visible += int(show)
            if query and visible and first is None:
                first = index
        if first is not None and first != self.tabs.currentIndex():
            self.tabs.setCurrentIndex(first)
        page = self.scroll.widget()
        if page is not None:
            page.adjustSize()


def status(text):
    window = FreeCADGui.getMainWindow()
    if window is not None:
        window.statusBar().showMessage(text, 12000)


def _has(name):
    try:
        return FreeCADGui.Command.get(name) is not None
    except Exception:
        return False


def activate(name):
    if not name:
        return
    try:
        current = FreeCADGui.activeWorkbench().__class__.__name__
    except Exception:
        current = ""
    if current == name:
        return
    try:
        FreeCADGui.activateWorkbench(name)
    except Exception as exc:
        status(str(exc))


def editing_sketch():
    gui = getattr(FreeCADGui, "ActiveDocument", None)
    if gui is None:
        return None
    try:
        edit = gui.getInEdit()
    except Exception:
        return None
    obj = getattr(edit, "Object", edit) if edit is not None else None
    if obj is not None and "Sketcher::" in getattr(obj, "TypeId", ""):
        return obj
    return None


def selected_sketch():
    try:
        selection = FreeCADGui.Selection.getSelection()
    except Exception:
        return None
    for obj in selection:
        if "Sketcher::" in getattr(obj, "TypeId", ""):
            return obj
    return None


def apply_prefs():
    view = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View")
    view.SetString("NavigationStyle", "Gui::SolidWorksNavigationStyle")
    view.SetBool("Gradient", True)
    view.SetBool("RadialGradient", False)
    view.SetUnsigned("BackgroundColor", _pack(42, 42, 46))
    view.SetUnsigned("BackgroundColor2", _pack(58, 58, 62))
    view.SetUnsigned("BackgroundColor3", _pack(28, 28, 30))
    general = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/General")
    general.SetBool("ShowVersionInTitle", False)
    general.SetString("AutoloadModule", "PartDesignWorkbench")


def _next_label(doc, prefix):
    used = {obj.Label for obj in doc.Objects}
    number = 1
    while "%s%d" % (prefix, number) in used:
        number += 1
    return "%s%d" % (prefix, number)


def _relabel(obj):
    if _state["relabel"] or not hasattr(obj, "TypeId"):
        return
    if obj.TypeId == "App::Plane":
        label = PLANES.get(getattr(obj, "Role", ""))
        if label and obj.Label != label:
            _state["relabel"] = True
            try:
                obj.Label = label
            finally:
                _state["relabel"] = False
        return
    prefix = FEATURE_LABELS.get(obj.TypeId)
    if not prefix or obj.Label != obj.Name or obj.Document is None:
        return
    _state["relabel"] = True
    try:
        obj.Label = "Solid Bodies" if prefix == "Solid Bodies" else _next_label(obj.Document, prefix)
    finally:
        _state["relabel"] = False


def _label_origin(body):
    origin = getattr(body, "Origin", None)
    if origin is None:
        return
    origin.Label = "Origin"
    for feat in getattr(origin, "OriginFeatures", []):
        label = PLANES.get(getattr(feat, "Role", ""))
        if label:
            feat.Label = label


def _activate_body(body):
    document = getattr(body, "Document", None)
    gui = None
    if document is not None:
        try:
            gui = FreeCADGui.getDocument(document.Name)
        except Exception:
            gui = None
    if gui is None:
        gui = getattr(FreeCADGui, "ActiveDocument", None)
    view = getattr(gui, "ActiveView", None) if gui is not None else None
    if view is None:
        return
    try:
        view.setActiveObject("pdbody", body)
    except Exception:
        pass


def _add_body(doc):
    for obj in doc.Objects:
        if obj.TypeId == "PartDesign::Body":
            _activate_body(obj)
            return obj
    body = doc.addObject("PartDesign::Body", "Body")
    doc.recompute()
    _label_origin(body)
    if body.Label in ("Body", body.Name):
        body.Label = "Solid Bodies"
    _activate_body(body)
    return body


def _close_start_page():
    window = FreeCADGui.getMainWindow()
    area = window.findChild(QtWidgets.QMdiArea) if window is not None else None
    if area is None:
        return
    for sub in area.subWindowList():
        if sub.windowTitle().strip().lower() == "start":
            sub.close()


def _finish_view(doc):
    try:
        gui = FreeCADGui.getDocument(doc.Name)
    except Exception:
        return
    view = gui.ActiveView if gui is not None else None
    if view is not None:
        try:
            view.viewIsometric()
            view.fitAll()
        except Exception:
            pass
    _close_start_page()
    retitle()


def open_part():
    apply_prefs()
    activate("PartDesignWorkbench")
    doc = FreeCAD.newDocument("Part1")
    _add_body(doc)
    QtCore.QTimer.singleShot(200, lambda: _finish_view(doc))
    retitle()
    return doc


def ensure_part():
    doc = FreeCAD.ActiveDocument
    if doc is None:
        return open_part()
    _add_body(doc)
    return doc


def _show_task():
    # Sketch tools crash on the first mouse move if the task panel never
    # builds their on-view dimensions.
    try:
        FreeCADGui.Control.showTaskView()
    except Exception:
        pass
    window = FreeCADGui.getMainWindow()
    if window is None:
        return
    for dock in window.findChildren(QtWidgets.QDockWidget):
        key = (dock.objectName() + " " + dock.windowTitle()).lower()
        if "task" in key:
            dock.show()


def new_sketch():
    ensure_part()
    activate("PartDesignWorkbench")
    _show_task()
    FreeCADGui.runCommand("PartDesign_NewSketch")
    hide_toolbars()


def run_named(cmd, wb, profile=False, note=None):
    ensure_part()
    leaving = editing_sketch()

    def go():
        activate(wb)
        if leaving is not None:
            FreeCADGui.Selection.clearSelection()
            FreeCADGui.Selection.addSelection(leaving)
        if profile and leaving is None and selected_sketch() is None:
            status("Draw a sketch first. Pick a plane in the dialog.")
            new_sketch()
            return
        if note:
            status(note)
        if not _has(cmd):
            status("%s is not available in this FreeCAD build." % cmd)
            return
        FreeCADGui.runCommand(cmd)
        hide_toolbars()

    if leaving is not None and profile:
        FreeCADGui.runCommand("Sketcher_LeaveSketch")
        QtCore.QTimer.singleShot(0, go)
    else:
        go()


def dispatch(spec):
    try:
        kind = spec["kind"]
        if kind == "newsketch":
            new_sketch()
        elif kind == "exitsketch":
            if editing_sketch() is None:
                status("No sketch is open.")
            else:
                FreeCADGui.runCommand("Sketcher_LeaveSketch")
        elif kind == "sketch":
            if editing_sketch() is None:
                status("Start a sketch first.")
                new_sketch()
                return
            cmd = spec["cmd"]
            if not _has(cmd) and spec.get("fallback"):
                cmd = spec["fallback"]
            if not _has(cmd):
                status("%s is not available in this FreeCAD build." % spec["cmd"])
                return
            _show_task()
            FreeCADGui.runCommand(cmd)
        elif kind == "feature":
            run_named(spec["cmd"], "PartDesignWorkbench", spec.get("profile", False), spec.get("note"))
        elif kind == "command":
            run_named(spec["cmd"], spec.get("wb"), spec.get("profile", False), spec.get("note"))
        elif kind == "try":
            if _has(spec["cmd"]):
                run_named(spec["cmd"], spec.get("wb"), spec.get("profile", False), None)
            elif spec.get("fallback"):
                status(spec.get("note") or "")
                run_named(
                    spec["fallback"],
                    spec.get("fallback_wb") or "PartDesignWorkbench",
                    spec.get("profile", False),
                    None,
                )
            else:
                status(spec.get("note") or ("%s is not available." % spec["cmd"]))
        elif kind == "workbench":
            if FreeCAD.ActiveDocument is None:
                open_part()
            activate(spec["wb"])
            status("%s is active. Modeling commands stay on this ribbon." % spec["label"].replace("\n", " "))
            hide_toolbars()
    except Exception as exc:
        status("%s failed: %s" % (spec.get("label", "Command").replace("\n", " "), exc))
        FreeCAD.Console.PrintError(repr(exc) + "\n")


def hide_toolbars():
    window = FreeCADGui.getMainWindow()
    if window is None:
        return
    for toolbar in window.findChildren(QtWidgets.QToolBar):
        if toolbar.objectName() not in ("SWCommandManager", "SWViewTools") and toolbar.isVisible():
            toolbar.hide()


def retitle():
    window = FreeCADGui.getMainWindow()
    if window is None:
        return
    doc = FreeCAD.ActiveDocument
    label = doc.Label if doc is not None else "Part1"
    title = "%s.FCStd - SOLIDWORKS" % label
    if window.windowTitle() != title:
        QtWidgets.QMainWindow.setWindowTitle(window, title)
    editing = window.statusBar().findChild(QtWidgets.QLabel, "SWEditingPart")
    if editing is not None:
        editing.setText("Editing Part" if doc is not None else "Ready")


def _sync_sketch_tab():
    manager = _state.get("mgr")
    if manager is None:
        return
    editing = editing_sketch() is not None
    if editing and not _state["editing"]:
        manager.show_tab("Sketch")
    elif _state["editing"] and not editing and manager.current_id() == "Sketch":
        manager.show_tab("Features")
    _state["editing"] = editing


def _tick():
    _state["ticks"] += 1
    hide_toolbars()
    if _state["ticks"] < 8:
        _dress_docks()
    window = FreeCADGui.getMainWindow()
    if window is not None:
        _night_trees(window)
    _sync_sketch_tab()
    retitle()


def _dress_docks():
    window = FreeCADGui.getMainWindow()
    if window is None:
        return
    for dock in window.findChildren(QtWidgets.QDockWidget):
        key = (dock.objectName() + " " + dock.windowTitle()).lower()
        if any(word in key for word in ("report", "python", "console")):
            dock.hide()
            continue
        if "task" in key:
            dock.show()
            continue
        if any(word in key for word in ("combo", "tree", "model", "property")):
            dock.setWindowTitle("FeatureManager design tree")
            window.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)
            dock.setMinimumWidth(250)
            dock.show()


def _body_on_empty_doc():
    doc = FreeCAD.ActiveDocument
    if doc is None or doc.Objects:
        return
    _add_body(doc)
    retitle()


def _view_toolbar(window):
    rail = QtWidgets.QToolBar(window)
    rail.setObjectName("SWViewTools")
    rail.setWindowTitle("View")
    rail.setMovable(False)
    rail.setFloatable(False)
    rail.setOrientation(QtCore.Qt.Vertical)
    window.addToolBar(QtCore.Qt.RightToolBarArea, rail)
    for cmd, tip, icon in (
        ("Std_ViewFitAll", "Zoom to fit", "fit"),
        ("Std_ViewIsometric", "Isometric", "box"),
        ("Std_ViewFront", "Front", "rect"),
        ("Std_ViewTop", "Top", "rect"),
        ("Std_ViewRight", "Right", "rect"),
        ("Std_ViewFitSelection", "Zoom to selection", "measure"),
    ):
        action = rail.addAction(paint_icon(icon), "")
        action.setToolTip(tip)
        action.triggered.connect(lambda checked=False, name=cmd: FreeCADGui.runCommand(name))
    rail.setStyleSheet("QToolBar { background: #2b2b2b; border: none; spacing: 2px; }")


def _night_palette():
    palette = QtGui.QPalette()
    text = QtGui.QColor("#e8e8e8")
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor("#2b2b2b"))
    palette.setColor(QtGui.QPalette.WindowText, text)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor("#252526"))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor("#2e2e2e"))
    palette.setColor(QtGui.QPalette.Text, text)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor("#3c3c3c"))
    palette.setColor(QtGui.QPalette.ButtonText, text)
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor("#094771"))
    palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor("#ffffff"))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor("#3c3c3c"))
    palette.setColor(QtGui.QPalette.ToolTipText, text)
    dim = QtGui.QColor("#8a8a8a")
    for role in (QtGui.QPalette.Text, QtGui.QPalette.WindowText, QtGui.QPalette.ButtonText):
        palette.setColor(QtGui.QPalette.Disabled, role, dim)
    return palette


def _night_trees(window):
    # Tree items with an empty foreground role use this palette. A white
    # background with that light text was the blank feature tree.
    sheet = (
        "QTreeView, QTreeWidget { background-color: #252526; color: #e8e8e8; border: none; }"
        "QTreeView::item, QTreeWidget::item { color: #e8e8e8; }"
        "QTreeView::item:selected, QTreeWidget::item:selected,"
        "QTreeView::item:selected:active, QTreeWidget::item:selected:active"
        " { background-color: #094771; color: #ffffff; }"
    )
    palette = _night_palette()
    for view in window.findChildren(QtWidgets.QTreeView):
        view.setPalette(palette)
        view.setStyleSheet(sheet)


def _main_style(window):
    app = QtWidgets.QApplication.instance()
    if app is not None:
        app.setStyle("Fusion")
        app.setPalette(_night_palette())
    window.setStyleSheet(
        "QMainWindow { background: #2b2b2b; color: #e8e8e8; }"
        "QMenuBar { background: #2b2b2b; color: #e8e8e8; border-bottom: 1px solid #3c3c3c; }"
        "QMenuBar::item:selected { background: #094771; }"
        "QMenu { background: #2b2b2b; color: #e8e8e8; }"
        "QMenu::item:selected { background: #094771; }"
        "QStatusBar { background: #1e1e1e; color: #cccccc; border-top: 1px solid #3c3c3c; }"
        "QDockWidget { color: #e8e8e8; }"
        "QDockWidget::title { background: #333333; color: #e8e8e8; padding: 4px;"
        " border-bottom: 1px solid #1e1e1e; }"
        "QTreeView, QTreeWidget { background-color: #252526; color: #e8e8e8; border: none; }"
        "QTreeView::item, QTreeWidget::item { color: #e8e8e8; }"
        "QTreeView::item:selected, QTreeWidget::item:selected { background: #094771; color: #ffffff; }"
    )


def _selected_face():
    try:
        items = FreeCADGui.Selection.getSelectionEx()
    except Exception:
        return False
    for item in items:
        for name in item.SubElementNames:
            if name.startswith("Face"):
                return True
    return False


def align_camera_to_face():
    if not _selected_face():
        status("Select a face, then press Ctrl+H.")
        return
    FreeCADGui.runCommand("Std_AlignToSelection")


def _bind_align_shortcut(window):
    shortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+H"), window)
    shortcut.setContext(QtCore.Qt.ApplicationShortcut)
    shortcut.activated.connect(align_camera_to_face)
    _state["align_shortcut"] = shortcut


def _insert_menu(window):
    bar = window.menuBar()
    if bar.findChild(QtWidgets.QMenu, "SWInsertMenu"):
        return
    menu = QtWidgets.QMenu("Insert", bar)
    menu.setObjectName("SWInsertMenu")
    menu.addAction("New Part", open_part)
    menu.addAction("Sketch", new_sketch)
    anchor = None
    for action in bar.actions():
        if action.text().replace("&", "") in ("Tools", "Window", "Windows", "Macro"):
            anchor = action
            break
    if anchor is not None:
        bar.insertMenu(anchor, menu)
    else:
        bar.addMenu(menu)


class _Obs:
    def slotCreatedObject(self, obj):
        QtCore.QTimer.singleShot(0, lambda o=obj: _relabel(o))


def _selftest_gui():
    window = FreeCADGui.getMainWindow()
    host = window.findChild(QtWidgets.QWidget, "SWCommandManagerHost") if window else None
    names = []
    if host is not None:
        names = [child.objectName() for child in host.findChildren(SWButton)]
    doc = FreeCAD.ActiveDocument
    body = None
    planes = []
    if doc is not None:
        body = next((obj for obj in doc.Objects if obj.TypeId == "PartDesign::Body"), None)
        planes = [obj.Label for obj in doc.Objects if obj.Label in PLANES.values()]
    title = window.windowTitle() if window else ""
    ok = (
        host is not None
        and "SWbtn_Features_Extruded_Boss_Base" in names
        and "SWbtn_Sketch_Exit_Sketch" in names
        and body is not None
        and "Front Plane" in planes
        and "SOLIDWORKS" in title
    )
    path = os.environ.get("SWUI_SELFTEST_RESULT", "/tmp/swui-selftest.txt")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("ok\n" if ok else "fail\n")
        handle.write(title + "\n")
        handle.write("body %s\n" % (body.Label if body is not None else "none"))
        handle.write("planes %s\n" % ", ".join(planes))
        handle.write("\n".join(names))
    QtWidgets.QApplication.quit()


def install():
    try:
        _install()
    except Exception:
        import traceback

        FreeCAD.Console.PrintError(traceback.format_exc())


def _install():
    window = FreeCADGui.getMainWindow()
    if window is None:
        QtCore.QTimer.singleShot(200, install)
        return
    if window.findChild(QtWidgets.QToolBar, "SWCommandManager"):
        return
    apply_prefs()
    _main_style(window)
    toolbar = QtWidgets.QToolBar(window)
    toolbar.setObjectName("SWCommandManager")
    toolbar.setWindowTitle("CommandManager")
    toolbar.setMovable(False)
    toolbar.setFloatable(False)
    toolbar.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)
    window.addToolBar(QtCore.Qt.TopToolBarArea, toolbar)
    manager = CommandManager()
    toolbar.addWidget(manager)
    toolbar.setStyleSheet("QToolBar { background: #1e1e1e; border: none; padding: 0; spacing: 0; }")
    _state["mgr"] = manager
    _view_toolbar(window)
    editing = QtWidgets.QLabel("Editing Part")
    editing.setObjectName("SWEditingPart")
    editing.setStyleSheet("color: #cccccc; padding-right: 8px;")
    window.statusBar().addPermanentWidget(editing)
    _insert_menu(window)
    for action in window.findChildren(QtGui.QAction):
        if action.objectName() == "Std_New":
            action.triggered.connect(lambda checked=False: QtCore.QTimer.singleShot(50, _body_on_empty_doc))
            break
    if _state.get("obs") is None:
        obs = _Obs()
        FreeCAD.addDocumentObserver(obs)
        _state["obs"] = obs
    timer = QtCore.QTimer(window)
    timer.setObjectName("SWUiTimer")
    timer.setInterval(400)
    timer.timeout.connect(_tick)
    timer.start()
    _state["timer"] = timer
    _bind_align_shortcut(window)
    hide_toolbars()
    _dress_docks()
    _show_task()
    if FreeCAD.ActiveDocument is None:
        open_part()
    else:
        retitle()
    if os.environ.get("SWUI_SELFTEST"):
        QtCore.QTimer.singleShot(1200, _selftest_gui)
