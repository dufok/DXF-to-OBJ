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
DWG → (AutoCAD) → DXF → (dxf-obj-per-layer.py) → OBJ per layer → (Blender script) → Scene → (GLB export) → SketchUp
```

1. Export DXF from AutoCAD (non-exploded, blocks intact)
2. Python script reads the DXF, resolves all INSERT block references with full transforms, and writes one `.obj` per DXF layer
3. Blender script batch-imports all OBJs with correct axis orientation
4. Clean up geometry in Blender, then export to GLB
5. Batch-import GLBs into SketchUp with auto-tagging by layer name

---

## Requirements

```bash
pip install ezdxf
```

- Python 3.10+
- Blender 4.x
- AutoCAD (any version that can export DXF)
- SketchUp 2024+ (for native GLB import)

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

### Step 4 — Export from Blender to GLB (per object)

After cleanup in Blender, run `blender-export-glb.py` in the Scripting tab to export each object as a separate `.glb` file:

```python
EXPORT_DIR = r"C:\path\to\glb_export"
```

Each file will be named after its Blender object (e.g. `V_ROOF.glb`, `V_WALLS.glb`).

> **Tip:** If your objects are already correctly positioned in Blender, you can export the entire scene as one single GLB instead — everything will land in the right place on SketchUp import.

### Step 5 — Import GLBs into SketchUp

SketchUp 2024+ supports GLB natively (**File → Import**). To batch-import all files at once, open **Extensions → Ruby Console** and run:

```ruby
import_dir = "C:/path/to/glb_export"

files = Dir.glob("#{import_dir}/*.glb")
puts "Found #{files.count} GLB files..."

files.each_with_index do |filepath, i|
  puts "[#{i+1}/#{files.count}] Importing #{File.basename(filepath)}..."
  Sketchup.active_model.import(filepath)
end

puts "Done!"
```

Each GLB lands as a separate **component** named after its filename.

### Step 6 — Auto-Tag Components by Layer Name

GLB import does not assign Tags automatically. Run this Ruby script in the **Ruby Console** to create a Tag for every component and assign it — Tags will match your original DXF layer names:

```ruby
model = Sketchup.active_model
layers = model.layers
entities = model.active_entities

model.start_operation('Auto-tag by component name', true)

entities.grep(Sketchup::ComponentInstance).each do |instance|
  tag_name = instance.definition.name
  tag = layers[tag_name] || layers.add(tag_name)
  instance.layer = tag
  puts "Tagged: #{tag_name}"
end

model.commit_operation
puts "Done! All components tagged."
```

Result in the Tags panel:
```
✅ V_ROOF
✅ V_WALLS
✅ V_WINDOWS
✅ V_PIPES
...
```

Toggle visibility per tag exactly like you would in Blender's outliner.

---

## Scripts

| Script | Language | Description |
|---|---|---|
| `dxf-obj-per-layer.py` | Python | Main converter: DXF → one OBJ per layer |
| `blender-import-layers.py` | Python (Blender) | Batch OBJ importer for Blender 4.x |
| `blender-export-glb.py` | Python (Blender) | Batch GLB exporter — one GLB per object |
| `sketchup-import-glb.rb` | Ruby (SketchUp) | Batch GLB importer for SketchUp |
| `sketchup-autotag.rb` | Ruby (SketchUp) | Auto-tag all components by name |

---

## What It Handles

- ✅ `3DFACE`, `MESH`, polygon mesh and polyface mesh `POLYLINE`
- ✅ `INSERT` block references — translation, rotation, scale applied
- ✅ Nested `INSERT` blocks (up to 5 levels deep)
- ✅ Fallback for blocks where `virtual_entities()` returns nothing — reads block directly with manual transform
- ✅ Heavy files (900MB+ DXF tested)
- ✅ Cyrillic / non-ASCII layer names — sanitized to safe filenames, written as UTF-8
- ✅ Full Blender → SketchUp pipeline via GLB with auto-tagging
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
| GLB import not available in SketchUp | Requires SketchUp 2024+, use Skimp plugin on older versions |
| Components stack at origin in SketchUp | Export full scene as one GLB to preserve world positions |
| Tags not created after GLB import | Run `sketchup-autotag.rb` in Ruby Console |

---

## Tested On

- AutoCAD 2026 (DXF export)
- ezdxf 1.4.x on Python 3.13
- Blender 4.5
- SketchUp 2025 (GLB import + Ruby tagging)
- DXF files up to 900MB with 10M+ vertices

---

## License

MIT
