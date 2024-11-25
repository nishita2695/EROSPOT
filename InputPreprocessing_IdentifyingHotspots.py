"""
Author: Nishita Thakur
Concept: Marvin Melzer
Project: EROSPOT (DAKIS)
Last Update: 2024-11-20

Description: This script executes two processing steps: The first and most important - Integrates all the sub-models
as a function call and in the correct order of execution. The second: Integrates the identification of
hotspots after the first two steps of the model are executed. Some functions for the preprocessing
steps are coded in this file: Can be modularized in the future.

"""
import os

import arcpy
from arcpy.ia import *

from DGM_coordinates import find_coordinates
from DGM_copy import copyCoordinates_x_low, copyCoordinates_x_high, copyCoordinates_y_low, copyCoordinates_y_high, \
    addCoordinateFiles, stitchTiles
from Watershed_shape import create_shape
from calculate_k_factor import calculate_K_Factor
from invekos import calculate_lu_ws
from invekos_atkis_combined import flag
from invekos_atkis_combined import invekos_atkis_combined
from streams_atkis import streams_atkis

arcpy.env.overwriteOutput = True


# Function to identify hotspots, to be called after invest so that outputs are in the correct folder
def identify_hotspots(x, UserPath, MainPathGDB):
    arcpy.env.overwriteOutput = True
    feature_layer = MainPathGDB + "/ezg_by_erospot"
    selected_watershed = arcpy.SelectLayerByAttribute_management(
        in_layer_or_view=feature_layer,
        selection_type="NEW_SELECTION",
        where_clause="expl_num= " + str(x))
    print("***********************************************")
    print("STEP 3: IDENTIFYING HOTSPOTS")
    print("************************************************")
    print("Identifying hotspots for Watershed " + str(x) + "........")
    clipped_boundaries = MainPathGDB + "/field_boundaries_ws_" + str(x)
    sed_export = UserPath + "/OutputDataInvest/ws_" + str(x) + "/sed_export.tif"
    # Extract the invekos field boundaries by the year 2021
    # check the range from the user and use the last year
    field_boundaries = UserPath + "/InVeKoS/Nutzung_Aum_Bayern_2021/invekos_by_21_p.shp"  # user can decide the year (field-geometries)ies)
    # Clip the layers according to the watersheds
    arcpy.Clip_analysis(in_features=field_boundaries, clip_features=selected_watershed,
                        out_feature_class=clipped_boundaries)
    delete_identical = arcpy.DeleteIdentical_management(in_dataset=clipped_boundaries, fields=["Shape_Area"])[0]
    # Process: Buffer
    buffered_fields = MainPathGDB + "/buffered_dataset_ws_" + str(x)
    arcpy.Buffer_analysis(in_features=delete_identical, out_feature_class=buffered_fields,
                          buffer_distance_or_field="-0.1 Meters")
    # user needs to set the field name default: to bavarian, set them here
    # Process: Dissolve - maybe not necesssary here as the bavarian dataset does not have it. Create
    # this_?
    dissolved_dataset = MainPathGDB + "/dissolved_dataset"
    arcpy.Dissolve_management(in_features=buffered_fields, out_feature_class=dissolved_dataset,
                              dissolve_field=["OBJECTID"])

    # Process: Extract by Mask
    extract_ws = MainPathGDB + "/masked_sed_raster_ws_" + str(x)
    extract_ws = arcpy.sa.ExtractByMask(sed_export, dissolved_dataset, "INSIDE")
    print("Extracting by mask....")

    # Process: Zonal Statistics as Table
    table = MainPathGDB + "/table_ws_" + str(x)
    arcpy.ia.ZonalStatisticsAsTable(dissolved_dataset, "OBJECTID", extract_ws, table, ignore_nodata="DATA",
                                    statistics_type="MEAN_STD", process_as_multidimensional="CURRENT_SLICE",
                                    percentile_values=[90], percentile_interpolation_type="AUTO_DETECT",
                                    circular_calculation=
                                    "ARITHMETIC", circular_wrap_value=360)
    statistics_zonal = MainPathGDB + "/statistics_ws_" + str(x)
    arcpy.Statistics_analysis(in_table=table, out_table=statistics_zonal, statistics_fields=[["MEAN", "MEAN"],
                                                                                             ["STD", "MEAN"]])
    print("Computing zonal statistics....")
    # Add field min value
    add_field_zonal_statistics = arcpy.management.AddField(in_table=statistics_zonal, field_name="min_value",
                                                           field_type="DOUBLE",
                                                           field_precision=10)[0]
    cal_field_zonal_statistics = \
        arcpy.management.CalculateField(in_table=add_field_zonal_statistics, field="min_value",
                                        expression="!MEAN_MEAN! + (1.5*!MEAN_STD!)")[0]

    # Process: Create Constant Raster (Create Constant Raster) (sa)
   # constant_raster_location = MainPathGDB + "/createConstantRaster"
   # print("Creating constant raster....")
 #   constant_raster = constant_raster_location
    cursor = arcpy.SearchCursor(cal_field_zonal_statistics)
    field = "min_value"
    # check if one or more than one building footprint exist
    for row in cursor:
        min_value = (row.getValue(field))
        print(min_value)
    # constant_raster_location = arcpy.sa.CreateConstantRaster(min_value, "FLOAT", "1", extract_ws)
    # constant raster not getting saved in the gdb
    #constant_raster_location.save(constant_raster)

    # Process: filter Raster and set hotspots to value 1 (Raster Calculator) (ia)
    #con_raster_cal = MainPathGDB + "/raster_constant_ws_" + str(x)
    #filter_values_in_raster = con_raster_cal
    con_raster_cal = Con(extract_ws > min_value, 1, 0)
    #con_raster_cal.save(filter_values_in_raster)
    # Process: Raster to Polygon (Raster to Polygon) (conversion)
    raster_polygon = MainPathGDB + "/raster_to_pol_hotspots_ws_" + str(x)
    arcpy.conversion.RasterToPolygon(in_raster=con_raster_cal, out_polygon_features=raster_polygon)

    # Process: Select Layer By Attribute (Select Layer By Attribute) (management)
    selected_hotspot = arcpy.SelectLayerByAttribute_management(in_layer_or_view=raster_polygon,
                                                               where_clause="gridcode = 1")
    print("Converting to polygon...")

    # Process: Buffer of 3 M (Buffer) (analysis)
    buffer1 = MainPathGDB + "/hotspot_buffer1_ws_" + str(x)
    arcpy.Buffer_analysis(in_features=selected_hotspot, out_feature_class=buffer1, buffer_distance_or_field="3 Meters",
                          dissolve_option="ALL")

    #  Process: Buffer of -4M (Buffer) (analysis)
    buffer2 = MainPathGDB + "/hotspot_buffer2_ws_" + str(x)
    arcpy.Buffer_analysis(in_features=buffer1, out_feature_class=buffer2, buffer_distance_or_field="-4 Meters",
                          dissolve_option="ALL")
    print("Buffering...")

    # Process: Multipart To Singlepart (2) (Multipart To Singlepart) (management)
    multi_to_single = MainPathGDB + "/hotspot_multi_ws_" + str(x)
    arcpy.MultipartToSinglepart_management(in_features=buffer2, out_feature_class=multi_to_single)

    # Process: Select Layer By Attribute (2) (Select Layer By Attribute) (management)
    selection_shapearea = arcpy.SelectLayerByAttribute_management(in_layer_or_view=multi_to_single,
                                                                  where_clause="Shape_Area > 100")

    # Process: Minimum Bounding Geometry = convex (Minimum Bounding Geometry) (management)
    min_bounding = MainPathGDB + "/hotspot_min_bounding_ws_" + str(x)
    arcpy.MinimumBoundingGeometry_management(in_features=selection_shapearea, out_feature_class=min_bounding,
                                             geometry_type="CONVEX_HULL", group_option="NONE")

    # Process: Select Layer By Attribute (3) (Select Layer By Attribute) (management)
    selection_shapearea_bigger = arcpy.SelectLayerByAttribute_management(in_layer_or_view=min_bounding,
                                                                         where_clause="Shape_Area > 250")

    # Process: Add Field (Add Field) (management)
    add_ident_hotspot = arcpy.AddField_management(in_table=selection_shapearea_bigger, field_name="ident_hotsp",
                                                  field_type="SHORT", field_alias="ident_hotsp")[0]

    # Process: Calculate Field (Calculate Field) (management)
    cal_ident_hotspot = arcpy.CalculateField_management(in_table=add_ident_hotspot, field="ident_hotsp",
                                                        expression="1")[0]

    # Process: Union (Union) (analysis)
    hotspot_union = MainPathGDB + "/hotspot_union_ws_" + str(x)
    arcpy.Union_analysis(in_features=[[dissolved_dataset, ""], [cal_ident_hotspot, ""]],
                         out_feature_class=hotspot_union)
    print("Performing Union...")

    # Process: Select Layer By Attribute (4) (Select Layer By Attribute) (management)
    selection_hotspot_invekos = arcpy.SelectLayerByAttribute_management(in_layer_or_view=hotspot_union,
                                                                        where_clause="FID_dissolved_dataset <> -1 "
                                                                                     "And Shape_Area > 250 And "
                                                                                     "ident_hotsp = 1")

    # Process: Final Raster with Multipart To Singlepart (Multipart To Singlepart) (management)
    hotspot_final = MainPathGDB + "/hotspot_finalraster_ws_" + str(x)
    arcpy.MultipartToSinglepart_management(in_features=selection_hotspot_invekos,
                                           out_feature_class=hotspot_final)
    print('Hotspots Identified...')
    # Process: Select Layer By Attribute (8) (Select Layer By Attribute) (management)
    hotspots_shapearea_400 = arcpy.SelectLayerByAttribute_management(in_layer_or_view=hotspot_final,
                                                                     where_clause="Shape_Area < 400")

    # Process: Delete Rows (Delete Rows) (management)
    Updated_Input_With_Rows_Removed = arcpy.management.DeleteRows(in_rows=hotspots_shapearea_400)[0]

    # Process: Add Field (2) (Add Field) (management)
    hotspots_add_sed_exp = \
        arcpy.management.AddField(in_table=Updated_Input_With_Rows_Removed, field_name="sed_export_tons_hot",
                                  field_type="DOUBLE", field_alias="sed_export_tons_hot")[0]
    # Process: Add Field (3) (Add Field) (management)
    hotspots_add_tons_ha = \
        arcpy.management.AddField(in_table=hotspots_add_sed_exp, field_name="sed_export_tons_ha", field_type="DOUBLE",
                                  field_alias="sed_export_tons_ha")[0]

    # Process: Zonal Statistics as Table (2) (Zonal Statistics as Table) (ia)
    Zonal_hotspot = MainPathGDB + "/hotspot_zone_stats_ws_" + str(x)
    arcpy.ia.ZonalStatisticsAsTable(Updated_Input_With_Rows_Removed, "ORIG_FID",
                                    sed_export,
                                    Zonal_hotspot, "DATA", "MEAN", "CURRENT_SLICE", [90], "AUTO_DETECT",
                                    "ARITHMETIC", 360)

    # Process: Please Ckeck Join Fields! Join Field (Join Field) (management)
    hotspots_check_join = \
        arcpy.management.JoinField(in_data=hotspots_add_tons_ha, in_field="ORIG_FID",
                                   join_table=Zonal_hotspot,
                                   join_field="ORIG_FID", fields=["MEAN"])[0]

    # Process: Calculate Field (3) (Calculate Field) (management)
    hotspots_cal_erosion = \
        arcpy.management.CalculateField(in_table=hotspots_check_join,
                                        field="sed_export_tons_ha", expression="""Round($feature.MEAN * 10000, 2)
        """, expression_type="ARCADE", code_block="""rec =0
        def result_1()
            round !MEAN!*10000""")[0]

    # Process: Calculate Field (2) (Calculate Field) (management)
    hotspots_cal_erosion_hotspot = \
        arcpy.management.CalculateField(in_table=hotspots_cal_erosion, field="sed_export_tons_hot",
                                        expression="Round($feature.MEAN * $feature.Shape_Area, 2)",
                                        expression_type="ARCADE", code_block="""Round($feature.MEAN *
        , 2)""")[0]
    print("Converting features to json...")
    # Process: Features To JSON (2) (Features To JSON) (conversion)
    if os.path.exists(UserPath + "/Hotspots"):
        print("Folder for Hotspots already exist!")
    else:
        os.makedirs(UserPath + "/Hotspots")
        print("Hotspots folder created for storing .geojson files!")

    json_path = UserPath + "/Hotspots/ws_" + str(x) + ".geojson"
    arcpy.conversion.FeaturesToJSON(in_features=hotspots_cal_erosion_hotspot,
                                    out_json_file=json_path, geoJSON="GEOJSON",
                                    outputToWGS84="WGS84")
    print("Deleting extra layers...")
    # Process: Delete (Delete) (management)
    Delete_Succeeded = arcpy.Delete_management(in_data=[hotspots_add_sed_exp, min_bounding, multi_to_single,
                                                        Zonal_hotspot, buffer2, buffer1, dissolved_dataset,
                                                        statistics_zonal, raster_polygon, hotspot_union
                                                        ])[0]

    # Process: Zonal Statistics as Table (3) (Zonal Statistics as Table) (ia)
    zonal_ws_stats = MainPathGDB + "/stats_zonal_final_ws_" + str(x)
    arcpy.ia.ZonalStatisticsAsTable(buffered_fields, "OBJECTID", extract_ws,
                                    zonal_ws_stats, "DATA", "MEAN_STD", "CURRENT_SLICE", [90],
                                    "AUTO_DETECT", "ARITHMETIC", 360)

    # Process: Join Field (2) (Join Field) (management)
    invekos_hotspots = \
        arcpy.management.JoinField(in_data=buffered_fields, in_field="OBJECTID",
                                   join_table=zonal_ws_stats, join_field="OBJECTID_1",
                                   fields=["MEAN", "MEDIAN", "STD"])[0]

    # Process: Calculate Field (5) (Calculate Field) (management)
    cal_mean = \
        arcpy.management.CalculateField(in_table=invekos_hotspots, field="MEAN", expression="!MEAN!*10000")[0]

    # Process: Alter Field (Alter Field) (management)
    mean_tonnes_ha = \
        arcpy.management.AlterField(in_table=cal_mean, field="MEAN", new_field_name="Tonnen_pro_Hektar",
                                    new_field_alias="Tonnen_pro_Hektar")[0]

    # Process: Feature Class To Feature Class (Feature Class To Feature Class) (conversion)
    Statistics_per_field = arcpy.conversion.FeatureClassToFeatureClass(in_features=mean_tonnes_ha,
                                                                       out_path=MainPathGDB,
                                                                       out_name="Statistics_per_field",
                                                                       field_mapping="Tonnen_pro_Hektar "
                                                                                     "\"Tonnen_pro_Hektar\" "
                                                                                     "true true false 8 Double 0 0,"
                                                                                     "First,#," +
                                                                                     MainPathGDB + "/layer_hotspot,"
                                                                                                   "Tonnen_pro_Hektar,-1,-1")[
        0]
    print("Calculating the erosion in tonnes per hectare...")
    # Process: Features To JSON (Features To JSON) (conversion)
    Statistics_per_field_json = UserPath + "/stats_per_field_ws_" + str(x) + ".geojson"
    arcpy.conversion.FeaturesToJSON(in_features=Statistics_per_field,
                                    out_json_file=Statistics_per_field_json, geoJSON="GEOJSON",
                                    outputToWGS84="WGS84")


