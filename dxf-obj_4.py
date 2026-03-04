import sys
import logging
import math
import os
import ezdxf
from ezdxf import recover
from collections import defaultdict

logging.getLogger("ezdxf").setLevel(logging.ERROR)

input_file = sys.argv[1]
output_dir = sys.argv[2]   # folder, not a file

os.makedirs(output_dir, exist_ok=True)

layer_vertices = defaultdict(list)
layer_faces = defaultdict(list)

def add_face_for_layer(pts, layer):
    if len(pts) < 3:
        return
    verts = layer_vertices[layer]
    base = len(verts) + 1
    verts.extend(pts)
    layer_faces[layer].append(tuple(range(base, base + len(pts))))

def handle_polyline(pl, layer):
    if not (pl.is_polygon_mesh or pl.is_poly_face_mesh):
        return
    poly_verts = [v.dxf.location for v in pl.vertices if not v.is_face_record]
    face_verts = [v for v in pl.vertices if v.is_face_record]
    for fv in face_verts:
        raw = [fv.dxf.vtx0, fv.dxf.vtx1, fv.dxf.vtx2, fv.dxf.vtx3]
        idxs = [abs(v) - 1 for v in raw if v is not None]
        pts = [poly_verts[i] for i in idxs if 0 <= i < len(poly_verts)]
        add_face_for_layer(pts, layer)

def handle_entity(e, layer_override=None):
    layer = layer_override or e.dxf.layer
    et = e.dxftype()
    if et == "3DFACE":
        pts = [e.dxf.vtx0, e.dxf.vtx1, e.dxf.vtx2, e.dxf.vtx3]
        add_face_for_layer(pts, layer)
    elif et == "MESH":
        verts = list(e.vertices)
        for face in e.faces:
            add_face_for_layer([verts[i] for i in face], layer)
    elif et == "POLYLINE":
        handle_polyline(e, layer)

def apply_insert_transform(pt, insert_pt, rotation_deg, scale):
    angle = math.radians(rotation_deg)
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    x, y, z = pt[0] * scale, pt[1] * scale, pt[2] * scale
    return (
        x * cos_a - y * sin_a + insert_pt[0],
        x * sin_a + y * cos_a + insert_pt[1],
        z + insert_pt[2]
    )

def handle_insert_direct(ins, doc):
    block = doc.blocks[ins.dxf.name]
    layer = ins.dxf.layer
    insert_pt = ins.dxf.insert
    rot = ins.dxf.rotation if ins.dxf.hasattr("rotation") else 0.0
    scale = ins.dxf.xscale if ins.dxf.hasattr("xscale") else 1.0
    for e in block:
        if e.dxftype() == "POLYLINE" and e.is_poly_face_mesh:
            poly_verts = [v for v in e.vertices if not v.is_face_record]
            face_verts = [v for v in e.vertices if v.is_face_record]
            transformed = [apply_insert_transform(v.dxf.location, insert_pt, rot, scale)
                           for v in poly_verts]
            for fv in face_verts:
                raw = [fv.dxf.vtx0, fv.dxf.vtx1, fv.dxf.vtx2, fv.dxf.vtx3]
                idxs = [abs(v) - 1 for v in raw if v is not None]
                pts = [transformed[i] for i in idxs if 0 <= i < len(transformed)]
                add_face_for_layer(pts, layer)

def handle_insert_recursive(ins, doc, depth=0):
    if depth > 5:
        return
    insert_layer = ins.dxf.layer
    entities = list(ins.virtual_entities())
    if not entities:
        handle_insert_direct(ins, doc)
        return
    for e in entities:
        if e.dxftype() == "INSERT":
            handle_insert_recursive(e, doc, depth + 1)
        else:
            handle_entity(e, layer_override=insert_layer)

print("Step 1: Reading file...", flush=True)
doc, auditor = recover.readfile(input_file)
msp = doc.modelspace()
print("Step 2: Processing entities...", flush=True)

for i, e in enumerate(msp):
    if i % 100 == 0:
        total = sum(len(v) for v in layer_vertices.values())
        print(f"Entity {i}... vertices={total}", flush=True)
    if e.dxftype() == "INSERT":
        handle_insert_recursive(e, doc)
    else:
        handle_entity(e)

print("Step 3: Writing one OBJ per layer...", flush=True)
for layer, verts in layer_vertices.items():
    if not verts:
        continue
    safe_name = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in layer)
    if not safe_name:
        safe_name = "Layer"
    obj_path = os.path.join(output_dir, f"{safe_name}.obj")
    with open(obj_path, "w", encoding="utf-8") as f:
        f.write(f"o {safe_name}\n")
        for v in verts:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for face in layer_faces[layer]:
            f.write("f " + " ".join(map(str, face)) + "\n")
    print(f"  Wrote {obj_path}")

print("Done!")
