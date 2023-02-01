# importing libraries:
from maya import cmds
import zipfile
import shutil
import os


DPPACKAGER_VERSION = 1.0


class Packager(object):
    def __init__(self, *args):
        """ 
        """
        # define variables
        print("loaded Packager here, merci...")


    def zipToClient(self, filePath, fileName, destinationFolder, date=None, *args):
        """ Create a zipped file with given filePath and fileName replacing the extention (.ma or .mb) to .zip
            Add date at the end of the file if it's given.
            Write the zip file in the destinationFolder.
            Returns the zipFilePathName.
        """
        if date:
            zipName = fileName[:-3]+"_"+date+".zip"
        else:
            zipName = fileName[:-3]+".zip"
        zip = zipfile.ZipFile(destinationFolder+"/"+zipName, "w", zipfile.ZIP_DEFLATED)
        zip.write(filename=filePath+"/"+fileName, arcname=fileName)
        zip.close()
        return destinationFolder+"/"+zipName
        




    
    
    def imager(self, destinationFolder=None, *args):
        """
        """
        print ("Carreto's photo!")


    def toHistory(self, scenePath, fileShortName, destinationFolder, *args):
        """ List all Maya scene files in the given scenePath.
            Put all found Maya scene file into the given destinationFolder, except the current given fileShortName.
        """
        sceneList = []
        folderContentObj = os.scandir(scenePath)
        for entry in folderContentObj :
            if entry.is_file():
                if not entry.name == fileShortName:
                    sceneList.append(entry.name)
        if sceneList:
            for item in sceneList:
                shutil.move(scenePath+"/"+item, destinationFolder)

    
    def toDropbox(self, file, toPath, *args):
        """ Just copy the zipped file to the destination path.
            TODO: Returns Dropbox's download link
        """        
        if file and toPath:
            shutil.copy2(file, toPath)

            # WIP
            #if host:
                #dropLink = "https://dl.dropboxusercontent.com/u/"+str(host)+file[file.rfind("/"):]+"?dl=1"
                #return dropLink
