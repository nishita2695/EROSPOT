Running instructions:

In your editor running environment, the following packages should be installed: geopandas, rasterio, shapely, numpy, fiona
What could be done: Create a file requirements.txt in your editor, with the following content:
geopandas==0.14.3
fiona==1.9.6
shapely==2.0.2
Pyproj==3.6.1
rasterio==1.3.9

then in your python environment run the command: pip install -r requirements.txt

To run the script: Just change the paths in the main function - to mirror local paths in your computer


Data required:
All the datasets for erosion modelling(Check UserGuide)
To check output, check the folder InputDataInvest/testing/ws_4/k-factor/k-factor_resampled_ws_4.tif -> open this tif file in ArcGIS and compare it with the example output