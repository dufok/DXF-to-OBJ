# DXF → Blender Pipeline

A Python-based pipeline to convert AutoCAD DWG/DXF files into Blender-ready OBJ files, 
separated by layer, with correct transforms — no web tools, no size limits.

Built to handle heavy architectural DXF files (tested on 900MB+) where online converters 
and Blender's native DXF importer fail or lose geometry.

---

## Why This Exists

- Blender's built-in DXF importer silently drops many entity types (polyface meshes, block references)
- Online converters crash or time out on heavy files
- AutoCAD 2019+ removed native FBX/OBJ export
- This pipeline handles all of the above locally, via pure Python + ezdxf

---

## How It Works

```
DWG → (AutoCAD) → DXF → (dxf-obj-per-layer.py) → OBJ per layer → (Blender script) → Scene
```

1. Export DXF from AutoCAD (non-exploded, blocks intact)
2. Python script reads the DXF, resolves all INSERT block references with full transforms, and writes one `.obj` per DXF layer
3. Blender script batch-imports all OBJs with correct axis orientation

---

## Requirements

```bash
pip install ezdxf
```

- Python 3.10+
- Blender 4.x
- AutoCAD (any version that can export DXF)

---

## Usage

### Step 1 — Export DXF from AutoCAD
- Open your `.dwg`
- Do **not** explode — keep blocks intact
- `Save As` → DXF 2010 format
- Run `AUDIT` + `PURGE` before saving

### Step 2 — Convert DXF → OBJ per layer

```bash
python dxf-obj-per-layer.py "input.dxf" "./out_objs"
```

Output:
```
out_objs/
  V_ROOF.obj
  V_WALLS.obj
  V_WINDOWS.obj
  V_PIPES.obj
  ...
```

### Step 3 — Import into Blender

Open Blender → Scripting tab → paste `blender-import-layers.py`, set `OBJ_DIR` to your output folder, run.

```python
OBJ_DIR = r"C:\path\to\out_objs"
```

All layers will be imported as separate named objects, correctly oriented (Z-up).

---

## Scripts

| Script | Description |
|---|---|
| `dxf-obj-per-layer.py` | Main converter: DXF → one OBJ per layer |
| `blender-import-layers.py` | Batch OBJ importer for Blender 4.x |
| `check-types.py` | Diagnostic: list entity types in modelspace |
| `check-block-types.py` | Diagnostic: list entity types inside blocks |
| `find-layer.py` | Diagnostic: inspect a specific layer's contents |

---

## What It Handles

- ✅ `3DFACE`, `MESH`, polygon mesh and polyface mesh `POLYLINE`
- ✅ `INSERT` block references — translation, rotation, scale applied
- ✅ Nested `INSERT` blocks (up to 5 levels deep)
- ✅ Fallback for blocks where `virtual_entities()` returns nothing — reads block directly with manual transform
- ✅ Heavy files (900MB+ DXF tested)
- ✅ Cyrillic / non-ASCII layer names — sanitized to safe filenames, written as UTF-8
- ❌ `3DSOLID` / `BODY` / `REGION` (ACIS solids) — not supported by ezdxf, explode in AutoCAD first
- ❌ `LWPOLYLINE`, `LINE`, `SPLINE` — no mesh geometry, skipped by design

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `0 vertices` exported | Run `check-types.py` to inspect entity types |
| Specific object missing | Run `find-layer.py` with the layer name |
| `UnicodeEncodeError` | Already handled — output is UTF-8 |
| Wrong orientation in Blender | Already handled via `forward_axis='Y'`, `up_axis='Z'` on import |
| `ezdxf DXFStructureError` on DWG | ezdxf does not support DWG — export to DXF first |
| `virtual_entities()` returns nothing | Script falls back to direct block reading automatically |

---

## Tested On

- AutoCAD 2026 (DXF export)
- ezdxf 1.4.x on Python 3.13
- Blender 4.5
- DXF files up to 900MB with 10M+ vertices

---

## License

MIT
