# importing libraries:
from maya import cmds
import os
import json
from functools import partial
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
                return content


    def getDriveByPath(self, *args):
        """ Returns the pipeline drive if the scene is saved.
        """
        sceneName = self.pipeData['sceneName']
        if sceneName:
            return sceneName[:sceneName.find("/")+1]


    def getStudioByPath(self, *args):
        """ Returns the pipeline studio name if there's one.
        """
        sceneName = self.pipeData['sceneName']
        if sceneName:
            studioName = sceneName.split(self.pipeData['drive'])[1]
            return studioName[:studioName.find("/")]


    def getProjectByPath(self, *args):
        """ Returns the pipeline project name if there's one.
        """
        sceneName = self.pipeData['sceneName']
        if sceneName:
            projectName = sceneName.split(self.pipeData['studio']+"/")[1]
            return projectName[:projectName.find("/")]


    def declareDefaultPipelineInfo(self, *args):
        """
        """
        defaultPipeInfo = {
        "name"    : "Default Pipeline Info",
        "author"  : "Danilo Pinheiro",
        "date"    : "2023-01-01",
        "updated" : "2023-01-01",
        
        "f_drive"      : "",
        "f_studio"     : "",
        "f_project"    : "",
        "f_presets"    : "dpPresets",
        "f_addOns"     : "dpAddOns",
        "f_wip"        : "Rigging/WIP",
        "f_publish"    : "Rigging/Publish",
        "f_toClient"   : "Data/ToClient",
        "f_hist"       : "Hist",
        "s_prefix"     : "",
        "s_middle"     : "_rig_v",
        "s_suffix"     : "",
        "s_model"      : "_m",
        "s_rig"        : "_v",
        "s_type"       : "mayaAscii",
        "i_padding"    : 3,
        "b_capitalize" : False,
        "b_upper"      : False,
        "b_lower"      : False,
        "b_assetDir"   : True,
        "b_dateDir"    : True,
        "b_zip"        : True,
        "b_imager"     : True
        }

        return defaultPipeInfo



    def getPipelineData(self, *args):
        """ Read the dpPipelineSetting to find the pipeline info.
            Mount the pipeData dictionary and return it.
        """
        loaded = True
        self.pipeInfo = self.declareDefaultPipelineInfo()
        self.pipeData = {}
        self.pipeData['addOnsPath'] = False
        self.pipeData['presetsPath'] = False
        # mouting pipeline data dictionary
        self.pipeData['sceneName'] = cmds.file(query=True, sceneName=True)
        self.pipeData['shortName'] = cmds.file(query=True, sceneName=True, shortName=True)
        # getting pipeline settings
        self.pipeData['path'] = self.getPipelinePath()
        if not self.pipeData['path']:
            if self.pipeData['sceneName']:
                self.pipeData['drive'] = self.getDriveByPath()
                self.pipeData['studio'] = self.getStudioByPath()
                self.pipeData['path'] = self.pipeData['drive']+self.pipeData['studio']+"/"+PIPE_FOLDER #dpTeam
                if not os.path.exists(self.pipeData['path']):
                    loaded = False
            else:
                loaded = False
        if loaded:
            # merger pipeline info
            self.pipeInfo = self.getPipelineInfo()
            # mounting structured pipeline data
            self.pipeData['addOnsPath'] = self.pipeData['path']+"/"+self.pipeData['f_addOns']
            self.pipeData['presetsPath'] = self.pipeData['path']+"/"+self.pipeData['f_presets']
        return self.pipeData


    def loadInfoKey(self, key, *args):
        """
        """
        print("loading here key =", key)




    def mainUI(self, dpUIinst, *args):
        """
        """
        print ("merci... WIP")
        
        self.langDic = dpUIinst.langDic
        self.langName = dpUIinst.langName

        dpUtils.closeUI('dpPipelinerWindow')
        # window
        pipeliner_winWidth  = 380
        pipeliner_winHeight = 300
        cmds.window('dpPipelinerWindow', title="Pipeliner "+str(DPPIPELINER_VERSION), widthHeight=(pipeliner_winWidth, pipeliner_winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        cmds.showWindow('dpPipelinerWindow')
        # create UI layout and elements:
        pipelinerLayout = cmds.columnLayout('pipelinerLayout', adjustableColumn=True, columnOffset=("both", 10))
        cmds.separator(style="none", parent=pipelinerLayout)

        pipelinerLayoutA = cmds.rowColumnLayout('pipelinerLayoutA', numberOfColumns=2, columnWidth=[(1, 100), (2, 280)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'both', 5), (2, 'both', 5)], rowSpacing=[(1, 5), (2, 5), (3, 5)], parent=pipelinerLayout)
        if self.pipeInfo:
            self.infoUI = {}
            for key in list(self.pipeInfo):
                if "_" in key:
                    if key.startswith("f_"):
                        self.infoUI[key] = cmds.textFieldButtonGrp(key, label=key[2:], text=self.pipeInfo[key], buttonLabel=self.langDic[self.langName]['i187_load'], buttonCommand=partial(self.loadInfoKey, key), adjustableColumn=2, parent=pipelinerLayout)
                    elif key.startswith("i_"):
                        self.infoUI[key] = cmds.intFieldGrp(key, label=key[2:], value1=self.pipeInfo[key], numberOfFields=1, parent=pipelinerLayout)
                    elif key.startswith("b_"):
                        self.infoUI[key] = cmds.checkBox(key, label=key[2:], value=self.pipeInfo[key], parent=pipelinerLayout)
                    elif key.startswith("s_"):
                        self.infoUI[key] = cmds.textFieldGrp(key, label=key[2:], text=self.pipeInfo[key], parent=pipelinerLayout)
            # try to force loading empty data info
            if self.pipeData['sceneName']:
                if not cmds.textFieldButtonGrp(self.infoUI['f_drive'], query=True, text=True):
                    self.pipeData['drive'] = self.getDriveByPath()
                    cmds.textFieldButtonGrp(self.infoUI['f_drive'], edit=True, text=self.pipeData['drive'])
                if not cmds.textFieldButtonGrp(self.infoUI['f_studio'], query=True, text=True):
                    self.pipeData['studio'] = self.getStudioByPath()
                    cmds.textFieldButtonGrp(self.infoUI['f_studio'], edit=True, text=self.pipeData['studio'])
                if not cmds.textFieldButtonGrp(self.infoUI['f_project'], query=True, text=True):
                    self.pipeData['project'] = self.getProjectByPath()
                    cmds.textFieldButtonGrp(self.infoUI['f_project'], edit=True, text=self.pipeData['project'])
        

        

        
        # TODO
        #
        # create an asset
        # specify the pipeline root drive
        # set a studio name
        # define ToClient, Publish, Riggging WIP folders
        # toClientFolder with or without date subFolder to zip the file
        # create validator preset
        # etc
        #
        # after save data, reload pipeData using getPipelineData ?
        
        #dpUtils.closeUI('dpPipelinerWindow')
