# importing libraries:
from maya import cmds
from maya import mel
from functools import partial
from os import walk
from ..Modules.Library import dpUtils


DPPIPELINER_VERSION = 1.0

PIPE_DRIVE = "R:/"
PIPE_FOLDER = "_dpPipeline"

class Pipeliner(object):
    def __init__(self, *args):
        """ Initialize the module class loading variables.
        """
        # defining variables:

        # get folder
        # get fileName
        # get studioPath
        # get studioName
        # mount pipeData

        self.pipeData = {}
        self.studioName = None
        self.studioPath = None
        self.folder = PIPE_FOLDER

    def getAddOnsFolder(self, *args):
        #(self, *args):
        """
        """
        print("passed by here")
        return PIPE_FOLDER


    def getPipelineStudioName(self, drive=PIPE_DRIVE, *args):
        # try to find a pipeline structure
        filePath = cmds.file(query=True, sceneName=True)
        print("debug 1 filepath PIPE =", filePath)
        if filePath:
            print("debug 2 filepath =", filePath)
            if drive in filePath:
                self.studioName = filePath.split(drive)[1]
                self.studioName = self.studioName[:self.studioName.find("/")]
                self.studioPath = drive+self.studioName
                print("from pipeliner == studio data:", self.studioName, self.studioPath)
                return self.studioName, self.studioPath


    def getPipelineData(self, drive=PIPE_DRIVE, *args):
        # WIP

        self.pipeData['drive'] = "merci"

        return self.pipeData



    def mainUI(self, dpUIinst, *args):
        print ("merci")
        
        # TODO
        #
        # create a asset
        # specify the pipeline root drive
        # set a studio name
        # define ToClient, Publish, WIP folders
        # etc