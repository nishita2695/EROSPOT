import geopandas as gpd
import pandas as pd
import rasterio
from rasterio.features import rasterize
import os
import numpy as np
from shapely.geometry import box


def streams_atkis(gdb_path, UserPath, watershed_id):
    print("Calculating the Water bodies from ATKIS data...")

    # Load ATKIS data
    gew01_f = gpd.read_file(os.path.join(UserPath, "ATKIS/gew01_f.shp"))
    gew01_l = gpd.read_file(os.path.join(UserPath, "ATKIS/gew01_l.shp"))

    print("Step 1: Reading watershed from GDB...")
    watershed = gpd.read_file(gdb_path, layer="ezg_by_erospot")
    watershed = watershed[watershed['expl_num'] == watershed_id]
    if watershed.empty:
        raise ValueError(f"Watershed {watershed_id} not found!")

    print("Step 2: Clipping gew01_l (lines) to watershed...")
    gew01_l_clip = gpd.overlay(gew01_l, watershed, how="intersection")

    print("Step 3: Filtering BRG = 3 & HDU_X = 0...")
    gew01_l_filter1 = gew01_l_clip.query("HDU_X == 0 and BRG == 3")
    print("Buffering BRG=3 by 1m...")
    buffer1 = gew01_l_filter1.buffer(1)
    buffer1_gdf = gpd.GeoDataFrame(geometry=buffer1, crs=gew01_l.crs)
    buffer1_gdf["wb_3_gew_l"] = 1

    print("Step 4: Filtering BRG = 6 & HDU_X = 0...")
    gew01_l_filter2 = gew01_l_clip.query("HDU_X == 0 and BRG == 6")
    print("Buffering BRG=6 by 2.5m...")
    buffer2 = gew01_l_filter2.buffer(2.5)
    buffer2_gdf = gpd.GeoDataFrame(geometry=buffer2, crs=gew01_l.crs)
    buffer2_gdf["wb_6_gew_l"] = 1

    print("Step 5: Clipping gew01_f (polygons) to watershed...")
    gew01_f_clip = gpd.overlay(gew01_f, watershed, how="intersection")
    gew01_f_clip["wb_gew_f"] = 1

    print("Step 6: Union of buffers and polygons...")
    combined = pd.concat([gew01_f_clip, buffer1_gdf, buffer2_gdf], ignore_index=True)
    combined = gpd.GeoDataFrame(combined, crs=gew01_f.crs)

    print("Step 7: Overlay with watershed...")
    combined_union = gpd.overlay(combined, watershed, how="union", keep_geom_type=False)

    print("Step 8: Computing final 'waterbody' field...")
    for field in ["wb_3_gew_l", "wb_6_gew_l", "wb_gew_f"]:
        if field not in combined_union.columns:
            combined_union[field] = 0
        combined_union[field] = combined_union[field].fillna(0).astype(int)

    combined_union["waterbody"] = (
        combined_union[["wb_3_gew_l", "wb_6_gew_l", "wb_gew_f"]].sum(axis=1).clip(upper=1)
    )

    print("Step 9: Memory-safe rasterization to 0.5m...")
    raster_out_path = os.path.join(UserPath, f"InputDataInvest/testing/ws_{watershed_id}/gew_{watershed_id}.tif")
    os.makedirs(os.path.dirname(raster_out_path), exist_ok=True)

    reference_raster_path = os.path.join(UserPath, "K_Faktor_Bayern/k_factor_komplett_bayern.tif")
    with rasterio.open(reference_raster_path) as ref:
        profile = ref.profile
        profile.update({
            "driver": "GTiff",
            "dtype": "uint8",
            "count": 1,
            "compress": "deflate"
        })

        with rasterio.open(raster_out_path, "w", **profile) as dst:
            for idx, window in ref.block_windows(1):
                window_transform = ref.window_transform(window)
                bounds = rasterio.windows.bounds(window, ref.transform)
                window_geom = box(*bounds)

                intersects = combined_union.geometry.intersects(window_geom)
                shapes = [
                    (geom, val) for geom, val in zip(
                        combined_union.geometry[intersects],
                        combined_union["waterbody"][intersects]
                    )
                    if geom.is_valid and not geom.is_empty
                ]

                if shapes:
                    rasterized = rasterize(
                        shapes,
                        out_shape=(window.height, window.width),
                        transform=window_transform,
                        fill=0,
                        dtype="uint8"
                    )
                else:
                    rasterized = np.zeros((window.height, window.width), dtype="uint8")

                dst.write(rasterized, 1, window=window)

    print(" Waterbody raster saved:", raster_out_path)


if __name__ == "__main__":
    UserPath = "E:/DAKISWorkspace"
    GDBPath = "E:/DAKISWorkspace/EROSPOT.gdb"
    watershed_number = 4

    print("Running memory-safe waterbody rasterization...")
    streams_atkis(GDBPath, UserPath, watershed_number)
    print("Done.")
