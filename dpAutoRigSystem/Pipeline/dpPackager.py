# importing libraries:
from maya import cmds
import zipfile
import shutil


DPPACKAGER_VERSION = 1.0


class Packager(object):
    def __init__(self, *args):
        """ 
        """
        # define variables
        print("loaded Packager here, merci...")
        

# WIP
# 
# To DELETE:
#
#    def getPackList(self, packList=None, *args):
#        """ Verify the active checkboxes to run the packaging actions to export the files.
#            If we received a list, we just return it because we're runing all by code withou UI dependence.
#        """
#        if not packList:
#            print("generating a packList here... carretos in action!")
#            packList = ["test", "kombi", "frete"]
#        return packList


    def compactor(self, filePath=None, fileName=None, destinationFolder=None, date=None, *args):
        """
        """
        if filePath and fileName and destinationFolder and date:
            
            # WIP
            zipName = fileName[:-3]+"_"+date
            print("zipName", zipName)
            zip = zipfile.ZipFile(destinationFolder+"/"+zipName+".zip", "w", zipfile.ZIP_DEFLATED)
            zip.write(filename=filePath+"/"+fileName, arcname=fileName)
            zip.close()

            print(destinationFolder+"/"+zipName+".zip")
            return destinationFolder+"/"+zipName+".zip"
        




    
    def sendToClient(self, filePath=None, destinationFolder=None, *args):
        """
        """
        print ("delivering...")
        print("filePath =", filePath)
        print("destinationFolder =", destinationFolder)


    def imager(self, destinationFolder=None, *args):
        """
        """
        print ("Carreto's photo!")


    def history(self, filePath=None, destinationFolder=None, *args):
        """
        """
        print("history file here...")

    
    def toDropbox(self, file=None, toPath=None, host=None, *args):
        """
            # https://help.dropbox.com/fr-fr/installs/locate-dropbox-folder
            Returns Dropbox's download link
        """
        print("to use dropPath + / + s_dropbox + / + studio + / + project")
        
        if file and toPath:
            shutil.copy2(file, toPath)


            # WIP
            if host:
                dropLink = "https://www.dropbox.com/s/"+str(host)+file[file.rfind("/"):]+"?dl=1"
                return dropLink
        
        



