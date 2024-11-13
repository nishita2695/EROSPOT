# EROSPOT
Instructions: Running the python combined ModelBuilder
Installations Required
•	ArcGIS Pro (Any version)
•	Python 3.4+
•	A code editor like VisualStudioCode or PyCharm(preferred)
o	Please create the following folders before you run:
1. DriveName/Workspace/ (For ex: D:/Users/Thakur/ErospotWorkspace/)
2. DriveName/Workspace/Geodatabase.gdb (For the geodatabase that will be storing intermediate inputs for computation during the model run)
Adjusting the sdr.py Natcap.Invest code
This part to be added from the workflow that we cannot access in the EROSPOT folder
Preparations - Python and Anaconda
•	Please open the file named: EROSPOT.py using a code editor like pycharm. Right click on the files on the pycharm editor screen and go to Modify Run Configurations. 

 

•	On the Python Interpreter drop down tab, select the ArcGISPro (python) environment and click ok. This is done so that the arcpy libraries are recognized by the editor.  

Running the Combined Model
•	Open the file: EROSPOT.py and change the paths named UserPath and MainPathGDB and save the file. The UserPath should simply point to your workspace, and the MainPathGDB should point to the Geodatabase inside your workspace. 

 
•	Please select and copy the version of sdr.py that was modified by you and paste it in the folder: External libraries -> arcpy -> site-packages ->natcap -> invest -> sdr  There will be a prompt that will ask you for admin rights and that if you are sure to replace the sdr.py file in the destination – you have to agree for the sdr.py to be pasted into this location. And now when the model runs, the correct sdr.py file will be referred to.
•	Right Click on the EROSPOT.py and select run. The script should be running and the watershed numbers and models being calculated should appear on the screen. Please wait till the watersheds have finished running and open your output folder (DriveName/Workspace/Hotspots) and check if your outputs have been generated. If yes, you have successfully run the Model on python.

