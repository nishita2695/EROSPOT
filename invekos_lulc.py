#  author:nishita
import arcpy

# Allowing overwriting outputs on reruns
arcpy.env.overwriteOutput = True


def DataExists_mb(in_data, data_type):
    try:
        arcpy.Describe(in_data, data_type)
        return True
    except ValueError:
        return False


# Function called from combined model code
def add_aum_code():
    print("no aum code")


def add_aum_beschr():
    print("no aum beschr")


def add_aum_beschreibu():
    print("no_aum_beschreibu")


def invekos_lulc(selected_watershed, x, UserPath, MainPathGDB):
    # Error check
    print("Evaluating using InVeKoS data.....")
    flag = "False"

    # Lists for all the intermediate outputs
    year = []
    InvekosSHP = []
    InvekosOutput = []
    InvekosDisOutput = []
    InvekosYearData = []
    invekos_output_Dis2 = []
    invekos_output_Dis3 = []
    invekos_output_Dis4 = []
    invekos_output_Dis5 = []
    invekos_output_Dis6 = []
    invekos_union_buffer = []
    invekos_union_buffer1 = []
    yearList = []
    Missing_Fields_New_Regulations = ["aum_code", "aum_beschr", "beschreibu"]


    # Path specification
    invekos_union_nobuffer_py_ws = MainPathGDB + "/invekos_union_py_nb_ws_" + str(x)
    invekos_union_buffer1_py_ws = MainPathGDB + "/invekos_union_py_b1_ws_" + str(x)
    invekos_union_final_py_ws = MainPathGDB + "/invekos_union_py_trial_ws_" + str(x)
    invekos_union_py_ws = MainPathGDB + "/invekos_union_py_FINAL_ws_" + str(x)
    invekos_union_totransfere = MainPathGDB + "/invekos_union_totransfer"
    invekos_final = MainPathGDB + "/invekos_union_transfer_final_1"

    # NOTE: str(y) or str(x) is converting the indexes 0-4 to string,
    # for concatenation of int to string is not possible without a type conversion
    # for an index y starting from 15 and ending at 19 (20 is excluded in python lists)
    for y in range(15, 22):
        # In the list year, add 15-21 at respective
        # indexes starting from 0 and ending at 6 (as 15-21 has 7 values and lists always start from 0
        year.append(y)
        # To the list yearList, add the following : invekos_15_shp_final for 2015 and so on
        yearList.append("invekos_" + str(y) + "_shp_final")
        # To the lists InvekosSHP add the path below, customized for each year
        InvekosSHP.append(UserPath + "/InVeKoS/Nutzung_Aum_Bayern_20" + str(y) + "/invekos_by_" + str(y) + ".shp")
        InvekosOutput.append(MainPathGDB + "/invekos_" + str(y) + "_clip_ws_" + str(x))
        InvekosDisOutput.append(MainPathGDB + "/invekos_" + str(y) + "_clip_Dis_ws_" + str(x))
        # Throws error if we do not initialize all values of all lists to null
        InvekosYearData.append("null")
        invekos_output_Dis2.append("null")
        invekos_output_Dis3.append("null")
        invekos_output_Dis4.append("null")
        invekos_output_Dis5.append("null")
        invekos_output_Dis6.append("null")
        invekos_union_buffer1.append("null")
        invekos_union_buffer.append("null")

    # Run checks
    print(InvekosOutput)
    print(year)
    print(yearList)
    print(InvekosSHP)
    print(InvekosDisOutput)

    # CODE BLOCK for years from 2015 to 2021
    # IN_Y is nothing but an index like x,y, signifying Inside Years loop. So for every year, this loop will run
    for IN_Y in range(0, 7):
        print("IN_Y FOR:" + str(IN_Y))
        print("IN YEAR: 20" + str(year[IN_Y]))
        ws = "ws_" + str(x)
        with arcpy.EnvManager(extent="DEFAULT",
                              outputCoordinateSystem=
                              'PROJCS["ETRS_1989_UTM_Zone_32N", \
                              GEOGCS["GCS_ETRS_1989", \
                              DATUM["D_ETRS_1989", \
                              SPHEROID["GRS_1980",6378137.0,298.257222101]], \
                              PRIMEM["Greenwich",0.0], \
                              UNIT["Degree",0.0174532925199433]], \
                              PROJECTION["Transverse_Mercator"], \
                              PARAMETER["False_Easting",500000.0], \
                              PARAMETER["False_Northing",0.0], \
                              PARAMETER["Central_Meridian",9.0], \
                              PARAMETER["Scale_Factor",0.9996], \
                              PARAMETER["Latitude_Of_Origin",0.0], \
                              UNIT["Meter",1.0]]'):
            arcpy.Clip_analysis(in_features=InvekosSHP[IN_Y], clip_features=selected_watershed,
                                out_feature_class=InvekosOutput[IN_Y],
                                cluster_tolerance="")
        yearList[IN_Y] = \
            arcpy.DeleteIdentical_management(in_dataset=InvekosOutput[IN_Y], fields=["Shape"], xy_tolerance="",
                                             z_tolerance=0)[
                0]
        # add aum code if missing, set value to 0
        Check_Missing_attributes = set(Missing_Fields_New_Regulations)
        listFieldsYear = ["{0}".format(x.name) for x in arcpy.ListFields(yearList[IN_Y])]
        for attribute in Missing_Fields_New_Regulations:
            if attribute in listFieldsYear:
                Check_Missing_attributes.remove(attribute)
            else:
                if attribute == "aum_code":
                    add_aum_code()
                    yearList[IN_Y] = arcpy.AddField_management(in_table=yearList[IN_Y], field_name=f"aum_code",
                                                               field_type="TEXT", field_precision=None,
                                                               field_scale=None,
                                                               field_length=None,
                                                               field_alias=f"aum_code", field_is_nullable="NULLABLE",
                                                               field_is_required="NON_REQUIRED", field_domain="")[0]
                    yearList[IN_Y] = arcpy.CalculateField_management(in_table=yearList[IN_Y],
                                                                     field=f"aum_code",
                                                                     expression="\"0\"", expression_type="PYTHON3",
                                                                     code_block="",
                                                                     field_type="TEXT",
                                                                     enforce_domains="NO_ENFORCE_DOMAINS")[0]
                    print("AUM CODE ADDED")
                elif attribute == "aum_beschr":
                    add_aum_beschr()
                    yearList[IN_Y] = arcpy.AddField_management(in_table=yearList[IN_Y], field_name=f"aum_beschr",
                                                               field_type="TEXT", field_precision=None,
                                                               field_scale=None,
                                                               field_length=None,
                                                               field_alias=f"aum_beschr", field_is_nullable="NULLABLE",
                                                               field_is_required="NON_REQUIRED", field_domain="")[0]
                    yearList[IN_Y] = arcpy.CalculateField_management(in_table=yearList[IN_Y],
                                                                     field=f"aum_beschr",
                                                                     expression="\"0\"", expression_type="PYTHON3",
                                                                     code_block="",
                                                                     field_type="TEXT",
                                                                     enforce_domains="NO_ENFORCE_DOMAINS")[0]
                    print("aum_beschr ADDED")
                elif attribute == "beschreibu":
                    add_aum_beschreibu()
                    yearList[IN_Y] = arcpy.AddField_management(in_table=yearList[IN_Y], field_name=f"beschreibu",
                                                               field_type="TEXT", field_precision=None,
                                                               field_scale=None,
                                                               field_length=None,
                                                               field_alias=f"beschreibu", field_is_nullable="NULLABLE",
                                                               field_is_required="NON_REQUIRED", field_domain="")[0]
                    yearList[IN_Y] = arcpy.CalculateField_management(in_table=yearList[IN_Y],
                                                                     field=f"beschreibu",
                                                                     expression="\"0\"", expression_type="PYTHON3",
                                                                     code_block="",
                                                                     field_type="TEXT",
                                                                     enforce_domains="NO_ENFORCE_DOMAINS")[0]
                    print("beschreibu ADDED")

        if not Check_Missing_attributes:
            print("all specified attributes exist in layer")

        arcpy.Dissolve_management(in_features=yearList[IN_Y], out_feature_class=InvekosDisOutput[IN_Y],
                                  dissolve_field=["nutz_code", "beschreibu", "aum_code", "aum_beschr"],  # ,
                                  statistics_fields=[], multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
        InvekosYearData[IN_Y] = arcpy.AlterField_management(in_table=InvekosDisOutput[IN_Y], field="beschreibu",
                                                            new_field_name=f"besch_" + str(year[IN_Y]),
                                                            new_field_alias=f"besch_" + str(year[IN_Y]),
                                                            field_type="TEXT",
                                                            field_is_nullable="NULLABLE",
                                                            clear_field_alias="DO_NOT_CLEAR")[0]

        listFields = arcpy.ListFields(InvekosYearData[IN_Y])
        for x in listFields:
            print("{0}".format(x.name))
            if x.name == "aum_code":
                flag = "True"
                break

            else:
                flag = "False"
        print("Out of inner loop, into outer")
        if flag == "True":
            print("FLAG set to True")
            invekos_output_Dis2[IN_Y] = arcpy.AlterField_management(in_table=InvekosYearData[IN_Y], field="aum_code",
                                                                    new_field_name=f"aum_code_" + str(year[IN_Y]),
                                                                    new_field_alias=f"aum_code_" + str(year[IN_Y]),
                                                                    field_type="TEXT",
                                                                    field_is_nullable="NULLABLE",
                                                                    clear_field_alias="DO_NOT_CLEAR")[0]
            invekos_output_Dis3[IN_Y] = \
                arcpy.AlterField_management(in_table=invekos_output_Dis2[IN_Y], field="nutz_code",
                                            new_field_name=f"nu_code_" + str(year[IN_Y]),
                                            new_field_alias=f"nu_code_" + str(year[IN_Y]),
                                            field_type="TEXT", field_length=3,
                                            field_is_nullable="NULLABLE",
                                            clear_field_alias="DO_NOT_CLEAR")[0]
        if flag == "False":
            print("FLAG set to False")
            invekos_output_Dis4[IN_Y] = \
                arcpy.AddField_management(in_table=InvekosYearData[IN_Y], field_name=f"aum_code_" + str(year[IN_Y]),
                                          field_type="TEXT", field_precision=None, field_scale=None, field_length=None,
                                          field_alias=f"aum_code_" + str(year[IN_Y]), field_is_nullable="NULLABLE",
                                          field_is_required="NON_REQUIRED", field_domain="")[0]
            invekos_output_Dis5[IN_Y] = \
                arcpy.CalculateField_management(in_table=invekos_output_Dis4[IN_Y],
                                                field=f"aum_code_" + InvekosYearData[IN_Y],
                                                expression="\"0\"", expression_type="PYTHON3", code_block="",
                                                field_type="TEXT",
                                                enforce_domains="NO_ENFORCE_DOMAINS")[0]
            invekos_output_Dis6[IN_Y] = \
                arcpy.AlterField_management(in_table=invekos_output_Dis5[IN_Y], field="nutz_code",
                                            new_field_name=f"nutz_code_" + str(year[IN_Y]),
                                            new_field_alias=f"nu_code_" + str(year[IN_Y]),
                                            field_type="",
                                            field_is_nullable="NON_NULLABLE",
                                            clear_field_alias="DO_NOT_CLEAR")[0]
        if flag == "True":
            print("FLAG set to True")
            InvekosOutput[IN_Y] = invekos_output_Dis3[IN_Y]
            print(InvekosOutput[IN_Y])
        else:
            InvekosOutput[IN_Y] = invekos_output_Dis6[IN_Y]
            print("FLAG set to False")

    # UNION

    arcpy.Union_analysis(
        in_features=[[InvekosOutput[6], ""], [InvekosOutput[5], ""], [InvekosOutput[4], ""], [InvekosOutput[3], ""],
                     [InvekosOutput[2], ""],
                     [InvekosOutput[1], ""], [InvekosOutput[0], ""]],
        out_feature_class=invekos_union_nobuffer_py_ws, join_attributes="NO_FID", cluster_tolerance="", gaps="GAPS")
    Delete_succeeded = arcpy.Delete_management(
        in_data=[InvekosOutput, yearList], data_type="")[0]
    arcpy.Buffer_analysis(in_features=invekos_union_nobuffer_py_ws, out_feature_class=invekos_union_buffer1_py_ws,
                          buffer_distance_or_field="-1.4 Meters", line_side="FULL", line_end_type="ROUND",
                          dissolve_option="NONE",
                          dissolve_field=[], method="PLANAR")
    arcpy.Buffer_analysis(in_features=invekos_union_buffer1_py_ws, out_feature_class=invekos_union_final_py_ws,
                          buffer_distance_or_field="1.4 Meters", line_side="FULL", line_end_type="ROUND",
                          dissolve_option="NONE", dissolve_field=[], method="PLANAR")
    invekos_union_buffer_field = \
        arcpy.AddField_management(in_table=invekos_union_final_py_ws, field_name="dummy_aum", field_type="TEXT",
                                  field_precision=None, field_length=None, field_scale=None, field_alias="dummy_aum",
                                  field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")[0]
    invekos_union_buffer[-1] = \
        arcpy.CalculateField_management(in_table=invekos_union_buffer_field, field="dummy_aum", expression="\"XXX\"",
                                        expression_type="PYTHON3", code_block="",
                                        field_type="TEXT",
                                        enforce_domains="NO_ENFORCE_DOMAINS")[0]
    for IN_Y in range(0, 7):
        invekos_union_buffer1[IN_Y] = arcpy.SelectLayerByAttribute_management(
            in_layer_or_view=invekos_union_buffer[IN_Y - 1], selection_type="NEW_SELECTION",
            where_clause=f"aum_code_" + str(year[IN_Y]) + " <> 'A33' And aum_code_" + str(
                year[IN_Y]) + " <> 'B37' And aum_code_" + str(year[IN_Y]) + " <> 'B38'", invert_where_clause="")
        invekos_union_buffer[IN_Y] = arcpy.CalculateField_management(in_table=invekos_union_buffer1[IN_Y],
                                                                     field=f"dummy_aum_" + str(year[IN_Y]),
                                                                     expression="!dummy_aum!",
                                                                     expression_type="PYTHON3", code_block="",
                                                                     field_type="TEXT",
                                                                     enforce_domains="NO_ENFORCE_DOMAINS")[0]

        arcpy.Clip_analysis(in_features=invekos_union_buffer[IN_Y], clip_features=selected_watershed,
                            out_feature_class=invekos_union_py_ws, cluster_tolerance="")

    Delete_final = \
        arcpy.Delete_management(in_data=[invekos_union_final_py_ws, invekos_union_buffer1_py_ws,
                                         invekos_union_nobuffer_py_ws],
                                data_type="")[0]


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
    invekos_lulc(selected_watershed, 4, UserPath, MainPathGDB)
    # invekos_atkis_combined(selected_watershed, 4, UserPath, MainPathGDB)
    print("Done")
