# importing libraries:
from maya import cmds
import os
import json
from ..Modules.Library import dpUtils


DPPIPELINER_VERSION = 1.0

PIPE_FOLDER = "_dpPipeline"


class Pipeliner(object):
    def __init__(self, *args):
        """ Initialize the module class loading variables and store them in a dictionary.
        """
        # define variables
        self.settingsFile = "_dpPipelineSettings.json"
        self.infoFile = "dpPipelineInfo.json"
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


    def getJsonContent(self, jsonPath, *args):
        """ Open, read, close and return the json file content.
        """
        dic = open(jsonPath, "r", encoding='utf-8')
        content = json.loads(dic.read())
        dic.close()
        return content


    def getPipelinePath(self, *args):
        """ Returns the path content of the _dpPipelineSetting json file if it exists.
            Otherwise returns False.
        """
        basePath = dpUtils.findPath("dpAutoRig.py")
        basePath = basePath[:basePath.rfind("dpAutoRigSystem")+15]
        jsonPath = os.path.join(basePath, self.settingsFile).replace("\\", "/")
        if os.path.exists(jsonPath):
            content = self.getJsonContent(jsonPath)
            if content:
                if os.path.exists(content['path']):
                    return content['path']
        return False
        

    def getPipelineInfo(self, *args):
        """ Read the json info file and return the merged pipeData and it's content if it exists.
        """
        jsonInfoPath = os.path.join(self.pipeData['path'], self.infoFile).replace("\\", "/")
        if os.path.exists(jsonInfoPath):
            content = self.getJsonContent(jsonInfoPath)
            if content:
                self.pipeData = self.pipeData | content


    def getDrive(self, *args):
        """ Returns the pipeline drive if the scene is saved.
        """
        sceneName = self.pipeData['sceneName']
        if sceneName:
            return sceneName[:sceneName.find("/")+1]


    def getStudio(self, *args):
        """ Returns the pipeline studio name if there's one.
        """
        sceneName = self.pipeData['sceneName']
        if sceneName:
            studioName = sceneName.split(self.pipeData['drive'])[1]
            return studioName[:studioName.find("/")]


    def getPipelineData(self, *args):
        """ Read the dpPipelineSetting to find the pipeline info.
            Mount the pipeData dictionary and return it.
        """
        self.pipeData = {}
        # mouting pipeline data dictionary
        self.pipeData['sceneName'] = cmds.file(query=True, sceneName=True)
        self.pipeData['shortName'] = cmds.file(query=True, sceneName=True, shortName=True)
        self.pipeData['drive'] = self.getDrive()
        self.pipeData['studio'] = self.getStudio()
        # getting pipeline settings
        self.pipeData['path'] = self.getPipelinePath()
        if not self.pipeData['path']:
            self.pipeData['path'] = self.pipeData['drive']+self.pipeData['studio']+"/"+PIPE_FOLDER #dpTeam
        # merger pipeline info
        self.pipeInfo = self.getPipelineInfo()
        # mounting structured pipeline data
        self.pipeData['addOnsPath'] = self.pipeData['path']+"/"+self.pipeData['addOns']
        self.pipeData['presetsPath'] = self.pipeData['path']+"/"+self.pipeData['presets']
        return self.pipeData


    def mainUI(self, dpUIinst, *args):
        print ("merci")
        print("dpUIinst = ", dpUIinst)
        print("dpUIinst langDic = ", dpUIinst.langDic)
        
        # TODO
        #
        # create an asset
        # specify the pipeline root drive
        # set a studio name
        # define ToClient, Publish, Riggging WIP folders
        # toClientFolder with or without date subFolder to zip the file
        # create validator preset
        # etc