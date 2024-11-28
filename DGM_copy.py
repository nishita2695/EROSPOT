"""
Authors: Nishita Thakur, Marvin Melzer

Credit authorship contribution statement:
Nishita Thakur: Software (lead). Marvin Melzer: Conceptualization (lead);
Methodology (lead); Data duration (lead); Funding acquisition (lead); Software (supporting).

Project: EROSPOT (DAKIS)

Last Update: 2024-11-26

Description: This script is used to copy all raster tile coordinates that are within the minimum bounding rectangle as
files in a folder and stitched together for each watershed to get the Digital Elevation Model for each Watershed
which is an important parameter for the InVeST model as well.

License: Please refer to the document titled 'License.docx' in the repository

"""
import arcpy
import os.path
import shutil
import os


# _______________________________________________________________________________
# Please scroll down to the main function and do the necessary changes there
# Recommended testing file structure : Please create a folder called DGM1 inside your
# UserPath and paste tiles of several watershed there (between numbers 1 to 10) and then run this code
# For example: D:/Users/Thakur/ErospotWorkspace/DGM1
# ________________________________________________________________________________
'''SECTION 1.2, User Guide'''
def copyCoordinates_x_low(layer):
    dictionary__x_low = {}
    arcpy.env.overwriteOutput = True
    fldName1 = 'x_low'
    fldName_no = "expl_num"

    for col in arcpy.SearchCursor(layer, fields=fldName_no):
        for row in arcpy.SearchCursor(layer, fields=fldName1):
            dictionary__x_low.update({col.getValue(fldName_no): row.getValue(fldName1)})
    return dictionary__x_low
    print("DICTIONARY::::x_low::")


def copyCoordinates_x_high(layer):

    dictionary__x_high = {}
    arcpy.env.overwriteOutput = True
    fldName1 = 'x_high'
    fldName_no = "expl_num"

    for col in arcpy.SearchCursor(layer, fields=fldName_no):
        for row in arcpy.SearchCursor(layer, fields=fldName1):
            dictionary__x_high.update({col.getValue(fldName_no): row.getValue(fldName1)})
    return dictionary__x_high
    print("DICTIONARY::::x_high::")


def copyCoordinates_y_low(layer):

    dictionary__y_low = {}
    arcpy.env.overwriteOutput = True
    fldName2 = 'y_low'
    fldName_no = "expl_num"

    for col in arcpy.SearchCursor(layer, fields=fldName_no):
        for row in arcpy.SearchCursor(layer, fields=fldName2):
            dictionary__y_low.update({col.getValue(fldName_no): row.getValue(fldName2)})
    return dictionary__y_low
    print("DICTIONARY::::y_low::")


def copyCoordinates_y_high(layer):
    dictionary__y_high = {}
    arcpy.env.overwriteOutput = True
    fldName1 = 'y_high'
    fldName_no = "expl_num"

    for col in arcpy.SearchCursor(layer, fields=fldName_no):
        for row in arcpy.SearchCursor(layer, fields=fldName1):
            dictionary__y_high.update({col.getValue(fldName_no): row.getValue(fldName1)})
    return dictionary__y_high
    print("DICTIONARY::::y_high::")


