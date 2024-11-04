# importing libraries:
from maya import cmds
from functools import partial
import os
import json
import time
import shutil

PIPE_FOLDER = "_dpPipeline"
DISCORD_URL = "https://discord.com/api/webhooks"

DP_PIPELINER_VERSION = 1.11


class Pipeliner(object):
    def __init__(self, dpUIinst, *args):
        """ Initialize the module class loading variables and store them in a dictionary.
        """
        # define variables
        self.dpUIinst = dpUIinst
        self.utils = dpUIinst.utils
        self.settingsFile = "_dpPipelineSettings.json"
        self.infoFile = "dpPipelineInfo.json"
        self.webhookFile = "dpWebhook.json"
        self.hookFile = "dpHook.json"
        self.callbackFile = "dpPublishCallback.py"
        self.customAssetNameFile = "dpCustomAssetName.json"
        self.pipeData = self.getPipelineData()
        self.declarePipelineAnnotation()
        self.refreshAssetData()


    def refreshAssetData(self, *args):
        """ Load the asset data from saved file in the pipeline.
        """
        self.pipeData = self.getPipelineData()
        self.getPipeFileName()
        self.refreshAssetNameUI()
        

    def getToday(self, fullTime=False, *args):
        """ Just returns the date like 1980-11-13
        """
        if fullTime:
            return str(time.asctime(time.localtime(time.time())))
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


    def getCustomAssetNameInfo(self, assetName, *args):
        """ Returns the path content of the dpCustomAssetName json file if it exists.
            Otherwise returns the given assetName.
        """
        if assetName:
            if os.path.exists(self.pipeData['path']+"/"+self.customAssetNameFile):
                content = self.getJsonContent(self.pipeData['path']+"/"+self.customAssetNameFile)
                if content:
                    if assetName in list(content.keys()):
                        return content[assetName]
        return assetName
    

    def declareDefaultPipelineInfo(self, *args):
        """ Returns a default pipeline info data to load the UI if there isn't any.
        """
        defaultPipeInfo = {
        "name"    : "Default Pipeline Info",
        "author"  : "Danilo Pinheiro",
        "date"    : "2023-01-01",
        "updated" : "2024-10-31",
        
        "f_drive"            : "",
        "f_studio"           : "",
        "f_project"          : "",
        "f_wip"              : "Rigging/WIP",
        "f_publish"          : "Rigging/Published",
        "f_toClient"         : "Data/ToClient",
        "s_presets"          : "dpPresets",
        "s_addOns"           : "dpAddOns",
        "s_hist"             : self.dpUIinst.dpData+"/dpHist",
        "s_modelIO"          : self.dpUIinst.dpData+"/dpModel",
        "s_setupGeometryIO"  : self.dpUIinst.dpData+"/dpSetupGeometry",
        "s_blendShapeIO"     : self.dpUIinst.dpData+"/dpBlendShape",
        "s_shaderIO"         : self.dpUIinst.dpData+"/dpShader",
        "s_guideIO"          : self.dpUIinst.dpData+"/dpGuide",
        "s_controlShapeIO"   : self.dpUIinst.dpData+"/dpControlShape",
        "s_skinningIO"       : self.dpUIinst.dpData+"/dpSkinning",
        "s_deformationIO"    : self.dpUIinst.dpData+"/dpDeformation",
        "s_inputOrderIO"     : self.dpUIinst.dpData+"/dpInputOrder",
        "s_parentingIO"      : self.dpUIinst.dpData+"/dpParenting",
        "s_transformationIO" : self.dpUIinst.dpData+"/dpTransformation",
        "s_rivetIO"          : self.dpUIinst.dpData+"/dpRivet",
        "s_calibrationIO"    : self.dpUIinst.dpData+"/dpCalibration",
        "s_attributeIO"      : self.dpUIinst.dpData+"/dpAttribute",
        "s_componentTagIO"   : self.dpUIinst.dpData+"/dpComponentTag",
        "s_connectionIO"     : self.dpUIinst.dpData+"/dpConnection",
        "s_constraintIO"     : self.dpUIinst.dpData+"/dpConstraint",
        "s_drivenKeyIO"      : self.dpUIinst.dpData+"/dpDrivenKey",
        "s_old"              : "dpOld",
        "s_dropbox"          : "Job",
        "s_webhook"          : "",
        "s_callback"         : "",
        "s_prefix"           : "",
        "s_middle"           : "_rig_v",
        "s_suffix"           : "",
        "s_model"            : "_m",
        "s_rig"              : "_v",
        "i_padding"          : 3,
        "b_capitalize"       : False,
        "b_upper"            : False,
        "b_lower"            : False,
        "b_deliver"          : True,
        "b_dateDir"          : True,
        "b_assetDir"         : True,
        "b_archive"          : True,
        "b_zip"              : True,
        "b_cloud"            : True,
        "b_discord"          : True,
        "b_imager"           : True,
        "b_i_maya"           : True,
        "b_i_version"        : True,
        "b_i_studio"         : True,
        "b_i_project"        : True,
        "b_i_asset"          : True,
        "b_i_model"          : True,
        "b_i_wip"            : True,
        "b_i_publish"        : True,
        "b_i_date"           : True,
        "b_i_degrade"        : True        
        }
        return defaultPipeInfo


    def declarePipelineAnnotation(self, *args):
        """ Just declare a member variable to get the pipeline annotation data to search the values in the language dictionary.
        """
        self.pipelineAnnotaion = {
        "name"    : "Default Pipeline Annotation",
        "author"  : "Danilo Pinheiro",
        "date"    : "2023-02-09",
        "updated" : "2024-11-04",
        
        "f_drive"            : "i228_fDriveAnn",
        "f_studio"           : "i229_fStudioAnn",
        "f_project"          : "i230_fProjectAnn",
        "f_wip"              : "i231_fWipAnn",
        "f_publish"          : "i232_fPublishAnn",
        "f_toClient"         : "i233_fToClientAnn",
        "s_presets"          : "i234_sPresetsAnn",
        "s_addOns"           : "i235_sAddOnsAnn",
        "s_hist"             : "i236_sHistAnn",
        "s_modelIO"          : "i293_sModelIOAnn",
        "s_setupGeometryIO"  : "i302_sSetupGeometryIOAnn",
        "s_blendShapeIO"     : "i309_sBlendShapeIOAnn",
        "s_shaderIO"         : "i294_sShaderIOAnn",
        "s_guideIO"          : "i295_sGuideIOAnn",
        "s_controlShapeIO"   : "i296_sControlShapeIOAnn",
        "s_skinningIO"       : "i297_sSkinningIOAnn",
        "s_deformationIO"    : "i310_sDeformationIOAnn",
        "s_inputOrderIO"     : "i311_sInputOrderIOAnn",
        "s_parentingIO"      : "i300_sParentingIOAnn",
        "s_transformationIO" : "i312_sTransformationIOAnn",
        "s_rivetIO"          : "i323_sRivetIOAnn",
        "s_calibrationIO"    : "i324_sCalibrationIOAnn",
        "s_attributeIO"      : "i325_sAttributeIOAnn",
        "s_componentTagIO"   : "i326_sComponentTagIOAnn",
        "s_connectionIO"     : "i327_sConnectionIOAnn",
        "s_constraintIO"     : "i328_sConstraintIOAnn",
        "s_drivenKeyIO"      : "i330_sDrivenKeyIOAnn",
        "s_old"              : "i237_sOldAnn",
        "s_dropbox"          : "i238_sDropboxAnn",
        "s_prefix"           : "i239_sPrefixAnn",
        "s_middle"           : "i240_sMiddleAnn",
        "s_suffix"           : "i241_sSuffixAnn",
        "s_model"            : "i242_sModelAnn",
        "s_rig"              : "i243_sRigAnn",
        "i_padding"          : "i245_iPaddingAnn",
        "b_capitalize"       : "i246_bCaptalizeAnn",
        "b_upper"            : "i247_bUpperAnn",
        "b_lower"            : "i248_bLowerAnn",
        "b_deliver"          : "i249_bDeliverAnn",
        "b_dateDir"          : "i250_bDateDirAnn",
        "b_assetDir"         : "i251_bAssetDirAnn",
        "b_archive"          : "i252_bArchiveAnn",
        "b_zip"              : "i253_bZipAnn",
        "b_cloud"            : "i254_bCloudAnn",
        "b_imager"           : "i255_bImagerAnn",
        "b_i_maya"           : "i269_biMaya",
        "b_i_version"        : "i256_biVersionAnn",
        "b_i_studio"         : "i257_biStudioAnn",
        "b_i_project"        : "i258_biProjectAnn",
        "b_i_asset"          : "i259_biAssetAnn",
        "b_i_model"          : "i260_biModelAnn",
        "b_i_wip"            : "i261_biRigAnn",
        "b_i_publish"        : "i262_biPublishAnn",
        "b_i_date"           : "i263_biDateAnn",
        "b_i_degrade"        : "i264_biDegradeAnn",
        "s_webhook"          : "i277_sWebhookAnn",
        "b_discord"          : "i278_bDiscordAnn",
        "s_callback"         : "i284_sCallbackAnn"
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
                self.pipeData['projectPath'] = self.pipeData['f_drive']+"/"+self.pipeData['f_studio']+"/"+self.pipeData['f_project']
                self.pipeData['path'] = self.pipeData['f_drive']+"/"+self.pipeData['f_studio']+"/"+PIPE_FOLDER #dpTeam
                if not os.path.exists(self.pipeData['path']):
                    self.pipeData['f_drive'] = ""
                    self.pipeData['f_studio'] = ""
                    self.pipeData['f_project'] = ""
                    self.pipeData['projectPath'] = ""
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
            Returns True if it worked well.
        """
        if pathToMake:
            if not os.path.exists(pathToMake):
                os.makedirs(pathToMake)
                return True


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


    def getCurrentFileName(self, complete=False, *args):
        """ Returns the current file name with or without the extension depending of the given complete parameter.
        """
        shortSceneName = cmds.file(query=True, sceneName=True, shortName=True)
        if shortSceneName:
            if complete:
                return shortSceneName
            return shortSceneName[:shortSceneName.rfind(".")]
    
    
    def getFileExtension(self, *args):
        """ Returns the current file extension.
        """
        shortSceneName = cmds.file(query=True, sceneName=True, shortName=True)
        if shortSceneName:
            return shortSceneName[shortSceneName.rfind("."):]


    def saveJsonFile(self, dataDic, fileNamePath, indentation=4, sortKeys=True, *args):
        """ Save the json file with the given data dic in the given file name path.
        """
        # write json file in the HD:
        with open(fileNamePath, 'w') as jsonFile:
            json.dump(dataDic, jsonFile, indent=indentation, sort_keys=sortKeys)


    def defineFileVersion(self, assetNameList, *args):
        """ Return the max number plus one of a versioned files list.
        """
        if assetNameList:
            numberList = []
            for item in assetNameList:
                numberList.append(int(item[:item.rfind(".")].split(self.pipeData['s_middle'])[1]))
            return max(numberList)+1
    

    def getRigWIPVersion(self, *args):
        """ Find the rig version by scene name and return it.
        """
        rigWipVersion = 0
        shortName = cmds.file(query=True, sceneName=True, shortName=True)
        if self.pipeData['s_rig'] in shortName:
            rigWipVersion = shortName[shortName.rfind(self.pipeData['s_rig'])+len(self.pipeData['s_rig']):shortName.rfind(".")]
        return rigWipVersion


    def getAssetName(self, *args):
        """ Compare the sceneName with the father folder name to define if we use the assetName as a default pipeline setup.
            Return True or False and the shortName of the asset if found.
            Otherwise return False
        """
        folderName = None
        assetName = None
        currentPath = self.getCurrentPath()
        if currentPath:
            folderName = currentPath[currentPath.rfind("/")+1:]
        shortSceneName = self.getCurrentFileName()
        if shortSceneName:
            assetName = shortSceneName
            if "_" in shortSceneName:
                assetName = shortSceneName[:shortSceneName.find("_")]
            for ext in [".ma", ".mb"]:
                if assetName.endswith(ext):
                    assetName = assetName[:-3]
        if folderName or assetName:
            if folderName == assetName:
                return [True, assetName]
        if assetName:
            return [False, assetName]
        elif folderName:
            return [False, folderName]
        return [False, None]


    def getPipeFileName(self, filePath=None, *args):
        """ Return the generated file name based on the pipeline publish folder.
            It's check the asset name and define the file version to save the published file.
        """
        self.pipeData['assetName'] = None
        self.assetNameList = []
        if not filePath:
            filePath = self.getCurrentPath()
        if os.path.exists(filePath):
            self.pipeData['assetNameFolderIssue'], assetName = self.getAssetName()
            publishVersion = 1 #starts the number versioning by one to have the first delivery file as _v001.
            fileNameList = next(os.walk(filePath))[2]
            if fileNameList:
                for fileName in fileNameList:
                    if assetName+self.pipeData['s_middle'] in fileName:
                        if not fileName in self.assetNameList:
                            self.assetNameList.append(fileName)
                if self.assetNameList:
                    publishVersion = self.defineFileVersion(self.assetNameList)
            if self.pipeData['b_capitalize']:
                assetName = assetName.capitalize()
            elif self.pipeData['b_lower']:
                assetName = assetName.lower()
            elif self.pipeData['b_upper']:
                assetName = assetName.upper()
            self.pipeData['assetName'] = assetName
            self.pipeData['assetPath'] = self.getCurrentPath()
            self.pipeData['currentFileName'] = self.getCurrentFileName()
            self.pipeData['extension'] = self.getFileExtension()
            self.pipeData['rigVersion'] = self.getRigWIPVersion()
            self.pipeData['publishVersion'] = publishVersion
            self.pipeData['fileName'] = self.pipeData['s_prefix']+assetName+self.pipeData['s_middle']+(str(publishVersion).zfill(int(self.pipeData['i_padding']))+self.pipeData['s_suffix'])
            return self.pipeData['fileName']
        else:
            return False


    def refreshAssetNameUI(self, newSceneValue=False, *args):
        """ Just read again the pipeline data and set the UI with the assetName.
        """
        if newSceneValue:
            cmds.frameLayout(self.dpUIinst.allUIs["rebuilderAssetFL"], edit=True, label=self.dpUIinst.lang['i303_asset']+" - None")
        else:
            if self.pipeData['assetName']:
                if self.pipeData['assetName'] == "None":
                    print(self.dpUIinst.lang['r027_noAssetContext'])
                else:
                    try:
                        cmds.frameLayout(self.dpUIinst.allUIs["rebuilderAssetFL"], edit=True, label=self.dpUIinst.lang['i303_asset']+" - "+self.pipeData['assetName'])
                    except:
                        pass
            else:
                try:
                    cmds.frameLayout(self.dpUIinst.allUIs["rebuilderAssetFL"], edit=True, label=self.dpUIinst.lang['i303_asset']+" - None")
                except:
                    pass


    def checkAssetContext(self, *args):
        """ Returns True if there's an asset context to work the rebuilding or False if not.
        """
        hasAssetContext = False
        if self.pipeData:
            if self.pipeData['assetName']:
                if not self.pipeData['assetName'] == "None":
                    hasAssetContext = True
        return hasAssetContext
    

    def loadProjectPath(self, *args):
        """ Open a file dialog to get the project path and write it in the respective field.
        """
        resultInfoList = cmds.fileDialog2(fileMode=3, dialogStyle=2)
        if resultInfoList:
            cmds.textFieldButtonGrp(self.projectPathTFBG, edit=True, text=resultInfoList[0])


    def getNewAssetPreviewTextByUI(self, *args):
        """ Generate and return the new asset file name with complete path, using the UI info.
        """
        self.newAssetFile = ""
        newAssetName = cmds.textFieldGrp(self.newAssetNameTFG, query=True, text=True)
        newModelVersion = cmds.textFieldGrp(self.newModelVersionTFG, query=True, text=True)
        newWIPVersion = cmds.textFieldGrp(self.newWIPVersionTFG, query=True, text=True)
        projectPath = cmds.textFieldButtonGrp(self.projectPathTFBG, query=True, text=True)
        if projectPath:
            if not projectPath.endswith("/"):
                projectPath = projectPath+"/"
            wipFolder = self.pipeData['f_wip']
            if wipFolder:
                if not wipFolder.endswith("/"):
                    wipFolder = wipFolder+"/"
            if newWIPVersion and newModelVersion and newAssetName:
                self.newAssetFile = projectPath+wipFolder+newAssetName+"/"+newAssetName+self.pipeData['s_model']+newModelVersion.zfill(self.pipeData['i_padding'])+self.pipeData['s_rig']+newWIPVersion.zfill(self.pipeData['i_padding'])+".ma"
        if self.newAssetFile:
            cmds.text(self.newAssetPreviewTxt, edit=True, label=self.newAssetFile)
        return self.newAssetFile


    def createNewAssetUI(self, *args):
        """ A simple UI to get the asset info like name, model version, wip rig version in order to create a new asset context.
        """
        # declaring variables:
        self.newAsset_title     = 'dpAutoRig - '+self.dpUIinst.lang['i158_create']+" "+self.dpUIinst.lang['i304_new']+" "+self.dpUIinst.lang['i303_asset']
        self.newAsset_winWidth  = 420
        self.newAsset_winHeight = 250
        self.newAsset_align     = "left"
        # creating New Asset Window:
        self.utils.closeUI("dpNewAssetWindow")
        dpNewAssetWin = cmds.window('dpNewAssetWindow', title=self.newAsset_title, iconName='dpInfo', widthHeight=(self.newAsset_winWidth, self.newAsset_winHeight), menuBar=False, sizeable=False, minimizeButton=False, maximizeButton=False)
        # creating text layout:
        newAssetColumnLayout = cmds.columnLayout('newAssetColumnLayout', adjustableColumn=True, columnOffset=['both', 20], rowSpacing=5, parent=dpNewAssetWin)
        cmds.separator(style='none', height=10, parent=newAssetColumnLayout)
        self.newAssetNameTFG = cmds.textFieldGrp('newAssetNameTFG', label=self.dpUIinst.lang['i303_asset']+" "+self.dpUIinst.lang['m006_name'].lower(), columnWidth2=(80, 150), textChangedCommand=self.getNewAssetPreviewTextByUI, parent=newAssetColumnLayout)
        self.newModelVersionTFG = cmds.textFieldGrp('newModelVersionTFG', label="Model "+self.dpUIinst.lang['m205_version'].lower(), text="1", columnWidth2=(80, 150), textChangedCommand=self.getNewAssetPreviewTextByUI, parent=newAssetColumnLayout)
        self.newWIPVersionTFG = cmds.textFieldGrp('newWIPVersionTFG', label="WIP "+self.dpUIinst.lang['m205_version'].lower(), text="1", columnWidth2=(80, 150), textChangedCommand=self.getNewAssetPreviewTextByUI, parent=newAssetColumnLayout)
        try:
            self.projectPathTFBG = cmds.textFieldButtonGrp('projectPathTFG', label=self.dpUIinst.lang['i301_project']+" path", text=self.pipeData['projectPath'], columnWidth3=(80, 150, 30), buttonLabel=self.dpUIinst.lang['i187_load'], buttonCommand=self.loadProjectPath, adjustableColumn=2, textChangedCommand=self.getNewAssetPreviewTextByUI, parent=newAssetColumnLayout)
        except:
            self.projectPathTFBG = cmds.textFieldButtonGrp('projectPathTFG', label=self.dpUIinst.lang['i301_project']+" path", text="", columnWidth3=(80, 150, 30), buttonLabel=self.dpUIinst.lang['i187_load'], buttonCommand=self.loadProjectPath, adjustableColumn=2, textChangedCommand=self.getNewAssetPreviewTextByUI, parent=newAssetColumnLayout)
        cmds.separator(style='none', height=10, parent=newAssetColumnLayout)
        cmds.text('previewTxt', label="Preview:", font="obliqueLabelFont", align=self.newAsset_align, parent=newAssetColumnLayout)
        previewTextLayout = cmds.scrollLayout("previewTextLayout", height=35, parent=newAssetColumnLayout)
        self.newAssetPreviewTxt = cmds.text('newAssetPreviewTxt', label="", font="boldLabelFont", align="center", parent=previewTextLayout)
        cmds.separator(style='none', height=10, parent=newAssetColumnLayout)
        cmds.button('runCreateNewAssetBT', label=self.dpUIinst.lang['i158_create'], align=self.newAsset_align, command=self.createNewAsset, parent=newAssetColumnLayout)
        # call New Asset Window:
        cmds.showWindow(dpNewAssetWin)
        self.getNewAssetPreviewTextByUI()


    def createNewAsset(self, assetFile=None, *args):
        """ Create a new asset context saving a maya file with the given asset file complete path.
        """
        if assetFile:
            self.newAssetFile = assetFile
        if self.newAssetFile:
            if self.makeDirIfNotExists(self.newAssetFile[:self.newAssetFile.rfind("/")]):
                cmds.file(rename=self.newAssetFile)
                cmds.file(save=True, type="mayaAscii", force=True)
                self.utils.closeUI("dpNewAssetWindow")
        else:
            cmds.confirmDialog(title=self.dpUIinst.lang['i158_create']+" "+self.dpUIinst.lang['i304_new']+" "+self.dpUIinst.lang['i303_asset'], message=self.dpUIinst.lang['i307_fillFieldCorrectly'], button="Ok")


    def replaceDPData(self, path=None, toReplaceList=None, *args):
        """ Check given path and to replace list and call the method to replace or the UI to choose what to replace in the dpData folder.
        """
        if self.checkAssetContext():
            if not path:
                pathList = cmds.fileDialog2(fileMode=3, caption=self.dpUIinst.lang['m219_replace']+" "+self.dpUIinst.dpData, okCaption=self.dpUIinst.lang['i196_import'])
                if pathList:
                    path = pathList[0]
            if path:
                if os.path.exists(path):
                    self.pathToReplaceFrom = path
                    if self.dpUIinst.dpData in path:
                        self.pathToReplaceFrom = path[:path.rfind(self.dpUIinst.dpData)-1]
                    if not toReplaceList:
                        self.getDPDataExistListToReplace(self.pathToReplaceFrom)
                        if self.existList:
                            self.dpDataToReplaceUI(self.existList)
                    else:
                        self.runReplaceDPData(path, toReplaceList)
        else:
            cmds.confirmDialog(title=self.dpUIinst.lang['m219_replace']+" "+self.dpUIinst.dpData, message=self.dpUIinst.lang['r027_noAssetContext'], button="Ok")


    def getDPDataExistListToReplace(self, path, *args):
        """ Check if exists exported module data in the given path.
        """
        defaultList = [
            "modelIO",
            "setupGeometryIO",
            "shaderIO",
            "guideIO",
            "controlShapeIO",
            "skinningIO",
            "parentIO"
            ]
        self.existList = []
        for item in defaultList:
            if os.path.exists(path+"/"+self.pipeData["s_"+item]):
                self.existList.append(item)


    def dpDataToReplaceUI(self, existList, *args):
        """ UI to list exist items as a checkboxes to let the user choose what to replace in the dpData.
        """
        # declaring variables:
        self.replaceDPData_title     = 'dpAutoRig - '+self.dpUIinst.lang['m219_replace']+" "+self.dpUIinst.dpData+" - "+self.dpUIinst.lang['i303_asset']
        self.replaceDPData_winWidth  = 220
        self.replaceDPData_winHeight = 350
        self.replaceDPData_align     = "left"
        # creating replace dpData Window:
        self.utils.closeUI("dpReplaceDPDataWindow")
        dpReplaceDPDataWindow = cmds.window('dpReplaceDPDataWindow', title=self.replaceDPData_title, iconName='dpInfo', widthHeight=(self.replaceDPData_winWidth, self.replaceDPData_winHeight), menuBar=False, sizeable=False, minimizeButton=False, maximizeButton=False)
        # creating layout:
        replaceDPDataColumnLayout = cmds.columnLayout('replaceDPDataColumnLayout', adjustableColumn=True, columnOffset=['both', 20], rowSpacing=5, parent=dpReplaceDPDataWindow)
        cmds.separator(style='none', height=10, parent=replaceDPDataColumnLayout)
        cmds.text("rebuilderReplaceDataText", label=self.dpUIinst.lang['i308_toReplaceDPData']+" "+self.pipeData['assetName'], parent=replaceDPDataColumnLayout)
        cmds.separator(style='none', height=10, parent=replaceDPDataColumnLayout)
        for item in existList:
            cmds.checkBox(item+"CB", label=item, value=True)
        cmds.separator(style='none', height=10, parent=replaceDPDataColumnLayout)
        cmds.button('runReplaceDPDataBT', label=self.dpUIinst.lang['m219_replace'].upper(), align=self.replaceDPData_align, command=self.getDPDataToReplaceByUI, parent=replaceDPDataColumnLayout)
        # call New Asset Window:
        cmds.showWindow(dpReplaceDPDataWindow)
        

    def getDPDataToReplaceByUI(self, *args):
        """ Read the dpReplaceDPDataWindow UI to get the active checkBoxes in order to return it in a list.
        """
        self.dpDataToReplaceList = []
        for item in self.existList:
            if cmds.checkBox(item+"CB", query=True, value=True):
                self.dpDataToReplaceList.append(item)
        if self.dpDataToReplaceList:
            self.runReplaceDPData()
            self.utils.closeUI("dpReplaceDPDataWindow")
        

    def runReplaceDPData(self, path=None, toReplaceList=None, *args):
        """ Replace the dpData subFolder with the given arguments.
        """
        if not path:
            path = self.pathToReplaceFrom
        if not toReplaceList:
            toReplaceList = self.dpDataToReplaceList
        if path and toReplaceList:
            for toReplace in toReplaceList:
                sourcePath = path+"/"+self.pipeData['s_'+toReplace]
                destPath = self.pipeData['assetPath']+"/"+self.pipeData['s_'+toReplace]
                if os.path.exists(sourcePath):
                    if os.path.exists(destPath):
                        for destFile in next(os.walk(destPath))[2]:
                            try:
                                os.remove(destPath+"/"+destFile)
                            except PermissionError as exc:
                                # use a brute force to delete without permission:
                                os.chmod(destPath+"/"+destFile, stat.S_IWUSR)
                                os.remove(destPath+"/"+destFile)
                    else:
                        self.makeDirIfNotExists(destPath)
                    sourceItem = next(os.walk(sourcePath))[2][-1]
                    ext = sourceItem[sourceItem.rfind("."):]
                    prefix = sourceItem[:sourceItem.find("_")+1]
                    destItem = destPath+"/"+prefix+self.pipeData['assetName']+self.pipeData['s_model']+"0".zfill(self.pipeData['i_padding'])+self.pipeData['s_rig']+"0".zfill(self.pipeData['i_padding'])+ext
                    shutil.copy2(sourcePath+"/"+sourceItem, destItem)
