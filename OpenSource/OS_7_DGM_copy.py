import os
import shutil
import rasterio
from rasterio.merge import merge
import geopandas as gpd
import pandas as pd
import numpy as np

def load_coordinate_dicts(gdf):
    print("Extracting bounding coordinates from attribute table...")
    x_low_dict = {}
    x_high_dict = {}
    y_low_dict = {}
    y_high_dict = {}

    for idx, row in gdf.iterrows():
        if pd.isna(row['expl_num']) or pd.isna(row['x_low']) or pd.isna(row['x_high']) or pd.isna(row['y_low']) or pd.isna(row['y_high']):
            continue  # Skip rows with missing data
        ws = int(row['expl_num'])
        x_low_dict[ws] = int(row['x_low'])
        x_high_dict[ws] = int(row['x_high'])
        y_low_dict[ws] = int(row['y_low'])
        y_high_dict[ws] = int(row['y_high'])
    print("Coordinate dictionaries created.")
    return x_low_dict, x_high_dict, y_low_dict, y_high_dict
def copy_and_stitch_tiles(user_path, watershed_id, x_low, x_high, y_low, y_high):
    print(f"\nProcessing Watershed {watershed_id}...")
    dgm_folder = os.path.join(user_path, "DGM1")
    ws_folder = os.path.join(user_path, "InputDataInvest", "testing", f"ws_{watershed_id}")
    os.makedirs(ws_folder, exist_ok=True)
    dgm_ws_folder = os.path.join(ws_folder, f"DGM_ws_{watershed_id}")
    os.makedirs(dgm_ws_folder, exist_ok=True)

    x_range = range(x_low[watershed_id], x_high[watershed_id] + 1)
    y_range = range(y_low[watershed_id], y_high[watershed_id] + 1)

    raster_files = []
    for x in x_range:
        for y in y_range:
            tile_name = f"{x}_{y}.asc"
            asc_path = os.path.join(dgm_folder, tile_name)
            prj_path = os.path.join(dgm_folder, tile_name.replace(".asc", ".prj"))

            if os.path.exists(asc_path):
                shutil.copy(asc_path, dgm_ws_folder)
                print(f"  Copied: {asc_path}")
                if os.path.exists(prj_path):
                    shutil.copy(prj_path, dgm_ws_folder)
                raster_files.append(os.path.join(dgm_ws_folder, tile_name))
            else:
                print(f"  !!Missing tile: {tile_name}")

    print(f"Stitching {len(raster_files)} tiles...")
    datasets = [rasterio.open(r) for r in raster_files if os.path.exists(r)]
    if datasets:
        mosaic, out_trans = merge(datasets)
        out_meta = datasets[0].meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": mosaic.shape[1],
            "width": mosaic.shape[2],
            "transform": out_trans
        })
        out_tif_path = os.path.join(dgm_ws_folder, f"dgm_ws_{watershed_id}.tif")
        with rasterio.open(out_tif_path, "w", **out_meta) as dest:
            dest.write(mosaic)
        print(f"Stitched DEM saved to: {out_tif_path}")
    else:
        print("No valid raster tiles found for stitching.")


if __name__ == '__main__':
    user_path = "E:/DAKISWorkspace"  # <-- Update this if needed
    gdb_path = os.path.join(user_path, "EROSPOT.gdb")
    ezg_layer = gpd.read_file(gdb_path, layer="ezg_by_erospot")

    x_low_dict, x_high_dict, y_low_dict, y_high_dict = load_coordinate_dicts(ezg_layer)

    for ws_id in range(4, 5):
        copy_and_stitch_tiles(user_path, ws_id, x_low_dict, x_high_dict, y_low_dict, y_high_dict)

    print("\nAll watersheds processed.")