# Function definition for copying and pasting
def addCoordinateFiles(UserPathSent, x, dictionary__x_low, dictionary__x_high, dictionary__y_low,
                       dictionary__y_high):
    # Variable and list initializations
    print(""+str(x))
    list_temp = []
    watershed_folders = UserPathSent + "/InputDataInvest/testing"
    folder_ws = watershed_folders + "/ws_" + str(x)
    print(dictionary__x_low)
    print(dictionary__x_high)
    print(dictionary__y_low)
    print(dictionary__y_high)
    print('' + str(dictionary__x_low.get(x)))
    if x in dictionary__y_low:
        print("X is"+ str(x))
    # Code for separating corner coordinates according to key value pairs extracted from layers
    if (int(x) in dictionary__y_low and int(x) in dictionary__y_high and int(x) in dictionary__x_high and
            int(x) in dictionary__x_low):
        print("Loop entered for DGM Coordinates")
        print(dictionary__x_low.get(int(x)))
        print(dictionary__y_high.keys())  # List all the keys in the dictionary
        print(type(dictionary__y_high))  # Ensure it's a dictionary
        print(type(dictionary__y_high.get(int(x))))  # Check the type of the value returned
        # This part essentially checks in the dictionaries if values exist for the selected watershed and adds all four
        # corner coordinates of one watershed to a single sorted list - now it is no longer a dictionary data structure
        # For example, list_temp for ws_1 is [818,821,5377,5381]
        list_temp.append(dictionary__y_high.get(int(x)))
        list_temp.append(dictionary__x_high.get(int(x)))
        list_temp.append(dictionary__y_low.get(int(x)))
        list_temp.append(dictionary__x_low.get(int(x)))
    else:
        print("WATERSHED NOT FOUND, PLEASE CHECK IF THE WATERSHED EXISTS")
    # Sorts the list so that file names can go serially from x_low to y_high
    list_temp.sort()
    print("Corner Coordinates of Watershed " + str(x) + " are:")

    # Debugging print statement
    print(list_temp)
    x_name = list_temp[0]
    y_name = list_temp[2]
    list_raster = []
    # Code for copying and pasting - iterate through x coordinates starting from x_low to x_high
    # Iterate in a nested loop through y_low to y_high and dynamically construct the file name
    for x_coord in range(list_temp[0], (list_temp[1] + 1)):
        for y_coord in range(list_temp[2], (list_temp[3] + 2)):
            # First check if y_high has been reached. If yes, then inner loop stops and goes to outer loop
            # This is to stop the loop at y_high and return to the outer loop with x coordinate being x+1 greater
            # than the previous value
            if y_coord == list_temp[3] + 1:
                # Debugging print statement
                print("Y_COORD:" + str(y_coord))
                # Increase x coordinate value by 1 if the y_igh has been reached
                x_name += 1
                # Reassign the y coordinate value to y_low as it has to be repeated for the next incremented x value
                y_name = list_temp[2]
                # End inner loop
                break
            # Construct file name out of the inner loop - x_coord+_+y_coord.asc
            filename_to_be_copied_asc = "" + str(x_name) + "_" + str(y_name) + ".asc"
            filename_to_be_copied_prj = "" + str(x_name) + "_" + str(y_name) + ".prj"

            # increment y coordinate value by 1 within loop
            y_name += 1

            # Filepath for source folder - NEEDS TO BE GENERALIZED LATER (SSD DATA)
            filepath = UserPathSent + "/DGM1"
            # Filepath for destination folder
            titlefolder = folder_ws + "/DGM_ws_" + str(x)

            # File IO operations checking if folders exist and then proceeding to copy

            if folder_ws:
                folder_ws_dgm = arcpy.CreateFolder_management(out_folder_path=folder_ws,
                                                              out_name="DGM_ws_" + str(x))

                path_individual_file_asc = UserPathSent + "/" + filename_to_be_copied_asc
                #list_raster.append(path_individual_file_asc)
                path_individual_file_prj = UserPathSent + "/" + filename_to_be_copied_asc
                #list_raster.append(path_individual_file_prj)
            #print(list_raster)
            shutil.copy(filepath + "/" + filename_to_be_copied_asc, titlefolder)
            shutil.copy(filepath + "/" + filename_to_be_copied_prj, titlefolder)

            #arcpy.CreateFolder_management(out_folder_path=)
            print(filename_to_be_copied_asc)
    '''if len(list_raster):
        convert = \
            arcpy.MosaicToNewRaster_management(input_rasters=list_raster, output_location=output_filepath,
                                               raster_dataset_name_with_extension="dgm_ws_" + str(
                                                   x) + ".tif", pixel_type="32_BIT_FLOAT",
                                               cellsize=None, number_of_bands=1, mosaic_method="LAST",
                                               mosaic_colormap_mode="FIRST")[0]
        print("Tiles Stitched!")'''


def stitchTiles(x, UserPathTiles):
    list_raster = []
    filepath = UserPathTiles + "/InputDataInvest/testing/ws_" + str(x) + "/DGM_ws_" + str(x)
    for path in os.listdir(filepath):
        list_raster.append(filepath + "/" + path)
    print("LIST RASTER:")
    print(list_raster)
    if len(list_raster):
        convert = \
            arcpy.MosaicToNewRaster_management(input_rasters=list_raster, output_location=filepath,
                                               raster_dataset_name_with_extension="dgm_ws_" + str(
                                                   x) + ".tif", pixel_type="32_BIT_FLOAT",
                                               cellsize=None, number_of_bands=1, mosaic_method="LAST",
                                               mosaic_colormap_mode="FIRST")[0]
    print("Tiles Stitched!")


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

    # Entry Point - creating feature layer out of the layer
    ezg_by_erospot = MainPathGDB + "/ezg_by_erospot"
    feature_layer = arcpy.MakeFeatureLayer_management(ezg_by_erospot, 'feature')

    # Initializing dictionaries. Dictionaries are data structures with key-value pairs. The key is the watershed
    # number (which is unique) and the values in all these lists are the x and y coordinates of the minimum bounding
    # rectangle of the respective watersheds For example for watershed numbers 1-5, dictionary_x__low will contain
    # the values [1: 818, 2: 814, 3:803, 4:791, 5:790]
    dictionary__x_low = {}
    dictionary__y_high = {}
    dictionary__y_low = {}
    dictionary__x_high = {}

    # Currently, loop for watersheds 1-10 for test purposes, can be modified to user defined range of watersheds later
    for x in range(1, 11):
        selected_watershed = arcpy.SelectLayerByAttribute_management(
            in_layer_or_view=feature_layer,
            selection_type="NEW_SELECTION",
            where_clause="expl_num=" + str(x))
        #InputPath = "Z:/FOR/FOR-Projects/EROSPOT/InputDataInvest/testing"
        #folder_ws = arcpy.CreateFolder_management(out_folder_path=InputPath, out_name="ws_" + str(x))
        # Function call for extracting x_low coordinate from the layer's attribute table
        dictionary__x_low = copyCoordinates_x_low(feature_layer)
        # Function call for extracting x_high coordinate from the layer's attribute table
        dictionary__x_high = copyCoordinates_x_high(feature_layer)
        # Function call for extracting y_low coordinate from the layer's attribute table
        dictionary__y_low = copyCoordinates_y_low(feature_layer)
        # Function call for extracting y_high coordinate from the layer's attribute table
        dictionary__y_high = copyCoordinates_y_high(feature_layer)
        # Function call for the actual copying and pasting (python file io operations with os module)
        addCoordinateFiles(UserPath, x, dictionary__x_low, dictionary__x_high, dictionary__y_low, dictionary__y_high)
        # Function to stitch the mosaic into one single raster
        stitchTiles(x, UserPath)


