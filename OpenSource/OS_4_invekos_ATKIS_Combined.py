import geopandas as gpd
import pandas as pd
import rasterio
from rasterio.features import rasterize
from shapely.geometry import mapping
import numpy as np
import os
import shutil

def combine_invekos_atkis(watershed_path, watershed_number, user_path):
    print("Combining InVeKoS and ATKIS data...")

    gdb_path = watershed_path
    inv_layer = f"invekos_union_py_FINALUNION_ws_{watershed_number}"
    atkis_layer = f"atkis_union_py_ws_{watershed_number}"
    sum_c_table = "sum_c_new"

    union_layer_name = f"union_invekos_atkis_ws_{watershed_number}"
    output_vector_path = os.path.join(user_path, f"{union_layer_name}.shp")
    output_raster_path = os.path.join(user_path, f"lc_ws_{watershed_number}.tif")
    output_csv_path = os.path.join(user_path, f"biophysical_table_ws_{watershed_number}.csv")

    target_crs = "EPSG:25832"  # UTM zone 32N (common in Germany)

    # Read data from GDB
    inv = gpd.read_file(gdb_path, layer=inv_layer)
    atk = gpd.read_file(gdb_path, layer=atkis_layer)
    c_table = gpd.read_file(gdb_path, layer=sum_c_table)

    # Reproject if needed
    for gdf in [inv, atk]:
        if gdf.crs is None:
            raise ValueError("One of the input layers has no CRS defined.")
        if gdf.crs.to_string() != target_crs:
            gdf.to_crs(target_crs, inplace=True)

    # Union
    unioned = gpd.overlay(inv, atk, how="union")

    # Descriptions and basic fields
    unioned["description"] = unioned["besch_15"].astype(str) + "_" + unioned["besch_19"].astype(str)
    unioned["usle_p"] = 1
    unioned["lucode"] = unioned.index + 1

    # C-value processing for 2015–2021
    for year in range(15, 22):
        n = f"nu_code_{year}"
        a = f"aum_code_{year}"
        c = f"combi_code_{year}"
        if n in unioned.columns and a in unioned.columns:
            unioned[c] = unioned[n].astype(str) + unioned[a].astype(str)
            unioned = unioned.merge(c_table[["combi_code", "sum_c"]],
                                    left_on=c, right_on="combi_code", how="left")
            unioned.rename(columns={"sum_c": f"sum_c_{year}"}, inplace=True)
            unioned.drop(columns=["combi_code"], errors="ignore", inplace=True)

    # ATKIS-based code
    components = [col for col in unioned.columns if "OA_" in col or "VEG_" in col]
    if components:
        unioned["combi_code_atkis"] = unioned[components].astype(str).agg("".join, axis=1)
        unioned = unioned.merge(c_table[["combi_code", "sum_c"]],
                                left_on="combi_code_atkis", right_on="combi_code", how="left")
        unioned.rename(columns={"sum_c": "sum_c_atkis"}, inplace=True)
        unioned.drop(columns=["combi_code"], errors="ignore", inplace=True)

    # Final usle_c value
    sc_cols = [f"sum_c_{y}" for y in range(15, 22)]
    unioned["usle_c"] = unioned[sc_cols].mean(axis=1)
    unioned["usle_c"].fillna(unioned.get("sum_c_atkis", 0.5), inplace=True)
    unioned["usle_c"] = unioned["usle_c"].apply(lambda x: 0.004 if x < 0.001 else x)
    unioned["usle_c"].fillna(0.5, inplace=True)

    # Ensure CRS before saving
    unioned.set_crs(target_crs, inplace=True, allow_override=True)

    # Save shapefile
    unioned.to_file(output_vector_path)

    # Save CSV biophysical table
    bio_cols = ["lucode", "description", "usle_c", "usle_p"]
    unioned[bio_cols].drop_duplicates().to_csv(output_csv_path, index=False)

    # Rasterize
    print("Rasterizing lucode field...")
    bounds = unioned.total_bounds
    res = 1
    width = int((bounds[2] - bounds[0]) / res)
    height = int((bounds[3] - bounds[1]) / res)
    transform = rasterio.transform.from_origin(bounds[0], bounds[3], res, res)
    shapes = ((geom, value) for geom, value in zip(unioned.geometry, unioned["lucode"]))
    raster = rasterize(shapes, out_shape=(height, width), transform=transform)
    with rasterio.open(output_raster_path, "w", driver="GTiff",
                       height=height, width=width,
                       count=1, dtype=raster.dtype, transform=transform,
                       crs=target_crs) as dst:
        dst.write(raster, 1)

    # Copy to test-outputs
    test_output_dir = os.path.join(user_path, "test-outputs")
    os.makedirs(test_output_dir, exist_ok=True)

    def safe_copy(src_path, label):
        try:
            shutil.copy(src_path, test_output_dir)
        except Exception as e:
            print(f"⚠ Could not copy {label}: {e}")

    safe_copy(output_vector_path, "vector")
    safe_copy(output_raster_path, "raster")
    safe_copy(output_csv_path, "CSV")

    print("\nOutput file locations:")
    print(f"- Vector: {output_vector_path}")
    print(f"- Raster: {output_raster_path}")
    print(f"- Biophysical Table: {output_csv_path}")
    print(f"\nAll outputs also copied to: {test_output_dir}")


if __name__ == "__main__":
    print("Running InVeKoS–ATKIS combination processor...")
    watershed_number = 4
    user_path = "E:/DAKISWorkspace"
    watershed_path = os.path.join(user_path, "EROSPOT.gdb")
    combine_invekos_atkis(watershed_path, watershed_number, user_path)
    print("Done.")
