import geopandas as gpd
import os


def create_shape(ws_number, full_gdf, user_path):
    print(f"Creating shapefile for watershed {ws_number}...")

    # Filter for selected watershed
    selected_ws = full_gdf[full_gdf["expl_num"] == ws_number]

    if selected_ws.empty:
        print(f"!!Watershed {ws_number} not found in input data.")
        return

    # Define output folder and path
    output_folder = os.path.join(user_path, f"InputDataInvest_OS/testing/ws_{ws_number}")
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, f"ws_{ws_number}.shp")

    # Save to shapefile
    selected_ws.to_file(output_path)
    print(f"Shapefile saved: {output_path}\n")


if __name__ == '__main__':
    print("Extracting watershed boundaries and creating shapefiles...")

    # ___________________________________________________________________________________________
    # PLEASE SET YOUR PATHS HERE
    # ___________________________________________________________________________________________
    user_path = "D:/Users/Thakur/ErospotWorkspace"
    main_gdb_path = os.path.join(user_path, "EROSPOT.gdb")
    layer_name = "ezg_by_erospot"
    # ------------------------------------------------------------------------------------------

    # Load full GDB layer into GeoDataFrame
    gdf = gpd.read_file(main_gdb_path, layer=layer_name)

    # Iterate through watersheds 1–10
    for ws_num in range(4, 5):  # loop for a lot of watersheds, changed to ws 4 for testing purposes
        create_shape(ws_num, gdf, user_path)

    print("All shapefiles created.")
