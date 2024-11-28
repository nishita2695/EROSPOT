"""
Authors: Nishita Thakur, Marvin Melzer

Credit authorship contribution statement:
Nishita Thakur: Software (lead). Marvin Melzer: Conceptualization (lead);
Methodology (lead); Data duration (lead); Funding acquisition (lead); Software (supporting).

Project: EROSPOT (DAKIS)

Last Update: 2024-11-26

Description: This script is used to combine the invekos data to get the field boundaries,
and also adjust the attributes as per the general description provided in the guidebook for the years from 2015-2021

License: Please refer to the document titled 'License.docx' in the repository
"""
import arcpy

# Allowing overwriting outputs on reruns
arcpy.env.overwriteOutput = True


# This Part below has to be added to all seperated models if you want to run them, it is also part of the combined one.
def calculate_lu_ws(selected_watershed, x, UserPath, MainPathGDB):
    print("Calculating using InVeKoS Data 2015.....2021")
    invekos_union_nobuffer_py_ws = MainPathGDB + "/invekos_union_DEBUG_ws_" + str(x)
    invekos_union_buffer1_py_ws = MainPathGDB + "/invekos_union_py_b1_ws_" + str(x)
    invekos_union_final_py_ws = MainPathGDB + "/invekos_union_py_DEBUGBUFFER_ws_" + str(x)
    invekos_union_py_ws = MainPathGDB + "/invekos_union_py_FINALUNION_ws_" + str(x)
    invekos_2015 = UserPath + "/InVeKoS/Nutzung_Aum_Bayern_2015/invekos_by_15_p.shp"
    invekos_2016 = UserPath + "/InVeKoS/Nutzung_Aum_Bayern_2016/invekos_by_16_p.shp"
    invekos_2017 = UserPath + "/InVeKoS/Nutzung_Aum_Bayern_2017/invekos_by_17_p.shp"
    invekos_2018 = UserPath + "/InVeKoS/Nutzung_Aum_Bayern_2018/invekos_by_18_p.shp"
    invekos_2019 = UserPath + "/InVeKoS/Nutzung_Aum_Bayern_2019/invekos_by_19_p.shp"
    invekos_2020 = UserPath + "/InVeKoS/Nutzung_Aum_Bayern_2020/invekos_by_20_p.shp"
    invekos_2021 = UserPath + "/InVeKoS/Nutzung_Aum_Bayern_2021/invekos_by_21_p.shp"

    invekos_clip_15 = MainPathGDB + "/clip_invekos_15_debug"
    invekos_clip_16 = MainPathGDB + "/clip_invekos_16_debug"
    invekos_clip_17 = MainPathGDB + "/clip_invekos_17_debug"
    invekos_clip_18 = MainPathGDB + "/clip_invekos_18_debug"
    invekos_clip_19 = MainPathGDB + "/clip_invekos_19_debug"
    invekos_clip_20 = MainPathGDB + "/clip_invekos_20_debug"
    invekos_clip_21 = MainPathGDB + "/clip_invekos_21_debug"

    invekos_dissolve_15 = MainPathGDB + "/dissolve_invekos_15_debug"
    invekos_dissolve_16 = MainPathGDB + "/dissolve_invekos_16_debug"
    invekos_dissolve_17 = MainPathGDB + "/dissolve_invekos_17_debug"
    invekos_dissolve_18 = MainPathGDB + "/dissolve_invekos_18_debug"
    invekos_dissolve_19 = MainPathGDB + "/dissolve_invekos_19_debug"
    invekos_dissolve_20 = MainPathGDB + "/dissolve_invekos_20_debug"
    invekos_dissolve_21 = MainPathGDB + "/dissolve_invekos_21_debug"

    '''with arcpy.EnvManager(extent="DEFAULT",
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
                          UNIT["Meter",1.0]]'):'''
    arcpy.Clip_analysis(in_features=invekos_2015, clip_features=selected_watershed,
                        out_feature_class=invekos_clip_15,
                        cluster_tolerance="")
    '''with arcpy.EnvManager(extent="DEFAULT",
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
                          UNIT["Meter",1.0]]'):'''
    arcpy.Clip_analysis(in_features=invekos_2016, clip_features=selected_watershed,
                        out_feature_class=invekos_clip_16,
                        cluster_tolerance="")
    arcpy.Clip_analysis(in_features=invekos_2017, clip_features=selected_watershed,
                        out_feature_class=invekos_clip_17,
                        cluster_tolerance="")
    arcpy.Clip_analysis(in_features=invekos_2018, clip_features=selected_watershed,
                        out_feature_class=invekos_clip_18,
                        cluster_tolerance="")
    arcpy.Clip_analysis(in_features=invekos_2019, clip_features=selected_watershed,
                        out_feature_class=invekos_clip_19,
                        cluster_tolerance="")
    arcpy.Clip_analysis(in_features=invekos_2020, clip_features=selected_watershed,
                        out_feature_class=invekos_clip_20,
                        cluster_tolerance="")
    arcpy.Clip_analysis(in_features=invekos_2021, clip_features=selected_watershed,
                        out_feature_class=invekos_clip_21,
                        cluster_tolerance="")
    yearlist15 = arcpy.DeleteIdentical_management(in_dataset=invekos_clip_15, fields=["Shape"], xy_tolerance="",
                                                  z_tolerance=0)[
        0]
    yearlist16 = arcpy.DeleteIdentical_management(in_dataset=invekos_clip_16, fields=["Shape"], xy_tolerance="",
                                                  z_tolerance=0)[
        0]
    yearlist17 = arcpy.DeleteIdentical_management(in_dataset=invekos_clip_17, fields=["Shape"], xy_tolerance="",
                                                  z_tolerance=0)[
        0]
    yearlist18 = arcpy.DeleteIdentical_management(in_dataset=invekos_clip_18, fields=["Shape"], xy_tolerance="",
                                                  z_tolerance=0)[
        0]
    yearlist19 = arcpy.DeleteIdentical_management(in_dataset=invekos_clip_19, fields=["Shape"], xy_tolerance="",
                                                  z_tolerance=0)[
        0]
    yearlist20 = arcpy.DeleteIdentical_management(in_dataset=invekos_clip_20, fields=["Shape"], xy_tolerance="",
                                                  z_tolerance=0)[
        0]
    yearlist21 = arcpy.DeleteIdentical_management(in_dataset=invekos_clip_21, fields=["Shape"], xy_tolerance="",
                                                  z_tolerance=0)[
        0]

    yearList15 = \
        arcpy.AddField_management(in_table=yearlist15, field_name="dummy_aum_15",
                                  field_type="TEXT",
                                  field_precision=None, field_length=None, field_scale=None,
                                  field_alias="dummy_aum_15",
                                  field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")[
            0]
    yearList15 = \
        arcpy.CalculateField_management(in_table=yearlist15, field="dummy_aum_15",
                                        expression="\"XXX\"",
                                        expression_type="PYTHON3", code_block="",
                                        field_type="TEXT",
                                        enforce_domains="NO_ENFORCE_DOMAINS")[
            0]
    yearList16 = \
        arcpy.AddField_management(in_table=yearlist16, field_name="dummy_aum_16",
                                  field_type="TEXT",
                                  field_precision=None, field_length=None, field_scale=None,
                                  field_alias="dummy_aum_16",
                                  field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")[
            0]
    yearList16 = \
        arcpy.CalculateField_management(in_table=yearlist16, field="dummy_aum_16",
                                        expression="\"XXX\"",
                                        expression_type="PYTHON3", code_block="",
                                        field_type="TEXT",
                                        enforce_domains="NO_ENFORCE_DOMAINS")[
            0]
    yearList17 = \
        arcpy.AddField_management(in_table=yearlist17, field_name="dummy_aum_17",
                                  field_type="TEXT",
                                  field_precision=None, field_length=None, field_scale=None,
                                  field_alias="dummy_aum_17",
                                  field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")[
            0]
    yearList17 = \
        arcpy.CalculateField_management(in_table=yearlist17, field="dummy_aum_17",
                                        expression="\"XXX\"",
                                        expression_type="PYTHON3", code_block="",
                                        field_type="TEXT",
                                        enforce_domains="NO_ENFORCE_DOMAINS")[
            0]
    yearList18 = \
        arcpy.AddField_management(in_table=yearlist18, field_name="dummy_aum_18",
                                  field_type="TEXT",
                                  field_precision=None, field_length=None, field_scale=None,
                                  field_alias="dummy_aum_18",
                                  field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")[
            0]
    yearList18 = \
        arcpy.CalculateField_management(in_table=yearlist18, field="dummy_aum_18",
                                        expression="\"XXX\"",
                                        expression_type="PYTHON3", code_block="",
                                        field_type="TEXT",
                                        enforce_domains="NO_ENFORCE_DOMAINS")[
            0]
    yearList19 = \
        arcpy.AddField_management(in_table=yearlist19, field_name="dummy_aum_19",
                                  field_type="TEXT",
                                  field_precision=None, field_length=None, field_scale=None,
                                  field_alias="dummy_aum_19",
                                  field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")[
            0]
    yearList19 = \
        arcpy.CalculateField_management(in_table=yearlist19, field="dummy_aum_19",
                                        expression="\"XXX\"",
                                        expression_type="PYTHON3", code_block="",
                                        field_type="TEXT",
                                        enforce_domains="NO_ENFORCE_DOMAINS")[
            0]
    yearList20 = \
        arcpy.AddField_management(in_table=yearlist20, field_name="dummy_aum_20",
                                  field_type="TEXT",
                                  field_precision=None, field_length=None, field_scale=None,
                                  field_alias="dummy_aum_20",
                                  field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")[
            0]
    yearList20 = \
        arcpy.CalculateField_management(in_table=yearlist20, field="dummy_aum_20",
                                        expression="\"XXX\"",
                                        expression_type="PYTHON3", code_block="",
                                        field_type="TEXT",
                                        enforce_domains="NO_ENFORCE_DOMAINS")[
            0]
    yearList21 = \
        arcpy.AddField_management(in_table=yearlist21, field_name="dummy_aum_21",
                                  field_type="TEXT",
                                  field_precision=None, field_length=None, field_scale=None,
                                  field_alias="dummy_aum_21",
                                  field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")[
            0]
    yearList21 = \
        arcpy.CalculateField_management(in_table=yearlist21, field="dummy_aum_21",
                                        expression="\"XXX\"",
                                        expression_type="PYTHON3", code_block="",
                                        field_type="TEXT",
                                        enforce_domains="NO_ENFORCE_DOMAINS")[
            0]
    yearlist20 = arcpy.AddField_management(in_table=yearlist20, field_name=f"aum_code",
                                           field_type="TEXT", field_precision=None,
                                           field_scale=None,
                                           field_length=None,
                                           field_alias=f"aum_code", field_is_nullable="NULLABLE",
                                           field_is_required="NON_REQUIRED", field_domain="")[0]
    yearlist20 = arcpy.CalculateField_management(in_table=yearlist20,
                                                 field=f"aum_code",
                                                 expression="\"0\"", expression_type="PYTHON3",
                                                 code_block="",
                                                 field_type="TEXT",
                                                 enforce_domains="NO_ENFORCE_DOMAINS")[0]
    print("YEAR 2020: AUM_CODE missing -> AUM CODE ADDED")

    yearlist20 = arcpy.AddField_management(in_table=yearlist20, field_name=f"aum_beschr",
                                           field_type="TEXT", field_precision=None,
                                           field_scale=None,
                                           field_length=None,
                                           field_alias=f"aum_beschr", field_is_nullable="NULLABLE",
                                           field_is_required="NON_REQUIRED", field_domain="")[0]

    print("YEAR 2020: AUM BESCHR MISSING -> AUM BESCHR ADDED")
    yearlist20 = arcpy.AddField_management(in_table=yearlist20, field_name=f"beschreibu",
                                           field_type="TEXT", field_precision=None,
                                           field_scale=None,
                                           field_length=None,
                                           field_alias=f"beschreibu", field_is_nullable="NULLABLE",
                                           field_is_required="NON_REQUIRED", field_domain="")[0]

    print("YEAR 2020: bescreibu MISSING -> beschreibu ADDED")
    yearlist21 = arcpy.AddField_management(in_table=yearlist21, field_name=f"aum_code",
                                           field_type="TEXT", field_precision=None,
                                           field_scale=None,
                                           field_length=None,
                                           field_alias=f"aum_code", field_is_nullable="NULLABLE",
                                           field_is_required="NON_REQUIRED", field_domain="")[0]
    yearlist21 = arcpy.CalculateField_management(in_table=yearlist21,
                                                 field=f"aum_code",
                                                 expression="\"0\"", expression_type="PYTHON3",
                                                 code_block="",
                                                 field_type="TEXT",
                                                 enforce_domains="NO_ENFORCE_DOMAINS")[0]
    print("YEAR 2021: AUM_CODE MISSING -> AUM CODE ADDED")

    yearlist21 = arcpy.AddField_management(in_table=yearlist21, field_name=f"aum_beschr",
                                           field_type="TEXT", field_precision=None,
                                           field_scale=None,
                                           field_length=None,
                                           field_alias=f"aum_beschr", field_is_nullable="NULLABLE",
                                           field_is_required="NON_REQUIRED", field_domain="")[0]

    print("YEAR 2021: AUM BESCHR MISSING -> AUM BESCHR ADDED")
    yearlist21 = arcpy.AddField_management(in_table=yearlist21, field_name=f"beschreibu",
                                           field_type="TEXT", field_precision=None,
                                           field_scale=None,
                                           field_length=None,
                                           field_alias=f"beschreibu", field_is_nullable="NULLABLE",
                                           field_is_required="NON_REQUIRED", field_domain="")[0]

    print("YEAR 2021: beschreibu MISSING -> beschreibu ADDED")

    arcpy.Dissolve_management(in_features=yearlist15, out_feature_class=invekos_dissolve_15,
                              dissolve_field=["nutz_code", "beschreibu", "aum_code", "aum_beschr"],  # ,
                              statistics_fields=[], multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
    arcpy.Dissolve_management(in_features=yearlist16, out_feature_class=invekos_dissolve_16,
                              dissolve_field=["nutz_code", "beschreibu", "aum_code", "aum_beschr"],  # ,
                              statistics_fields=[], multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
    arcpy.Dissolve_management(in_features=yearlist17, out_feature_class=invekos_dissolve_17,
                              dissolve_field=["nutz_code", "beschreibu", "aum_code", "aum_beschr"],  # ,
                              statistics_fields=[], multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
    arcpy.Dissolve_management(in_features=yearlist18, out_feature_class=invekos_dissolve_18,
                              dissolve_field=["nutz_code", "beschreibu", "aum_code", "aum_beschr"],  # ,
                              statistics_fields=[], multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
    arcpy.Dissolve_management(in_features=yearlist19, out_feature_class=invekos_dissolve_19,
                              dissolve_field=["nutz_code", "beschreibu", "aum_code", "aum_beschr"],  # ,
                              statistics_fields=[], multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
    arcpy.Dissolve_management(in_features=yearlist20, out_feature_class=invekos_dissolve_20,
                              dissolve_field=["nutz_code", "beschreibu", "aum_code", "aum_beschr"],  # ,
                              statistics_fields=[], multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
    arcpy.Dissolve_management(in_features=yearlist21, out_feature_class=invekos_dissolve_21,
                              dissolve_field=["nutz_code", "beschreibu", "aum_code", "aum_beschr"],  # ,
                              statistics_fields=[], multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
    print("Computing 2015.....")
    InvekosYearData_15 = arcpy.AlterField_management(in_table=invekos_dissolve_15, field="beschreibu",
                                                     new_field_name=f"besch_15",
                                                     new_field_alias=f"besch_15",
                                                     field_type="TEXT",
                                                     field_is_nullable="NULLABLE",
                                                     clear_field_alias="DO_NOT_CLEAR")[0]

    InvekosYearData_15_Dis = arcpy.AlterField_management(in_table=InvekosYearData_15, field="aum_code",
                                                         new_field_name=f"aum_code_15",
                                                         new_field_alias=f"aum_code_15",
                                                         field_type="TEXT",
                                                         field_is_nullable="NULLABLE",
                                                         clear_field_alias="DO_NOT_CLEAR")[0]
    InvekosYearData_15_Dis2 = \
        arcpy.AlterField_management(in_table=InvekosYearData_15_Dis, field="nutz_code",
                                    new_field_name=f"nu_code_15",
                                    new_field_alias=f"nu_code_15",
                                    field_type="TEXT", field_length=3,
                                    field_is_nullable="NULLABLE",
                                    clear_field_alias="DO_NOT_CLEAR")[0]
    print("Computing 2016.....")
    InvekosYearData_16 = arcpy.AlterField_management(in_table=invekos_dissolve_16, field="beschreibu",
                                                     new_field_name=f"besch_16",
                                                     new_field_alias=f"besch_16",
                                                     field_type="TEXT",
                                                     field_is_nullable="NULLABLE",
                                                     clear_field_alias="DO_NOT_CLEAR")[0]

    InvekosYearData_16_Dis = arcpy.AlterField_management(in_table=InvekosYearData_16, field="aum_code",
                                                         new_field_name=f"aum_code_16",
                                                         new_field_alias=f"aum_code_16",
                                                         field_type="TEXT",
                                                         field_is_nullable="NULLABLE",
                                                         clear_field_alias="DO_NOT_CLEAR")[0]
    InvekosYearData_16_Dis2 = \
        arcpy.AlterField_management(in_table=InvekosYearData_16_Dis, field="nutz_code",
                                    new_field_name=f"nu_code_16",
                                    new_field_alias=f"nu_code_16",
                                    field_type="TEXT", field_length=3,
                                    field_is_nullable="NULLABLE",
                                    clear_field_alias="DO_NOT_CLEAR")[0]
    print("Computing 2017.....")
    InvekosYearData_17 = arcpy.AlterField_management(in_table=invekos_dissolve_17, field="beschreibu",
                                                     new_field_name=f"besch_17",
                                                     new_field_alias=f"besch_17",
                                                     field_type="TEXT",
                                                     field_is_nullable="NULLABLE",
                                                     clear_field_alias="DO_NOT_CLEAR")[0]

    InvekosYearData_17_Dis = arcpy.AlterField_management(in_table=InvekosYearData_17, field="aum_code",
                                                         new_field_name=f"aum_code_17",
                                                         new_field_alias=f"aum_code_17",
                                                         field_type="TEXT",
                                                         field_is_nullable="NULLABLE",
                                                         clear_field_alias="DO_NOT_CLEAR")[0]
    InvekosYearData_17_Dis2 = \
        arcpy.AlterField_management(in_table=InvekosYearData_17_Dis, field="nutz_code",
                                    new_field_name=f"nu_code_17",
                                    new_field_alias=f"nu_code_17",
                                    field_type="TEXT", field_length=3,
                                    field_is_nullable="NULLABLE",
                                    clear_field_alias="DO_NOT_CLEAR")[0]
    print("Computing 2018.....")
    InvekosYearData_18 = arcpy.AlterField_management(in_table=invekos_dissolve_18, field="beschreibu",
                                                     new_field_name=f"besch_18",
                                                     new_field_alias=f"besch_18",
                                                     field_type="TEXT",
                                                     field_is_nullable="NULLABLE",
                                                     clear_field_alias="DO_NOT_CLEAR")[0]

    InvekosYearData_18_Dis = arcpy.AlterField_management(in_table=InvekosYearData_18, field="aum_code",
                                                         new_field_name=f"aum_code_18",
                                                         new_field_alias=f"aum_code_18",
                                                         field_type="TEXT",
                                                         field_is_nullable="NULLABLE",
                                                         clear_field_alias="DO_NOT_CLEAR")[0]
    InvekosYearData_18_Dis2 = \
        arcpy.AlterField_management(in_table=InvekosYearData_18_Dis, field="nutz_code",
                                    new_field_name=f"nu_code_18",
                                    new_field_alias=f"nu_code_18",
                                    field_type="TEXT", field_length=3,
                                    field_is_nullable="NULLABLE",
                                    clear_field_alias="DO_NOT_CLEAR")[0]
    print("Computing 2019.....")
    InvekosYearData_19 = arcpy.AlterField_management(in_table=invekos_dissolve_19, field="beschreibu",
                                                     new_field_name=f"besch_19",
                                                     new_field_alias=f"besch_19",
                                                     field_type="TEXT",
                                                     field_is_nullable="NULLABLE",
                                                     clear_field_alias="DO_NOT_CLEAR")[0]

    InvekosYearData_19_Dis = arcpy.AlterField_management(in_table=InvekosYearData_19, field="aum_code",
                                                         new_field_name=f"aum_code_19",
                                                         new_field_alias=f"aum_code_19",
                                                         field_type="TEXT",
                                                         field_is_nullable="NULLABLE",
                                                         clear_field_alias="DO_NOT_CLEAR")[0]
    InvekosYearData_19_Dis2 = \
        arcpy.AlterField_management(in_table=InvekosYearData_19_Dis, field="nutz_code",
                                    new_field_name=f"nu_code_19",
                                    new_field_alias=f"nu_code_19",
                                    field_type="TEXT", field_length=3,
                                    field_is_nullable="NULLABLE",
                                    clear_field_alias="DO_NOT_CLEAR")[0]
    print("Computing 2020.....")
    InvekosYearData_20 = arcpy.AlterField_management(in_table=yearlist20, field="beschreibu",
                                                     new_field_name=f"besch_20",
                                                     new_field_alias=f"besch_20",
                                                     field_type="TEXT",
                                                     field_is_nullable="NULLABLE",
                                                     clear_field_alias="DO_NOT_CLEAR")[0]

    InvekosYearData_20_Dis = arcpy.AlterField_management(in_table=InvekosYearData_20, field="aum_code",
                                                         new_field_name=f"aum_code_20",
                                                         new_field_alias=f"aum_code_20",
                                                         field_type="TEXT",
                                                         field_is_nullable="NULLABLE",
                                                         clear_field_alias="DO_NOT_CLEAR")[0]
    InvekosYearData_20_Dis2 = \
        arcpy.AlterField_management(in_table=yearlist20, field="nutz_code",
                                    new_field_name=f"nu_code_20",
                                    new_field_alias=f"nu_code_20",
                                    field_type="TEXT", field_length=3,
                                    field_is_nullable="NULLABLE",
                                    clear_field_alias="DO_NOT_CLEAR")[0]
    print("Computing 2021.....")
    InvekosYearData_21 = arcpy.AlterField_management(in_table=yearlist21, field="beschreibu",
                                                     new_field_name=f"besch_21",
                                                     new_field_alias=f"besch_21",
                                                     field_type="TEXT",
                                                     field_is_nullable="NULLABLE",
                                                     clear_field_alias="DO_NOT_CLEAR")[0]

    InvekosYearData_21_Dis = arcpy.AlterField_management(in_table=InvekosYearData_21, field="aum_code",
                                                         new_field_name=f"aum_code_21",
                                                         new_field_alias=f"aum_code_21",
                                                         field_type="TEXT",
                                                         field_is_nullable="NULLABLE",
                                                         clear_field_alias="DO_NOT_CLEAR")[0]
    InvekosYearData_21_Dis2 = \
        arcpy.AlterField_management(in_table=yearlist21, field="nutz_code",
                                    new_field_name=f"nu_code_21",
                                    new_field_alias=f"nu_code_21",
                                    field_type="TEXT", field_length=3,
                                    field_is_nullable="NULLABLE",
                                    clear_field_alias="DO_NOT_CLEAR")[0]

    invekos_clip_15 = InvekosYearData_15_Dis2
    invekos_clip_16 = InvekosYearData_16_Dis2
    invekos_clip_17 = InvekosYearData_17_Dis2
    invekos_clip_18 = InvekosYearData_18_Dis2
    invekos_clip_19 = InvekosYearData_19_Dis2
    invekos_clip_20 = InvekosYearData_20_Dis2
    invekos_clip_21 = InvekosYearData_21_Dis2
    print("Union InVeKoS data in progress....")
    arcpy.Union_analysis(
        in_features=[[invekos_clip_15, ""], [invekos_clip_16, ""], [invekos_clip_17, ""], [invekos_clip_18, ""]
            , [invekos_clip_19, ""],[invekos_clip_20, ""],[invekos_clip_21, ""]],
        out_feature_class=invekos_union_nobuffer_py_ws, join_attributes="NO_FID", cluster_tolerance="", gaps="GAPS")
    print("Buffer running.....")
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
    invekos_union_buffer_dummy_aum = \
        arcpy.CalculateField_management(in_table=invekos_union_buffer_field, field="dummy_aum", expression="\"XXX\"",
                                        expression_type="PYTHON3", code_block="",
                                        field_type="TEXT",
                                        enforce_domains="NO_ENFORCE_DOMAINS")[0]
    print("Computing aum_code_15.....")
    invekos_union_buffer15 = arcpy.SelectLayerByAttribute_management(
        in_layer_or_view=invekos_union_buffer_dummy_aum, selection_type="NEW_SELECTION",
        where_clause=f"aum_code_15 <> 'A33' And aum_code_15 <> 'B37' And aum_code_15 <> 'B38'", invert_where_clause="")
    invekos_union_buffer15 = arcpy.CalculateField_management(in_table=invekos_union_buffer15,
                                                             field=f"aum_code_15",
                                                             expression="\"XXX\"",
                                                             expression_type="PYTHON3", code_block="",
                                                             field_type="TEXT",
                                                             enforce_domains="NO_ENFORCE_DOMAINS")[0]
    invekos_union_buffer15 = arcpy.SelectLayerByAttribute_management(
        in_layer_or_view=invekos_union_buffer15,
        selection_type="CLEAR_SELECTION",
        where_clause="", invert_where_clause="")

    arcpy.Clip_analysis(in_features=invekos_union_buffer15, clip_features=selected_watershed,
                        out_feature_class=invekos_union_py_ws, cluster_tolerance="")
    print("Computing aum_code_16.....")
    invekos_union_buffer16 = arcpy.SelectLayerByAttribute_management(
        in_layer_or_view=invekos_union_buffer15, selection_type="NEW_SELECTION",
        where_clause=f"aum_code_16 <> 'A33' And aum_code_16 <> 'B37' And aum_code_16 <> 'B38'", invert_where_clause="")
    invekos_union_buffer16 = arcpy.CalculateField_management(in_table=invekos_union_buffer16,
                                                             field=f"aum_code_16",
                                                             expression="\"XXX\"",
                                                             expression_type="PYTHON3", code_block="",
                                                             field_type="TEXT",
                                                             enforce_domains="NO_ENFORCE_DOMAINS")[0]
    invekos_union_buffer16 = arcpy.SelectLayerByAttribute_management(
        in_layer_or_view=invekos_union_buffer16,
        selection_type="CLEAR_SELECTION",
        where_clause="", invert_where_clause="")

    arcpy.Clip_analysis(in_features=invekos_union_buffer16, clip_features=selected_watershed,
                        out_feature_class=invekos_union_py_ws, cluster_tolerance="")
    print("Computing aum_code_17.....")
    invekos_union_buffer17 = arcpy.SelectLayerByAttribute_management(
        in_layer_or_view=invekos_union_buffer16, selection_type="NEW_SELECTION",
        where_clause=f"aum_code_17 <> 'A33' And aum_code_17 <> 'B37' And aum_code_17 <> 'B38'", invert_where_clause="")
    invekos_union_buffer17 = arcpy.CalculateField_management(in_table=invekos_union_buffer17,
                                                             field=f"aum_code_17",
                                                             expression="\"XXX\"",
                                                             expression_type="PYTHON3", code_block="",
                                                             field_type="TEXT",
                                                             enforce_domains="NO_ENFORCE_DOMAINS")[0]
    invekos_union_buffer17 = arcpy.SelectLayerByAttribute_management(
        in_layer_or_view=invekos_union_buffer17,
        selection_type="CLEAR_SELECTION",
        where_clause="", invert_where_clause="")

    arcpy.Clip_analysis(in_features=invekos_union_buffer17, clip_features=selected_watershed,
                        out_feature_class=invekos_union_py_ws, cluster_tolerance="")
    print("Computing aum_code_18.....")
    invekos_union_buffer18 = arcpy.SelectLayerByAttribute_management(
        in_layer_or_view=invekos_union_buffer17, selection_type="NEW_SELECTION",
        where_clause=f"aum_code_18 <> 'A33' And aum_code_18 <> 'B37' And aum_code_18 <> 'B38'", invert_where_clause="")
    invekos_union_buffer18 = arcpy.CalculateField_management(in_table=invekos_union_buffer18,
                                                             field=f"aum_code_18",
                                                             expression="\"XXX\"",
                                                             expression_type="PYTHON3", code_block="",
                                                             field_type="TEXT",
                                                             enforce_domains="NO_ENFORCE_DOMAINS")[0]
    invekos_union_buffer18 = arcpy.SelectLayerByAttribute_management(
        in_layer_or_view=invekos_union_buffer18,
        selection_type="CLEAR_SELECTION",
        where_clause="", invert_where_clause="")

    arcpy.Clip_analysis(in_features=invekos_union_buffer18, clip_features=selected_watershed,
                        out_feature_class=invekos_union_py_ws, cluster_tolerance="")
    print("Computing aum_code_19.....")
    invekos_union_buffer19 = arcpy.SelectLayerByAttribute_management(
        in_layer_or_view=invekos_union_buffer18, selection_type="NEW_SELECTION",
        where_clause=f"aum_code_19 <> 'A33' And aum_code_19 <> 'B37' And aum_code_19 <> 'B38'", invert_where_clause="")
    invekos_union_buffer19 = arcpy.CalculateField_management(in_table=invekos_union_buffer19,
                                                             field=f"aum_code_19",
                                                             expression="\"XXX\"",
                                                             expression_type="PYTHON3", code_block="",
                                                             field_type="TEXT",
                                                             enforce_domains="NO_ENFORCE_DOMAINS")[0]
    invekos_union_buffer19 = arcpy.SelectLayerByAttribute_management(
        in_layer_or_view=invekos_union_buffer19,
        selection_type="CLEAR_SELECTION",
        where_clause="", invert_where_clause="")
    arcpy.Clip_analysis(in_features=invekos_union_buffer19, clip_features=selected_watershed,
                        out_feature_class=invekos_union_py_ws, cluster_tolerance="")
    print("Computing aum_code_20.....NO RELEVANT CODES FOUND -> ALL VALUES ARE XXX")

    invekos_union_buffer20 = arcpy.SelectLayerByAttribute_management(
        in_layer_or_view=invekos_union_buffer19, selection_type="NEW_SELECTION",
        where_clause=f"aum_code_20 <> 'A33' And aum_code_20 <> 'B37' And aum_code_20 <> 'B38'", invert_where_clause="")
    invekos_union_buffer20 = arcpy.CalculateField_management(in_table=invekos_union_buffer20,
                                                             field=f"aum_code_20",
                                                             expression="\"XXX\"",
                                                             expression_type="PYTHON3", code_block="",
                                                             field_type="TEXT",
                                                             enforce_domains="NO_ENFORCE_DOMAINS")[0]
    invekos_union_buffer20 = arcpy.SelectLayerByAttribute_management(
        in_layer_or_view=invekos_union_buffer20,
        selection_type="CLEAR_SELECTION",
        where_clause="", invert_where_clause="")

    arcpy.Clip_analysis(in_features=invekos_union_buffer20, clip_features=selected_watershed,
                        out_feature_class=invekos_union_py_ws, cluster_tolerance="")
    print("Computing aum_code_21.....NO RELEVANT CODES FOUND -> ALL VALUES ARE XXX")
    invekos_union_buffer21 = arcpy.SelectLayerByAttribute_management(
        in_layer_or_view=invekos_union_buffer20, selection_type="NEW_SELECTION",
        where_clause=f"aum_code_21 <> 'A33' And aum_code_21 <> 'B37' And aum_code_21 <> 'B38'", invert_where_clause="")
    invekos_union_buffer21 = arcpy.CalculateField_management(in_table=invekos_union_buffer21,
                                                             field=f"aum_code_21",
                                                             expression="\"XXX\"",
                                                             expression_type="PYTHON3", code_block="",
                                                             field_type="TEXT",
                                                             enforce_domains="NO_ENFORCE_DOMAINS")[0]
    invekos_union_buffer21 = arcpy.SelectLayerByAttribute_management(
        in_layer_or_view=invekos_union_buffer21,
        selection_type="CLEAR_SELECTION",
        where_clause="", invert_where_clause="")

    arcpy.Clip_analysis(in_features=invekos_union_buffer21, clip_features=selected_watershed,
                        out_feature_class=invekos_union_py_ws, cluster_tolerance="")


if __name__ == '__main__':
    # Please change the path here This Part below (two lines) has to be added to all seperated models if you want to
    # run them, it is also part of the combined one.
    UserPath = "D:/Users/Thakur/ErospotWorkspace"
    MainPathGDB = "D:/Users/Thakur/ErospotWorkspace/EROSPOT.gdb"
    ezg_by_erospot = MainPathGDB + "/ezg_by_erospot"
    feature_layer = arcpy.MakeFeatureLayer_management(ezg_by_erospot, 'feature')
    selected_watershed = arcpy.SelectLayerByAttribute_management(
        in_layer_or_view=feature_layer,
        selection_type="NEW_SELECTION",
        where_clause="expl_num=4")
    calculate_lu_ws(selected_watershed, 4, UserPath, MainPathGDB)
    # invekos_atkis_combined(selected_watershed, 4, UserPath, MainPathGDB)
    print("Done")
