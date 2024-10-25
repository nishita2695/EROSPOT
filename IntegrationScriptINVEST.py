import arcpy
from osgeo import gdal
from shapely import speedups
import arcpy
from arcpy.ia import *


speedups.disable()
import os
import logging
import sys
from ModelsIntegrated import model_combined, identify_hotspots
import natcap.invest.sdr.sdr
import natcap.invest.utils

LOGGER = logging.getLogger(__name__)
root_logger = logging.getLogger()

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    fmt=natcap.invest.utils.LOG_FMT,
    datefmt='%m/%d/%Y %H:%M:%S ')
handler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO, handlers=[handler])


# Set the values sent from GUI to variables that can be used by the Input Models
def set_values(start, end, watershed, directory, gdb):
    global start_watershed, end_watershed, watershed_numbers, main_directory, geodatabase
    start_watershed = start
    end_watershed = end
    watershed_numbers = watershed
    main_directory = directory
    geodatabase = gdb


def get_user_values(**kwargs):
    print("Received User Values:")

    print("Starting watershed:", start_watershed)
    print("Ending watershed:", end_watershed)
    print("Watershed Numbers:", watershed_numbers)
    print("Main Directory:", main_directory)
    print("Geodatabase", geodatabase)
    set_values(start_watershed, end_watershed, watershed_numbers, main_directory, geodatabase)
    start_process(start_watershed, end_watershed, watershed_numbers, main_directory, geodatabase)


