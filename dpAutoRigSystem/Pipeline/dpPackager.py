# importing libraries:
from maya import cmds


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


    def compactor(self, filePath=None, destinationFolder=None, *args):
        """
        """
        if filePath and destinationFolder:
            print("Neeeeeed frete information here to track the gps....")
        else:
            print("just make directory and zip the file to logistica.")

    
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

    
    def toDropbox(self, *args):
        """
        """
        # https://help.dropbox.com/fr-fr/installs/locate-dropbox-folder
        print("to use dropPath + / + s_dropbox + / + studio + / + project")
        return "dropbox link"



