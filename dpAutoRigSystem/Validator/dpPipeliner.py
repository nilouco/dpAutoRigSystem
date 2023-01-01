# importing libraries:
from maya import cmds
from maya import mel
from functools import partial
from os import walk
from ..Modules.Library import dpUtils


DPPIPELINER_VERSION = 1.0

PIPE_FOLDER = "_dpPipeline"


class Pipeliner(object):
    def __init__(self, *args):
        """ Initialize the module class loading variables and store them in a dictionary.
        """
        # define variables
        self.pipeData = self.getPipelineData()
        




    def checkSavedScene(self, *args):
        """ Check if the current scene is saved to return True.
            Otherwise return False.
        """
        scenePath = cmds.file(query=True, sceneName=True)
        modifiedScene = cmds.file(query=True, modified=True)
        if not scenePath or modifiedScene:
            return False
        return True


    def getPipelineFolder(self, *args):
        """
        """
        print("wip getPipelineFolder here....")
        # WIP
        





    def getDrive(self, *args):
        """
        """
        sceneName = self.pipeData['sceneName']
        if sceneName:
            return sceneName[:sceneName.find("/")+1]


    def getStudio(self, *args):
        """
        """
        sceneName = self.pipeData['sceneName']
        if sceneName:
            studioName = sceneName.split(self.pipeData['drive'])[1]
            return studioName[:studioName.find("/")]


    def getPipelineData(self, *args):
        """
        """

        self.pipeData = {}
        if self.checkSavedScene():
            # getting pipeline info
            pipeFolder = self.getPipelineFolder()
            if pipeFolder:
                self.pipeData['folder'] = PIPE_FOLDER
            else:
                self.pipeData['folder'] = PIPE_FOLDER

            # mouting pipeline data dictionary
            self.pipeData['sceneName'] = cmds.file(query=True, sceneName=True)
            self.pipeData['shortName'] = cmds.file(query=True, sceneName=True, shortName=True)
            self.pipeData['drive'] = self.getDrive()
            self.pipeData['studio'] = self.getStudio()
            
            
            # mounting structured pipeline data
            self.pipeData['addOnsFolder'] = self.pipeData['drive']+self.pipeData['studio']+"/"+self.pipeData['folder']


            print("DRIVE = ", self.pipeData['drive'])
            print("STUDIO = ", self.pipeData['studio'])


        return self.pipeData



    def mainUI(self, *args):
        print ("merci")
        
        # TODO
        #
        # create an asset
        # specify the pipeline root drive
        # set a studio name
        # define ToClient, Publish, Riggging WIP folders
        # toClientFolder with or without date subFolder to zip the file
        # etc