# if __name__ == '__main__':
def start_process(lower, upper, numbers, mainpath, gdbpath):
    UserPath = mainpath
    MainPathGDB = gdbpath
    # UserPath = "D:/Users/Thakur/ErospotWorkspace"
    # MainPathGDB = "D:/Users/Thakur/ErospotWorkspace/EROSPOT.gdb"
    # 1
    # model_combined(UserPath, MainPathGDB)
    # Asking the user to choose either to run a range of watersheds or a randomized list
    # choice = input("Please select 1 if you want  to run invest for a serial range of "
    #              "watersheds and select 2 if you want to run individual watersheds and press enter:")
    # Code Block: Choosing the range of watersheds and executing invest in a loop for this range
    if numbers == '':
       # gdal.SetConfigOption("GTIFF_SRS_SOURCE", "EPSG") #for the reprojection of rasters
        lower_limit = lower
        upper_limit = upper
        # lower_limit = input('Please type the starting watershed of the range and press enter:')
        # upper_limit = input(
        #   'Please type the ending watershed of the range upto which you want the calculation to run and press enter:')
        OutputFolder = mainpath + "/OutputDataInvest"
        # FOLDER INPUTDATAINVEST CREATION
        InputInvest = UserPath + "/InputDataInvest"
        if not os.path.exists(InputInvest):
            os.makedirs(InputInvest)
        else:
            print(f"Folder '{InputInvest}' exists")
        model_combined(UserPath, MainPathGDB, lower_limit, upper_limit, numbers)
        for x in range(int(lower_limit), int(upper_limit) + 1):
            if not os.path.exists(OutputFolder):
                os.makedirs(OutputFolder)
            else:
                print("Folder '{OutputFolder}' exists")
            if not os.path.exists(OutputFolder+"/ws_"+str(x)):
                os.makedirs(OutputFolder+"/ws_"+str(x))
            else:
                print("Folder OutputFolder/WS_X exists")

            # arcpy.CreateFolder_management(out_folder_path=UserPath + "/OutputDataInvest", out_name="ws_" + str(x))
            # ScriptInputInvest.main(x) DOES NOT WORK
            args = {
                'biophysical_table_path': UserPath + '/InputDataInvest/testing/ws_' + str(
                    x) + '/biophysical_table_ws_' + str(x) + '.csv '
                ,
                'dem_path': UserPath + '/InputDataInvest/testing/ws_' + str(x) + '/DGM_ws_' + str(
                    x) + '/dgm_ws_' + str(x) + '.tif',
                'drainage_path': UserPath + '/InputDataInvest/testing/ws_' + str(x) + '/gew_' + str(x) + '.tif',
                'erodibility_path': UserPath + '/InputDataInvest/testing/ws_' + str(x) + '/k-factor/k-factor'
                                                                                         '-resampled_ws_' + str(
                    x) + '.tif',
                'erosivity_path': UserPath + '/InputDataInvest/testing/ws_' + str(x) + '/r_factor/r_ws_times' + str(
                    x) + '.tif',
                'ic_0_param': '0.5',
                'k_param': '2',
                'lulc_path': UserPath + '/InputDataInvest/testing/ws_' + str(x) + '/lc_ws_' + str(x) + '.tif',
                'results_suffix': '',
                'sdr_max': '0.8',
                'l_max': '122',
                'threshold_flow_accumulation': '10000',
                'watersheds_path': UserPath + '/InputDataInvest/testing/ws_' + str(x) + '/ws_shape_' + str(
                    x) + '.shp',
                'workspace_dir': UserPath + '/OutputDataInvest/ws_' + str(x)
                ,
            }
            # If there is something wrong with the data inputs of a
            # particular watershed, then an error message is displayed and the next watershed in the loop is executed
            try:
                natcap.invest.sdr.sdr.execute(args)

            except:
                print(
                    'WATERSHED NUMBER ' + str(x) + ' FAILED EXECUTION: PLEASE CHECK ERROR DESCRIPTION. RESUMING WITH '
                                                   'THE '
                                                   'NEXT WATERSHED.....')
                print('\n\n')
                continue
            finally:
                identify_hotspots(x,UserPath, MainPathGDB)
    else:

        user_input = [int(item) for item in numbers.split()]
        model_combined(UserPath, MainPathGDB, lower, upper, numbers)
        for x in user_input:
            OutputFolder = mainpath + "/OutputDataInvest"
            if not os.path.exists(OutputFolder):
                os.makedirs(OutputFolder)
            else:
                print("Folder '{OutputFolder}' exists")
            if not os.path.exists(OutputFolder+"/ws_"+str(x)):
                os.makedirs(OutputFolder+"/ws_"+str(x))
            else:
                print("Folder OutputFolder/WS_X_NUMBERS exists")

            #arcpy.CreateFolder_management(out_folder_path=UserPath + "/OutputDataInvest", out_name="ws_" + str(x))
            # ScriptInputInvest.main(x) DOES NOT WORK
            args = {
                'biophysical_table_path': UserPath + '/InputDataInvest/testing/ws_' + str(
                    x) + '/biophysical_table_ws_' + str(x) + '.csv '
                ,
                'dem_path': UserPath + '/InputDataInvest/testing/ws_' + str(x) + '/DGM_ws_' + str(
                    x) + '/dgm_ws_' + str(x) + '.tif',
                'drainage_path': UserPath + '/InputDataInvest/testing/ws_' + str(x) + '/gew_' + str(x) + '.tif',
                'erodibility_path': UserPath + '/InputDataInvest/testing/ws_' + str(x) + '/k-factor/k-factor'
                                                                                         '-resampled_ws_' + str(
                    x) + '.tif',
                'erosivity_path': UserPath + '/InputDataInvest/testing/ws_' + str(x) + '/r_factor/r_ws_times' + str(
                    x) + '.tif',
                'ic_0_param': '0.5',
                'k_param': '2',
                'lulc_path': UserPath + '/InputDataInvest/testing/ws_' + str(x) + '/lc_ws_' + str(x) + '.tif',
                'results_suffix': '',
                'sdr_max': '0.8',
                'l_max': '122',
                'threshold_flow_accumulation': '10000',
                'watersheds_path': UserPath + '/InputDataInvest/testing/ws_' + str(x) + '/ws_shape_' + str(
                    x) + '.shp',
                'workspace_dir': UserPath + '/OutputDataInvest/ws_' + str(x)
                ,
            }
            # If there is something wrong with the data inputs of a
            # particular watershed, then an error message is displayed and the next watershed in the loop is executed
            try:
                natcap.invest.sdr.sdr.execute(args)

            except:
                print(
                    'WATERSHED NUMBER ' + str(x) + ' FAILED EXECUTION: PLEASE CHECK ERROR DESCRIPTION. RESUMING WITH '
                                                   'THE '
                                                   'NEXT WATERSHED.....')
                print('\n\n')
                continue
            finally:
                identify_hotspots(x,UserPath, MainPathGDB)
    print("Done")
