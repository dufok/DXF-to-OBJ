import bpy, os

EXPORT_DIR = r"./glb_export"
os.makedirs(EXPORT_DIR, exist_ok=True)

bpy.ops.object.select_all(action='DESELECT')

for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    safe_name = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in obj.name)
    filepath = os.path.join(EXPORT_DIR, f"{safe_name}.glb")

    bpy.ops.export_scene.gltf(
        filepath=filepath,
        use_selection=True,
        export_format='GLB',
        export_materials='EXPORT'
    )
    obj.select_set(False)
    print(f"Exported: {filepath}")
