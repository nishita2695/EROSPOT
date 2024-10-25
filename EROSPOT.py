from IntegrationScriptINVEST import start_process

if __name__ == '__main__':
    CentralFolderPath = "E:/ErospotWorkspace"
    GDBPath = "E:/ErospotWorkspace/EROSPOT.gdb"
    starting_watershed = '4'
    ending_watershed = '5'
    No_of_watersheds = '' #int(ending_watershed)-int(starting_watershed)
    start_process(starting_watershed,ending_watershed,No_of_watersheds,CentralFolderPath, GDBPath)

    print("Done")
