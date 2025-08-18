import geopandas as gpd
import pandas as pd
import numpy as np
import os


def find_coordinates_open_source(gdb_path, watershed_layer, watershed_id, user_path):
    print("Running open-source coordinate extractor...")

    # Read watershed data
    watershed = gpd.read_file(gdb_path, layer=watershed_layer)

    # Filter selected watershed by expl_num (equivalent to ArcPy selection)
    selected = watershed[watershed["expl_num"] == watershed_id]

    if selected.empty:
        raise ValueError(f"Watershed ID {watershed_id} not found in layer {watershed_layer}.")

    # Get bounding box
    minx, miny, maxx, maxy = selected.total_bounds

    # Round coordinates down/up to nearest 1000 (like ArcPy code logic)
    x_low = int(np.floor(minx / 1000))
    x_high = int(np.ceil(maxx / 1000))
    y_low = int(np.floor(miny / 1000))
    y_high = int(np.ceil(maxy / 1000))

    # Add/overwrite columns
    for col, val in zip(["x_low", "x_high", "y_low", "y_high"], [x_low, x_high, y_low, y_high]):
        watershed[col] = watershed.apply(lambda row: val if row["expl_num"] == watershed_id else row.get(col, np.nan),
                                         axis=1)

    # Save summary as CSV
    summary = pd.DataFrame({
        "expl_num": [watershed_id],
        "x_low": [x_low],
        "x_high": [x_high],
        "y_low": [y_low],
        "y_high": [y_high]
    })
    summary_path = os.path.join(user_path, f"ezg_by_erospot_ws_{watershed_id}.csv")
    summary.to_csv(summary_path, index=False)

    print(f"\nBounding box for watershed {watershed_id} (rounded to 1km):")
    print(f"  x_low: {x_low}")
    print(f"  x_high: {x_high}")
    print(f"  y_low: {y_low}")
    print(f"  y_high: {y_high}")
    print(f"Summary written to: {summary_path}\n")

    return summary_path


if __name__ == "__main__":
    # Standalone execution block
    watershed_id = 4
    user_path = "E:/DAKISWorkspace"
    gdb_path = os.path.join(user_path, "EROSPOT.gdb")
    watershed_layer = "ezg_by_erospot"

    find_coordinates_open_source(
        gdb_path=gdb_path,
        watershed_layer=watershed_layer,
        watershed_id=watershed_id,
        user_path=user_path
    )
