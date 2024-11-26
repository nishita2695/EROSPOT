"""
Authors: Nishita Thakur, Marvin Melzer

Credit authorship contribution statement:
Nishita Thakur: Software (lead). Marvin Melzer: Conceptualization (lead);
Methodology (lead); Data duration (lead); Funding acquisition (lead); Software (supporting).

Project: EROSPOT (DAKIS)

Last Update: 2024-11-26

Description: This script is used to get the corner coordinates of the minimum bounding rectangle
of the watershed and store them as files in a coherent naming structure

License: Please refer to the document titled 'License.docx' in the repository

"""
import arcpy

'''SECTION 1.2, User Guide'''
def find_coordinates(selected_watershed, x, UserPath, MainPathGDB, ezg_by_erospot):
    arcpy.env.overwriteOutput = True
    #ezg_by_erospot = MainPathGDB + "/ezg_by_erospot"
    erospot_minimum = MainPathGDB + "/ezg_by_erospot_minimum"
    vertice_minimum = MainPathGDB + "/ezg_by_erospot_ver_minimum"
    summary_attr = MainPathGDB + "/ezg_by_erospot_ws_" + str(x)
    arcpy.AddField_management(in_table=ezg_by_erospot, field_name="dummy_coordinate", field_type="TEXT",
                              field_precision=None, field_length=None, field_scale=None, field_alias="dummy_coordinate",
                              field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")[0]
    cal_coord_XH = \
        arcpy.CalculateField_management(in_table=selected_watershed, field="x_low", expression="!dummy_coordinate!",
                                        expression_type="PYTHON3", code_block="", field_type="LONG",
                                        enforce_domains="NO_ENFORCE_DOMAINS")[0]
    cal_coord_XH = \
        arcpy.CalculateField_management(in_table=selected_watershed, field="x_high", expression="!dummy_coordinate!",
                                        expression_type="PYTHON3", code_block="", field_type="LONG",
                                        enforce_domains="NO_ENFORCE_DOMAINS")[0]
    cal_coord_YL = \
        arcpy.CalculateField_management(in_table=selected_watershed, field="y_low", expression="!dummy_coordinate!",
                                        expression_type="PYTHON3", code_block="", field_type="LONG",
                                        enforce_domains="NO_ENFORCE_DOMAINS")[0]
    cal_coord_YH = \
        arcpy.CalculateField_management(in_table=selected_watershed, field="y_high", expression="!dummy_coordinate!",
                                        expression_type="PYTHON3", code_block="", field_type="LONG",
                                        enforce_domains="NO_ENFORCE_DOMAINS")[0]
    # Minimum Bounding Geometry
    arcpy.MinimumBoundingGeometry_management(in_features=selected_watershed, out_feature_class=erospot_minimum,
                                             geometry_type="ENVELOPE", group_option="NONE", group_field=[],
                                             mbg_fields_option="NO_MBG_FIELDS")
    # Vertices to Points
    arcpy.FeatureVerticesToPoints_management(in_features=erospot_minimum, out_feature_class=vertice_minimum,
                                             point_location="ALL")

    # Add XY Coordinates
    Updated_input_features = arcpy.AddXY_management(in_features=vertice_minimum)[0]

    # Point X obj ID 1
    layer_minimum_1 = arcpy.SelectLayerByAttribute_management(in_layer_or_view=Updated_input_features,
                                                              selection_type="NEW_SELECTION",
                                                              where_clause="OBJECTID = 1",
                                                              invert_where_clause="")
    layer_minimum_1_cal = arcpy.CalculateField_management(in_table=layer_minimum_1, field="POINT_X",
                                                          expression="""floor($feature.POINT_X/1000)""",
                                                          expression_type="ARCADE",
                                                          code_block="round((!POINT_X! /1000)+1,0)", field_type="TEXT",
                                                          enforce_domains="NO_ENFORCE_DOMAINS")[0]

    # Point X obj ID 3
    layer_minimum_3 = arcpy.SelectLayerByAttribute_management(in_layer_or_view=layer_minimum_1_cal,
                                                              selection_type="NEW_SELECTION",
                                                              where_clause="OBJECTID = 3",
                                                              invert_where_clause="")
    layer_minimum_3_cal = arcpy.CalculateField_management(in_table=layer_minimum_3, field="POINT_X",
                                                          expression="""floor($feature.POINT_X/1000)""",
                                                          expression_type="ARCADE",
                                                          code_block="round((!POINT_X! /1000)+1,0)", field_type="TEXT",
                                                          enforce_domains="NO_ENFORCE_DOMAINS")[0]

    # Point Y obj ID 1
    layer_minimum_1y = arcpy.SelectLayerByAttribute_management(in_layer_or_view=layer_minimum_3_cal,
                                                               selection_type="NEW_SELECTION",
                                                               where_clause="OBJECTID = 1",
                                                               invert_where_clause="")
    layer_minimum_1y_cal = arcpy.CalculateField_management(in_table=layer_minimum_1y, field="POINT_Y",
                                                           expression="""floor($feature.POINT_Y/1000)""",
                                                           expression_type="ARCADE",
                                                           code_block="round((!POINT_X! /1000)+1,0)", field_type="TEXT",
                                                           enforce_domains="NO_ENFORCE_DOMAINS")[0]
    # Point Y obj ID 3
    layer_minimum_3y = arcpy.SelectLayerByAttribute_management(in_layer_or_view=layer_minimum_1y_cal,
                                                               selection_type="NEW_SELECTION",
                                                               where_clause="OBJECTID = 3",
                                                               invert_where_clause="")
    layer_minimum_3y_cal = arcpy.CalculateField_management(in_table=layer_minimum_3y, field="POINT_Y",
                                                           expression="""floor($feature.POINT_Y/1000)""",
                                                           expression_type="ARCADE",
                                                           code_block="round((!POINT_X! /1000)+1,0)", field_type="TEXT",
                                                           enforce_domains="NO_ENFORCE_DOMAINS")[0]

    # x-low
    layer_minimum_x_low = arcpy.SelectLayerByAttribute_management(in_layer_or_view=layer_minimum_3y_cal,
                                                                  selection_type="NEW_SELECTION",
                                                                  where_clause="OBJECTID = 1",
                                                                  invert_where_clause="")
    layer_minimum_x_low_cal = arcpy.CalculateField_management(in_table=layer_minimum_x_low, field="x_low",
                                                              expression="!POINT_X!",
                                                              expression_type="PYTHON3",
                                                              code_block="",
                                                              field_type="TEXT",
                                                              enforce_domains="NO_ENFORCE_DOMAINS")[0]

    # x-high
    layer_minimum_x_high = arcpy.SelectLayerByAttribute_management(in_layer_or_view=layer_minimum_x_low_cal,
                                                                   selection_type="NEW_SELECTION",
                                                                   where_clause="OBJECTID = 3",
                                                                   invert_where_clause="")
    layer_minimum_x_high_cal = arcpy.CalculateField_management(in_table=layer_minimum_x_high, field="x_high",
                                                               expression="!POINT_X!",
                                                               expression_type="PYTHON3",
                                                               code_block="",
                                                               field_type="TEXT",
                                                               enforce_domains="NO_ENFORCE_DOMAINS")[0]

    # y-low
    layer_minimum_y_low = arcpy.SelectLayerByAttribute_management(in_layer_or_view=layer_minimum_x_high_cal,
                                                                  selection_type="NEW_SELECTION",
                                                                  where_clause="OBJECTID = 1",
                                                                  invert_where_clause="")
    layer_minimum_y_low_cal = arcpy.CalculateField_management(in_table=layer_minimum_y_low, field="y_low",
                                                              expression="!POINT_Y!",
                                                              expression_type="PYTHON3",
                                                              code_block="",
                                                              field_type="TEXT",
                                                              enforce_domains="NO_ENFORCE_DOMAINS")[0]

    # y-high
    layer_minimum_y_high = arcpy.SelectLayerByAttribute_management(in_layer_or_view=layer_minimum_y_low_cal,
                                                                   selection_type="NEW_SELECTION",
                                                                   where_clause="OBJECTID = 3",
                                                                   invert_where_clause="")
    layer_minimum_y_high_cal = arcpy.CalculateField_management(in_table=layer_minimum_y_high, field="y_high",
                                                               expression="!POINT_Y!",
                                                               expression_type="PYTHON3",
                                                               code_block="",
                                                               field_type="TEXT",
                                                               enforce_domains="NO_ENFORCE_DOMAINS")[0]

    # Clear selection
    layer_clear_selection = arcpy.SelectLayerByAttribute_management(in_layer_or_view=layer_minimum_y_high_cal,
                                                                    selection_type="CLEAR_SELECTION", where_clause="",
                                                                    invert_where_clause="")
    arcpy.SummarizeAttributes_gapro(input_layer=layer_clear_selection, out_table=summary_attr, fields=[],
                                    summary_fields=[["x_low", "SUM"], ["x_high", "SUM"], ["y_low", "SUM"],
                                                    ["y_high", "SUM"], ["expl_num", "MEAN"]], time_step_interval="",
                                    time_step_repeat="", time_step_reference="")

    # Join Field
    join_field = arcpy.JoinField_management(in_data=ezg_by_erospot, in_field="expl_num", join_table=summary_attr,
                                            join_field="MEAN_expl_num",
                                            fields=["SUM_x_low", "SUM_x_high", "SUM_y_low", "SUM_y_high"])[0]

    # Selection
    ezg_layer = arcpy.SelectLayerByAttribute_management(in_layer_or_view=join_field, selection_type="NEW_SELECTION",
                                                        where_clause=f"expl_num = " + str(x), invert_where_clause="")

    # Calculation
    x_low_erospot = arcpy.CalculateField_management(in_table=ezg_layer, field="x_low", expression="!SUM_x_low!",
                                                    expression_type="PYTHON3", code_block="", field_type="TEXT",
                                                    enforce_domains="NO_ENFORCE_DOMAINS")[0]
    x_high_erospot = arcpy.CalculateField_management(in_table=x_low_erospot, field="x_high", expression="!SUM_x_high!",
                                                     expression_type="PYTHON3", code_block="", field_type="TEXT",
                                                     enforce_domains="NO_ENFORCE_DOMAINS")[0]
    y_low_erospot = arcpy.CalculateField_management(in_table=x_high_erospot, field="y_low", expression="!SUM_y_low!",
                                                    expression_type="PYTHON3", code_block="", field_type="TEXT",
                                                    enforce_domains="NO_ENFORCE_DOMAINS")[0]
    y_high_erospot = arcpy.CalculateField_management(in_table=y_low_erospot, field="y_high", expression="!SUM_y_high!",
                                                     expression_type="PYTHON3", code_block="", field_type="TEXT",
                                                     enforce_domains="NO_ENFORCE_DOMAINS")[0]
    print(x_high_erospot)
    print(x_low_erospot)
    print(y_high_erospot)
    print(y_low_erospot)
    # Clear Selection
    ezg_layer_final = arcpy.SelectLayerByAttribute_management(in_layer_or_view=y_high_erospot,
                                                              selection_type="CLEAR_SELECTION", where_clause="",
                                                              invert_where_clause="")

    # Deletion
    Delete_succeeded = arcpy.Delete_management(in_data=[summary_attr, erospot_minimum, vertice_minimum], data_type="")[
       0]
    ezg_by_erospot_last = arcpy.DeleteField_management(in_table=y_high_erospot,
                                                      drop_field=["SUM_x_low", "SUM_x_high", "SUM_y_low",
                                                                 "SUM_y_high"], method="DELETE_FIELDS")[0]
