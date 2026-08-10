# importing libraries:
from maya import cmds
from functools import partial
import os
import json
import time
import shutil
import stat

PIPE_FOLDER = "_dpPipeline"
#DISCORD_URL = "https://discord.com/api/webhooks"



class Pipeliner(object):
    def __init__(self, ar):
        """ Initialize the module class loading variables and store them in a dictionary.
        """
        # define variables
        self.ar = ar
        self.settings_file = "pipeline_settings.json"
        self.default_info_file = "pipeline_info.json"
        self.info_file = self.default_info_file
        self.webhook_file = "webhook.json"
        self.hook_file = "hook.json"
        self.callback_file = "publish_callback.py"
        self.custom_asset_name_file = "custom_asset_name.json"
        self.pipe_data = {}
        self.pipe_data = self.get_pipeline_data()
        self.declare_pipeline_annotation()
        self.refresh_asset_data()


    def refresh_asset_data(self, *args):
        """ Load the asset data from saved file in the pipeline.
        """
        if not self.ar.data.rebuilding:
            self.pipe_data = self.get_pipeline_data()
            self.get_pipe_filename()
            self.refresh_project_ui()
            self.refresh_asset_name_ui()
        

    def get_today(self, full=False):
        """ Just returns the simple date like: 1980-11-13
            or full: 1980-11-13_15-32-39
        """
        if full:
            return str(time.asctime(time.localtime(time.time())))
        return time.strftime("%Y-%m-%d", time.localtime())
    

    def get_json_content(self, json_path):
        """ Open, read, close and return the json file content.
        """
        try:
            dic = open(json_path, "r", encoding='utf-8')
            content = json.loads(dic.read())
            dic.close()
        except:
            content = None
        return content


    def get_json_settings_path(self):
        """ Returns the json path for the pipeline settings file.
        """
        base_path = self.ar.data.dp_auto_rig_path+"/library/pipeline"
        return os.path.join(base_path, self.settings_file).replace("\\", "/")


    def get_pipeline_path(self):
        """ Returns the path content of the _dpPipelineSetting json file if it exists.
            Otherwise returns False.
        """
        json_path = self.get_json_settings_path()
        if os.path.exists(json_path):
            content = self.get_json_content(json_path)
            if content:
                if os.path.exists(content['path']):
                    self.info_file = content['file']
                    return content['path']
        return False
        
    
    def update_data_by_json_path(self, json_path):
        """ Read the json file and return the merged pipe_data and it's content if it exists.
        """
        if os.path.exists(json_path):
            content = self.get_json_content(json_path)
            if content:
                self.pipe_data.update(content)
                return content


    def get_pipeline_info(self):
        """ Load PipelineInfo data and returns it.
        """
        json_info_path = os.path.join(self.pipe_data['path'], self.info_file).replace("\\", "/")
        return self.update_data_by_json_path(json_info_path)


    def get_hook_info(self):
        """ Load Hook data and returns it.
        """
        json_hook_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.hook_file).replace("\\", "/")
        return self.update_data_by_json_path(json_hook_path)
    

    def get_info_by_path(self, field, dependent, path=None):
        """ Use field as the given data to return the result about.
            Use dependent as the split data to edit the result.
            Returns the pipeline info name if there's one.
        """
        name = None
        if "sceneName" in self.pipe_data.keys():
            name = self.pipe_data['sceneName']
        if path:
            name = path
        if name:
            if dependent:
                if self.pipe_data[dependent]:
                    try:
                        name = name[name.rfind(self.pipe_data[dependent]+"/")+len(self.pipe_data[dependent])+1:]
                        to_end_it = False
                        if self.pipe_data["f_wip"]:
                            if self.pipe_data["f_wip"] in name:
                                name = name.split(self.pipe_data["f_wip"])[0]
                                to_end_it = True
                        if self.pipe_data["f_publish"]:
                            if self.pipe_data["f_publish"] in name:
                                name = name.split(self.pipe_data["f_publish"])[0]
                                to_end_it = True
                        if to_end_it:
                            if name.endswith("/"):
                                name = name[:-1]
                            if "/" in name:
                                name = name[:name.rfind("/")]
                    except:
                        self.pipe_data[field] = ""
                        self.pipe_data[dependent] = ""
                        return self.pipe_data[field]
            else:
                name = name[:name.find("/")]
            self.pipe_data[field] = name
            return self.pipe_data[field]


    def getCustomAssetNameInfo(self, asset_name, *args):
        """ Returns the path content of the custom_asset_name json file if it exists.
            Otherwise returns the given asset_name.
        """
        if asset_name:
            if os.path.exists(self.pipe_data['path']+"/"+self.custom_asset_name_file):
                content = self.get_json_content(self.pipe_data['path']+"/"+self.custom_asset_name_file)
                if content:
                    if asset_name in list(content.keys()):
                        return content[asset_name]
        return asset_name
    

    def get_default_pipeline_info(self):
        """ Returns a default pipeline info data to load the UI if there isn't any.
        """
        return {
        "name"    : "Default Pipeline Info",
        "author"  : "Danilo Pinheiro",
        "date"    : "2023-01-01",
        "updated" : "2025-11-10",
        
        "f_drive"            : "",
        "f_studio"           : "",
        "f_project"          : "",
        "f_wip"              : "Rigging/WIP",
        "f_publish"          : "Rigging/Published",
        "f_toClient"         : "Data/ToClient",
        "s_presets"          : "dpPresets",
        "s_addOns"           : "dpAddOns",
        "s_finishing"        : "dpFinishing",
        "s_hist"             : self.ar.data.dp_data+"/dpHist",
        "s_modelIO"          : self.ar.data.dp_data+"/dpModel",
        "s_supportNodeIO"    : self.ar.data.dp_data+"/dpSupportNode",
        "s_blendShapeIO"     : self.ar.data.dp_data+"/dpBlendShape",
        "s_shaderIO"         : self.ar.data.dp_data+"/dpShader",
        "s_guideIO"          : self.ar.data.dp_data+"/guide",
        "s_rivetIO"          : self.ar.data.dp_data+"/dpRivet",
        "s_parentingIO"      : self.ar.data.dp_data+"/dpParenting",
        "s_skinningIO"       : self.ar.data.dp_data+"/skinning",
        "s_deformationIO"    : self.ar.data.dp_data+"/dpDeformation",
        "s_componentTagIO"   : self.ar.data.dp_data+"/dpComponentTag",
        "s_inputOrderIO"     : self.ar.data.dp_data+"/dpInputOrder",
        "s_renameIO"         : self.ar.data.dp_data+"/dpRename",
        "s_transformationIO" : self.ar.data.dp_data+"/dpTransformation",
        "s_controlShapeIO"   : self.ar.data.dp_data+"/dpControlShape",
        "s_attributeIO"      : self.ar.data.dp_data+"/dpAttribute",
        "s_constraintIO"     : self.ar.data.dp_data+"/dpConstraint",
        "s_utilityIO"        : self.ar.data.dp_data+"/dpUtility",
        "s_drivenKeyIO"      : self.ar.data.dp_data+"/dpDrivenKey",
        "s_offsetMatrixIO"   : self.ar.data.dp_data+"/dpOffsetMatrix",
        "s_connectionIO"     : self.ar.data.dp_data+"/dpConnection",
        "s_calibrationIO"    : self.ar.data.dp_data+"/dpCalibration",
        "s_visibilityIO"     : self.ar.data.dp_data+"/dpVisibility",
        "s_channelIO"        : self.ar.data.dp_data+"/dpChannel",
        "s_hierarchyIO"      : self.ar.data.dp_data+"/dpHierarchy",
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


    def declare_pipeline_annotation(self):
        """ Just declare a member variable to get the pipeline annotation data to search the values in the language dictionary.
        """
        self.pipeline_annotation = {
        "name"    : "Default Pipeline Annotation",
        "author"  : "Danilo Pinheiro",
        "date"    : "2023-02-09",
        "updated" : "2025-11-10",
        
        "f_drive"            : "i228_fDriveAnn",
        "f_studio"           : "i229_fStudioAnn",
        "f_project"          : "i230_fProjectAnn",
        "f_wip"              : "i231_fWipAnn",
        "f_publish"          : "i232_fPublishAnn",
        "f_toClient"         : "i233_fToClientAnn",
        "s_presets"          : "i234_sPresetsAnn",
        "s_addOns"           : "i235_sAddOnsAnn",
        "s_finishing"        : "i353_sFinishingAnn",
        "s_hist"             : "i236_sHistAnn",
        "s_modelIO"          : "i293_sModelIOAnn",
        "s_supportNodeIO"    : "i302_sSupportNodeIOAnn",
        "s_blendShapeIO"     : "i309_sBlendShapeIOAnn",
        "s_shaderIO"         : "i294_sShaderIOAnn",
        "s_guideIO"          : "i295_sGuideIOAnn",
        "s_rivetIO"          : "i323_sRivetIOAnn",
        "s_parentingIO"      : "i300_sParentingIOAnn",
        "s_skinningIO"       : "i297_sSkinningIOAnn",
        "s_deformationIO"    : "i310_sDeformationIOAnn",
        "s_componentTagIO"   : "i326_sComponentTagIOAnn",
        "s_inputOrderIO"     : "i311_sInputOrderIOAnn",
        "s_renameIO"         : "i338_sRenameIOAnn",
        "s_transformationIO" : "i312_sTransformationIOAnn",
        "s_controlShapeIO"   : "i296_sControlShapeIOAnn",
        "s_attributeIO"      : "i325_sAttributeIOAnn",
        "s_constraintIO"     : "i328_sConstraintIOAnn",
        "s_utilityIO"        : "i337_sUtilityIOAnn",
        "s_drivenKeyIO"      : "i330_sDrivenKeyIOAnn",
        "s_offsetMatrixIO"   : "i345_sOffsetMatrixIOAnn",
        "s_connectionIO"     : "i327_sConnectionIOAnn",
        "s_calibrationIO"    : "i324_sCalibrationIOAnn",
        "s_visibilityIO"     : "i356_sVisibilityIOAnn",
        "s_channelIO"        : "i347_sChannelIOAnn",
        "s_hierarchyIO"      : "i362_sHierarchyAnn",
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


    def get_pipeline_data(self, loaded_pipe_info=None):
        """ Read the dpPipelineSetting to find the pipeline info.
            Mount the pipe_data dictionary and return it.
        """
        loaded = True
        old_pipe_data = {}
        if self.pipe_data:
            old_pipe_data = self.pipe_data.copy()
        if not loaded_pipe_info:
            self.pipe_info = self.get_default_pipeline_info()
            self.pipe_data = self.pipe_info
            self.restore_old_pipe_data(old_pipe_data)
            self.pipe_data['publishPath'] = False
            self.pipe_data['addOnsPath'] = False
            self.pipe_data['finishingPath'] = False
            self.pipe_data['presetsPath'] = False
            # getting pipeline settings
            self.pipe_data['path'] = self.get_pipeline_path()
        self.pipe_data['sceneName'] = cmds.file(query=True, sceneName=True)
        self.pipe_data['shortName'] = cmds.file(query=True, sceneName=True, shortName=True)
        self.pipe_data['mayaProject'] = cmds.workspace(query=True, fullName=True)
        self.pipe_data['projectPath'] = self.pipe_data['mayaProject']
        self.pipe_data['wipPath'] = self.pipe_data['mayaProject']+"/"+self.pipe_data['f_wip']
        if not self.pipe_data['path']:
            # mouting pipeline data dictionary
            if self.pipe_data['sceneName']:
                self.get_info_by_path("f_drive", None)
                if not self.pipe_data['sceneName'] == self.pipe_data['f_drive']+"/"+self.pipe_data['shortName']:
                    self.get_info_by_path("f_studio", "f_drive")
                    self.get_info_by_path("f_project", "f_studio")
                self.pipe_data['wipPath'] = self.pipe_data['f_drive']+"/"+self.pipe_data['f_studio']+"/"+self.pipe_data['f_project']+"/"+self.pipe_data['f_wip']
                self.pipe_data['projectPath'] = self.pipe_data['f_drive']+"/"+self.pipe_data['f_studio']+"/"+self.pipe_data['f_project']
                self.pipe_data['path'] = self.pipe_data['f_drive']+"/"+self.pipe_data['f_studio']+"/"+PIPE_FOLDER #dpTeam
                if not os.path.exists(self.pipe_data['path']):
                    self.restore_old_pipe_data(old_pipe_data)
                    self.pipe_data['wipPath'] = self.pipe_data['mayaProject']+"/"+self.pipe_data['f_wip']
                    loaded = False
                if not os.path.exists(self.pipe_data['projectPath']):
                    self.pipe_data['projectPath'] = self.pipe_data['mayaProject']
            else:
                loaded = False
        if loaded:
            # merge pipeline info
            self.pipe_info = self.get_pipeline_info()
            if self.pipe_info:
                # mounting structured pipeline data
                self.pipe_data['publishPath'] = self.pipe_data['f_drive']+"/"+self.pipe_data['f_studio']+"/"+self.pipe_data['f_project']+"/"+self.pipe_data['f_publish']
                self.pipe_data['addOnsPath'] = self.pipe_data['path']+"/"+self.pipe_data['s_addOns']
                self.pipe_data['finishingPath'] = self.pipe_data['path']+"/"+self.pipe_data['s_finishing']
                self.pipe_data['presetsPath'] = self.pipe_data['path']+"/"+self.pipe_data['s_presets']
            else:
                self.pipe_info = self.get_default_pipeline_info()
                print('Not found', self.info_file)
        self.get_hook_info()
        return self.pipe_data


    def restore_old_pipe_data(self, old_pipe_data=None):
        """ Check if there are old loaded path to restore them after loading the default dictionary.
        """
        items = ["f_drive", "f_studio", "f_project", "f_wip", "f_publish", "f_toClient", "projectPath", "path"]
        if old_pipe_data:
            for item in items:
                if item in old_pipe_data.keys():
                    if old_pipe_data[item]:
                        self.pipe_data[item] = old_pipe_data[item]
                    else:
                        self.pipe_data[item] = ""


    def conform_loaded_info(self, item, result_items):
        """ Edit the loaded info to conform the splited data correctly.
        """
        conform_info = result_items[0].replace("\\", "/")
        if item == "f_drive":
            conform_info = self.get_info_by_path("f_drive", None, conform_info)
        elif item == "f_studio":
            conform_info = self.get_info_by_path("f_studio", "f_drive", conform_info)
        elif item == "f_project":
            conform_info = self.get_info_by_path("f_project", "f_studio", conform_info)
        elif item == "f_wip":
            conform_info = self.get_info_by_path("f_wip", "f_project", conform_info)
        elif item == "f_publish":
            conform_info = self.get_info_by_path("f_publish", "f_project", conform_info)
        elif item == "f_toClient":
            conform_info = self.get_info_by_path("f_toClient", "f_project", conform_info)
        return conform_info

    
    def load_info_key(self, item, *args):
        """ Method called by the Pipeliner UI button to load the info about the item.
        """
        result_items = cmds.fileDialog2(fileMode=3, dialogStyle=2)
        if result_items:
            conform_info = self.conform_loaded_info(item, result_items)
            cmds.textFieldButtonGrp(self.infoUI[item], edit=True, text=conform_info)
            self.set_pipeline_info_file()


    def mainUI(self, ar=None, loadedFileInfo=False, *args):
        """ Open an UI to load, set and save the pipeline info.
        """
        self.ar.utils.close_ui('dpPipelinerWindow')
        self.get_pipeline_data(loadedFileInfo)
        # window
        if ar:
            self.ar = ar
            pipeliner_winWidth  = 380
            pipeliner_winHeight = 480
            cmds.window('dpPipelinerWindow', title="Pipeliner "+str(self.ar.data.version), widthHeight=(pipeliner_winWidth, pipeliner_winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
            cmds.showWindow('dpPipelinerWindow')
            # create UI layout and elements:
            self.pipelinerLayout = cmds.columnLayout('self.pipelinerLayout', adjustableColumn=True, columnOffset=("both", 10))
            # pipeline info
            pipelineInfoLayout = cmds.columnLayout('pipelineInfoLayout', adjustableColumn=True, columnOffset=("left", 10), parent=self.pipelinerLayout)
            cmds.separator(style='in', height=20, parent=pipelineInfoLayout)
            cmds.text('pipelineInfo', label="Pipeline "+self.ar.data.lang['i013_info'], height=30, font='boldLabelFont', parent=pipelineInfoLayout)
            path_data = self.get_path_data()
            self.pathDataTBG = cmds.textFieldButtonGrp('pathDataTBG', label=self.ar.data.lang['i220_filePath'], text=path_data, buttonLabel=self.ar.data.lang['i187_load'], buttonCommand=self.load_pipe_info, changeCommand=partial(self.load_pipe_info, True), adjustableColumn=2, parent=pipelineInfoLayout)
            cmds.separator(style='in', height=20, parent=pipelineInfoLayout)
            # pipeline data
            cmds.text('pipelineData', height=30, label="Pipeline Data", font='boldLabelFont', parent=pipelineInfoLayout)
            self.pipelineScrollLayout = cmds.scrollLayout('pipelineScrollLayout', parent=self.pipelinerLayout)
            self.pipelineDataLayout = cmds.columnLayout('pipelineDataLayout', adjustableColumn=True, width=400, columnOffset=("left", 10), parent=self.pipelineScrollLayout)
            self.pipelineFooterLayout = cmds.columnLayout('pipelineFooterLayout', adjustableColumn=True, width=400, columnOffset=("left", 10), parent=self.pipelinerLayout)
            # load data from pipeline info
            self.load_ui_data()


    def load_ui_data(self, *args):
        """ Populate the UI with loaded data file info.
        """
        cmds.deleteUI(self.pipelineDataLayout)
        cmds.deleteUI(self.pipelineFooterLayout)
        self.pipelineDataLayout = cmds.columnLayout('pipelineDataLayout', adjustableColumn=True, width=400, columnOffset=("left", 10), parent=self.pipelineScrollLayout)
        if self.pipe_info:
            self.infoUI = {}
            for key in list(self.pipe_info):
                if "_" in key:
                    if key.startswith("f_"):
                        self.infoUI[key] = cmds.textFieldButtonGrp(key, label=key[2:], text=self.pipe_info[key], annotation=self.ar.data.lang[self.pipeline_annotation[key]], buttonLabel=self.ar.data.lang['i187_load'], buttonCommand=partial(self.load_info_key, key), adjustableColumn=2, parent=self.pipelineDataLayout)
                    elif key.startswith("i_"):
                        self.infoUI[key] = cmds.intFieldGrp(key, label=key[2:], value1=self.pipe_info[key], annotation=self.ar.data.lang[self.pipeline_annotation[key]], numberOfFields=1, parent=self.pipelineDataLayout)
                    elif key.startswith("b_"):
                        self.infoUI[key] = cmds.checkBox(key, label=key[2:], value=self.pipe_info[key], annotation=self.ar.data.lang[self.pipeline_annotation[key]], parent=self.pipelineDataLayout)
                    elif key.startswith("s_"):
                        self.infoUI[key] = cmds.textFieldGrp(key, label=key[2:], text=self.pipe_info[key], annotation=self.ar.data.lang[self.pipeline_annotation[key]], parent=self.pipelineDataLayout)
            # try to force loading empty data info
            try:
                if self.pipe_data['sceneName']:
                    if not cmds.textFieldButtonGrp(self.infoUI['f_drive'], query=True, text=True):
                        self.get_info_by_path("f_drive", None)
                        cmds.textFieldButtonGrp(self.infoUI['f_drive'], edit=True, text=self.pipe_data['f_drive'])
                    if not cmds.textFieldButtonGrp(self.infoUI['f_studio'], query=True, text=True):
                        self.get_info_by_path("f_studio", "f_drive")
                        cmds.textFieldButtonGrp(self.infoUI['f_studio'], edit=True, text=self.pipe_data['f_studio'])
                    if not cmds.textFieldButtonGrp(self.infoUI['f_project'], query=True, text=True):
                        self.get_info_by_path("f_project", "f_studio")
                        cmds.textFieldButtonGrp(self.infoUI['f_project'], edit=True, text=self.pipe_data['f_project'])
            except:
                pass
            self.pipelineFooterLayout = cmds.columnLayout('pipelineFooterLayout', adjustableColumn=True, width=400, columnOffset=("left", 10), parent=self.pipelinerLayout)
            cmds.separator(style='in', height=20, parent=self.pipelineFooterLayout)
            self.pipelineFooterButtonsLayout = cmds.paneLayout("pipelineFooterButtonsLayout", configuration="vertical3", separatorThickness=2.0, parent=self.pipelineFooterLayout)
            cmds.button('resetPipeInfoBT', label=self.ar.data.lang['i271_reset'], command=self.reset_pipe_info, backgroundColor=(0.75, 0.75, 0.75), parent=self.pipelineFooterButtonsLayout)
            cmds.button('newPipeInfoBT', label=self.ar.data.lang['i304_new'], command=self.new_pipe_info, backgroundColor=(0.75, 0.75, 0.75), parent=self.pipelineFooterButtonsLayout)
            cmds.button('savePipeInfoBT', label=self.ar.data.lang['i222_save'], command=self.save_pipe_info, backgroundColor=(0.75, 0.75, 0.75), parent=self.pipelineFooterButtonsLayout)
            cmds.separator(style='none', height=5, parent=self.pipelineFooterLayout)
        else:
            path_data = self.get_path_data()
            cmds.text(path_data, parent=self.pipelineDataLayout)


    def get_path_data(self, *args):
        """ Returns the concatenated path and info file name.
        """
        path_data = self.ar.data.lang['i062_notFound']
        if self.pipe_info and self.pipe_data['path']:
            path_data = self.pipe_data['path']+"/"+self.info_file
        return path_data


    def load_publish_path(self):
        """ Returns the absolute path to publish the current file.
        """
        if self.pipe_data['path']:
            project_folder = self.pipe_data['f_project']
            if project_folder:
                project_folder += "/"
            else:
                # try to find the project name by scene path
                project_folder = self.pipe_data['sceneName'][self.pipe_data['sceneName'].rfind(self.pipe_data['f_studio'])+len(self.pipe_data['f_studio'])+1:self.pipe_data['sceneName'].rfind(self.pipe_data['f_wip'])]
            self.pipe_data['publishPath'] = self.pipe_data['f_drive']+"/"+self.pipe_data['f_studio']+"/"+project_folder+self.pipe_data['f_publish']
            return self.pipe_data['publishPath']
        else:
            print(self.ar.data.lang['i350_notFoundPipeInfoFile'])


    def load_pipe_info(self, loaded=None, *args):
        """ Update the Pipeliner UI data section with loaded info file.
        """
        loaded_file_paths = None
        if loaded:
            loaded = cmds.textFieldButtonGrp(self.pathDataTBG, query=True, text=True)
            if loaded.endswith('.json'):
                loaded = loaded.replace("\\", "/")
                if os.path.exists(loaded):
                    loaded_file_paths = [loaded]
        else:
            loaded_file_paths = cmds.fileDialog2(fileFilter='*.json', fileMode=1, dialogStyle=2)
        if loaded_file_paths:
            loaded_file_path = loaded_file_paths[0].replace("\\", "/")
            self.pipe_data['path'] = loaded_file_path[:loaded_file_path.rfind("/")]
            self.info_file = loaded_file_path[loaded_file_path.rfind("/")+1:]
            cmds.textFieldButtonGrp(self.pathDataTBG, edit=True, text=loaded_file_path)
            self.get_pipeline_data(self.info_file)
            self.load_ui_data()
            self.set_pipeline_settings_path(self.pipe_data['path'], self.info_file)

    
    def set_pipeline_settings_path(self, path, file):
        """ Set the json file for dpPipelineSetting in the main dpAutoRigSystem folder to use the path and file given.
        """
        if path and file:
            json_path = self.get_json_settings_path()
            print("jasonPath =", json_path)
            if os.path.exists(json_path):
                settings_data = self.get_json_content(json_path)
                settings_data['path'] = path
                settings_data['file'] = file
                # write json file in the HD
                with open(json_path, 'w') as json_file:
                    json.dump(settings_data, json_file, indent=4, sort_keys=True)

    
    def get_ui_data_to_save(self):
        """ Read the UI fields and load them values in the pipe_data dictionary.
        """
        for k, key in enumerate(list(self.infoUI)):
            if key.startswith("f_"):
                self.pipe_data[key] = cmds.textFieldButtonGrp(self.infoUI[key], query=True, text=True)
            elif key.startswith("i_"):
                self.pipe_data[key] = cmds.intFieldGrp(self.infoUI[key], query=True, value1=True)
            elif key.startswith("b_"):
                self.pipe_data[key] = cmds.checkBox(self.infoUI[key], query=True, value=True)
            elif key.startswith("s_"):
                self.pipe_data[key] = cmds.textFieldGrp(self.infoUI[key], query=True, text=True)


    def set_pipeline_info_file(self):
        """ Save the pipeline info file with all pipe_data into a json file.
            Except the current scene data info.
        """
        self.pipe_data['updated'] = self.get_today()
        clean_pipe_data = self.pipe_data
        clean_pipe_data.pop('sceneName', None)
        clean_pipe_data.pop('shortName', None)
        out_file = open(self.pipe_data['path']+"/"+self.info_file, "w")
        json.dump(clean_pipe_data, out_file, indent=4)
        out_file.close()


    def make_dir_if_not_exists(self, path_to_make=None):
        """ Check if the path exists and create it if it doesn't exists.
            Returns True if it worked well.
        """
        if path_to_make:
            if not os.path.exists(path_to_make):
                os.makedirs(path_to_make)
                return True


    def create_pipeline_info_sub_folders(self):
        """ Create pipeline info addOnsPath, finishingPath and presetsPath sub folders if they don't exists.
        """
        self.make_dir_if_not_exists(self.pipe_data['addOnsPath'])
        self.make_dir_if_not_exists(self.pipe_data['finishingPath'])
        self.make_dir_if_not_exists(self.pipe_data['presetsPath'])


    def reset_pipe_info(self, *args):
        """ Reset the pipeline info data to default values.
        """
        cmds.textFieldButtonGrp(self.pathDataTBG, edit=True, text="")
        self.pipe_info = self.get_default_pipeline_info()
        self.pipe_data = self.pipe_info
        self.load_ui_data()
        self.set_pipeline_settings_path(self.ar.data.lang['i357_putInfoFilePathHere'], self.default_info_file)


    def new_pipe_info(self, file_path=None, *args):
        """ Will create a new pipeline info file with default setting in the given path and filename given or choose by user.
        """
        if not file_path:
            file_path_names = cmds.fileDialog2(fileFilter='*.json', fileMode=0, dialogStyle=2) or None
            if file_path_names:
                file_path = file_path_names[0]
                if "." in file_path:
                    if not file_path.endswith(".json"):
                        file_path = file_path[:file_path.rfind(".")]+".json"
        if file_path:
            cmds.textFieldButtonGrp(self.pathDataTBG, edit=True, text=file_path)
            self.pipe_data['path'] = file_path[:file_path.rfind("/")]
            self.pipe_data['date'] = self.get_today()
            self.info_file = file_path[file_path.rfind("/")+1:]
            self.save_pipe_info(close_ui=False)


    def save_pipe_info(self, close_ui=True, *args):
        """ Save the pipeline data into the json file in the HD.
            Write the pipeline data path in the pipeline setting json file.
        """
        self.get_ui_data_to_save()
        path_data_from_ui = cmds.textFieldButtonGrp(self.pathDataTBG, query=True, text=True)
        if path_data_from_ui:
            if "/" in path_data_from_ui:
                self.pipe_data['path'] = path_data_from_ui[:path_data_from_ui.rfind("/")]
            if path_data_from_ui.endswith(".json"):
                self.info_file = path_data_from_ui[path_data_from_ui.rfind("/")+1:]
        if self.pipe_data['path'] and self.info_file:
            self.make_dir_if_not_exists(self.pipe_data['path'])
            self.set_pipeline_info_file()
            self.create_pipeline_info_sub_folders()
            self.set_pipeline_settings_path(self.pipe_data['path'], self.info_file)
        else:
            print("Unexpected Error: There's no pipeline data to save, sorry.")
        if close_ui:
            self.ar.utils.close_ui('dpPipelinerWindow')


    def mount_package_path(self):
        """ Mount paths into pipe_data to use them in the Package module.
        """
        self.pipe_data['toClientPath'] = None
        self.pipe_data['historyPath'] = None
        self.pipe_data['dropboxPath'] = None
        self.pipe_data['publishedWebhook'] = None
        self.pipe_data['callback'] = None
        # mount paths
        if self.pipe_data['publishPath']:
            # send to client path
            if self.pipe_data['b_deliver']:
                self.pipe_data['toClientPath'] = self.pipe_data['f_drive']+"/"+self.pipe_data['f_studio']+"/"+self.pipe_data['f_project']+"/"+self.pipe_data['f_toClient']
                if self.pipe_data['b_dateDir']:
                    self.pipe_data['toClientPath'] += "/"+self.get_today()
                self.make_dir_if_not_exists(self.pipe_data['toClientPath'])
            # hist path
            if self.pipe_data['b_archive']:
                if self.pipe_data['assetNameFolderIssue']:
                    self.pipe_data['scenePath'] = self.get_current_path()
                else:
                    self.pipe_data['scenePath'] = self.pipe_data['f_drive']+"/"+self.pipe_data['f_studio']+"/"+self.pipe_data['f_project']+"/"+self.pipe_data['f_wip']+"/"+self.pipe_data['assetName']
                self.pipe_data['historyPath'] = self.pipe_data['scenePath']+"/"+self.pipe_data['s_hist']
                self.make_dir_if_not_exists(self.pipe_data['historyPath'])
            # dropbox path
            if self.pipe_data['b_cloud']:
                if self.pipe_data['s_dropbox']:
                    # https://help.dropbox.com/fr-fr/installs/locate-dropbox-folder
                    if os.name == "posix": #Linux or Mac
                        dropbox_folder = "~/.dropbox"
                    else: #Windows
                        dropbox_folder = os.getenv('LOCALAPPDATA')+"/Dropbox"
                    if os.path.exists(dropbox_folder):
                        dropbox_info = dropbox_folder+"/info.json"
                        if os.path.exists(dropbox_info):
                            content = self.get_json_content(dropbox_info)
                            if content:
                                self.pipe_data['dropInfoPath'] = content[list(content)[0]]['path'].replace("\\", "/")
#                                self.pipe_data['dropInfoHost'] = content[list(content)[0]]['host']
                                self.pipe_data['dropboxPath'] = self.pipe_data['dropInfoPath']+"/"+self.pipe_data['s_dropbox']+"/"+self.pipe_data['f_studio']+"/"+self.pipe_data['f_project']
                                self.make_dir_if_not_exists(self.pipe_data['dropboxPath'])
            # old
            self.make_dir_if_not_exists(self.pipe_data['publishPath']+"/"+self.pipe_data['s_old'])
            # discord
            if self.pipe_data['b_discord']:
                if self.pipe_data['s_webhook']:
                    self.pipe_data['publishedWebhook'] = self.pipe_data['s_webhook']
                else: 
                    self.json_webhook_path = os.path.join(self.pipe_data['path'], self.webhook_file).replace("\\", "/")
                    wh = None
                    if os.path.exists(self.json_webhook_path):
                        content = self.get_json_content(self.json_webhook_path)
                        if content:
                            wh = content['webhook']
                    else:
                        wh = self.pipe_data['h001_publishing']
                    if wh:
                        self.pipe_data['publishedWebhook'] = self.ar.utils.mountWH(self.ar.data.discord_url, wh)
            # callback
            if not self.pipe_data['s_callback']:
                callback = os.path.join(self.pipe_data['path'], self.callback_file)
                if os.path.exists(callback):
                    self.pipe_data['s_callback'] = callback
            if self.pipe_data['s_callback']:
                callback = self.pipe_data['s_callback'].replace("\\", "/")
                self.pipe_data['callbackPath'] = callback[:callback.rfind("/")]
                self.pipe_data['callbackFile'] = callback[callback.rfind("/")+1:-3]


    def get_current_path(self):
        """ Returns the current scene path.
        """
        current_path = cmds.file(query=True, sceneName=True)
        return current_path[:current_path.rfind("/")]


    def get_current_filename(self, complete=False, *args):
        """ Returns the current file name with or without the extension depending of the given complete parameter.
        """
        short_scene_name = cmds.file(query=True, sceneName=True, shortName=True)
        if short_scene_name:
            if complete:
                return short_scene_name
            return short_scene_name[:short_scene_name.rfind(".")]
    
    
    def get_file_extension(self):
        """ Returns the current file extension.
        """
        short_scene_name = cmds.file(query=True, sceneName=True, shortName=True)
        if short_scene_name:
            return short_scene_name[short_scene_name.rfind("."):]


    def save_json_file(self, data, filename_path, indentation=4, to_sort_keys=True):
        """ Save the json file with the given data dic in the given file name path.
        """
        # write json file in the HD:
        with open(filename_path, 'w') as json_file:
            json.dump(data, json_file, indent=indentation, sort_keys=to_sort_keys)


    def define_file_version(self, asset_names):
        """ Return the max number plus one of a versioned files list.
        """
        if asset_names:
            numbers = []
            for item in asset_names:
                numbers.append(int(item[:item.rfind(".")].split(self.pipe_data['s_middle'])[1]))
            return max(numbers)+1
    

    def get_wip_rig_version(self, short_name=None, *args):
        """ Find the rig version by scene name and return it.
        """
        wip_rig_version = 0
        if not short_name:
            short_name = cmds.file(query=True, sceneName=True, shortName=True)
        if self.pipe_data['s_rig'] in short_name:
            wip_rig_version = short_name[short_name.rfind(self.pipe_data['s_rig'])+len(self.pipe_data['s_rig']):short_name.rfind(".")]
        return wip_rig_version


    def get_model_version(self, short_name=None, *args):
        """ Find the model version by scene name and return it.
        """
        model_version = 0
        if not short_name:
            short_name = cmds.file(query=True, sceneName=True, shortName=True)
        if self.pipe_data['s_model'] in short_name:
            model_version = short_name[short_name.rfind(self.pipe_data['s_model'])+len(self.pipe_data['s_model']):short_name.rfind(self.pipe_data['s_rig'])]
        return model_version
    

    def get_asset_name(self):
        """ Compare the sceneName with the father folder name to define if we use the assetName as a default pipeline setup.
            Return True or False and the shortName of the asset if found.
            Otherwise return False
        """
        folder_name = None
        asset_name = None
        current_path = self.get_current_path()
        if current_path:
            folder_name = current_path[current_path.rfind("/")+1:]
        short_scene_name = self.get_current_filename()
        if short_scene_name:
            asset_name = short_scene_name
            if "_" in short_scene_name:
                asset_name = short_scene_name[:short_scene_name.find("_")]
            for ext in [".ma", ".mb"]:
                if asset_name.endswith(ext):
                    asset_name = asset_name[:-3]
        if folder_name or asset_name:
            if folder_name == asset_name:
                return [True, asset_name]
        if asset_name:
            return [False, asset_name]
        elif folder_name:
            return [False, folder_name]
        return [False, None]


    def get_pipe_filename(self, file_path=None):
        """ Return the generated file name based on the pipeline publish folder.
            It checks the asset name and define the file version to save the published file.
        """
        self.pipe_data['assetName'] = None
        self.asset_names = []
        if not file_path:
            file_path = self.get_current_path()
        self.pipe_data['assetNameFolderIssue'], asset_name = self.get_asset_name()
        if asset_name:
            publish_version = 1 #starts the number versioning by one to have the first delivery file as _v001.
            if os.path.exists(file_path):
                filenames = next(os.walk(file_path))[2]
                if filenames:
                    for filename in filenames:
                        if asset_name+self.pipe_data['s_middle'] in filename or asset_name.lower()+self.pipe_data['s_middle'] in filename or asset_name.upper()+self.pipe_data['s_middle'] in filename:
                            if not filename in self.asset_names:
                                self.asset_names.append(filename)
                    if self.asset_names:
                        publish_version = self.define_file_version(self.asset_names)
            if self.pipe_data['b_capitalize']:
                asset_name = asset_name.capitalize()
            elif self.pipe_data['b_lower']:
                asset_name = asset_name.lower()
            elif self.pipe_data['b_upper']:
                asset_name = asset_name.upper()
            self.pipe_data['assetName'] = asset_name
            self.pipe_data['assetPath'] = self.get_current_path()
            self.pipe_data['currentFileName'] = self.get_current_filename()
            self.pipe_data['extension'] = self.get_file_extension()
            self.pipe_data['rigVersion'] = self.get_wip_rig_version()
            self.pipe_data['publishVersion'] = publish_version
            self.pipe_data['fileName'] = self.pipe_data['s_prefix']+asset_name+self.pipe_data['s_middle']+(str(publish_version).zfill(int(self.pipe_data['i_padding']))+self.pipe_data['s_suffix'])
            return self.pipe_data['fileName']
        else:
            return False


    def save_version(self, *args):
        """ UI to chose save asset version options.
        """
        if self.check_asset_context():
            # declaring variables:
            saveVersion_title     = 'dpAutoRig - '+self.ar.data.lang['i222_save']+" "+self.ar.data.lang['i303_asset']+" "+self.ar.data.lang['m205_version'].lower()
            saveVersion_winWidth  = 380
            saveVersion_winHeight = 220
            saveVersion_align     = "left"
            # window:
            self.ar.utils.close_ui("dpSaveVersionWindow")
            dpSaveVersionWin = cmds.window('dpSaveVersionWindow', title=saveVersion_title, iconName='dpInfo', widthHeight=(saveVersion_winWidth, saveVersion_winHeight), menuBar=False, sizeable=False, minimizeButton=False, maximizeButton=False)
            # creating text layout:
            saveVersionColumnLayout = cmds.columnLayout('saveVersionColumnLayout', adjustableColumn=True, columnOffset=['both', 20], rowSpacing=3, parent=dpSaveVersionWin)
            cmds.separator(style='none', height=10, parent=saveVersionColumnLayout)
            cmds.textFieldGrp('currentPathTFG', label="Path", text=self.pipe_data['wipPath'], columnWidth2=(80, 150), editable=False, adjustableColumn=2, parent=saveVersionColumnLayout)
            cmds.textFieldGrp('currentFileNameTFG', label=self.ar.data.lang['i276_current'], text=self.get_current_filename(), columnWidth2=(80, 150), editable=False, adjustableColumn=2, parent=saveVersionColumnLayout)
            self.saveModelVersionTFG = cmds.textFieldGrp('saveModelVersionTFG', label="Model "+self.ar.data.lang['m205_version'].lower(), text=str(int(self.get_model_version())), columnWidth2=(80, 50), textChangedCommand=self.getSaveVersionPreviewTextByUI, parent=saveVersionColumnLayout)
            self.saveRigVersionTFG = cmds.textFieldGrp('saveRigVersionTFG', label="WIP "+self.ar.data.lang['m205_version'].lower(), text=str(int(self.get_wip_rig_version())+1), columnWidth2=(80, 50), textChangedCommand=self.getSaveVersionPreviewTextByUI, parent=saveVersionColumnLayout)
            cmds.separator(style='none', height=10, parent=saveVersionColumnLayout)
            cmds.text('previewTxt', label="Preview:", font="obliqueLabelFont", align=saveVersion_align, parent=saveVersionColumnLayout)
            previewTextLayout = cmds.scrollLayout("previewTextLayout", height=35, parent=saveVersionColumnLayout)
            self.saveVersionPreviewTxt = cmds.text('saveVersionPreviewTxt', label="", font="boldLabelFont", align="center", parent=previewTextLayout)
            cmds.button('runSaveVersionBT', label=self.ar.data.lang['i222_save'], align=saveVersion_align, command=self.runSaveVersion, parent=saveVersionColumnLayout)
            # call save asset version Window:
            cmds.showWindow(dpSaveVersionWin)
            self.getSaveVersionPreviewTextByUI()
        else:
            cmds.confirmDialog(title=self.ar.data.lang['i222_save']+" "+self.ar.data.lang['i303_asset']+" "+self.ar.data.lang['m205_version'].lower(), message=self.ar.data.lang['r069_noAssetToSaveVersion'], button="Ok")


    def runSaveVersion(self, *args):
        """ Just save a new asset file version.
        """
        if self.saveVersionFile:
            thisType = "mayaAscii"
            if "extension" in self.pipe_data.keys() and self.pipe_data['extension'].endswith("mb"):
                thisType = "mayaBinary"
            cmds.file(rename=self.saveVersionFile)
            cmds.file(save=True, type=thisType, force=True)
            self.ar.utils.close_ui("dpSaveVersionWindow")
            self.ar.data.rebuilding = False
            self.refresh_asset_data()


    def refresh_asset_name_ui(self, *args):
        """ Just read again the pipeline data and set the UI with the assetName.
        """
        if self.check_asset_context():
            try:
                cmds.frameLayout("asset_fl", edit=True, label=self.ar.data.lang['i303_asset']+" - "+self.pipe_data['assetName'])
                cmds.textFieldGrp("asset_name_tfg", edit=True, text=self.pipe_data['assetName'])
                if self.ar.data.verbose:
                    print(self.ar.data.lang['r067_currentAssetContext']+" "+self.pipe_data['assetName'])
            except:
                pass
        else:
            try:
                cmds.frameLayout("asset_fl", edit=True, label=self.ar.data.lang['i303_asset']+" - "+self.ar.data.lang['i305_none'])
                cmds.textFieldGrp("asset_name_tfg", edit=True, text=self.ar.data.lang['i305_none'])
                if self.ar.data.verbose:
                    print(self.ar.data.lang['r027_noAssetContext'])
            except:
                pass


    def check_asset_context(self):
        """ Returns True if there's an asset context to work the rebuilding or False if not.
        """
        has_asset_context = False
        if self.pipe_data:
            if self.pipe_data['assetName']:
                if not self.pipe_data['assetName'] == "None":
                    has_asset_context = True
        return has_asset_context
    

    def refresh_project_ui(self):
        """ Just edit the UI with the current pipeline path.
        """
        # get path to update open_folder button command
        path = self.pipe_data['projectPath']
        if "wipPath" in self.pipe_data.keys():
            path = self.pipe_data['wipPath']
        if self.pipe_data['assetName'] and self.pipe_data['assetPath']:
            path = self.pipe_data['assetPath']
        try:
            cmds.textFieldGrp("asset_maya_project_tfg", edit=True, text=self.pipe_data['mayaProject'])
            cmds.textFieldGrp("asset_pipeline_tfg", edit=True, text=self.pipe_data['projectPath'])
            cmds.button("asset_open_folder_bt", edit=True, command=partial(self.ar.packager.open_folder, path))
        except:
            pass


    def get_latest_file(self, path):
        """ Returns the latest listed file in the given path.
        """
        latest_files = next(os.walk(path))[2]
        if latest_files:
            latest_files.sort()
            return latest_files[-1]


    def load_asset(self, path=None, file=None, mode=0, *args):
        """ Open the saved Maya file with the user choose by UI or given path and file name arguments.
            Mode:
            0 = load: open Maya scene.
            1 = replaceData: copy dpData from the selected or given asset to this current file.
            2 = checkBoxes UI to select assets.
        """
        if not path:
            if "wipPath" in list(self.pipe_data.keys()):
                path = self.pipe_data['wipPath']
            else:
                # There's no path to load assets
                cmds.confirmDialog(title=self.ar.data.lang['i187_load']+" "+self.ar.data.lang['i303_asset'], message=self.ar.data.lang['i350_notFoundPipeInfoFile'], button="Ok")
        if path and os.path.exists(path):
            if not file:
                assetList = next(os.walk(path))[1]
                if assetList:
                    assetList.sort()
                    if mode == 2:
                        self.selectAssetCheckBoxUI(assetList, path, mode)
                        return
                    elif mode == 1: #replaceData exclude the current asset from given list to chose.
                        assetList.remove(self.pipe_data['assetName'])
                    # Load UI to choose one asset to define the file to use
                    self.selectAssetFromListUI(assetList, path, mode)
                    return
                else:
                    # Inform that it isn't possible to continue without wip assets to load
                    cmds.confirmDialog(title=self.ar.data.lang['i187_load']+" "+self.ar.data.lang['i303_asset'], message=self.ar.data.lang['i351_notFoundWIPAssets'], button="Ok")
            if file:
                assetFolder = path+"/"+file
                if mode == 0: #load
                    # Get latest version
                    latestFile = self.get_latest_file(assetFolder)
                    # Open maya scene
                    if latestFile:
                        savedScene = self.ar.utils.checkSavedScene()
                        if not savedScene:
                            savedScene = self.userSaveThisScene(False)
                        if savedScene:
                            self.ar.data.rebuilding = False
                            cmds.file(assetFolder+"/"+latestFile, open=True, ignoreVersion=True, force=True)
                            cmds.workspace(directory=assetFolder)
                            self.pipe_data['sceneName'] = cmds.file(query=True, sceneName=True)
                            self.pipe_data['shortName'] = cmds.file(query=True, sceneName=True, shortName=True)
                elif mode == 1: #replaceData
                    # Open UI to select each desired module dpData to replace from
                    self.pathToReplaceFrom = assetFolder
                    self.getDPDataExistListToReplace(self.pathToReplaceFrom)
                    if self.existDataList:
                        self.dpDataToReplaceUI(file)
                    else:
                        # There's no data do replace from the selected asset
                        cmds.confirmDialog(title=self.ar.data.lang['i187_load']+" "+self.ar.data.lang['i303_asset'], message=self.ar.data.lang['r007_notExportedData']+": "+file, button="Ok")
        else:
            # There's no wip path to load assets
            cmds.confirmDialog(title=self.ar.data.lang['i187_load']+" "+self.ar.data.lang['i303_asset'], message=self.ar.data.lang['i352_notFoundWIPPath'], button="Ok")


    def selectAssetFromListUI(self, assetList, path, mode, *args):
        """ Let user select the asset file we use in the given mode (load or replaceData).
            Button will call the load_asset method again passing the choose arguments.
            Works well for load and replace data.
        """
        # declaring variables:
        selectAsset_title = 'dpAutoRig - '+self.ar.data.lang['m004_select']+" "+self.ar.data.lang['i303_asset']
        select_winWidth = 240
        select_winHeight = 285
        select_align = "center"
        self.ar.utils.close_ui("dpSelectAssetWindow")
        dpSelectAssetWin = cmds.window('dpSelectAssetWindow', title=selectAsset_title, iconName='dpInfo', widthHeight=(select_winWidth, select_winHeight), menuBar=False, sizeable=False, minimizeButton=False, maximizeButton=False)
        # creating layout:
        selectColumnLayout = cmds.columnLayout('selectColumnLayout', adjustableColumn=True, columnOffset=['both', 20], rowSpacing=10, parent=dpSelectAssetWin)
        cmds.separator(style='none', height=10, parent=selectColumnLayout)
        cmds.text(label=self.ar.data.lang['m004_select']+" "+self.ar.data.lang['i303_asset']+":", align="left", parent=selectColumnLayout)
        self.selectAssetTSL = cmds.textScrollList('selectAssetTSL', allowMultiSelection=False, append=assetList, parent=selectColumnLayout)
        self.runSelectAssetBT = cmds.button('runSelectAssetBT', label=self.ar.data.lang['m004_select'], align=select_align, command=partial(self.selectAssetFromUI, path, mode), parent=selectColumnLayout)
        # call Window:
        cmds.showWindow(dpSelectAssetWin)


    def selectAssetFromUI(self, path, mode, *args):
        """ Transfer path and mode arguments to load_asset method and also pass the selected item from the text scroll list UI.
        """
        selectedAssetItemList = cmds.textScrollList(self.selectAssetTSL, query=True, selectItem=True)
        if selectedAssetItemList:
            self.load_asset(path, selectedAssetItemList[0], mode)
            self.ar.utils.close_ui("dpSelectAssetWindow")


    def selectAssetCheckBoxUI(self, assetList, path, mode, *args):
        """ Let user select the assets to publish in batch.
        """
        # declaring variables:
        selectAssetCB_title = 'dpAutoRig - '+self.ar.data.lang['m046_publisher']+" "+self.ar.data.lang['i358_batch']
        selectCB_winWidth = 240
        selectCB_winHeight = 285
        selectCB_align = "center"
        self.ar.utils.close_ui("dpSelectAssetCBWindow")
        dpSelectAssetCBWin = cmds.window('dpSelectAssetCBWindow', title=selectAssetCB_title, iconName='dpInfo', widthHeight=(selectCB_winWidth, selectCB_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False)
        # creating layout:
        selectBatchLayout = cmds.columnLayout('selectBatchLayout', adjustableColumn=True, columnOffset=['both', 20], rowSpacing=10, parent=dpSelectAssetCBWin)
        cmds.separator(style='none', height=10, parent=selectBatchLayout)
        cmds.text(label=self.ar.data.lang['m004_select']+" "+self.ar.data.lang['i303_asset']+"s:", align="left", parent=selectBatchLayout)
        if len(assetList) > 1:
            cmds.checkBox(label=self.ar.data.lang['m004_select']+" "+self.ar.data.lang['i211_all'], value=False, changeCommand=self.selectAllAssetCB, parent=selectBatchLayout)
        cmds.separator(style='in', height=10, parent=selectBatchLayout)
        selectCBAssetSL = cmds.scrollLayout('selectCBAssetSL', parent=selectBatchLayout)
        selectCBColumnLayout = cmds.columnLayout('selectCBColumnLayout', adjustableColumn=True, columnOffset=['both', 20], rowSpacing=10, parent=selectCBAssetSL)
        # assets checkboxes
        self.selectedBatchList = []
        for asset in assetList:
            self.selectedBatchList.append(cmds.checkBox(asset+"CB", label=asset, parent=selectCBColumnLayout))
        cmds.separator(style='in', height=10, parent=selectBatchLayout)
        self.commentBatchTFG = cmds.textFieldGrp('commentBatchTFG', label=self.ar.data.lang['i219_comments'], text='', adjustableColumn=2, editable=True, columnAlign2=("left", "left"), columnAttach2=("left", "left"), columnWidth=[(1, 55), (2, 50)], parent=selectBatchLayout)
        self.runSelectCBAssetBT = cmds.button('runSelectCBAssetBT', label=self.ar.data.lang['i216_publish'], align=selectCB_align, command=partial(self.ar.publisher.loadPublishingBatch, path), height=30, backgroundColor=(0.75, 0.75, 0.75), parent=selectBatchLayout)
        cmds.separator(style='none', height=5, parent=selectBatchLayout)
        # call Window:
        cmds.showWindow(dpSelectAssetCBWin)


    def loadProjectPath(self, *args):
        """ Open a file dialog to get the project path and write it in the respective field.
        """
        result_items = cmds.fileDialog2(fileMode=3, dialogStyle=2)
        if result_items:
            cmds.textFieldButtonGrp(self.projectPathTFBG, edit=True, text=result_items[0])


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
            wipFolder = self.pipe_data['f_wip']
            if wipFolder:
                if not wipFolder.endswith("/"):
                    wipFolder = wipFolder+"/"
            if newWIPVersion and newModelVersion and newAssetName:
                self.newAssetFile = projectPath+wipFolder+newAssetName+"/"+newAssetName+self.pipe_data['s_model']+newModelVersion.zfill(self.pipe_data['i_padding'])+self.pipe_data['s_rig']+newWIPVersion.zfill(self.pipe_data['i_padding'])+".ma"
        if self.newAssetFile:
            cmds.text(self.newAssetPreviewTxt, edit=True, label=self.newAssetFile)
        return self.newAssetFile


    def getSaveVersionPreviewTextByUI(self, *args):
        """ Concatenate UI info to compose rig version file name to save.
        """
        modelVersionValue = cmds.textFieldGrp(self.saveModelVersionTFG, query=True, text=True)
        rigVersionValue = cmds.textFieldGrp(self.saveRigVersionTFG, query=True, text=True)
        previewSaveVersionFileName = self.pipe_data['assetName']+self.pipe_data['s_model']+modelVersionValue.zfill(self.pipe_data['i_padding'])+self.pipe_data['s_rig']+rigVersionValue.zfill(self.pipe_data['i_padding'])+self.pipe_data['extension']
        self.saveVersionFile = self.pipe_data['assetPath']+"/"+previewSaveVersionFileName
        if self.saveVersionFile:
            cmds.text(self.saveVersionPreviewTxt, edit=True, label=previewSaveVersionFileName)
        return self.saveVersionPreviewTxt
        

    def getNextFileVersionName(self, existingFile=True, *args):
        """ Concatenate asset info to compose rig version file name to save.
        """
        if existingFile and "wipPath" in list(self.pipe_data.keys()):
            path = self.pipe_data['wipPath']+"/"+self.pipe_data['assetName']
            modelVersionValue = str(int(self.get_model_version(self.get_latest_file(path))))
            rigVersionValue = str(int(self.get_wip_rig_version(self.get_latest_file(path)))+1)
        else:
            modelVersionValue = str(int(self.get_model_version()))
            rigVersionValue = str(int(self.get_wip_rig_version())+1)
        return self.pipe_data['assetPath']+"/"+self.pipe_data['assetName']+self.pipe_data['s_model']+modelVersionValue.zfill(self.pipe_data['i_padding'])+self.pipe_data['s_rig']+rigVersionValue.zfill(self.pipe_data['i_padding'])+self.pipe_data['extension']
    

    def createNewAssetUI(self, *args):
        """ A simple UI to get the asset info like name, model version, wip rig version in order to create a new asset context.
        """
        # declaring variables:
        self.newAsset_title     = 'dpAutoRig - '+self.ar.data.lang['i158_create']+" "+self.ar.data.lang['i304_new']+" "+self.ar.data.lang['i303_asset']
        self.newAsset_winWidth  = 380
        self.newAsset_winHeight = 220
        self.newAsset_align     = "left"
        # creating New Asset Window:
        self.ar.utils.close_ui("dpNewAssetWindow")
        dpNewAssetWin = cmds.window('dpNewAssetWindow', title=self.newAsset_title, iconName='dpInfo', widthHeight=(self.newAsset_winWidth, self.newAsset_winHeight), menuBar=False, sizeable=False, minimizeButton=False, maximizeButton=False)
        # creating text layout:
        newAssetColumnLayout = cmds.columnLayout('newAssetColumnLayout', adjustableColumn=True, columnOffset=['both', 20], rowSpacing=3, parent=dpNewAssetWin)
        cmds.separator(style='none', height=10, parent=newAssetColumnLayout)
        self.newAssetNameTFG = cmds.textFieldGrp('newAssetNameTFG', label=self.ar.data.lang['i303_asset']+" "+self.ar.data.lang['m006_name'].lower(), columnWidth2=(80, 150), textChangedCommand=self.getNewAssetPreviewTextByUI, adjustableColumn=2, parent=newAssetColumnLayout)
        self.newModelVersionTFG = cmds.textFieldGrp('newModelVersionTFG', label="Model "+self.ar.data.lang['m205_version'].lower(), text="0", columnWidth2=(80, 50), textChangedCommand=self.getNewAssetPreviewTextByUI, parent=newAssetColumnLayout)
        self.newWIPVersionTFG = cmds.textFieldGrp('newWIPVersionTFG', label="WIP "+self.ar.data.lang['m205_version'].lower(), text="0", columnWidth2=(80, 50), textChangedCommand=self.getNewAssetPreviewTextByUI, parent=newAssetColumnLayout)
        try:
            self.projectPathTFBG = cmds.textFieldButtonGrp('projectPathTFG', label=self.ar.data.lang['i301_project']+" path", text=self.pipe_data['projectPath'], columnWidth3=(80, 150, 30), buttonLabel=self.ar.data.lang['i187_load'], buttonCommand=self.loadProjectPath, adjustableColumn=2, textChangedCommand=self.getNewAssetPreviewTextByUI, parent=newAssetColumnLayout)
        except:
            self.projectPathTFBG = cmds.textFieldButtonGrp('projectPathTFG', label=self.ar.data.lang['i301_project']+" path", text="", columnWidth3=(80, 150, 30), buttonLabel=self.ar.data.lang['i187_load'], buttonCommand=self.loadProjectPath, adjustableColumn=2, textChangedCommand=self.getNewAssetPreviewTextByUI, parent=newAssetColumnLayout)
        cmds.separator(style='none', height=10, parent=newAssetColumnLayout)
        cmds.text('previewTxt', label="Preview:", font="obliqueLabelFont", align=self.newAsset_align, parent=newAssetColumnLayout)
        previewTextLayout = cmds.scrollLayout("previewTextLayout", height=35, parent=newAssetColumnLayout)
        self.newAssetPreviewTxt = cmds.text('newAssetPreviewTxt', label="", font="boldLabelFont", align="center", parent=previewTextLayout)
        cmds.button('runCreateNewAssetBT', label=self.ar.data.lang['i158_create'], align=self.newAsset_align, command=self.createNewAsset, parent=newAssetColumnLayout)
        # call New Asset Window:
        cmds.showWindow(dpNewAssetWin)
        self.getNewAssetPreviewTextByUI()


    def createNewAsset(self, assetFile=None, *args):
        """ Create a new asset context saving a maya file with the given asset file complete path.
        """
        if assetFile:
            self.newAssetFile = assetFile
        if self.newAssetFile:
            folder = self.newAssetFile[:self.newAssetFile.rfind("/")]
            if self.make_dir_if_not_exists(folder):
                cmds.file(rename=self.newAssetFile)
                cmds.workspace(directory=folder)
                cmds.file(save=True, type="mayaAscii", force=True)
                self.ar.utils.close_ui("dpNewAssetWindow")
                self.ar.data.rebuilding = False
                self.refresh_asset_data()
            else:
                cmds.confirmDialog(title=self.ar.data.lang['i158_create']+" "+self.ar.data.lang['i304_new']+" "+self.ar.data.lang['i303_asset'], message=self.ar.data.lang['i349_alreadyExistsAsset'], button="Ok")
        else:
            cmds.confirmDialog(title=self.ar.data.lang['i158_create']+" "+self.ar.data.lang['i304_new']+" "+self.ar.data.lang['i303_asset'], message=self.ar.data.lang['i307_fillFieldCorrectly'], button="Ok")


    def getDPDataExistListToReplace(self, path, *args):
        """ Check if exists exported module data in the given path.
        """
        defaultList = [
            "modelIO",
            "supportNodeIO",
            "blendShapeIO",
            "shaderIO",
            "guideIO",
            "rivetIO",
            "parentingIO",
            "skinningIO",
            "deformationIO",
            "componentTagIO",
            "inputOrderIO",
            "renameIO",
            "transformationIO",
            "controlShapeIO",
            "attributeIO",
            "constraintIO",
            "utilityIO",
            "drivenKeyIO",
            "offsetMatrixIO",
            "connectionIO",
            "calibrationIO",
            "visibilityIO",
            "channelIO"
            ]
        self.existDataList = []
        for item in defaultList:
            if os.path.exists(path+"/"+self.pipe_data["s_"+item]):
                self.existDataList.append(item)


    def dpDataToReplaceUI(self, fromAssetName, *args):
        """ UI to list exist items as a checkboxes to let the user choose what to replace in the dpData.
        """
        # declaring variables:
        self.replaceDPData_title     = 'dpAutoRig - '+self.ar.data.lang['m219_replace']+" "+self.ar.data.dp_data+" - "+self.ar.data.lang['i303_asset']
        self.replaceDPData_winWidth  = 220
        self.replaceDPData_winHeight = 330+(len(self.existDataList)*16)
        self.replaceDPData_align     = "left"
        # creating replace dpData Window:
        self.ar.utils.close_ui("dpReplaceDPDataWindow")
        dpReplaceDPDataWindow = cmds.window('dpReplaceDPDataWindow', title=self.replaceDPData_title, iconName='dpInfo', widthHeight=(self.replaceDPData_winWidth, self.replaceDPData_winHeight), menuBar=False, sizeable=False, minimizeButton=False, maximizeButton=False)
        # creating layout:
        replaceDataColumnLayout = cmds.columnLayout('replaceDataColumnLayout', adjustableColumn=True, columnOffset=['both', 20], rowSpacing=5, parent=dpReplaceDPDataWindow)
        cmds.separator(style='none', height=10, parent=replaceDataColumnLayout)
        cmds.text("rebuilderReplaceDataText", label=self.ar.data.lang['i308_toReplaceDPData'], parent=replaceDataColumnLayout)
        cmds.text("rebuilderReplaceDataAssetText", label="\n"+self.pipe_data['assetName'], font="boldLabelFont", parent=replaceDataColumnLayout)
        cmds.separator(style='none', height=10, parent=replaceDataColumnLayout)
        for item in self.existDataList:
            cmds.checkBox(item+"CB", label=item, value=True)
        cmds.separator(style='none', height=10, parent=replaceDataColumnLayout)
        if len(self.existDataList) > 1:
            cmds.checkBox(label=self.ar.data.lang['m004_select']+" "+self.ar.data.lang['i211_all'], value=True, changeCommand=self.selectAllDataCB, parent=replaceDataColumnLayout)
            cmds.separator(style='none', height=10, parent=replaceDataColumnLayout)
        cmds.button('runReplaceDataBT', label=self.ar.data.lang['m219_replace'].upper()+"\n"+fromAssetName+" -> "+self.pipe_data['assetName'], align=self.replaceDPData_align, command=self.replaceDataByUI, parent=replaceDataColumnLayout)
        # call New Asset Window:
        cmds.showWindow(dpReplaceDPDataWindow)
        
    
    def selectAllDataCB(self, cbValue, *args):
        """ Set all existing data checkbox values.
        """
        for item in self.existDataList:
            cmds.checkBox(item+"CB", edit=True, value=cbValue)


    def selectAllAssetCB(self, cbValue, *args):
        """ Set all existing asset checkbox values.
        """
        for item in self.selectedBatchList:
            cmds.checkBox(item, edit=True, value=cbValue)


    def replaceDataByUI(self, *args):
        """ Read the dpReplaceDPDataWindow UI to get the active checkBoxes in order to return it in a list.
        """
        self.dpDataToReplaceList = []
        for item in self.existDataList:
            if cmds.checkBox(item+"CB", query=True, value=True):
                self.dpDataToReplaceList.append(item)
        if self.dpDataToReplaceList:
            self.runReplaceData()
            self.ar.utils.close_ui("dpReplaceDPDataWindow")
        

    def runReplaceData(self, path=None, toReplaceList=None, *args):
        """ Replace the dpData sub_folder with the given arguments.
        """
        if not path:
            path = self.pathToReplaceFrom
        if not toReplaceList:
            toReplaceList = self.dpDataToReplaceList
        if path and toReplaceList:
            for toReplace in toReplaceList:
                sourcePath = path+"/"+self.pipe_data['s_'+toReplace]
                destPath = self.pipe_data['assetPath']+"/"+self.pipe_data['s_'+toReplace]
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
                        self.make_dir_if_not_exists(destPath)
                    sourceItem = next(os.walk(sourcePath))[2][-1]
                    ext = sourceItem[sourceItem.rfind("."):]
                    prefix = sourceItem[:sourceItem.find("_")+1]
                    destItem = destPath+"/"+prefix+self.pipe_data['assetName']+self.pipe_data['s_model']+"0".zfill(self.pipe_data['i_padding'])+self.pipe_data['s_rig']+"0".zfill(self.pipe_data['i_padding'])+ext
                    shutil.copy2(sourcePath+"/"+sourceItem, destItem)
            # Concatenate done message
            sucessMessageText = self.ar.data.lang['r068_replacedDataSuccess']+"\n\n"+self.ar.data.lang['i036_from']+": "+path+"\n"+self.ar.data.lang['i037_to']+": "+self.pipe_data['assetName']+"\n\n"+" \n".join(toReplaceList)
            cmds.confirmDialog(title="dpAutoRigSystem", message=sucessMessageText, button="Ok")


    def userSaveThisScene(self, mustSaveIt=True, *args):
        """ Open a confirmDialog to user save or save as this file.
            Return the saved file path or False if canceled.
            If not mustSaveIt, the user can choose continue without saving, them it'll return True.
        """
        shortName = cmds.file(query=True, sceneName=True, shortName=True)
        saveName = self.ar.data.lang['i222_save']
        saveAsName = self.ar.data.lang['i223_saveAs']
        cancelName = self.ar.data.lang['i132_cancel']
        continueName = self.ar.data.lang['i174_continue']
        if mustSaveIt:
            confirmResult = cmds.confirmDialog(title="dpAutoRigSystem - Pipeliner "+str(self.ar.data.version), message=self.ar.data.lang['i201_saveScene'], button=[saveName, saveAsName, cancelName], defaultButton=saveName, cancelButton=cancelName, dismissString=cancelName)
        else:
            confirmResult = cmds.confirmDialog(title="dpAutoRigSystem - Pipeliner "+str(self.ar.data.version), message=self.ar.data.lang['i201_saveScene'], button=[saveName, saveAsName, cancelName, continueName], defaultButton=saveName, cancelButton=cancelName, dismissString=cancelName)
        if confirmResult == cancelName:
            return False
        if confirmResult == continueName:
            return True
        else:
            if not shortName or confirmResult == saveAsName: #untitled or saveAs
                newNameList = cmds.fileDialog2(fileFilter="Maya ASCII (*.ma);;Maya Binary (*.mb);;", fileMode=0, dialogStyle=2)
                if newNameList:
                    newName = newNameList[0]
                    ext = self.ar.publisher.getFileTypeByExtension(newName)
                    cmds.file(rename=newName)
                    return cmds.file(save=True, type=ext)
                else:
                    return False
            else: #save
                cmds.file(rename=cmds.file(query=True, sceneName=True))
                ext = cmds.file(type=True, query=True)[0]
                return cmds.file(save=True, type=ext)
