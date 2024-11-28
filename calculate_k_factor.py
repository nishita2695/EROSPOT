
"""
Authors: Nishita Thakur, Marvin Melzer

Credit authorship contribution statement:
Nishita Thakur: Software (lead). Marvin Melzer: Conceptualization (lead);
Methodology (lead); Data duration (lead); Funding acquisition (lead); Software (supporting).

Project: EROSPOT (DAKIS)

Last Update: 2024-11-26

Description: This script is used to calculate the k-factor for watersheds, including sealed areas as well.
To be called in a loop from the integrated model. Standalone version works as well. Loop parameters need to be changed,
adjustable statically by user.

License: Please refer to the document titled 'License.docx' in the repository
"""
import arcpy
import os

# Overwriting results during rerun = True
arcpy.env.overwriteOutput = True


# Calculate k - factor Function, parameters: Main folder path, Geodatabase Path, and the iteration number
# which in this case, is the watershed number
'''SECTION 1.4, User Guide'''
def calculate_K_Factor(GeoDatabasePath, DirectoryPath, selected_watershed, x):
    # Extensions required for vector and raster data processing
    arcpy.CheckOutExtension("spatial")
    arcpy.CheckOutExtension("ImageAnalyst")

    # File Path for ezg Layer used for selection
    ezg_by_erospot = GeoDatabasePath + "/ezg_by_erospot"

    # Intermediate file paths
    buffered_main_layer = GeoDatabasePath + "/ezg_by_erospot_buffered_INITIAL"
    process_buffer_ver01l = GeoDatabasePath + "/buffered_processed_layer_ver01_l"
    process_buffer_ver02l = GeoDatabasePath + "/buffered_processed_layer_ver02_l"
    union_initial = GeoDatabasePath + "/sealed_areas_preliminary"
    union_sealed_watershed = GeoDatabasePath + "/sealed_areas_union_watershed"
    sealed_areas_ws = GeoDatabasePath + "/sealed_areas_ws"

    # File paths for the shape files of ATKIS data, Bavaria, Stored outside the GDB
    ver01_shp = DirectoryPath + "/ATKIS/ver01_f.shp"
    ver03_shp = DirectoryPath + "/ATKIS/ver03_f.shp"
    sie02_shp = DirectoryPath + "/ATKIS/sie02_f.shp"
    gew01_shp = DirectoryPath + "/ATKIS/gew01_f.shp"
    ver01_l_shp = DirectoryPath + "/ATKIS/ver01_l.shp"
    ver02_l_shp = DirectoryPath + "/ATKIS/ver02_l.shp"

    # File Path for the whole k-factor, Bayern
    k_factor_komplett_bayern_tif = arcpy.Raster(
        DirectoryPath + "/K_Faktor_Bayern/k_factor_komplett_bayern.tif")

    # Loop for each watershed

    if os.path.exists(DirectoryPath + "/InputDataInvest/testing/ws_" + str(x) + "/k-factor"):
        print("Folder for storage of k-factor raster exists!")
    else:
        os.makedirs(DirectoryPath + "/InputDataInvest/testing/ws_" + str(x) + "/k-factor")
    clipped_k_factor = GeoDatabasePath + "/k_factor_clipped_str_" + str(x)
    ver_01_ClipOutput = GeoDatabasePath + "/ver01_f_Clip_ws_" + str(x)
    ver_01_ClipOutput_Dissolve = GeoDatabasePath + "/ver01_f_Clip_ws_" + str(x) + "_Dissolve"
    ver_03_ClipOutput = GeoDatabasePath + "/ver03_f_Clip_ws_" + str(x)
    ver_03_ClipOutput_Dissolve = GeoDatabasePath + "/ver03_f_Clip_ws_" + str(x) + "_Dissolve"
    sie_02_ClipOutput = GeoDatabasePath + "/sie_02_f_Clip_ws_" + str(x)
    sie_02_ClipOutput_Dissolve = GeoDatabasePath + "/sie_02_f_Clip_ws_" + str(x) + "_Dissolve"
    gew_01_ClipOutput = GeoDatabasePath + "/gew01_f_Clip_ws_" + str(x)
    gew_01_ClipOutput_Dissolve = GeoDatabasePath + "/gew01_f_Clip_ws_" + str(x) + "_Dissolve"
    ver_01_l_ClipOutput = GeoDatabasePath + "/ver01_l_Clip_ws_" + str(x)
    ver_01_l_ClipOutput_Dissolve = GeoDatabasePath + "/ver01_l_Clip_ws_" + str(x) + "_Dissolve"
    ver_02_l_ClipOutput = GeoDatabasePath + "/ver02_l_Clip_ws_" + str(x)
    ver_02_l_ClipOutput_Dissolve = GeoDatabasePath + "/ver02_l_Clip_ws_" + str(x) + "_Dissolve"

    # Selection of each watershed according to the expl_number
    selected_watershed_output = selected_watershed

    # Buffer selected watershed
    arcpy.Buffer_analysis(in_features=selected_watershed_output, out_feature_class=buffered_main_layer,
                          buffer_distance_or_field="5 Meters")

    # Clip k factor from each selected watershed
    arcpy.Clip_management(in_raster=k_factor_komplett_bayern_tif, out_raster=clipped_k_factor,
                          in_template_dataset=buffered_main_layer)
    clipped_k_factor = arcpy.Raster(clipped_k_factor)

    # Data Processing for ATKIS variables

    # ver01_f
    arcpy.Clip_analysis(in_features=ver01_shp, clip_features=selected_watershed_output,
                        out_feature_class=ver_01_ClipOutput)
    arcpy.Dissolve_management(in_features=ver_01_ClipOutput,
                              out_feature_class=ver_01_ClipOutput_Dissolve,
                              dissolve_field=["OBJART", "OBJART_TXT"])
    ver_01_f_AlterField = arcpy.AlterField_management(in_table=ver_01_ClipOutput_Dissolve, field="OBJART",
                                                      new_field_name="OA_ver01_f", new_field_alias="OA_ver01_f")[0]

    # ver03_f
    arcpy.Clip_analysis(in_features=ver03_shp, clip_features=selected_watershed_output,
                        out_feature_class=ver_03_ClipOutput)
    arcpy.Dissolve_management(in_features=ver_03_ClipOutput,
                              out_feature_class=ver_03_ClipOutput_Dissolve,
                              dissolve_field=["OBJART", "OBJART_TXT"])
    ver_03_f_AlterField = arcpy.AlterField_management(in_table=ver_03_ClipOutput_Dissolve, field="OBJART",
                                                      new_field_name="OA_ver03_f", new_field_alias="OA_ver03_f")[0]

    # sie02_f
    arcpy.Clip_analysis(in_features=sie02_shp, clip_features=selected_watershed_output,
                        out_feature_class=sie_02_ClipOutput)
    arcpy.Dissolve_management(in_features=sie_02_ClipOutput,
                              out_feature_class=sie_02_ClipOutput_Dissolve,
                              dissolve_field=["OBJART", "OBJART_TXT"])
    sie_02_f_AlterField = arcpy.AlterField_management(in_table=sie_02_ClipOutput_Dissolve, field="OBJART",
                                                      new_field_name="OA_sie02_f", new_field_alias="OA_sie02_f")[0]

    # gew01_f
    arcpy.Clip_analysis(in_features=gew01_shp, clip_features=selected_watershed_output,
                        out_feature_class=gew_01_ClipOutput)
    arcpy.Dissolve_management(in_features=gew_01_ClipOutput,
                              out_feature_class=gew_01_ClipOutput_Dissolve,
                              dissolve_field=["OBJART", "OBJART_TXT"])
    gew_01_f_AlterField = arcpy.AlterField_management(in_table=gew_01_ClipOutput_Dissolve, field="OBJART",
                                                      new_field_name="OA_gew01_f", new_field_alias="OA_gew01_f")[0]

    # ver01_l
    arcpy.Clip_analysis(in_features=ver01_l_shp, clip_features=selected_watershed_output,
                        out_feature_class=ver_01_l_ClipOutput)
    arcpy.Dissolve_management(in_features=ver_01_l_ClipOutput,
                              out_feature_class=ver_01_l_ClipOutput_Dissolve,
                              dissolve_field=["OBJART", "OBJART_TXT"])
    ver_01_l_AlterField = arcpy.AlterField_management(in_table=ver_01_l_ClipOutput_Dissolve, field="OBJART",
                                                      new_field_name="OA_ver01_l", new_field_alias="OA_ver01_l")[0]
    # Buffer after processing ver01
    arcpy.Buffer_analysis(in_features=ver_01_l_AlterField, out_feature_class=process_buffer_ver01l,
                          buffer_distance_or_field="2.75 Meters", dissolve_option="ALL")

    # ver02_l
    arcpy.Clip_analysis(in_features=ver02_l_shp, clip_features=selected_watershed_output,
                        out_feature_class=ver_02_l_ClipOutput)
    arcpy.Dissolve_management(in_features=ver_02_l_ClipOutput,
                              out_feature_class=ver_02_l_ClipOutput_Dissolve,
                              dissolve_field=["OBJART", "OBJART_TXT"])
    ver_02_l_AlterField = arcpy.AlterField_management(in_table=ver_02_l_ClipOutput_Dissolve, field="OBJART",
                                                      new_field_name="OA_ver02_l", new_field_alias="OA_ver02_l")[0]

    # Buffer after processing ver02
    arcpy.Buffer_analysis(in_features=ver_02_l_AlterField, out_feature_class=process_buffer_ver02l,
                          buffer_distance_or_field="2.75 Meters", dissolve_option="ALL")

    # Process: Union of Sealed Areas
    arcpy.Union_analysis(
        in_features=[[ver_01_f_AlterField, ""], [ver_03_f_AlterField, ""], [sie_02_f_AlterField, ""],
                     [gew_01_f_AlterField, ""], [process_buffer_ver01l, ""], [process_buffer_ver02l, ""]],
        out_feature_class=union_initial, join_attributes="ALL", gaps="GAPS")
    sealed_add_field = arcpy.AddField_management(in_table=union_initial, field_name="sealed_areas_atkis",
                                                 field_type="SHORT")[0]
    sealed_calculate_field = arcpy.CalculateField_management(in_table=sealed_add_field, field="sealed_areas_atkis",
                                                             expression="1")[0]
    # Process: Union to combine sealed areas with remaining areas of watershed
    arcpy.Union_analysis(in_features=[[sealed_calculate_field, ""], [selected_watershed_output, ""]],
                         out_feature_class=union_sealed_watershed)

    sealed_areas_add_field = arcpy.AddField_management(in_table=union_sealed_watershed,
                                                       field_name="sealed_area_union", field_type="SHORT"
                                                       )[0]

    sealed_areas_calculate_field = arcpy.CalculateField_management(in_table=sealed_areas_add_field,
                                                                   field="sealed_area_union", expression="1")[0]

    select_union_layer = arcpy.SelectLayerByAttribute_management(in_layer_or_view=sealed_areas_calculate_field,
                                                                 where_clause="sealed_areas_atkis=1")
    sealed_areas_layer_2 = arcpy.CalculateField_management(in_table=select_union_layer, field="sealed_area_union",
                                                           expression="0")[0]

    # Select Layer by attribute - clear selection
    sealed_areas_layer_2 = arcpy.SelectLayerByAttribute_management(in_layer_or_view=sealed_areas_layer_2,
                                                                   selection_type="CLEAR_SELECTION")
    # Polygon to raster
    arcpy.PolygonToRaster_conversion(in_features=sealed_areas_layer_2, value_field="sealed_area_union",
                                     out_rasterdataset=sealed_areas_ws, cellsize="1", build_rat="DO_NOT_BUILD")

    # Raster Calculator multiplies sealed areas of K-Factor by 0
    k_ws_tif = DirectoryPath + "/InputDataInvest/testing/ws_" + str(x) + "/k-factor/k-factor-ws_" + str(x) + ".tif"
    print("Calculating sealed areas ...")
    Raster_multiplication = k_ws_tif
    k_ws_tif = clipped_k_factor * sealed_areas_ws
    # arcpy.env.cellSize = 1
    # Resample Raster to reset cellsize to 1
    # arcpy.env.compression = 'NONE'
    # arcpy.CopyRaster_management(k_ws_tif, DirectoryPath + "/InputDataInvest/testing/ws_" + str(x) +
    #                           "/k-factor/k-factor-resampled_ws_" + str(x))
    Raster_multiplication = arcpy.Resample_management(k_ws_tif,
                                                      DirectoryPath + "/InputDataInvest/testing/ws_" + str(x) +
                                                      "/k-factor/k-factor-resampled_ws_" + str(x) + ".tif", "1")


if __name__ == '__main__':
    # The program executes from here, the functions written before are called from here, and executed in the sequence
    # that they are mentioned within the 'main' function
    # ___________________________________________________________________________________________
    # PLEASE CHANGE YOUR PATH HERE
    # ___________________________________________________________________________________________
    UserPath = "D:/Users/Thakur/ErospotWorkspace"
    MainPathGDB = "D:/Users/Thakur/ErospotWorkspace/EROSPOT.gdb"
    # ------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------
    if os.path.exists(UserPath + "/InputDataInvest"):
        print("folder '{}' exists!".format(MainPathGDB + "/InputDataInvest"))
    else:
        # create directory or directories until sub_folder1_path
        os.makedirs(UserPath + "/InputDataInvest")
    print("Created")
    calculate_K_Factor(MainPathGDB, UserPath, 4)
    print("Done")
