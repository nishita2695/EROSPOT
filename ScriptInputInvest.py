import sys

from ModelsIntegrated import model_combined


# PATHS: ATKIS: UserPath and then folder structure would be: /ATKIS
# OUTPUT:  Please create the folder UserPath+"/InputDataInvest/testing"
# K-Factor: As the tif is too big for the geodatabase, it is stored in the following path:
# UserPath+"/K_Faktor_Bayern/k_factor_komplett_bayern.tif"
# R-Factor: UserPath+"/R_Faktor_bayern/r_factor_bayern.tif"
# Recommended testing file structure : Please create a folder called DGM1 inside your
# UserPath and paste tiles of several watershed there (between numbers 1 to 10) and then run this code
# For example: D:/Users/Thakur/ErospotWorkspace/DGM1
# ________________________________________________________________________________
def main():
    args = sys.argv[1:]


if __name__ == '__main__':
    # Change Paths here
    UserPath = "D:/Users/Thakur/ErospotWorkspace"
    MainPathGDB = "D:/Users/Thakur/ErospotWorkspace/EROSPOT.gdb"
    model_combined(UserPath, MainPathGDB,1,2)
    print("Done")
