# coding=utf-8
"""
    this file can only be called by UE4Editor-Cmd.exe
"""
import unreal, os, shutil, uuid, zipfile
import sys


def exportMesh(uasset_path, output_path):
    unreal.AssetToolsHelpers.get_asset_tools().export_assets(uasset_path, output_path)


if __name__ == "__main__":
    uasset_path = sys.argv[1]
    uasset_paths = uasset_path.split(';')
    output_path = sys.argv[2]
    exportMesh(uasset_paths, output_path)