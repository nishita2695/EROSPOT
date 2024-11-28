"""
Authors: Nishita Thakur, Marvin Melzer

Credit authorship contribution statement:
Nishita Thakur: Software (lead). Marvin Melzer: Conceptualization (lead);
Methodology (lead); Data duration (lead); Funding acquisition (lead); Software (supporting).

Project: EROSPOT (DAKIS)

Last Update: 2024-11-26

Description: This script is used to combine the invekos data to the atkis data to calculate the summable c-values
as per Auerswald et al (2019) guidelines, and also to generate the biophysical table which is used as an input for
InVeST and also adjust the attributes as per the general description provided in the guidebook .

License: Please refer to the document titled 'License.docx' in the repository

"""
import arcpy

arcpy.env.overwriteOutput = True
flag = 'false'


def invekos_atkis_combined(selected_watershed, x, UserPath, MainPathGDB):
    # Declarations
    invekos_union_py_ws = MainPathGDB + "/invekos_union_py_FINALUNION_ws_" + str(x)
    atkis_union_py_ws = MainPathGDB + "/atkis_union_py_ws_" + str(x)
    invekos_atkis_union = MainPathGDB + "/UNION_atkis_invekos_ws_" + str(x)
    sum_c_new = MainPathGDB + "/sum_c_new"
    OutLayer = "union_invekos_atkis_ws_" + str(x)

    mapping = "description \"description\" true true false 0 Text 0 0,First,#," \
              "D:/Users/Thakur/ErospotWorkspace/EROSPOT.gdb/union_invekos_atkis_ws_" + str(
        x) + ",description,0,0;usle_c \"usle_c\" true true false 0 Double 0 0,First,#," \
             "D:/Users/Thakur/ErospotWorkspace/EROSPOT.gdb/union_invekos_atkis_ws_" + str(
        x) + ",usle_c,-1,-1;usle_p \"usle_p\" true true false 0 Double 0 0,First,#," \
             "D:/Users/Thakur/ErospotWorkspace/EROSPOT.gdb/union_invekos_atkis_ws_" + str(
        x) + ",usle_p,-1,-1;lucode \"lucode\" true true false 0 Long 0 0,First,#," \
             "D:/Users/Thakur/ErospotWorkspace/EROSPOT.gdb/union_invekos_atkis_ws_" + str(
        x) + ",lucode,-1,-1"
    watersheds = UserPath + "/InputDataInvest/testing/ws_" + str(x)
    lc_ws_id = watersheds + "/lc_ws_" + str(x) + ".tif"
    year = []
    fieldList_union_add = []
    fieldList_union_cal = []
    union_inv_atk_CalLucode = []
    sum_cal = []
    sum_c_join = []
    sum_c_cal = []
    sum_c_del = []
    bio = "biophysical_table_ws_" + str(x) + ".csv"
    # Set the years to combine - range of years
    crop_years = "7"

    # For years 2015-2021 initialize lists
    for y in range(15, 22):
        year.append(y)
        fieldList_union_add.append("null")
        fieldList_union_cal.append("null")
        union_inv_atk_CalLucode.append("null")
        sum_cal.append("null")
        sum_c_join.append("null")
        sum_c_cal.append("null")
        sum_c_del.append("null")
        # set range in the ""
        # switch orders
    # arcpy.env.outputCoordinateSystem=arcpy.SpatialReference("WGS 1989 UTM Zone 32N")
    # with arcpy.EnvManager(outputCoordinateSystem="PROJCS[@ETRS_1989_UTM_Zone_32N,GEOGCS["GCS_ETRS_1989",DATUM["D_ETRS_1989",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",9.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]")

    # Union of invekos and atkis
    arcpy.Union_analysis(in_features=[[invekos_union_py_ws, "1"], [atkis_union_py_ws, "2"]],
                         out_feature_class=invekos_atkis_union, join_attributes="NO_FID", cluster_tolerance="",
                         gaps="GAPS")

    # Add field description
    union_inv_atk_2 = \
        arcpy.AddField_management(in_table=invekos_atkis_union, field_name="description", field_type="TEXT",
                                  field_precision=None, field_scale=None, field_length=None, field_alias="description",
                                  field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")[0]

    # Add field usle_c
    union_inv_atk_3 = arcpy.AddField_management(in_table=union_inv_atk_2, field_name="usle_c", field_type="FLOAT",
                                                field_precision=None, field_scale=None, field_length=None,
                                                field_alias="usle_c", field_is_nullable="NULLABLE",
                                                field_is_required="NON_REQUIRED", field_domain="")

    # Add field usle_p
    union_inv_atk_4 = arcpy.AddField_management(in_table=union_inv_atk_3, field_name="usle_p", field_type="FLOAT",
                                                field_precision=None, field_scale=None, field_length=None,
                                                field_alias="usle_p", field_is_nullable="NULLABLE",
                                                field_is_required="NON_REQUIRED", field_domain="")

    # Add 1 for all values of usle_p
    union_inv_atk_CalP = \
        arcpy.CalculateField_management(in_table=union_inv_atk_4, field="usle_p", expression="1",
                                        expression_type="PYTHON3",
                                        code_block="", field_type="TEXT", enforce_domains="NO_ENFORCE_DOMAINS")[0]

    # Add field lucode
    union_inv_atk_Lucode = \
        arcpy.AddField_management(in_table=union_inv_atk_CalP, field_name="lucode", field_type="FLOAT",
                                  field_precision=None, field_scale=None, field_length=None, field_alias="",
                                  field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")[0]
    # Add values for field description
    union_inv_atk_CalDesc = arcpy.CalculateField_management(in_table=union_inv_atk_Lucode, field="description",
                                                            expression="!besch_15!+\"_\"+!besch_19!",
                                                            expression_type="PYTHON3",
                                                            code_block="", field_type="TEXT",
                                                            enforce_domains="NO_ENFORCE_DOMAINS")[0]
    # Calculate lucode = Object ID
    union_inv_atk_CalLucode[-1] = arcpy.CalculateField_management(in_table=union_inv_atk_CalDesc, field="lucode",
                                                                  expression="!OBJECTID!",
                                                                  expression_type="PYTHON3",
                                                                  code_block="", field_type="TEXT",
                                                                  enforce_domains="NO_ENFORCE_DOMAINS")[0]
    # Loop years
    print("Combining InVeKoS and ATKIS data...")
    for index in range(0, 7):
        # Add field combi_code_year
        union_inv_atk_CalLucode[index] = \
            arcpy.AddField_management(in_table=union_inv_atk_CalLucode[index - 1],
                                      field_name=f"combi_code_" + str(year[index]),
                                      field_type="TEXT", field_precision=None, field_scale=None, field_length=None,
                                      field_alias=f"combi_code_" + str(year[index]), field_is_nullable="NULLABLE",
                                      field_is_required="NON_REQUIRED", field_domain="")[0]
        # Calculate combi_code = nutz_code + aum_code
        fieldList_union_cal[index] = arcpy.CalculateField_management(in_table=union_inv_atk_CalLucode[index],
                                                                     field=f"combi_code_" + str(year[index]),
                                                                     expression=f"!nu_code_" + str(
                                                                         year[index]) + "! + !aum_code_" + str(
                                                                         year[index]) + "!",
                                                                     expression_type="PYTHON3",
                                                                     code_block="", field_type="TEXT",
                                                                     enforce_domains="NO_ENFORCE_DOMAINS")[0]
    # Add field combi_code_atkis, outside loop
    union_inv_atk_combi_atkis = \
        arcpy.AddField_management(in_table=fieldList_union_cal[6], field_name="combi_code_atkis", field_type="TEXT",
                                  field_precision=None, field_scale=None, field_length=None, field_alias="",
                                  field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")[0]
    # Calculate combi_code_atkis
    sum_cal[-1] = arcpy.CalculateField_management(in_table=union_inv_atk_combi_atkis,
                                                  field="combi_code_atkis",
                                                  expression="!OA_veg03_f! + !OA_ver03_f! + "
                                                             "!OA_sie02_f!+ "
                                                             "!OA_gew01_f!+!OA_veg02_f!+!OA_veg01_f"
                                                             "!+!OA_ver01_f!+!VEG_01!+!VEG_02!",
                                                  expression_type="PYTHON3", code_block="",
                                                  field_type="TEXT",
                                                  enforce_domains="NO_ENFORCE_DOMAINS")[0]
    # Loop
    for index in range(0,7):
        # Add field sum_c_year
        sum_cal[index] = \
            arcpy.AddField_management(in_table=sum_cal[index - 1], field_name=f"sum_c_" + str(year[index]),
                                      field_type="DOUBLE", field_precision=None, field_scale=None,
                                      field_length=None, field_alias=f"sum_c_" + str(year[index]),
                                      field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED",
                                      field_domain="")[0]
    # Add field sum_c_atkis, outside loop
    sum_c_del[-1] = arcpy.AddField_management(in_table=sum_cal[6], field_name="sum_c_atkis",
                                              field_type="DOUBLE", field_precision=None, field_scale=None,
                                              field_length=None, field_alias="sum_c_atkis",
                                              field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED",
                                              field_domain="")[0]
    # Join field for sum_c_atkis
    sum_c_join_atkis = \
        arcpy.JoinField_management(in_data=sum_c_del[-1], in_field="combi_code_atkis",
                                   join_table=sum_c_new, join_field="combi_code", fields=["sum_c"])[0]
    # Calculate sum_c_atkis
    sum_c_cal_atkis = \
        arcpy.CalculateField_management(in_table=sum_c_join_atkis, field=f"sum_c_atkis",
                                        expression="!sum_c!", expression_type="PYTHON3", code_block="",
                                        field_type="TEXT", enforce_domains="NO_ENFORCE_DOMAINS")[0]
    del_success = arcpy.DeleteField_management(in_table=sum_c_cal_atkis, drop_field=["sum_c"], method="DELETE_FIELDS")[
        0]
    # Loop
    for index in range(0, 7):
        '''SECTION 1.6, User Guide'''
        # Join sum_c_new with current table based on combi_code_year
        sum_c_join[index] = \
            arcpy.JoinField_management(in_data=sum_c_del[index - 1], in_field=f"combi_code_" + str(year[index]),
                                       join_table=sum_c_new, join_field="combi_code", fields=["sum_c"])[
                0]
        # Calculate sum_c per year
        sum_c_cal[index] = \
            arcpy.CalculateField_management(in_table=sum_c_join[index], field=f"sum_c_" + str(year[index]),
                                            expression="!sum_c!", expression_type="PYTHON3", code_block="",
                                            field_type="TEXT", enforce_domains="NO_ENFORCE_DOMAINS")[0]
        # Check deletion
        sum_c_del[index] = \
            arcpy.DeleteField_management(in_table=sum_c_cal[index], drop_field=["sum_c"], method="DELETE_FIELDS")[0]

    # Calculate field usle_c
    usle_c_cal = arcpy.CalculateField_management(in_table=sum_c_del[6], field="usle_c",
                                                 expression=f"(!sum_c_15!+!sum_c_16!+!sum_c_17!+!sum_c_18!+!sum_c_19!"
                                                            f"+!sum_c_20!+!sum_c_21!)"
                                                            f"/7",
                                                 expression_type="PYTHON3", code_block="", field_type="TEXT",
                                                 enforce_domains="NO_ENFORCE_DOMAINS")[0]
    # Feature Layer with the usle_c calculations
    arcpy.MakeFeatureLayer_management(in_features=usle_c_cal, out_layer=OutLayer, where_clause="")

    # Selection usle_c is NULL
    union_inv_atk_Selection = arcpy.SelectLayerByAttribute_management(in_layer_or_view=OutLayer,
                                                                      selection_type="NEW_SELECTION",
                                                                      where_clause="usle_c IS NULL",
                                                                      invert_where_clause="")
    # usle_c = sum_c_atkis for NULL values
    cal_usle_c = \
        arcpy.CalculateField_management(in_table=union_inv_atk_Selection, field="usle_c", expression="!sum_c_atkis!",
                                        expression_type="PYTHON3", code_block="", field_type="TEXT",
                                        enforce_domains="NO_ENFORCE_DOMAINS")[0]
    # Replace values less than 0.001 by 0.004
    union_inv_atkis_selection1 = arcpy.SelectLayerByAttribute_management(in_layer_or_view=cal_usle_c,
                                                                         selection_type="NEW_SELECTION",
                                                                         where_clause="usle_c < 0.001",
                                                                         invert_where_clause="")
    union_inv_atkis_selection1_cal = arcpy.CalculateField_management(in_table=union_inv_atkis_selection1,
                                                                     field="usle_c", expression="0.004",
                                                                     expression_type="PYTHON3", code_block="",
                                                                     field_type="TEXT",
                                                                     enforce_domains="NO_ENFORCE_DOMAINS")[0]
    updated_layer_table_view = arcpy.SelectLayerByAttribute_management(in_layer_or_view=union_inv_atkis_selection1_cal,
                                                                       selection_type="CLEAR_SELECTION",
                                                                       where_clause="", invert_where_clause="")
    updated_layer_table_view = arcpy.SelectLayerByAttribute_management(in_layer_or_view=updated_layer_table_view,
                                                                       selection_type="NEW_SELECTION",
                                                                       where_clause="usle_c is NULL",
                                                                       invert_where_clause="")
    updated_layer_table_view = arcpy.CalculateField_management(in_table=updated_layer_table_view,
                                                               field="usle_c", expression="0.5",
                                                               expression_type="PYTHON3", code_block="",
                                                               field_type="TEXT",
                                                               enforce_domains="NO_ENFORCE_DOMAINS")[0]
    updated_layer_table_view = arcpy.SelectLayerByAttribute_management(in_layer_or_view=updated_layer_table_view,
                                                                       selection_type="CLEAR_SELECTION",
                                                                       where_clause="", invert_where_clause="")
    # Create excel biophysical table
    biophysical_table = arcpy.TableToTable_conversion(in_rows=updated_layer_table_view, out_path=watersheds,
                                                      out_name=bio, where_clause="", field_mapping=mapping,
                                                      config_keyword="")[0]
    # lucode raster
    arcpy.PolygonToRaster_conversion(in_features=updated_layer_table_view, value_field="lucode",
                                     out_rasterdataset=lc_ws_id, cell_assignment="CELL_CENTER", priority_field="NONE",
                                     cellsize="1", build_rat="BUILD")


def flag():
    if flag == 'True':
        return True
    else:
        return False


# This Part below has to be added to all seperated models if you want to run them, it is also part of the combined one.
if __name__ == '__main__':
    # Please change the path here
    # This Part below (two lines) has to be added to all seperated models if you want to run them, it is also part of the combined one.
    UserPath = "D:/Users/Thakur/ErospotWorkspace"
    MainPathGDB = "D:/Users/Thakur/ErospotWorkspace/EROSPOT.gdb"
    ezg_by_erospot = MainPathGDB + "/ezg_by_erospot"
    feature_layer = arcpy.MakeFeatureLayer_management(ezg_by_erospot, 'feature')
    selected_watershed = arcpy.SelectLayerByAttribute_management(
        in_layer_or_view=feature_layer,
        selection_type="NEW_SELECTION",
        where_clause="expl_num=4")
    invekos_atkis_combined(selected_watershed, 4, UserPath, MainPathGDB)
    # invekos_atkis_combined(selected_watershed, 4, UserPath, MainPathGDB)
    print("Done")
