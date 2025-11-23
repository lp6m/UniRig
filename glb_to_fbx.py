#!/usr/bin/env python
"""
GLB to FBX converter using standalone bpy (no Blender GUI required)
Usage: python glb_to_fbx.py input.glb output.fbx
"""
import bpy
import sys
import os
import argparse

def clean_scene():
    """Clean all objects from the scene"""
    # Delete all objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Clean up orphaned data
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
    for armature in bpy.data.armatures:
        bpy.data.armatures.remove(armature)
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
    for image in bpy.data.images:
        bpy.data.images.remove(image)
    for texture in bpy.data.textures:
        bpy.data.textures.remove(texture)

# Parse arguments
parser = argparse.ArgumentParser(description='Convert GLB to FBX')
parser.add_argument('input_file', help='Input GLB file')
parser.add_argument('output_file', help='Output FBX file')
args = parser.parse_args()

input_file = args.input_file
output_file = args.output_file

# 1. 初期化（全削除）
print("Cleaning scene...")
clean_scene()

# 2. GLBインポート
print(f"Importing: {input_file}")
bpy.ops.import_scene.gltf(filepath=input_file, import_pack_images=True)

# 3. インポート後の不要なオブジェクトを削除
# Blender のデフォルトオブジェクト（Icosphere, Cube など）を削除
print("Removing unwanted objects...")
objects_to_remove = []
for obj in bpy.data.objects:
    # デフォルトオブジェクトの名前パターンで削除
    if obj.name in ['Icosphere', 'Cube', 'Light', 'Camera'] or obj.name.startswith('Icosphere') or obj.name.startswith('Cube'):
        objects_to_remove.append(obj)
    # EMPTY タイプで 'world' という名前のものも削除
    elif obj.type == 'EMPTY' and obj.name == 'world':
        objects_to_remove.append(obj)

for obj in objects_to_remove:
    print(f"  Removing: {obj.name}")
    bpy.data.objects.remove(obj, do_unlink=True)

# 使われていないメッシュデータも削除
for mesh in bpy.data.meshes:
    if mesh.users == 0:
        print(f"  Removing unused mesh: {mesh.name}")
        bpy.data.meshes.remove(mesh)

# 4. テクスチャ埋め込み設定のための準備
# FBX エクスポーターが packed 画像を扱えるように、一時的に画像を保存
print("Preparing textures for FBX export...")
import tempfile
temp_dir = tempfile.mkdtemp()
texture_files = []

for img in bpy.data.images:
    if img.packed_file and not img.name.startswith('Render') and not img.name.startswith('Viewer'):
        # Packed 画像を一時ファイルに保存
        temp_path = os.path.join(temp_dir, f"{img.name}.png")
        img.filepath_raw = temp_path
        img.file_format = 'PNG'
        img.save()
        texture_files.append(temp_path)
        print(f"  Saved texture: {img.name} -> {temp_path}")

# 5. FBXエクスポート
print(f"Exporting to FBX: {output_file}")
bpy.ops.export_scene.fbx(
    filepath=output_file,
    use_selection=False,          # シーン全体を出力
    object_types={'ARMATURE', 'MESH'}, # 骨とメッシュのみ
    mesh_smooth_type='FACE',      # メッシュのスムージング
    add_leaf_bones=False,         # Unity用に末端ボーンを削除
    axis_forward='-Z',            # Unityの前方向
    axis_up='Y',                  # Unityの上方向
    apply_scale_options='FBX_SCALE_UNITS',
    
    # ▼▼ テクスチャ埋め込みのキモ ▼▼
    path_mode='COPY',             # テクスチャをコピーモードにする
    embed_textures=True           # FBXファイル内にバイナリとして埋め込む
)

# 6. 一時ファイルのクリーンアップ
print("Cleaning up temporary files...")
import shutil
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
    print(f"  Removed temp directory: {temp_dir}")

print("Conversion Done.")