# Function for the atkis MB model (LULC)

def calculate_lulc(atkis_union, selected_watershed, x, watershed_names_lulc, watershed_folders, geodatabasePath,
                   UserPath, MainPathGDB):
    arcpy.env.overwriteOutput = True
    veg_03_ClipOutput = MainPathGDB + "/veg03_f_Clip_ws_" + str(x)
    veg_03_ClipOutput_Dissolve = MainPathGDB + "/veg03_f_Clip_ws_" + str(x) + "_Dissolve"
    ver_01_ClipOutput = MainPathGDB + "/ver01_f_Clip_ws_" + str(x)
    ver_01_ClipOutput_Dissolve = MainPathGDB + "/ver01_f_Clip_ws_" + str(x) + "_Dissolve"
    ver_03_ClipOutput = MainPathGDB + "/ver03_f_Clip_ws_" + str(x)
    ver_03_ClipOutput_Dissolve = MainPathGDB + "/ver03_f_Clip_ws_" + str(x) + "_Dissolve"
    sie_02_ClipOutput = MainPathGDB + "/sie_02_f_Clip_ws_" + str(x)
    sie_02_ClipOutput_Dissolve = MainPathGDB + "/sie_02_f_Clip_ws_" + str(x) + "_Dissolve"
    gew_01_ClipOutput = MainPathGDB + "/gew01_f_Clip_ws_" + str(x)
    gew_01_ClipOutput_Dissolve = MainPathGDB + "/gew01_f_Clip_ws_" + str(x) + "_Dissolve"
    veg_02_ClipOutput = MainPathGDB + "/veg02_f_Clip_ws_" + str(x)
    veg_02_ClipOutput_Dissolve = MainPathGDB + "/veg02_f_Clip_ws_" + str(x) + "_Dissolve"
    veg_01_ClipOutput = MainPathGDB + "/veg01_f_Clip_ws_" + str(x)
    veg_01_ClipOutput_Dissolve = MainPathGDB + "/veg01_f_Clip_ws_" + str(x) + "_Dissolve"

    print("Calculating LULC")
    veg03_shp = UserPath + "/ATKIS/veg03_f.shp"
    ver01_shp = UserPath + "/ATKIS/ver01_f.shp"
    ver03_shp = UserPath + "/ATKIS/ver03_f.shp"
    sie02_shp = UserPath + "/ATKIS/sie02_f.shp"
    gew01_shp = UserPath + "/ATKIS/gew01_f.shp"
    veg02_shp = UserPath + "/ATKIS/veg02_f.shp"
    veg01_shp = UserPath + "/ATKIS/veg01_f.shp"

    # veg03
    arcpy.Clip_analysis(in_features=veg03_shp, clip_features=selected_watershed, out_feature_class=veg_03_ClipOutput,
                        cluster_tolerance="")
    arcpy.Dissolve_management(in_features=veg_03_ClipOutput, out_feature_class=veg_03_ClipOutput_Dissolve,
                              dissolve_field=["OBJART", "OBJART_TXT"], statistics_fields=[], multi_part="MULTI_PART",
                              unsplit_lines="DISSOLVE_LINES")
    veg_03_Clip_shp = arcpy.AlterField_management(in_table=veg_03_ClipOutput_Dissolve, field="OBJART",
                                                  new_field_name="OA_veg03_f", new_field_alias="OA_veg03_f",
                                                  field_type="TEXT", field_length=5, field_is_nullable="NULLABLE",
                                                  clear_field_alias="DO_NOT_CLEAR")[0]

    # ver01
    arcpy.Clip_analysis(in_features=ver01_shp, clip_features=selected_watershed, out_feature_class=ver_01_ClipOutput,
                        cluster_tolerance="")

    arcpy.Dissolve_management(in_features=ver_01_ClipOutput, out_feature_class=ver_01_ClipOutput_Dissolve,
                              dissolve_field=["OBJART", "OBJART_TXT"], statistics_fields=[], multi_part="MULTI_PART",
                              unsplit_lines="DISSOLVE_LINES")
    ver_01_Clip_shp = arcpy.AlterField_management(in_table=ver_01_ClipOutput_Dissolve, field="OBJART",
                                                  new_field_name="OA_ver01_f", new_field_alias="OA_ver01_f",
                                                  field_type="TEXT", field_length=5, field_is_nullable="NULLABLE",
                                                  clear_field_alias="DO_NOT_CLEAR")[0]

    # ver03
    arcpy.Clip_analysis(in_features=ver03_shp, clip_features=selected_watershed, out_feature_class=ver_03_ClipOutput,
                        cluster_tolerance="")
    arcpy.Dissolve_management(in_features=ver_03_ClipOutput, out_feature_class=ver_03_ClipOutput_Dissolve,
                              dissolve_field=["OBJART", "OBJART_TXT"], statistics_fields=[], multi_part="MULTI_PART",
                              unsplit_lines="DISSOLVE_LINES")

    ver_03_Clip_shp = arcpy.AlterField_management(in_table=ver_03_ClipOutput_Dissolve, field="OBJART",
                                                  new_field_name="OA_ver03_f", new_field_alias="OA_ver03_f",
                                                  field_type="TEXT", field_length=5, field_is_nullable="NULLABLE",
                                                  clear_field_alias="DO_NOT_CLEAR")[0]

    # sie02
    arcpy.Clip_analysis(in_features=sie02_shp, clip_features=selected_watershed, out_feature_class=sie_02_ClipOutput,
                        cluster_tolerance="")
    arcpy.Dissolve_management(in_features=sie_02_ClipOutput, out_feature_class=sie_02_ClipOutput_Dissolve,
                              dissolve_field=["OBJART", "OBJART_TXT"], statistics_fields=[], multi_part="MULTI_PART",
                              unsplit_lines="DISSOLVE_LINES")

    sie_02_Clip_shp = arcpy.AlterField_management(in_table=sie_02_ClipOutput_Dissolve, field="OBJART",
                                                  new_field_name="OA_sie02_f", new_field_alias="OA_sie02_f",
                                                  field_type="TEXT", field_length=5, field_is_nullable="NULLABLE",
                                                  clear_field_alias="DO_NOT_CLEAR")[0]

    # gew01
    arcpy.Clip_analysis(in_features=gew01_shp, clip_features=selected_watershed, out_feature_class=gew_01_ClipOutput,
                        cluster_tolerance="")
    arcpy.Dissolve_management(in_features=gew_01_ClipOutput, out_feature_class=gew_01_ClipOutput_Dissolve,
                              dissolve_field=["OBJART", "OBJART_TXT"], statistics_fields=[], multi_part="MULTI_PART",
                              unsplit_lines="DISSOLVE_LINES")
    gew_01_Clip_shp = arcpy.AlterField_management(in_table=gew_01_ClipOutput_Dissolve, field="OBJART",
                                                  new_field_name="OA_gew01_f", new_field_alias="OA_gew01_f",
                                                  field_type="TEXT", field_length=5, field_is_nullable="NULLABLE",
                                                  clear_field_alias="DO_NOT_CLEAR")[0]

    # veg02
    arcpy.Clip_analysis(in_features=veg02_shp, clip_features=selected_watershed, out_feature_class=veg_02_ClipOutput,
                        cluster_tolerance="")
    arcpy.Dissolve_management(in_features=veg_02_ClipOutput, out_feature_class=veg_02_ClipOutput_Dissolve,
                              dissolve_field=["OBJART", "OBJART_TXT", "VEG"], statistics_fields=[],
                              multi_part="MULTI_PART",
                              unsplit_lines="DISSOLVE_LINES")
    veg_02_Clip_shp = arcpy.AlterField_management(in_table=veg_02_ClipOutput_Dissolve, field="OBJART",
                                                  new_field_name="OA_veg02_f", new_field_alias="OA_veg02_f",
                                                  field_type="TEXT", field_length=5, field_is_nullable="NULLABLE",
                                                  clear_field_alias="DO_NOT_CLEAR")[0]
    veg_02_Clip_shp1 = arcpy.AlterField_management(in_table=veg_02_Clip_shp, field="VEG",
                                                   new_field_name="VEG_02", new_field_alias="VEG_02",
                                                   field_type="TEXT", field_length=4, field_is_nullable="NULLABLE",
                                                   clear_field_alias="DO_NOT_CLEAR")[0]

    # veg01
    arcpy.Clip_analysis(in_features=veg01_shp, clip_features=selected_watershed, out_feature_class=veg_01_ClipOutput,
                        cluster_tolerance="")
    arcpy.Dissolve_management(in_features=veg_01_ClipOutput, out_feature_class=veg_01_ClipOutput_Dissolve,
                              dissolve_field=["OBJART", "OBJART_TXT", "VEG"], statistics_fields=[],
                              multi_part="MULTI_PART",
                              unsplit_lines="DISSOLVE_LINES")
    veg_01_Clip_shp = arcpy.AlterField_management(in_table=veg_01_ClipOutput_Dissolve, field="OBJART",
                                                  new_field_name="OA_veg01_f", new_field_alias="OA_veg01_f",
                                                  field_type="TEXT", field_length=5, field_is_nullable="NULLABLE",
                                                  clear_field_alias="DO_NOT_CLEAR")[0]
    veg_01_Clip_shp1 = arcpy.AlterField_management(in_table=veg_01_Clip_shp, field="VEG",
                                                   new_field_name="VEG_01", new_field_alias="VEG_01",
                                                   field_type="TEXT", field_length=4, field_is_nullable="NULLABLE",
                                                   clear_field_alias="DO_NOT_CLEAR")[0]

    # ATKIS Union
    atkis_union_watershed = MainPathGDB + "/atkis_union_py_ws_" + str(x)
    arcpy.Union_analysis(
        in_features=[[veg_03_Clip_shp, ""], [ver_01_Clip_shp, ""], [ver_03_Clip_shp, ""], [sie_02_Clip_shp, ""],
                     [gew_01_Clip_shp, ""], [veg_02_Clip_shp1, ""], [veg_01_Clip_shp1, ""]],
        out_feature_class=atkis_union_watershed, join_attributes="NO_FID", cluster_tolerance="", gaps="GAPS")

    # AddField
    atkis_union_watershed_shp = arcpy.AddField_management(in_table=atkis_union_watershed, field_name="lulc_atkis",
                                                          field_type="LONG", field_precision=None, field_length=None,
                                                          field_alias="", field_is_nullable="NULLABLE",
                                                          field_is_required="NON_REQUIRED", field_domain="")[0]
    # CalculateField
    atkis_union_calculate_watershed = arcpy.CalculateField_management(in_table=atkis_union_watershed_shp,
                                                                      field="lulc_atkis",
                                                                      expression="!OA_veg01_f!+!OA_veg02_f"
                                                                                 "!+!OA_veg03_f!+!OA_ver03_f!+"
                                                                                 "!OA_ver01_f!+ !OA_sie02_f!+ "
                                                                                 "!OA_gew01_f!",
                                                                      expression_type="PYTHON3", code_block="",
                                                                      field_type="TEXT",
                                                                      enforce_domains="NO_ENFORCE_DOMAINS")[0]

    # code to check if data exists (Default mb functions or code does not work)
    fcList = arcpy.ListFeatureClasses()

    Delete_Success = \
        arcpy.Delete_management(
            in_data=[veg_03_Clip_shp, ver_01_Clip_shp, ver_03_Clip_shp, sie_02_Clip_shp, gew_01_Clip_shp
                , veg_02_Clip_shp1, veg_01_Clip_shp1, veg_03_ClipOutput_Dissolve, veg_03_ClipOutput,

                     veg_02_ClipOutput_Dissolve, veg_02_ClipOutput,
                     veg_01_ClipOutput_Dissolve, veg_01_ClipOutput, gew_01_ClipOutput_Dissolve,
                     gew_01_ClipOutput, sie_02_ClipOutput, sie_02_ClipOutput_Dissolve,
                     ver_01_ClipOutput, ver_03_ClipOutput, ver_03_ClipOutput_Dissolve,
                     ver_01_ClipOutput_Dissolve
                     ], data_type="")[0]

    # CreateFolder
    # if watershed_folders:
    # arcpy.CreateFolder_management(out_folder_path=watershed_names_lulc, out_name="lulc_ws_" + str(x))[0]


