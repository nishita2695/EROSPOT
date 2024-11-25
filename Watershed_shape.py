"""
Author: Nishita Thakur
Concept: Marvin Melzer
Project: EROSPOT (DAKIS)
Last Update: 2024-11-25

Description: This script is used to get the shapefile for each watershed boundary

"""
import arcpy


# Conversion of the feature layer based on the selected attribute to a shapefile
def create_shape(y, selected_watershed_sent, Userpath):
    feature_layer = arcpy.MakeFeatureLayer_management(selected_watershed_sent, 'ws_shape_' + str(y))
    output_folder = Userpath + "/InputDataInvest/testing/ws_" + str(y)
    arcpy.FeatureClassToShapefile_conversion(feature_layer, output_folder)
    print("Shape created")


if __name__ == '__main__':
    arcpy.env.overwriteOutput = True
    # The program executes from here, the functions written before are called from here, and executed in the sequence
    # that they are mentioned within the 'main' function
    # ___________________________________________________________________________________________
    # PLEASE CHANGE YOUR PATH HERE
    # ___________________________________________________________________________________________
    UserPathNew = "D:/Users/Thakur/ErospotWorkspace"
    MainPathGDB = "D:/Users/Thakur/ErospotWorkspace/EROSPOT.gdb"
    # ------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------

    # Entry Point - creating feature layer out of the layer
    ezg_by_erospot = MainPathGDB + "/ezg_by_erospot"
    for x in range(1, 11):
        selected_watershed = arcpy.SelectLayerByAttribute_management(
            in_layer_or_view=ezg_by_erospot,
            selection_type="NEW_SELECTION",
            where_clause="expl_num=" + str(x))
        # Function call to create shape file
        create_shape(x, selected_watershed, UserPathNew)
