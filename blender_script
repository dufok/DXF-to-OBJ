import bpy
import os

OBJ_DIR = r"C:\Users\Stepan\Desktop\KUDINKOV_CONVERTING\building_layered_blocks_objs"

# get VIEW_3D area once
window = bpy.context.window_manager.windows[0]
screen = window.screen
area = next(a for a in screen.areas if a.type == "VIEW_3D")
region = next(r for r in area.regions if r.type == "WINDOW")

for filename in sorted(os.listdir(OBJ_DIR)):
    if not filename.endswith(".obj"):
        continue

    filepath = os.path.join(OBJ_DIR, filename)
    layer_name = filename[:-4]

    print(f"Importing {layer_name}...", flush=True)

    with bpy.context.temp_override(window=window, screen=screen, area=area, region=region):
        bpy.ops.wm.obj_import(
            filepath=filepath,
            forward_axis='Y',
            up_axis='Z'
        )

    imported = list(bpy.context.selected_objects)
    print(f"  Done: {len(imported)} objects → '{layer_name}'")

print("All layers imported!")