# k-factor and r-factor
def model_combined_once(CentralFolderPath, GDBPath, x):
    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("3D")
    arcpy.CheckOutExtension("spatial")
    arcpy.CheckOutExtension("ImageAnalyst")
    print("***********************************************")
    print("STEP 1: PREPROCESSING INPUTS")
    print("************************************************")
    # arr = np.empty(10, dtype=Union[Union[conversion, int, float, complex, str, Dict[Any, Any]], Any])

    r_factor_komplett_bayern_tif = arcpy.Raster(CentralFolderPath + "/R_Faktor_bayern/r_factor_bayern.tif")
    ezg_by_erospot = GDBPath + "/ezg_by_erospot"
    geodatabasePath = GDBPath
    if os.path.exists(CentralFolderPath + "/InputDataInvest"):
        print("folder '{}' exists!".format(CentralFolderPath + "/InputDataInvest"))
    else:
        # create directory or directories until sub_folder1_path
        os.makedirs(CentralFolderPath + "/InputDataInvest/testing")
    if os.path.exists(CentralFolderPath + "/OutputDataInvest"):
        print("folder '{}' exists!".format(CentralFolderPath + "/OutputDataInvest"))
    else:
        # create directory or directories until sub_folder1_path
        os.makedirs(CentralFolderPath + "/OutputDataInvest")
    # InputInvest = arcpy.CreateFolder_management(out_folder_path=CentralFolderPath, out_name="InputDataInvest")[0]
    print(" Folders Created! ")
    feature_layer = arcpy.MakeFeatureLayer_management(ezg_by_erospot, 'feature')
    # folder_name = arcpy.CreateFolder_management(out_folder_path=InputInvest, out_name="testing")[0]

    # NOTE FOR INVEST * INPUT
    # we nullify the iteration and link it with the x being sent. So instead of the iteration being created
    # in here, it will be triggered by the extra script
    print("WATERSHED NUMBER " + str(x))
    print(":::::::::::::::::::::")
    if os.path.exists(CentralFolderPath + "/InputDataInvest/testing/ws_" + str(x)):
        print("Folder for specific Watershed exists for Input Intermediate Data Storage!")
    else:
        os.makedirs(CentralFolderPath + "/InputDataInvest/testing/ws_" + str(x))
    if os.path.exists(CentralFolderPath + "/OutputDataInvest/ws_" + str(x)):
        print("Folder for specific Watershed exists for Output Data Storage!")
    else:
        os.makedirs(CentralFolderPath + "/OutputDataInvest/ws_" + str(x))
    folder_name = CentralFolderPath + "/InputDataInvest/testing"
    folder_ws = CentralFolderPath + "/InputDataInvest/testing/ws_" + str(x)
    selected_watershed = arcpy.SelectLayerByAttribute_management(
        in_layer_or_view=feature_layer,
        selection_type="NEW_SELECTION",
        where_clause="expl_num= " + str(x))
    create_shape(x, selected_watershed, CentralFolderPath)
    watershed_folders = CentralFolderPath + "/InputDataInvest/testing"

    folder_ws_r = arcpy.CreateFolder_management(out_folder_path=watershed_folders,
                                                out_name="ws_" + str(x) + "/r_factor")
    watershed_names_r = CentralFolderPath + "/InputDataInvest/testing/ws_" + str(
        x) + "/r_factor/r_ws_" + str(
        x) + ".tif"
    watershed_r_times = CentralFolderPath + "/InputDataInvest/testing/ws_" + str(
        x) + "/r_factor/r_ws_times" + str(
        x) + ".tif"
    watershed_names_lulc = CentralFolderPath + "/InputDataInvest/testing/ws_" + str(
        x) + "/lulc"
    atkis_union = GDBPath + "/atkis_union_ws_" + str(x)

    if folder_name:
        if folder_ws:
            calculate_lulc(atkis_union, selected_watershed, x, watershed_names_lulc, watershed_folders,
                           geodatabasePath, CentralFolderPath, GDBPath)
            calculate_lu_ws(selected_watershed, x, CentralFolderPath, GDBPath)
            invekos_atkis_combined(selected_watershed, x, CentralFolderPath, GDBPath)

            streams_atkis(selected_watershed, x, CentralFolderPath, GDBPath)
            print("Calculating k_factor...")
            calculate_K_Factor(GDBPath, CentralFolderPath, selected_watershed, x)
            # 100 m
            selected_watershed_buffer_r = GDBPath + "/selected_watershed_r"
            arcpy.Buffer_analysis(in_features=selected_watershed,
                                  out_feature_class=selected_watershed_buffer_r,
                                  buffer_distance_or_field=" 100 Meters ")
            print("Calculating r_factor...")
            arcpy.Clip_management(in_raster=r_factor_komplett_bayern_tif, rectangle="",
                                  out_raster=watershed_names_r,
                                  in_template_dataset=selected_watershed_buffer_r, nodata_value="1,79e+308",
                                  clipping_geometry="NONE",
                                  maintain_clipping_extent="NO_MAINTAIN_EXTENT")

            watershed_names_r = arcpy.Raster(watershed_names_r)
            arcpy.Times_3d(in_raster_or_constant1=watershed_names_r, in_raster_or_constant2=10,
                           out_raster=watershed_r_times)
            arcpy.Delete_management(watershed_names_r)
            find_coordinates(selected_watershed, x, CentralFolderPath, GDBPath, ezg_by_erospot)
            print("Copying and Creating folder....Please wait...")

            # Function call for extracting x_low coordinate from the layer's attribute table
            dictionary__x_low = copyCoordinates_x_low(feature_layer)
            # Function call for extracting x_high coordinate from the layer's attribute table
            dictionary__x_high = copyCoordinates_x_high(feature_layer)
            # Function call for extracting y_low coordinate from the layer's attribute table
            dictionary__y_low = copyCoordinates_y_low(feature_layer)
            # Function call for extracting y_high coordinate from the layer's attribute table
            dictionary__y_high = copyCoordinates_y_high(feature_layer)
            # Function call for the actual copying and pasting (python file io operations with os module)
            addCoordinateFiles(CentralFolderPath, x, dictionary__x_low, dictionary__x_high,
                               dictionary__y_low,
                               dictionary__y_high)
            # Function to stitch the mosaic into one single raster
            stitchTiles(x, CentralFolderPath)

            print("The DGM Tiles for the watershed have been stitched!")

            flag_check = flag()
            if flag_check is True:
                print(
                    "Some C Values are missing; Please note that they have been replaced by 0.5 for computation "
                    "purposes"
                    )


