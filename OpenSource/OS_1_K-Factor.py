import os
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.features import rasterize
import pandas as pd
import numpy as np


def calculate_k_factor(gdb_path, dir_path, x):
    # Read watershed directly from .gdb layer
    print("Watershed identified......")
    watershed = gpd.read_file(gdb_path, layer="ezg_by_erospot")
    print("Reading successful.......")
    watershed = watershed[watershed['expl_num'] == x]  # assuming expl_number is your ID filter
    if watershed.empty:
        raise ValueError(f"Watershed number {x} not found in ezg_by_erospot")
    print("Buffering.....please wait..")
    watershed_buffered = watershed.buffer(5)  # 5 meter buffer
    watershed_buffered_gdf = gpd.GeoDataFrame(geometry=watershed_buffered, crs=watershed.crs)
    print("Buffer created....")

    # Paths
    k_factor_input_path = os.path.join(dir_path, "K_Faktor_Bayern/k_factor_komplett_bayern.tif")
    k_factor_output_dir = os.path.join(dir_path, f"InputDataInvest_OS/testing/ws_{x}/k-factor")
    os.makedirs(k_factor_output_dir, exist_ok=True)
    clipped_k_factor_path = os.path.join(gdb_path, f"k_factor_clipped_str_{x}.tif")

    # ATKIS shapefiles (outside GDB)
    atkis_paths = {
        "ver01_f": os.path.join(dir_path, "ATKIS/ver01_f.shp"),
        "ver03_f": os.path.join(dir_path, "ATKIS/ver03_f.shp"),
        "sie02_f": os.path.join(dir_path, "ATKIS/sie02_f.shp"),
        "gew01_f": os.path.join(dir_path, "ATKIS/gew01_f.shp"),
        "ver01_l": os.path.join(dir_path, "ATKIS/ver01_l.shp"),
        "ver02_l": os.path.join(dir_path, "ATKIS/ver02_l.shp"),
    }

    # Clip K-Factor raster using watershed buffer
    print("Clipping the k-factor raster to the shape of current watershed...")
    with rasterio.open(k_factor_input_path) as src:
        out_image, out_transform = mask(src, watershed_buffered_gdf.geometry, crop=True)
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })
        with rasterio.open(clipped_k_factor_path, "w", **out_meta) as dest:
            dest.write(out_image)
        print("Clipped watershed stored....")

    # Helper: Process a vector layer —
    # clip, dissolve, alter field -
    # this function can be used as these three processing steps follow each other for each ATKIS layer
    def process_vector(name):
        print(f"Processing vector layer {name}.....")
        input_path = atkis_paths[name]
        clipped = gpd.overlay(gpd.read_file(input_path), watershed, how="intersection")
        dissolved = clipped.dissolve(by=["OBJART", "OBJART_TXT"])
        new_col = f"OA_{name}"
        dissolved = dissolved.rename(columns={"OBJART": new_col})
        return dissolved

    # Process polygon layers
    layers = {}
    for key in ["ver01_f", "ver03_f", "sie02_f", "gew01_f"]:
        layers[key] = process_vector(key)

    # Process and buffer line layers
    def process_line(name):
        print("Processing line layers....")
        layer = process_vector(name)
        buffered = layer.buffer(2.75)
        return gpd.GeoDataFrame(geometry=buffered, crs=layer.crs)

    layers["ver01_l"] = process_line("ver01_l")
    layers["ver02_l"] = process_line("ver02_l")

    print("Identifying sealed areas....")
    # Union all sealed areas
    sealed_union = gpd.GeoDataFrame(pd.concat(layers.values(), ignore_index=True), crs=watershed.crs)
    sealed_union["sealed_areas_atkis"] = 1

    # Combine with watershed polygon
    print("Union of sealed areas with the watershed boundaries...")
    combined_union = gpd.overlay(sealed_union, watershed, how="union",keep_geom_type=False)
    combined_union["sealed_area_union"] = 1
    combined_union.loc[combined_union["sealed_areas_atkis"] == 1, "sealed_area_union"] = 0

    # Rasterize sealed areas
    print("Rasterizing sealed areas...")
    sealed_raster_path = os.path.join(gdb_path, f"sealed_areas_ws_{x}.tif")
    with rasterio.open(clipped_k_factor_path) as ref_raster:
        meta = ref_raster.meta.copy()
        meta.update({"count": 1, "dtype": "uint8"})

        shapes = ((geom, value) for geom, value in zip(combined_union.geometry, combined_union["sealed_area_union"]))
        sealed_raster = rasterize(shapes=shapes,
                                  out_shape=(ref_raster.height, ref_raster.width),
                                  transform=ref_raster.transform,
                                  fill=1,
                                  dtype="uint8")

        with rasterio.open(sealed_raster_path, "w", **meta) as out_raster:
            out_raster.write(sealed_raster, 1)
        print("Sealed raster successfully saved.")

    print("Final k-factor raster computing- k-factor with sealed area mask added")
    # Multiply clipped K-Factor raster * sealed area mask
    final_k_path = os.path.join(k_factor_output_dir, f"k-factor-resampled_ws_{x}.tif")
    with rasterio.open(clipped_k_factor_path) as k_src, \
         rasterio.open(sealed_raster_path) as mask_src:

        meta = k_src.meta.copy()
        with rasterio.open(final_k_path, "w", **meta) as dst:
            for ji, window in k_src.block_windows(1):
                k_block = k_src.read(1, window=window)
                m_block = mask_src.read(1, window=window)
                result = k_block * m_block
                dst.write(result, 1, window=window)


if __name__ == "__main__":
    # Setting paths for input geodatabase and creates directory if not present
    user_path = "E:/DAKISWorkspace"
    gdb_path = "E:/DAKISWorkspace/EROSPOT.gdb"
    os.makedirs(os.path.join(user_path, "InputDataInvest_OS"), exist_ok=True)
    # Calls the main calculate K-factor function
    print("Running k-factor calculation...")
    calculate_k_factor(gdb_path, user_path, 4) # 4 is the example watershed.
    print("Done")
