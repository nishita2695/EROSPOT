"""
Authors: Nishita Thakur, Marvin Melzer

Credit authorship contribution statement:
Nishita Thakur: Software (lead). Marvin Melzer: Conceptualization (lead);
Methodology (lead); Data duration (lead); Funding acquisition (lead); Software (supporting).

Project: EROSPOT (DAKIS)

Last Update: 2024-11-26

InVEST MODEL Reference: Natural Capital Project, 2024. InVEST 0.0. Stanford University, University of Minnesota,
Chinese Academy of Sciences, The Nature Conservancy, World Wildlife Fund, Stockholm Resilience Centre and the Royal
Swedish Academy of Sciences. https://naturalcapitalproject.stanford.edu/software/invest

Description: This script is used to integrate all three functionalities: Input preprocessing,
InVeST SDR Model Run(Reference above) and Hotspot generation

License: Please refer to the document titled 'License.docx' in the repository
"""

from shapely import speedups

speedups.disable()
import os
import logging
import sys
# from ModelsIntegrated import model_combined, identify_hotspots
from InputPreprocessing_IdentifyingHotspots import model_combined_once, identify_hotspots
import natcap.invest.sdr.sdr
import natcap.invest.utils

# Logger for debugging InVeST Errors
LOGGER = logging.getLogger(__name__)
root_logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    fmt=natcap.invest.utils.LOG_FMT,
    datefmt='%m/%d/%Y %H:%M:%S ')
handler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO, handlers=[handler])


# Set the values sent  to variables that can be used by the Input Models - this is only for latr if we convert to GUI
def set_values(start, end, watershed, directory, gdb):
    # Global variables were used here so that they are in scope throughout this file
    global start_watershed, end_watershed, watershed_numbers, main_directory, geodatabase
    start_watershed = start
    end_watershed = end
    watershed_numbers = watershed
    main_directory = directory
    geodatabase = gdb


# Get Values from User
def get_user_values(**kwargs):
    print("Received User Values:")

    print("Starting watershed:", start_watershed)
    print("Ending watershed:", end_watershed)
    print("Watershed Numbers:", watershed_numbers)
    print("Main Directory:", main_directory)
    print("Geodatabase", geodatabase)
    set_values(start_watershed, end_watershed, watershed_numbers, main_directory, geodatabase)
    start_process(start_watershed, end_watershed, watershed_numbers, main_directory, geodatabase)


''' SECTION 2.5, User Guide - Modification to sdr.py described, please make the changes before running the model'''


