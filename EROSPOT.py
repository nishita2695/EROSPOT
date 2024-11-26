"""
Authors: Nishita Thakur, Marvin Melzer

Credit authorship contribution statement:
Nishita Thakur: Software (lead). Marvin Melzer: Conceptualization (lead);
Methodology (lead); Data duration (lead); Funding acquisition (lead); Software (supporting).

Project: EROSPOT (DAKIS)

Last Update: 2024-11-26

Tag: Verified

Funders: The Bavarian State Ministry of Food, Agriculture and Forestry. Funding reference number: A/22/01,
BMBF funding line "Agricultural Systems of the Future", Funding reference number: 031B0729A.

Description: This script is the starting point for the whole model - it takes the watershed IDs as user inputs, and
depending on the choices made by the user, executes the 'EROSPOT' model in a continuous, discrete or single execution.
Note to the executors: Please refer to the User Guide in the Repository for detailed description of how to run the model
Website: https://erospot.zalf.de/ (Relevant information like publications/upcoming publications including
the visualisation is available in German on the website.

License: Please refer to the document titled 'License.docx' in the repository

"""

from ExecutingInVeST import start_process

'''SECTION 2.4, User Guide - Please create folders according to the descriptions in this section
of the User Guide'''


def main():
    CentralFolderPath = "E:/ErospotWorkspace"
    GDBPath = "E:/ErospotWorkspace/EROSPOT.gdb"

    # Ask user if they want to run 1 watershed or several
    watershed_choice = input(
        "Do you want to run a single watershed (1) or several watersheds (2)? Please enter 1 or 2: ").strip()

    if watershed_choice == '1':
        # Single watershed
        starting_watershed = input("Enter the watershed ID you want to run: ").strip()
        ending_watershed = starting_watershed
        list_discrete_watersheds = ''
        start_process(starting_watershed, ending_watershed, list_discrete_watersheds, CentralFolderPath, GDBPath)

    elif watershed_choice == '2':
        # Multiple watersheds
        continuous_choice = (input(
            "Do you want to run a continuous range of watersheds (1) or discrete watersheds (2)? Please enter 1 or 2: ")
                             .strip())

        if continuous_choice == '1':
            # Continuous range of watersheds
            starting_watershed = input("Enter the starting watershed ID: ").strip()
            ending_watershed = input("Enter the ending watershed ID: ").strip()
            list_discrete_watersheds = ""
            start_process(starting_watershed, ending_watershed, list_discrete_watersheds, CentralFolderPath, GDBPath)

        elif continuous_choice == '2':
            # Discrete, non-continuous watersheds
            watersheds_input = input("Enter the watershed IDs, separated by commas (e.g., 1,3,5): ").strip()
            # Create a comma-separated string of watershed IDs
            list_discrete_watersheds = watersheds_input
            # Calculate the number of discrete watersheds
            start_process('', '', list_discrete_watersheds, CentralFolderPath, GDBPath)

        else:
            print("Invalid choice. Please enter either 1 or 2.")
            return

    else:
        print("Invalid choice. Please enter either 1 or 2.")
        return

    print("Done")


if __name__ == '__main__':
    main()
