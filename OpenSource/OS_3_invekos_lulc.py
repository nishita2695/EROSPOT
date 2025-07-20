import os
import geopandas as gpd
import pandas as pd


def process_invekos_data(watershed_path, watershed_number, user_path, gdb_path):
    print("Processing InVeKoS data 2015-2021...")

    # Paths for input data
    years = list(range(2015, 2022))
    inv_paths = {
        year: os.path.join(user_path, f"InVeKoS/Nutzung_Aum_Bayern_{year}/invekos_by_{str(year)[-2:]}_p.shp")
        for year in years
    }

    # Output paths
    ws_output_dir = os.path.join(user_path, f"InputDataInvest/testing/ws_{watershed_number}")
    os.makedirs(ws_output_dir, exist_ok=True)

    # Read watershed
    print("Reading watershed polygon...")
    watershed = gpd.read_file(watershed_path, layer="ezg_by_erospot")
    watershed = watershed[watershed["expl_num"] == watershed_number]
    if watershed.empty:
        raise ValueError(f"Watershed with expl_number={watershed_number} not found")

    # Fix any geometry issues
    watershed["geometry"] = watershed["geometry"].buffer(0)

    # Helper function for processing each year's data
    def process_year(year):
        print(f"\nProcessing year {year}...")
        shp_path = inv_paths[year]
        inv_gdf = gpd.read_file(shp_path)

        # Fix invalid geometry
        inv_gdf["geometry"] = inv_gdf["geometry"].buffer(0)

        # Clip to watershed
        clipped = gpd.overlay(inv_gdf, watershed, how="intersection")
        print(f"  Clipped: {len(clipped)} features")

        # Drop duplicates by geometry (simulates DeleteIdentical)
        clipped = clipped.drop_duplicates(subset="geometry")
        print(f"  Deduplicated: {len(clipped)} features")

        # Ensure required fields exist (simulates AddField)
        if "aum_code" not in clipped:
            clipped["aum_code"] = "0"
            print(f"  Field 'aum_code' added with default '0'")
        if "aum_beschr" not in clipped:
            clipped["aum_beschr"] = ""
            print(f"  Field 'aum_beschr' added")
        if "beschreibu" not in clipped:
            clipped["beschreibu"] = ""
            print(f"  Field 'beschreibu' added")

        # Rename fields like ArcPy AlterField
        clipped = clipped.rename(columns={
            "beschreibu": f"besch_{str(year)[-2:]}",
            "aum_code": f"aum_code_{str(year)[-2:]}",
            "nutz_code": f"nu_code_{str(year)[-2:]}"
        })

        # Return with consistent CRS
        return clipped.to_crs(watershed.crs)

    # Process each year safely
    processed_years = []
    for year in years:
        shp_path = inv_paths[year]
        if not os.path.exists(shp_path):
            print(f"⚠️  Skipping year {year}: file not found at {shp_path}")
            continue
        try:
            processed = process_year(year)
            processed_years.append(processed)
        except Exception as e:
            print(f"❌ Error processing year {year}: {e}")

    # Union all
    print("\nMerging all years into one GeoDataFrame...")
    unioned = gpd.GeoDataFrame(pd.concat(processed_years, ignore_index=True), crs=watershed.crs)

    # Buffer: first inward -1.4 m, then outward +1.4 m
    print("\nApplying buffering (1.4m in/out)...")
    buffered_in = unioned.buffer(-1.4)
    buffered_out = gpd.GeoDataFrame(geometry=buffered_in.buffer(1.4), crs=watershed.crs)

    # Reattach attributes (dummy_aum)
    buffered_out["dummy_aum"] = "XXX"

    # Filter for relevant aum_codes per year
    print("\nApplying attribute filters...")
    aum_codes = [f"aum_code_{str(y)[-2:]}" for y in years]
    for code_col in aum_codes:
        if code_col in buffered_out.columns:
            mask = buffered_out[code_col].isin(["A33", "B37", "B38"])
            buffered_out.loc[~mask, code_col] = "XXX"

    # Clip final union back to watershed
    print("\nFinal clipping to watershed...")
    final_clipped = gpd.overlay(buffered_out, watershed, how="intersection")

    # Save to file
    final_output_path = os.path.join(ws_output_dir, f"invekos_union_final_ws_{watershed_number}.gpkg")
    print(f"\nSaving result to {final_output_path}...")
    final_clipped.to_file(final_output_path, driver="GPKG")

    print("\nInVeKoS processing complete.")


if __name__ == "__main__":
    user_path = "E:/DAKISWorkspace"
    gdb_path = "E:/DAKISWorkspace/EROSPOT.gdb"
    watershed_number = 4

    print("Running InVeKoS processor...")
    process_invekos_data(gdb_path, watershed_number, user_path, gdb_path)
    print("Done.")