# Start process is called to check the User Input and redirect the parameters to the relevant execution.
# For example if User chooses to execute only 1 watershed or a range, the execution pathway will be different
# compared to when a user chooses to execute a discrete, non-continuous subset of watersheds
def start_process(lower, upper, numbers, mainpath, gdbpath):
    UserPath = mainpath
    MainPathGDB = gdbpath
    # Code Block: Choosing the range of watersheds and executing invest in a loop for this range
    # as well as adjusting the range to itself for a single watershed
    if numbers == '':
        if not lower == upper:
            print("_______________________________________________")
            print(" EXECUTING THE MODEL FOR A RANGE OF WATERSHEDS...")
            print("_______________________________________________")
            # gdal.SetConfigOption("GTIFF_SRS_SOURCE", "EPSG") #for the reprojection of rasters
            lower_limit = lower
            upper_limit = upper
            OutputFolder = mainpath + "/OutputDataInvest"
            # FOLDER INPUTDATAINVEST CREATION
            InputInvest = UserPath + "/InputDataInvest"
            if not os.path.exists(InputInvest):
                os.makedirs(InputInvest)
            else:
                print(f"Folder '{InputInvest}' exists")
            # The function being called here is for the preprocessing of Input data
            # model_combined(UserPath, MainPathGDB, lower_limit, upper_limit, numbers)
            # After the input data is processed, we set the conditions for running InVeST
            for x in range(int(lower_limit), int(upper_limit) + 1):
                model_combined_once(UserPath, MainPathGDB, x)
                if not os.path.exists(OutputFolder):
                    os.makedirs(OutputFolder)
                else:
                    print("Folder '{OutputFolder}' exists")
                if not os.path.exists(OutputFolder + "/ws_" + str(x)):
                    os.makedirs(OutputFolder + "/ws_" + str(x))
                else:
                    print("Folder OutputFolder/WS_X exists")
                # These arguments are the parameters for paths that need to be sent to the InVeST SDR function
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
                    print("***********************************************")
                    print("STEP 2: EROSION MODELLING WITH InVEST SDR")
                    print("************************************************")
                    natcap.invest.sdr.sdr.execute(args)

                except:
                    print(
                        'WATERSHED NUMBER ' + str(
                            x) + ' FAILED EXECUTION IN INVEST: PLEASE CHECK ERROR DESCRIPTION. RESUMING WITH '
                                 'THE '
                                 'NEXT WATERSHED.....')
                    print('\n\n')
                    continue
                finally:
                    # This function call is finally for the hotspot generation
                    identify_hotspots(x, UserPath, MainPathGDB)
        else:
            # This is the case when starting watershed is equal to the ending watershed,
            # This means that it is a single watershed, that the model runs for
            print("_______________________________________________")
            print(" EXECUTING THE MODEL FOR A SINGLE WATERSHED... ")
            print("_______________________________________________")
            # gdal.SetConfigOption("GTIFF_SRS_SOURCE", "EPSG") #for the reprojection of rasters
            lower_limit = lower
            upper_limit = upper
            # set x as the lower or upper limit
            x = lower_limit
            OutputFolder = mainpath + "/OutputDataInvest"
            # FOLDER INPUTDATAINVEST CREATION
            InputInvest = UserPath + "/InputDataInvest"
            if not os.path.exists(InputInvest):
                os.makedirs(InputInvest)
            else:
                print(f"Folder '{InputInvest}' exists")
            # The function being called here is for the preprocessing of Input data
            model_combined_once(UserPath, MainPathGDB, x)
            # After the input data is processed, we set the conditions for running InVeST
            if not os.path.exists(OutputFolder):
                os.makedirs(OutputFolder)
            else:
                print("Folder '{OutputFolder}' exists")
            if not os.path.exists(OutputFolder + "/ws_" + str(x)):
                os.makedirs(OutputFolder + "/ws_" + str(x))
            else:
                print("Folder OutputFolder/WS_X exists")
            # These arguments are the parameters for paths that need to be sent to the InVeST SDR function
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
                print("***********************************************")
                print("STEP 2: EROSION MODELLING WITH InVEST SDR")
                print("************************************************")
                natcap.invest.sdr.sdr.execute(args)

            except:
                print(
                    'WATERSHED NUMBER ' + str(
                        x) + ' FAILED EXECUTION IN INVEST: PLEASE CHECK ERROR DESCRIPTION. RESUMING WITH '
                             'THE '
                             'NEXT WATERSHED.....')
                print('\n\n')

            finally:
                # This function call is finally for the hotspot generation
                identify_hotspots(x, UserPath, MainPathGDB)
    if numbers != '':
        print("_______________________________________________")
        print(" EXECUTING THE MODEL FOR A DISCONTINUOUS LIST OF WATERSHEDS... ")
        print("_______________________________________________")
        #
        user_input = [int(item) for item in numbers.split(',')]
        # model_combined(UserPath, MainPathGDB, lower, upper, numbers)
        for x in user_input:
            OutputFolder = mainpath + "/OutputDataInvest"
            if not os.path.exists(OutputFolder):
                os.makedirs(OutputFolder)
            else:
                print("Folder '{OutputFolder}' exists")
            if not os.path.exists(OutputFolder + "/ws_" + str(x)):
                os.makedirs(OutputFolder + "/ws_" + str(x))
            else:
                print("Folder OutputFolder/WS_X_NUMBERS exists")
            model_combined_once(UserPath, MainPathGDB, x)
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
                print("***********************************************")
                print("STEP 2: EROSION MODELLING WITH InVEST SDR")
                print("************************************************")
                natcap.invest.sdr.sdr.execute(args)

            except:
                print(
                    'WATERSHED NUMBER ' + str(x) + ' FAILED EXECUTION: PLEASE CHECK ERROR DESCRIPTION. RESUMING WITH '
                                                   'THE '
                                                   'NEXT WATERSHED.....')
                print('\n\n')
                continue
            finally:
                identify_hotspots(x, UserPath, MainPathGDB)
    print("PROCESS ENDED - FINISHED COMPLETE EXECUTION!")
