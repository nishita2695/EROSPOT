# author:nishita
import arcpy

arcpy.env.overwriteOutput = True


def streams_atkis(selected_watershed, x, UserPath, MainPathGDB):
    print("Model Streams_ATKIS")
    gew01_shp = UserPath + "/ATKIS/gew01_f.shp"
    gew01_shp_l = UserPath + "/ATKIS/gew01_l.shp"
    gew01_l_Clip = MainPathGDB + "/gew01_Clip"
    gew01_Clip_Buffer1 = MainPathGDB + "/gew_01_Clip_buffer1"
    gew01_Clip_Buffer2 = MainPathGDB + "/gew_01_Clip_buffer2"
    gew01_f_Clip_ws = MainPathGDB + "/gew01_f_Clip_ws_" + str(x)
    OutputFeatureClass = MainPathGDB + "/gew01_l_Clip_Buffer1_Union"
    gew_ws_shape = MainPathGDB + "/gew_ws_shape"
    gew_ws_tif = UserPath + "/InputDataInvest/testing/ws_" + str(x) + "/gew_" + str(x) + ".tif"
    arcpy.Clip_analysis(in_features=gew01_shp_l, clip_features=selected_watershed, out_feature_class=gew01_l_Clip,
                        cluster_tolerance="")
    gew01_Clip_Layer = arcpy.SelectLayerByAttribute_management(in_layer_or_view=gew01_l_Clip,
                                                               selection_type="NEW_SELECTION",
                                                               where_clause="HDU_X = 0 And BRG = 3",
                                                               invert_where_clause="")

    arcpy.Buffer_analysis(in_features=gew01_Clip_Layer, out_feature_class=gew01_Clip_Buffer1,
                          buffer_distance_or_field="1 Meter", line_side="FULL", line_end_type="ROUND",
                          dissolve_option="NONE", dissolve_field=[], method="PLANAR")
    gew01_Clip_Layer2 = arcpy.SelectLayerByAttribute_management(in_layer_or_view=gew01_l_Clip,
                                                                selection_type="NEW_SELECTION",
                                                                where_clause="BRG = 6 And HDU_X= 0",
                                                                invert_where_clause="")
    arcpy.Buffer_analysis(in_features=gew01_Clip_Layer2, out_feature_class=gew01_Clip_Buffer2,
                          buffer_distance_or_field="2.5 Meters", line_side="FULL", line_end_type="ROUND",
                          dissolve_option="NONE", dissolve_field=[], method="PLANAR")
    arcpy.Clip_analysis(in_features=gew01_shp, clip_features=selected_watershed, out_feature_class=gew01_f_Clip_ws,
                        cluster_tolerance="")
    gew01_Clip_Layer_AddField = arcpy.AddField_management(in_table=gew01_f_Clip_ws, field_name="wb_gew_f",
                                                          field_type="SHORT", field_precision=None, field_scale=None,
                                                          field_length=None, field_alias="",
                                                          field_is_nullable="NULLABLE",
                                                          field_is_required="NON_REQUIRED", field_domain="")[0]
    gew01_Clip_Layer_CalField = arcpy.CalculateField_management(in_table=gew01_Clip_Layer_AddField, field="wb_gew_f",
                                                                expression="1", expression_type="PYTHON3",
                                                                code_block="", field_type="TEXT",
                                                                enforce_domains="NO_ENFORCE_DOMAINS")[0]
    gew01_Clip_Buffer1_AddField = arcpy.AddField_management(in_table=gew01_Clip_Buffer1, field_name="wb_3_gew_l",
                                                            field_type="SHORT", field_precision=None, field_scale=None,
                                                            field_length=None, field_alias=None,
                                                            field_is_nullable="NULLABLE",
                                                            field_is_required="NON_REQUIRED", field_domain="")[0]
    gew01_Clip_Buffer1_CalField = \
        arcpy.CalculateField_management(in_table=gew01_Clip_Buffer1_AddField, field="wb_3_gew_l", expression="1",
                                        expression_type="PYTHON3", code_block="", field_type="TEXT",
                                        enforce_domains="NO_ENFORCE_DOMAINS")[0]
    gew01_Clip_Buffer2_AddField = \
        arcpy.AddField_management(in_table=gew01_Clip_Buffer2, field_name="wb_6_gew_l", field_type="SHORT",
                                  field_precision=None, field_scale=None, field_length=None, field_alias="",
                                  field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")[0]
    gew01_Clip_Buffer2_CalField = \
        arcpy.CalculateField_management(in_table=gew01_Clip_Buffer2_AddField, field="wb_6_gew_l", expression="1",
                                        expression_type="PYTHON3", code_block="", field_type="TEXT",
                                        enforce_domains="NO_ENFORCE_DOMAINS")[0]

    # UNION
    arcpy.Union_analysis(in_features=[[gew01_Clip_Buffer1_CalField, ""], [gew01_Clip_Buffer2_CalField, ""]],
                         out_feature_class=OutputFeatureClass, join_attributes="ALL", cluster_tolerance="", gaps="GAPS")
    arcpy.Union_analysis(
        in_features=[[gew01_Clip_Layer_CalField, ""], [OutputFeatureClass, ""], [selected_watershed, ""]],
        out_feature_class=gew_ws_shape, join_attributes="NO_FID", cluster_tolerance="", gaps="GAPS")

    gew_ws_shape2 = \
        arcpy.AddField_management(in_table=gew_ws_shape, field_name="waterbody", field_type="DOUBLE",
                                  field_precision=None,
                                  field_scale=None, field_length=None, field_alias="", field_is_nullable="NULLABLE",
                                  field_is_required="NON_REQUIRED", field_domain="")[0]
    gew_ws_shape_layer1 = arcpy.SelectLayerByAttribute_management(in_layer_or_view=gew_ws_shape2,
                                                                  selection_type="NEW_SELECTION",
                                                                  where_clause="wb_gew_f = 1 Or wb_3_gew_l = 1 Or "
                                                                               "wb_6_gew_l = 1",
                                                                  invert_where_clause="")
    gew_ws_shape_layer1_calfield = \
        arcpy.CalculateField_management(in_table=gew_ws_shape_layer1, field="waterbody", expression="1",
                                        expression_type="PYTHON3", code_block="", field_type="TEXT",
                                        enforce_domains="NO_ENFORCE_DOMAINS")[0]
    gew_ws_shape_layer2 = arcpy.SelectLayerByAttribute_management(in_layer_or_view=gew_ws_shape_layer1_calfield,
                                                                  selection_type="NEW_SELECTION",
                                                                  where_clause="wb_3_gew_l <> 1 And wb_6_gew_l <> 1 "
                                                                               "And wb_gew_f <> 1",
                                                                  invert_where_clause="")
    gew_ws_shape_layer2_calfield = \
        arcpy.CalculateField_management(in_table=gew_ws_shape_layer2, field="waterbody", expression="0",
                                        expression_type="PYTHON3", code_block="", field_type="TEXT",
                                        enforce_domains="NO_ENFORCE_DOMAINS")[0]
    gew_ws_shape_layer3 = arcpy.SelectLayerByAttribute_management(in_layer_or_view=gew_ws_shape_layer2_calfield,
                                                                  selection_type="NEW_SELECTION",
                                                                  where_clause="waterbody = 1 Or waterbody = 0",
                                                                  invert_where_clause="")
    arcpy.PolygonToRaster_conversion(in_features=gew_ws_shape_layer3, value_field="waterbody",
                                     out_rasterdataset=gew_ws_tif, cell_assignment="CELL_CENTER",
                                     priority_field="waterbody", cellsize="0.5", build_rat="BUILD")
    DeleteSucceeded = \
        arcpy.Delete_management(
            in_data=[gew01_Clip_Buffer1, gew01_Clip_Buffer2, gew01_Clip_Layer_CalField, gew01_l_Clip],
            data_type="")[0]
