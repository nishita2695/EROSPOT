import arcpy
from arcpy.ia import *


def identify_hotspots(selected_watershed, x, UserPath, MainPathGDB):
    arcpy.env.overwriteOutput = True
    print("Identifying Hotspots")
    clipped_boundaries = MainPathGDB + "/field1_boundaries_ws_" + str(x)
    sed_export = UserPath + "/OutputDataInvest/ws_" + str(x) + "/sed_export.tif"
    # Extract the invekos field boundaries by the year 2021
    #check the range from the user and use the last year
    field_boundaries = UserPath + "/InVeKoS/Nutzung_Aum_Bayern_2021/invekos_by_21_p.shp"#user can decide the year (field-geometries)ies)
    # Clip the layers according to the watersheds
    arcpy.Clip_analysis(in_features=field_boundaries, clip_features=selected_watershed,
                        out_feature_class=clipped_boundaries)
    delete_identical = arcpy.DeleteIdentical_management(in_dataset=clipped_boundaries, fields=["Shape_Area"])[0]
    # Process: Buffer
    buffered_fields = MainPathGDB + "/buffered_dataset_ws_" + str(x)
    arcpy.Buffer_analysis(in_features=delete_identical, out_feature_class=buffered_fields,
                          buffer_distance_or_field="-0.1 Meters")
    #user needs to set the field name default: to bavarian, set them here
    # Process: Dissolve - maybe not necesssary here as the bavarian dataset does not have it. Create
    #this_?
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
    constant_raster_location = MainPathGDB + "/createConstantRaster"
    print("Creating constant raster....")
    constant_raster = constant_raster_location
    cursor = arcpy.SearchCursor(cal_field_zonal_statistics)
    field = "min_value"
    # check if one or more than one building footprint exist
    for row in cursor:
        min_value = (row.getValue(field))
        print(min_value)
    constant_raster_location = arcpy.sa.CreateConstantRaster(min_value, "FLOAT", "1", extract_ws)
    # constant raster not getting saved in the gdb
    constant_raster_location.save(constant_raster)

    # Process: filter Raster and set hotspots to value 1 (Raster Calculator) (ia)
    con_raster_cal = MainPathGDB + "/raster_constant_ws_" + str(x)
    filter_values_in_raster = con_raster_cal
    con_raster_cal = Con(extract_ws > constant_raster, 1, 0)
    con_raster_cal.save(filter_values_in_raster)
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


if __name__ == '__main__':
    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = True

    # Check out any necessary licenses.
    arcpy.CheckOutExtension("spatial")
    arcpy.CheckOutExtension("ImageExt")
    arcpy.CheckOutExtension("ImageAnalyst")
    arcpy.env.overwriteOutput = True
    # Please change the path here This Part below (two lines) has to be added to all separated models if you want to
    # run them, it is also part of the combined one.
    UserPath = "E:/ErospotWorkspace"
    MainPathGDB = "E:/ErospotWorkspace/EROSPOT.gdb"
    ezg_by_erospot = MainPathGDB + "/ezg_by_erospot"
    feature_layer = arcpy.MakeFeatureLayer_management(ezg_by_erospot, 'feature')
    for x in range(4, 5):
        selected_watershed = arcpy.SelectLayerByAttribute_management(
            in_layer_or_view=feature_layer,
            selection_type="NEW_SELECTION",
            where_clause="expl_num=" + str(x))
        identify_hotspots(selected_watershed, x, UserPath, MainPathGDB)

    print("Done")
