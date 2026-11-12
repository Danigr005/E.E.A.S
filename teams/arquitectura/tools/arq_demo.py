"""arq demo: generate a small synthetic plan with KNOWN defects, to self-test the toolchain.

Usage:
  arq demo <out_dir>
Writes demo_plan.dxf, demo_plan.pdf (vector), demo_plan.ifc and demo_rooms.csv. Known defects (the test oracle):
  D1  corridor 0.80 m wide
  D2  dimension of the living room shows text "5.5" but measures 5.0 m
  D3  declared area of the bedroom is 12.0 m2 but 3.5 x 3.0 = 10.5 m2
  D4  IFC door IfcDoor 'P-aseo' is 0.60 m wide
"""
from __future__ import annotations

import sys
from pathlib import Path

import ezdxf

ROOMS = {  # name: (x, y, width, depth) in metres
    "Salon": (0.0, 0.0, 5.0, 4.0),
    "Dormitorio": (5.8, 0.0, 3.5, 3.0),
    "Pasillo": (5.0, 0.0, 0.8, 4.0),
    "Cocina": (0.0, 4.0, 3.0, 2.5),
}
DECLARED = {"Salon": 20.0, "Dormitorio": 12.0, "Pasillo": 3.2, "Cocina": 7.5}


def build_dxf(out: Path) -> None:
    doc = ezdxf.new("R2018", setup=True)
    doc.header["$INSUNITS"] = 6  # metres
    for name, color in (("MUROS", 7), ("ESTANCIAS", 5), ("COTAS", 3), ("TEXTO", 2)):
        doc.layers.add(name, color=color)
    msp = doc.modelspace()
    for name, (x, y, w, d) in ROOMS.items():
        msp.add_lwpolyline([(x, y), (x + w, y), (x + w, y + d), (x, y + d)], close=True, dxfattribs={"layer": "ESTANCIAS"})
        msp.add_text(f"{name}", height=0.2, dxfattribs={"layer": "TEXTO"}).set_placement((x + 0.2, y + d / 2))
    dim = msp.add_linear_dim(base=(0, -0.8), p1=(0, 0), p2=(5.0, 0), dxfattribs={"layer": "COTAS"}, override={"dimtxt": 0.2})
    dim.render()
    dim_entities = list(msp.query("DIMENSION"))
    dim_entities[0].dxf.text = "5.5"  # defect D2: text override does not match geometry
    door = doc.blocks.new("PUERTA_80")
    door.add_line((0, 0), (0.8, 0))
    door.add_arc((0, 0), 0.8, 0, 90)
    msp.add_blockref("PUERTA_80", (1.0, 4.0), dxfattribs={"layer": "MUROS"})
    doc.saveas(str(out))


def build_pdf(dxf_path: Path, out: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

    doc = ezdxf.readfile(str(dxf_path))
    fig = plt.figure(figsize=(11.69, 8.27))
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    Frontend(RenderContext(doc), MatplotlibBackend(ax)).draw_layout(doc.modelspace(), finalize=True)
    fig.savefig(out)


def build_ifc(out: Path) -> None:
    import ifcopenshell
    import ifcopenshell.api

    api = ifcopenshell.api.run
    f = ifcopenshell.api.run("project.create_file", version="IFC4")
    project = api("root.create_entity", f, ifc_class="IfcProject", name="Demo")
    api("unit.assign_unit", f, length={"is_metric": True, "raw": "METERS"})
    site = api("root.create_entity", f, ifc_class="IfcSite", name="Parcela")
    building = api("root.create_entity", f, ifc_class="IfcBuilding", name="Edificio")
    storey = api("root.create_entity", f, ifc_class="IfcBuildingStorey", name="Planta 0")
    api("aggregate.assign_object", f, products=[site], relating_object=project)
    api("aggregate.assign_object", f, products=[building], relating_object=site)
    api("aggregate.assign_object", f, products=[storey], relating_object=building)
    for name, (_x, _y, w, d) in ROOMS.items():
        space = api("root.create_entity", f, ifc_class="IfcSpace", name=name)
        api("aggregate.assign_object", f, products=[space], relating_object=storey)
        qto = api("pset.add_qto", f, product=space, name="Qto_SpaceBaseQuantities")
        api("pset.edit_qto", f, qto=qto, properties={"NetFloorArea": round(w * d, 2)})
    door = api("root.create_entity", f, ifc_class="IfcDoor", name="P-aseo")
    door.OverallWidth, door.OverallHeight = 0.60, 2.03
    api("spatial.assign_container", f, products=[door], relating_structure=storey)
    f.write(str(out))


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    out = Path(argv[0])
    out.mkdir(parents=True, exist_ok=True)
    build_dxf(out / "demo_plan.dxf")
    build_pdf(out / "demo_plan.dxf", out / "demo_plan.pdf")
    build_ifc(out / "demo_plan.ifc")
    (out / "demo_rooms.csv").write_text(
        "name;declared_m2;width_m;depth_m\n"
        + "\n".join(f"{n};{DECLARED[n]};{w};{d}" for n, (_x, _y, w, d) in ROOMS.items()) + "\n"
    )
    print(f"demo files written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
