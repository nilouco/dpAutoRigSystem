# importing libraries:
from maya import cmds
from ..Modules.Library import dpUtils
from functools import partial
import os
import json
import time

PIPE_FOLDER = "_dpPipeline"
DISCORD_URL = "https://discord.com/api/webhooks"

DP_PIPELINER_VERSION = 1.10


class Pipeliner(object):
    def __init__(self, *args):
        """ Initialize the module class loading variables and store them in a dictionary.
        """
        # define variables
        self.utils = dpUtils.Utils()
        self.settingsFile = "_dpPipelineSettings.json"
        self.infoFile = "dpPipelineInfo.json"
        self.webhookFile = "dpWebhook.json"
        self.hookFile = "dpHook.json"
        self.callbackFile = "dpPublishCallback.py"
        self.pipeData = self.getPipelineData()
        self.declarePipelineAnnotation()
        

    def getToday(self, *args):
        """ Just returns the date like 1980-11-13
        """
        return time.strftime("%Y-%m-%d", time.localtime())
    

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
        basePath = self.utils.findPath("dpAutoRig.py")
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
        
    
    def updateDataByJsonPath(self, jsonPath, *args):
        """ Read the json file and return the merged pipeData and it's content if it exists.
        """
        if os.path.exists(jsonPath):
            content = self.getJsonContent(jsonPath)
            if content:
                self.pipeData.update(content)
                return content
            

    def getPipelineInfo(self, *args):
        """ Load PipelineInfo data and returns it.
        """
        jsonInfoPath = os.path.join(self.pipeData['path'], self.infoFile).replace("\\", "/")
        return self.updateDataByJsonPath(jsonInfoPath)


    def getHookInfo(self, *args):
        """ Load Hook data and returns it.
        """
        jsonHookPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.hookFile).replace("\\", "/")
        return self.updateDataByJsonPath(jsonHookPath)


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
                    try:
                        name = name.split(self.pipeData[dependent]+"/")[1]
                    except:
                        self.pipeData[field] = ""
                        self.pipeData[dependent] = ""
                        return self.pipeData[field]
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
        "updated" : "2024-02-13",
        
        "f_drive"          : "",
        "f_studio"         : "",
        "f_project"        : "",
        "f_wip"            : "Rigging/WIP",
        "f_publish"        : "Rigging/Published",
        "f_toClient"       : "Data/ToClient",
        "s_presets"        : "dpPresets",
        "s_addOns"         : "dpAddOns",
        "s_hist"           : "dpData/dpHist",
        "s_modelIO"        : "dpData/dpModel",
        "s_checkinIO"      : "dpData/dpCheckin",
        "s_shaderIO"       : "dpData/dpShader",
        "s_guideIO"        : "dpData/dpGuide",
        "s_controlShapeIO" : "dpData/dpControlShape",
        "s_skinningIO"     : "dpData/dpSkinning",
        "s_parentIO"       : "dpData/dpParent",
        "s_old"            : "dpOld",
        "s_dropbox"        : "Job",
        "s_webhook"        : "",
        "s_callback"       : "",
        "s_prefix"         : "",
        "s_middle"         : "_rig_v",
        "s_suffix"         : "",
        "s_model"          : "_m",
        "s_rig"            : "_v",
        "i_padding"        : 3,
        "b_capitalize"     : False,
        "b_upper"          : False,
        "b_lower"          : False,
        "b_deliver"        : True,
        "b_dateDir"        : True,
        "b_assetDir"       : True,
        "b_archive"        : True,
        "b_zip"            : True,
        "b_cloud"          : True,
        "b_discord"        : True,
        "b_imager"         : True,
        "b_i_maya"         : True,
        "b_i_version"      : True,
        "b_i_studio"       : True,
        "b_i_project"      : True,
        "b_i_asset"        : True,
        "b_i_model"        : True,
        "b_i_wip"          : True,
        "b_i_publish"      : True,
        "b_i_date"         : True,
        "b_i_degrade"      : True        
        }
        return defaultPipeInfo


    def declarePipelineAnnotation(self, *args):
        """ Just declare a member variable to get the pipeline annotation data to search the values in the language dictionary.
        """
        self.pipelineAnnotaion = {
        "name"    : "Default Pipeline Annotation",
        "author"  : "Danilo Pinheiro",
        "date"    : "2023-02-09",
        "updated" : "2024-02-13",
        
        "f_drive"          : "i228_fDriveAnn",
        "f_studio"         : "i229_fStudioAnn",
        "f_project"        : "i230_fProjectAnn",
        "f_wip"            : "i231_fWipAnn",
        "f_publish"        : "i232_fPublishAnn",
        "f_toClient"       : "i233_fToClientAnn",
        "s_presets"        : "i234_sPresetsAnn",
        "s_addOns"         : "i235_sAddOnsAnn",
        "s_hist"           : "i236_sHistAnn",
        "s_modelIO"        : "i293_sModelIOAnn",
        "s_checkinIO"      : "i301_sCheckinIOAnn",
        "s_shaderIO"       : "i294_sShaderIOAnn",
        "s_guideIO"        : "i295_sGuideIOAnn",
        "s_controlShapeIO" : "i296_sControlShapeIOAnn",
        "s_skinningIO"     : "i297_sSkinningIOAnn",
        "s_parentIO"       : "i300_sParentIOAnn",
        "s_old"            : "i237_sOldAnn",
        "s_dropbox"        : "i238_sDropboxAnn",
        "s_prefix"         : "i239_sPrefixAnn",
        "s_middle"         : "i240_sMiddleAnn",
        "s_suffix"         : "i241_sSuffixAnn",
        "s_model"          : "i242_sModelAnn",
        "s_rig"            : "i243_sRigAnn",
        "i_padding"        : "i245_iPaddingAnn",
        "b_capitalize"     : "i246_bCaptalizeAnn",
        "b_upper"          : "i247_bUpperAnn",
        "b_lower"          : "i248_bLowerAnn",
        "b_deliver"        : "i249_bDeliverAnn",
        "b_dateDir"        : "i250_bDateDirAnn",
        "b_assetDir"       : "i251_bAssetDirAnn",
        "b_archive"        : "i252_bArchiveAnn",
        "b_zip"            : "i253_bZipAnn",
        "b_cloud"          : "i254_bCloudAnn",
        "b_imager"         : "i255_bImagerAnn",
        "b_i_maya"         : "i269_biMaya",
        "b_i_version"      : "i256_biVersionAnn",
        "b_i_studio"       : "i257_biStudioAnn",
        "b_i_project"      : "i258_biProjectAnn",
        "b_i_asset"        : "i259_biAssetAnn",
        "b_i_model"        : "i260_biModelAnn",
        "b_i_wip"          : "i261_biRigAnn",
        "b_i_publish"      : "i262_biPublishAnn",
        "b_i_date"         : "i263_biDateAnn",
        "b_i_degrade"      : "i264_biDegradeAnn",
        "s_webhook"        : "i277_sWebhookAnn",
        "b_discord"        : "i278_bDiscordAnn",
        "s_callback"       : "i284_sCallbackAnn"
        }


    def getPipelineData(self, loadedPipeInfo=None, *args):
        """ Read the dpPipelineSetting to find the pipeline info.
            Mount the pipeData dictionary and return it.
        """
        loaded = True
        if not loadedPipeInfo:
            self.pipeInfo = self.declareDefaultPipelineInfo()
            self.pipeData = self.pipeInfo
            self.pipeData['publishPath'] = False
            self.pipeData['addOnsPath'] = False
            self.pipeData['presetsPath'] = False
            # getting pipeline settings
            self.pipeData['path'] = self.getPipelinePath()
        self.pipeData['sceneName'] = cmds.file(query=True, sceneName=True)
        self.pipeData['shortName'] = cmds.file(query=True, sceneName=True, shortName=True)
        if not self.pipeData['path']:
            # mouting pipeline data dictionary
            if self.pipeData['sceneName']:
                self.getInfoByPath("f_drive", None)
                if not self.pipeData['sceneName'] == self.pipeData['f_drive']+"/"+self.pipeData['shortName']:
                    self.getInfoByPath("f_studio", "f_drive", cut=True)
                    self.getInfoByPath("f_project", "f_studio", cut=True)
                self.pipeData['path'] = self.pipeData['f_drive']+"/"+self.pipeData['f_studio']+"/"+PIPE_FOLDER #dpTeam
                if not os.path.exists(self.pipeData['path']):
                    self.pipeData['f_drive'] = ""
                    self.pipeData['f_studio'] = ""
                    self.pipeData['f_project'] = ""
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
                self.pipeInfo = self.declareDefaultPipelineInfo()
                print('Not found', self.infoFile)
        self.getHookInfo()
        return self.pipeData


    def conformLoadedInfo(self, key, resultInfoList, *args):
        """ Edit the loaded info to conform the splited data correctly.
        """
        conformInfo = resultInfoList[0].replace("\\", "/")
        if key == "f_drive":
            conformInfo = self.getInfoByPath("f_drive", None, conformInfo)
        elif key == "f_studio":
            conformInfo = self.getInfoByPath("f_studio", "f_drive", conformInfo, cut=True)
        elif key == "f_project":
            conformInfo = self.getInfoByPath("f_project", "f_studio", conformInfo, cut=True)
        elif key == "f_wip":
            conformInfo = self.getInfoByPath("f_wip", "f_project", conformInfo)
        elif key == "f_publish":
            conformInfo = self.getInfoByPath("f_publish", "f_project", conformInfo)
        elif key == "f_toClient":
            conformInfo = self.getInfoByPath("f_toClient", "f_project", conformInfo)
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
        self.utils.closeUI('dpPipelinerWindow')
        self.getPipelineData(loadedFileInfo)
        # window
        if dpUIinst:
            self.dpUIinst = dpUIinst
            pipeliner_winWidth  = 380
            pipeliner_winHeight = 480
            cmds.window('dpPipelinerWindow', title="Pipeliner "+str(DP_PIPELINER_VERSION), widthHeight=(pipeliner_winWidth, pipeliner_winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
            cmds.showWindow('dpPipelinerWindow')
            # create UI layout and elements:
            self.pipelinerLayout = cmds.columnLayout('self.pipelinerLayout', adjustableColumn=True, columnOffset=("both", 10))
            # pipeline info
            pipelineInfoLayout = cmds.columnLayout('pipelineInfoLayout', adjustableColumn=True, columnOffset=("left", 10), parent=self.pipelinerLayout)
            cmds.separator(style='in', height=20, parent=pipelineInfoLayout)
            cmds.text('pipelineInfo', label="Pipeline "+self.dpUIinst.lang['i013_info'], height=30, font='boldLabelFont', parent=pipelineInfoLayout)
            pathData = self.getPathData()
            self.pathDataTBG = cmds.textFieldButtonGrp('pathDataTBG', label=self.dpUIinst.lang['i220_filePath'], text=pathData, buttonLabel=self.dpUIinst.lang['i187_load'], buttonCommand=self.loadPipeInfo, changeCommand=partial(self.loadPipeInfo, True), adjustableColumn=2, parent=pipelineInfoLayout)
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
                        self.infoUI[key] = cmds.textFieldButtonGrp(key, label=key[2:], text=self.pipeInfo[key], annotation=self.dpUIinst.lang[self.pipelineAnnotaion[key]], buttonLabel=self.dpUIinst.lang['i187_load'], buttonCommand=partial(self.loadInfoKey, key), adjustableColumn=2, parent=self.pipelineDataLayout)
                    elif key.startswith("i_"):
                        self.infoUI[key] = cmds.intFieldGrp(key, label=key[2:], value1=self.pipeInfo[key], annotation=self.dpUIinst.lang[self.pipelineAnnotaion[key]], numberOfFields=1, parent=self.pipelineDataLayout)
                    elif key.startswith("b_"):
                        self.infoUI[key] = cmds.checkBox(key, label=key[2:], value=self.pipeInfo[key], annotation=self.dpUIinst.lang[self.pipelineAnnotaion[key]], parent=self.pipelineDataLayout)
                    elif key.startswith("s_"):
                        self.infoUI[key] = cmds.textFieldGrp(key, label=key[2:], text=self.pipeInfo[key], annotation=self.dpUIinst.lang[self.pipelineAnnotaion[key]], parent=self.pipelineDataLayout)
            # try to force loading empty data info
            try:
                if self.pipeData['sceneName']:
                    if not cmds.textFieldButtonGrp(self.infoUI['f_drive'], query=True, text=True):
                        self.getInfoByPath("f_drive", None)
                        cmds.textFieldButtonGrp(self.infoUI['f_drive'], edit=True, text=self.pipeData['f_drive'])
                    if not cmds.textFieldButtonGrp(self.infoUI['f_studio'], query=True, text=True):
                        self.getInfoByPath("f_studio", "f_drive", cut=True)
                        cmds.textFieldButtonGrp(self.infoUI['f_studio'], edit=True, text=self.pipeData['f_studio'])
                    if not cmds.textFieldButtonGrp(self.infoUI['f_project'], query=True, text=True):
                        self.getInfoByPath("f_project", "f_studio", cut=True)
                        cmds.textFieldButtonGrp(self.infoUI['f_project'], edit=True, text=self.pipeData['f_project'])
            except:
                pass
            self.pipelineSaveLayout = cmds.columnLayout('pipelineSaveLayout', adjustableColumn=True, width=400, columnOffset=("left", 10), parent=self.pipelinerLayout)
            cmds.separator(style='in', height=20, parent=self.pipelineSaveLayout)
            cmds.button('savePipeInfoBT', label=self.dpUIinst.lang['i222_save'], command=self.savePipeInfo, backgroundColor=(0.75, 0.75, 0.75), parent=self.pipelineSaveLayout)
        else:
            pathData = self.getPathData()
            cmds.text(pathData, parent=self.pipelineDataLayout)


    def getPathData(self, *args):
        """ Returns the concatenated path and info file name.
        """
        pathData = self.dpUIinst.lang['i062_notFound']
        if self.pipeInfo and self.pipeData['path']:
            pathData = self.pipeData['path']+"/"+self.infoFile
        return pathData


    def loadPublishPath(self, *args):
        """ Returns the absolute path to publish the current file.
        """
        if self.pipeData['path']:
            projectFolder = self.pipeData['f_project']
            if projectFolder:
                projectFolder += "/"
            else:
                # try to find the project name by scene path
                projectFolder = self.pipeData['sceneName'][self.pipeData['sceneName'].rfind(self.pipeData['f_studio'])+len(self.pipeData['f_studio'])+1:self.pipeData['sceneName'].rfind(self.pipeData['f_wip'])]
            self.pipeData['publishPath'] = self.pipeData['f_drive']+"/"+self.pipeData['f_studio']+"/"+projectFolder+self.pipeData['f_publish']
            return self.pipeData['publishPath']
        else:
            print("Not found dpPipelineInfo.json file to setup the publishing data, sorry.")


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
            Except the current scene data info.
        """
        cleanPipeData = self.pipeData
        cleanPipeData.pop('sceneName', None)
        cleanPipeData.pop('shortName', None)
        outFile = open(self.pipeData['path']+"/"+self.infoFile, "w")
        json.dump(cleanPipeData, outFile, indent=4)
        outFile.close()


    def makeDirIfNotExists(self, pathToMake=None, *args):
        """ Check if the path exists and create it if it doesn't exists.
        """
        if pathToMake:
            if not os.path.exists(pathToMake):
                os.makedirs(pathToMake)


    def createPipelineInfoSubFolders(self, *args):
        """ Create pipeline info addOnsPath and presetsPath sub folders if they don't exists.
        """
        self.makeDirIfNotExists(self.pipeData['addOnsPath'])
        self.makeDirIfNotExists(self.pipeData['presetsPath'])


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
            self.makeDirIfNotExists(self.pipeData['path'])
            self.setPipelineInfoFile()
            self.createPipelineInfoSubFolders()
            self.setPipelineSettingsPath(self.pipeData['path'], self.infoFile)
        else:
            print("Unexpected Error: There's no pipeline data to save, sorry.")
        self.utils.closeUI('dpPipelinerWindow')


    def mountPackagePath(self, *args):
        """ Mount paths into pipeData to use them in the Package module.
        """
        self.pipeData['toClientPath'] = None
        self.pipeData['historyPath'] = None
        self.pipeData['dropboxPath'] = None
        self.pipeData['publishedWebhook'] = None
        self.pipeData['callback'] = None
        # mount paths
        if self.pipeData['publishPath']:
            # send to client path
            if self.pipeData['b_deliver']:
                self.pipeData['toClientPath'] = self.pipeData['f_drive']+"/"+self.pipeData['f_studio']+"/"+self.pipeData['f_project']+"/"+self.pipeData['f_toClient']
                if self.pipeData['b_dateDir']:
                    self.pipeData['toClientPath'] += "/"+self.getToday()
                self.makeDirIfNotExists(self.pipeData['toClientPath'])
            # hist path
            if self.pipeData['b_archive']:
                if self.pipeData['assetNameFolderIssue']:
                    self.pipeData['scenePath'] = self.getCurrentPath()
                else:
                    self.pipeData['scenePath'] = self.pipeData['f_drive']+"/"+self.pipeData['f_studio']+"/"+self.pipeData['f_project']+"/"+self.pipeData['f_wip']+"/"+self.pipeData['assetName']
                self.pipeData['historyPath'] = self.pipeData['scenePath']+"/"+self.pipeData['s_hist']
                self.makeDirIfNotExists(self.pipeData['historyPath'])
            # dropbox path
            if self.pipeData['b_cloud']:
                if self.pipeData['s_dropbox']:
                    # https://help.dropbox.com/fr-fr/installs/locate-dropbox-folder
                    if os.name == "posix": #Linux or Mac
                        dropDir = "~/.dropbox"
                    else: #Windows
                        dropDir = os.getenv('LOCALAPPDATA')+"/Dropbox"
                    if os.path.exists(dropDir):
                        dropInfo = dropDir+"/info.json"
                        if os.path.exists(dropInfo):
                            content = self.getJsonContent(dropInfo)
                            if content:
                                self.pipeData['dropInfoPath'] = content[list(content)[0]]['path'].replace("\\", "/")
#                                self.pipeData['dropInfoHost'] = content[list(content)[0]]['host']
                                self.pipeData['dropboxPath'] = self.pipeData['dropInfoPath']+"/"+self.pipeData['s_dropbox']+"/"+self.pipeData['f_studio']+"/"+self.pipeData['f_project']
                                self.makeDirIfNotExists(self.pipeData['dropboxPath'])
            # old
            self.makeDirIfNotExists(self.pipeData['publishPath']+"/"+self.pipeData['s_old'])
            # discord
            if self.pipeData['b_discord']:
                if self.pipeData['s_webhook']:
                    self.pipeData['publishedWebhook'] = self.pipeData['s_webhook']
                else: 
                    self.jsonWebhookPath = os.path.join(self.pipeData['path'], self.webhookFile).replace("\\", "/")
                    wh = None
                    if os.path.exists(self.jsonWebhookPath):
                        content = self.getJsonContent(self.jsonWebhookPath)
                        if content:
                            wh = content['webhook']
                    else:
                        wh = self.pipeData['h001_publishing']
                    if wh:
                        self.pipeData['publishedWebhook'] = self.utils.mountWH(DISCORD_URL, wh)
            # callback
            if not self.pipeData['s_callback']:
                callback = os.path.join(self.pipeData['path'], self.callbackFile)
                if os.path.exists(callback):
                    self.pipeData['s_callback'] = callback
            if self.pipeData['s_callback']:
                callback = self.pipeData['s_callback'].replace("\\", "/")
                self.pipeData['callbackPath'] = callback[:callback.rfind("/")]
                self.pipeData['callbackFile'] = callback[callback.rfind("/")+1:-3]


    def getCurrentPath(self, *args):
        """ Returns the current scene path.
        """
        currentPath = cmds.file(query=True, sceneName=True)
        return currentPath[:currentPath.rfind("/")]


    def getCurrentFileName(self, *args):
        """ Returns the current file name without the extension.
        """
        shortSceneName = cmds.file(query=True, sceneName=True, shortName=True)
        if shortSceneName:
            return shortSceneName[:shortSceneName.rfind(".")]


    def saveJsonFile(self, dataDic, fileNamePath, indentation=4, sortKeys=True, *args):
        """ Save the json file with the given data dic in the given file name path.
        """
        # write json file in the HD:
        with open(fileNamePath, 'w') as jsonFile:
            json.dump(dataDic, jsonFile, indent=indentation, sort_keys=sortKeys)
