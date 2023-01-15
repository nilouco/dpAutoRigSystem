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


    def getJsonSettingsPath(self, *args):
        """ Returns the json path for the pipeline settings file.
        """
        basePath = dpUtils.findPath("dpAutoRig.py")
        basePath = basePath[:basePath.rfind("dpAutoRigSystem")+15]
        return os.path.join(basePath, self.settingsFile).replace("\\", "/")


    def getPipelinePath(self, *args):
        """ Returns the path content of the _dpPipelineSetting json file if it exists.
            Otherwise returns False.
        """
        jsonPath = self.getJsonSettingsPath()
        if os.path.exists(jsonPath):
            content = self.getJsonContent(jsonPath)
            if content:
                if os.path.exists(content['path']):
                    self.infoFile = content['file']
                    return content['path']
        return False
        

    def getPipelineInfo(self, *args):
        """ Read the json info file and return the merged pipeData and it's content if it exists.
        """
        self.jsonInfoPath = os.path.join(self.pipeData['path'], self.infoFile).replace("\\", "/")
        if os.path.exists(self.jsonInfoPath):
            content = self.getJsonContent(self.jsonInfoPath)
            if content:
                self.pipeData = self.pipeData | content
                return content


    def getInfoByPath(self, field, dependent, path=None, cut=False, *args):
        """ Use field as the given data to return the result about.
            Use dependent as the split data to edit the result.
            Returns the pipeline info name if there's one.
        """
        name = self.pipeData['sceneName']
        if path:
            name = path
        if name:
            if dependent:
                if self.pipeData[dependent]:
                    name = name.split(self.pipeData[dependent]+"/")[1]
            else:
                name = name[:name.find("/")]
            if cut:
                if "/" in name:
                    name = name[:name.find("/")]
            self.pipeData[field] = name
            return self.pipeData[field]


    def declareDefaultPipelineInfo(self, *args):
        """ Returns a default pipeline info data to load the UI if there isn't any.
        """
        defaultPipeInfo = {
        "name"    : "Default Pipeline Info",
        "author"  : "Danilo Pinheiro",
        "date"    : "2023-01-01",
        "updated" : "2023-01-01",
        
        "f_drive"      : "",
        "f_studio"     : "",
        "f_project"    : "",
        "f_wip"        : "Rigging/WIP",
        "f_publish"    : "Rigging/Publish",
        "f_toClient"   : "Data/ToClient",
        "s_presets"    : "dpPresets",
        "s_addOns"     : "dpAddOns",
        "s_hist"       : "Hist",
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
        "b_archive"    : True,
        "b_dateDir"    : True,
        "b_zip"        : True,
        "b_imager"     : True
        }
        return defaultPipeInfo


    def getPipelineData(self, loadedPipeInfo=None, *args):
        """ Read the dpPipelineSetting to find the pipeline info.
            Mount the pipeData dictionary and return it.
        """
        loaded = True
        if not loadedPipeInfo:
            self.pipeInfo = self.declareDefaultPipelineInfo()
            self.pipeData = {}
            self.pipeData['addOnsPath'] = False
            self.pipeData['presetsPath'] = False
            # getting pipeline settings
            self.pipeData['path'] = self.getPipelinePath()
        if not self.pipeData['path']:
            # mouting pipeline data dictionary
            self.pipeData['sceneName'] = cmds.file(query=True, sceneName=True)
            self.pipeData['shortName'] = cmds.file(query=True, sceneName=True, shortName=True)
            if self.pipeData['sceneName']:
                self.pipeData['drive'] = self.getInfoByPath("drive", None)
                self.pipeData['studio'] = self.getInfoByPath("studio", "drive", cut=True)
                self.pipeData['path'] = self.pipeData['drive']+"/"+self.pipeData['studio']+"/"+PIPE_FOLDER #dpTeam
                if not os.path.exists(self.pipeData['path']):
                    self.pipeData['drive'] = ""
                    self.pipeData['studio'] = ""
                    self.pipeData['path'] = ""
                    loaded = False
            else:
                loaded = False
        if loaded:
            # merge pipeline info
            self.pipeInfo = self.getPipelineInfo()
            if self.pipeInfo:
                # mounting structured pipeline data
                self.pipeData['addOnsPath'] = self.pipeData['path']+"/"+self.pipeData['s_addOns']
                self.pipeData['presetsPath'] = self.pipeData['path']+"/"+self.pipeData['s_presets']
            else:
                print('Not found', self.infoFile)
        return self.pipeData


    def conformLoadedInfo(self, key, resultInfoList, *args):
        """ Edit the loaded info to conform the splited data correctly.
        """
        conformInfo = resultInfoList[0].replace("\\", "/")
        if key == "f_drive":
            conformInfo = self.getInfoByPath("drive", None, conformInfo)
        elif key == "f_studio":
            conformInfo = self.getInfoByPath("studio", "drive", conformInfo, cut=True)
        elif key == "f_project":
            conformInfo = self.getInfoByPath("project", "studio", conformInfo, cut=True)
        elif key == "f_wip":
            conformInfo = self.getInfoByPath("wip", "project", conformInfo)
        elif key == "f_publish":
            conformInfo = self.getInfoByPath("publish", "project", conformInfo)
        elif key == "f_toClient":
            conformInfo = self.getInfoByPath("toClient", "project", conformInfo)
        return conformInfo

    
    def loadInfoKey(self, key, *args):
        """ Method called by the Pipeliner UI button to load the info about the key.
        """
        resultInfoList = cmds.fileDialog2(fileMode=3, dialogStyle=2)
        if resultInfoList:
            conformInfo = self.conformLoadedInfo(key, resultInfoList)
            cmds.textFieldButtonGrp(self.infoUI[key], edit=True, text=conformInfo)


    def mainUI(self, dpUIinst=None, loadedFileInfo=False, *args):
        """ Open an UI to load, set and save the pipeline info.
        """
        dpUtils.closeUI('dpPipelinerWindow')
        if dpUIinst:
            self.dpUIinst = dpUIinst
            self.langDic = dpUIinst.langDic
            self.langName = dpUIinst.langName
        self.getPipelineData(loadedFileInfo)
        # window
        pipeliner_winWidth  = 380
        pipeliner_winHeight = 480
        cmds.window('dpPipelinerWindow', title="Pipeliner "+str(DPPIPELINER_VERSION), widthHeight=(pipeliner_winWidth, pipeliner_winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        cmds.showWindow('dpPipelinerWindow')
        # create UI layout and elements:
        self.pipelinerLayout = cmds.columnLayout('self.pipelinerLayout', adjustableColumn=True, columnOffset=("both", 10))
        # pipeline info
        pipelineInfoLayout = cmds.columnLayout('pipelineInfoLayout', adjustableColumn=True, columnOffset=("left", 10), parent=self.pipelinerLayout)
        cmds.separator(style='in', height=20, parent=pipelineInfoLayout)
        cmds.text('pipelineInfo', label="Pipeline "+self.langDic[self.langName]['i013_info'], height=30, font='boldLabelFont', parent=pipelineInfoLayout)
        pathData = self.getPathData()
        self.pathDataTBG = cmds.textFieldButtonGrp('pathDataTBG', label=self.langDic[self.langName]['i220_filePath'], text=pathData, buttonLabel=self.langDic[self.langName]['i187_load'], buttonCommand=self.loadPipeInfo, changeCommand=partial(self.loadPipeInfo, True), adjustableColumn=2, parent=pipelineInfoLayout)
        cmds.separator(style='in', height=20, parent=pipelineInfoLayout)
        # pipeline data
        cmds.text('pipelineData', height=30, label="Pipeline Data", font='boldLabelFont', parent=pipelineInfoLayout)
        self.pipelineScrollLayout = cmds.scrollLayout('pipelineScrollLayout', parent=self.pipelinerLayout)
        self.pipelineDataLayout = cmds.columnLayout('pipelineDataLayout', adjustableColumn=True, width=400, columnOffset=("left", 10), parent=self.pipelineScrollLayout)
        self.pipelineSaveLayout = cmds.columnLayout('pipelineSaveLayout', adjustableColumn=True, width=400, columnOffset=("left", 10), parent=self.pipelinerLayout)
        # load data from pipeline info
        self.loadUIData()


    def loadUIData(self, *args):
        """ Populate the UI with loaded data file info.
        """
        cmds.deleteUI(self.pipelineDataLayout)
        cmds.deleteUI(self.pipelineSaveLayout)
        self.pipelineDataLayout = cmds.columnLayout('pipelineDataLayout', adjustableColumn=True, width=400, columnOffset=("left", 10), parent=self.pipelineScrollLayout)
        if self.pipeInfo:
            self.infoUI = {}
            for key in list(self.pipeInfo):
                if "_" in key:
                    if key.startswith("f_"):
                        self.infoUI[key] = cmds.textFieldButtonGrp(key, label=key[2:], text=self.pipeInfo[key], buttonLabel=self.langDic[self.langName]['i187_load'], buttonCommand=partial(self.loadInfoKey, key), adjustableColumn=2, parent=self.pipelineDataLayout)
                    elif key.startswith("i_"):
                        self.infoUI[key] = cmds.intFieldGrp(key, label=key[2:], value1=self.pipeInfo[key], numberOfFields=1, parent=self.pipelineDataLayout)
                    elif key.startswith("b_"):
                        self.infoUI[key] = cmds.checkBox(key, label=key[2:], value=self.pipeInfo[key], parent=self.pipelineDataLayout)
                    elif key.startswith("s_"):
                        self.infoUI[key] = cmds.textFieldGrp(key, label=key[2:], text=self.pipeInfo[key], parent=self.pipelineDataLayout)
            # try to force loading empty data info
            try:
                if self.pipeData['sceneName']:
                    if not cmds.textFieldButtonGrp(self.infoUI['f_drive'], query=True, text=True):
                        self.pipeData['drive'] = self.getInfoByPath("drive", None)
                        cmds.textFieldButtonGrp(self.infoUI['f_drive'], edit=True, text=self.pipeData['drive'])
                    if not cmds.textFieldButtonGrp(self.infoUI['f_studio'], query=True, text=True):
                        self.pipeData['studio'] = self.getInfoByPath("studio", "drive", cut=True)
                        cmds.textFieldButtonGrp(self.infoUI['f_studio'], edit=True, text=self.pipeData['studio'])
                    if not cmds.textFieldButtonGrp(self.infoUI['f_project'], query=True, text=True):
                        self.pipeData['project'] = self.getInfoByPath("project", "studio", cut=True)
                        cmds.textFieldButtonGrp(self.infoUI['f_project'], edit=True, text=self.pipeData['project'])
            except:
                pass
            self.pipelineSaveLayout = cmds.columnLayout('pipelineSaveLayout', adjustableColumn=True, width=400, columnOffset=("left", 10), parent=self.pipelinerLayout)
            cmds.separator(style='in', height=20, parent=self.pipelineSaveLayout)
            cmds.button('savePipeInfoBT', label=self.langDic[self.langName]['i222_save'], command=self.savePipeInfo, backgroundColor=(0.75, 0.75, 0.75), parent=self.pipelineSaveLayout)
        else:
            pathData = self.getPathData()
            cmds.text(pathData, parent=self.pipelineDataLayout)


    def getPathData(self, *args):
        """ Returns the concatenated path and info file name.
        """
        pathData = self.langDic[self.langName]['i062_notFound']
        if self.pipeInfo and self.pipeData['path']:
            pathData = self.pipeData['path']+"/"+self.infoFile
        return pathData


    def loadPipeInfo(self, loaded=None, *args):
        """ Update the Pipeliner UI data section with loaded info file.
        """
        loadedFilePathList = None
        if loaded:
            loaded = cmds.textFieldButtonGrp(self.pathDataTBG, query=True, text=True)
            if loaded.endswith('.json'):
                loaded = loaded.replace("\\", "/")
                if os.path.exists(loaded):
                    loadedFilePathList = [loaded]
        else:
            loadedFilePathList = cmds.fileDialog2(fileFilter='*.json', fileMode=1, dialogStyle=2)
        if loadedFilePathList:
            loadedFilePath = loadedFilePathList[0].replace("\\", "/")
            self.pipeData['path'] = loadedFilePath[:loadedFilePath.rfind("/")]
            self.infoFile = loadedFilePath[loadedFilePath.rfind("/")+1:]
            cmds.textFieldButtonGrp(self.pathDataTBG, edit=True, text=loadedFilePath)
            self.getPipelineData(self.infoFile)
            self.loadUIData()
            self.setPipelineSettingsPath(self.pipeData['path'], self.infoFile)

    
    def setPipelineSettingsPath(self, path, file, *args):
        """ Set the json file for dpPipelineSetting in the main dpAutoRigSystem folder to use the path and file given.
        """
        if path and file:
            jsonPath = self.getJsonSettingsPath()
            if os.path.exists(jsonPath):
                settingsDic = self.getJsonContent(jsonPath)
                settingsDic['path'] = self.pipeData['path']
                settingsDic['file'] = self.infoFile
                # write json file in the HD
                with open(jsonPath, 'w') as jsonFile:
                    json.dump(settingsDic, jsonFile, indent=4, sort_keys=True)

    
    def getUIDataToSave(self, *args):
        """ Read the UI fields and load them values in the pipeData dictionary.
        """
        for k, key in enumerate(list(self.infoUI)):
            if key.startswith("f_"):
                self.pipeData[key] = cmds.textFieldButtonGrp(self.infoUI[key], query=True, text=True)
            elif key.startswith("i_"):
                self.pipeData[key] = cmds.intFieldGrp(self.infoUI[key], query=True, value1=True)
            elif key.startswith("b_"):
                self.pipeData[key] = cmds.checkBox(self.infoUI[key], query=True, value=True)
            elif key.startswith("s_"):
                self.pipeData[key] = cmds.textFieldGrp(self.infoUI[key], query=True, text=True)


    def setPipelineInfoFile(self, *args):
        """ Save the pipeline info file with all pipeData into a json file.
        """
        outFile = open(self.pipeData['path']+"/"+self.infoFile, "w")
        json.dump(self.pipeData, outFile, indent=4)
        outFile.close()


    def savePipeInfo(self, *args):
        """ Save the pipeline data into the json file in the HD.
            Write the pipeline data path in the pipeline setting json file.
        """
        self.getUIDataToSave()
        pathDataFromUI = cmds.textFieldButtonGrp(self.pathDataTBG, query=True, text=True)
        if pathDataFromUI:
            if "/" in pathDataFromUI:
                self.pipeData['path'] = pathDataFromUI[:pathDataFromUI.rfind("/")]
            if pathDataFromUI.endswith(".json"):
                self.infoFile = pathDataFromUI[pathDataFromUI.rfind("/")+1:]
        if self.pipeData['path'] and self.infoFile:
            if not os.path.exists(self.pipeData['path']):
                os.makedirs(self.pipeData['path'])
            self.setPipelineInfoFile()
            self.setPipelineSettingsPath(self.pipeData['path'], self.infoFile)
#           dpUIinst.jobReloadUI()
        else:
            print("Unexpected Error: There's no pipeline data to save, sorry.")





    # WIP
    # relative or absolute paths ???
    #
    #
    # TODO
    # process data before output json file
    # process data to find good concatenations to help getters
    # process data to create subfolders
    # process data to store relavante info to getters like publishPath, createAsset folder, fileName to save published file, etc
    #
    #
    # TODO
    #
    # create an asset
    # define ToClient, Publish, Riggging WIP folders
    # toClientFolder with or without date subFolder to zip the file
    # etc
    #
    # after save data, reload pipeData using getPipelineData ???
    # after save data, reload the UI using the dpUIinst.jobReloadUI() ???
    #
    #
    #