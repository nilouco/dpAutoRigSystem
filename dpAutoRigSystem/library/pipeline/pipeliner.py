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
            self.refresh_project()
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
            data = open(json_path, "r", encoding='utf-8')
            content = json.loads(data.read())
            data.close()
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
        
    
    def update_pipe_data_by_json_path(self, json_path):
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
        return self.update_pipe_data_by_json_path(json_info_path)


    def get_hook_info(self):
        """ Load Hook data and returns it.
        """
        json_hook_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.hook_file).replace("\\", "/")
        return self.update_pipe_data_by_json_path(json_hook_path)
    

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
            loaded = cmds.textFieldButtonGrp('pipeline_path_data_tfbg', query=True, text=True)
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
            cmds.textFieldButtonGrp('pipeline_path_data_tfbg', edit=True, text=loaded_file_path)
            self.get_pipeline_data(self.info_file)
            self.load_ui_data()
            self.set_pipeline_settings_path(self.pipe_data['path'], self.info_file)

    
    def set_pipeline_settings_path(self, path, file):
        """ Set the json file for dpPipelineSetting in the main dpAutoRigSystem folder to use the path and file given.
        """
        if path and file:
            json_path = self.get_json_settings_path()
            if os.path.exists(json_path):
                settings_data = self.get_json_content(json_path)
                settings_data['path'] = path
                settings_data['file'] = file
                # write json file in the HD
                with open(json_path, 'w') as json_file:
                    json.dump(settings_data, json_file, indent=4, sort_keys=True)


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
        cmds.textFieldButtonGrp('pipeline_path_data_tfbg', edit=True, text="")
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
            cmds.textFieldButtonGrp('pipeline_path_data_tfbg', edit=True, text=file_path)
            self.pipe_data['path'] = file_path[:file_path.rfind("/")]
            self.pipe_data['date'] = self.get_today()
            self.info_file = file_path[file_path.rfind("/")+1:]
            self.save_pipe_info(close_ui=False)


    def save_pipe_info(self, close_ui=True, *args):
        """ Save the pipeline data into the json file in the HD.
            Write the pipeline data path in the pipeline setting json file.
        """
        self.ar.pipeline_ui.get_ui_data_to_save()
        if self.ar.data.ui_state:
            path_data_from_ui = cmds.textFieldButtonGrp('pipeline_path_data_tfbg', query=True, text=True)
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
        """ Save the json file with the given data data in the given file name path.
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
        """ Just save a new asset file version.
        """
        if self.saveVersionFile:
            this_type = "mayaAscii"
            if "extension" in self.pipe_data.keys() and self.pipe_data['extension'].endswith("mb"):
                this_type = "mayaBinary"
            cmds.file(rename=self.saveVersionFile)
            cmds.file(save=True, type=this_type, force=True)
            self.ar.utils.close_ui("dpSaveVersionWindow")
            self.ar.data.rebuilding = False
            self.refresh_asset_data()


    def refresh_asset_name_ui(self):
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
    

    def refresh_project(self):
        """ Just edit the pipeline data with current pipeline path and call the UI manager to update them.
        """
        # get path to update open_folder button command
        path = self.pipe_data['projectPath']
        if "wipPath" in self.pipe_data.keys():
            path = self.pipe_data['wipPath']
        if self.pipe_data['assetName'] and self.pipe_data['assetPath']:
            path = self.pipe_data['assetPath']
        if self.ar.data.ui_state:
            self.ar.pipeline_ui.refresh_project_ui(path)


    def get_latest_file(self, path):
        """ Returns the latest listed file in the given path.
        """
        if path and os.path.exists(path):
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
                assets = next(os.walk(path))[1]
                if assets:
                    assets.sort()
                    if mode == 2:
                        self.ar.pipeline_ui.select_asset_checkbox_ui(assets, path)
                        return
                    elif mode == 1: #replaceData exclude the current asset from given list to chose.
                        assets.remove(self.pipe_data['assetName'])
                    # Load UI to choose one asset to define the file to use
                    self.ar.pipeline_ui.select_asset_ui(assets, path, mode)
                    return
                else:
                    # Inform that it isn't possible to continue without wip assets to load
                    cmds.confirmDialog(title=self.ar.data.lang['i187_load']+" "+self.ar.data.lang['i303_asset'], message=self.ar.data.lang['i351_notFoundWIPAssets'], button="Ok")
            if file:
                asset_folder = path+"/"+file
                if mode == 0: #load
                    # Get latest version
                    latest_file = self.get_latest_file(asset_folder)
                    # Open maya scene
                    if latest_file:
                        saved_scene = self.ar.utils.checkSavedScene()
                        if not saved_scene:
                            saved_scene = self.confirm_save_this_scene(False)
                        if saved_scene:
                            self.ar.data.rebuilding = False
                            cmds.file(asset_folder+"/"+latest_file, open=True, ignoreVersion=True, force=True)
                            cmds.workspace(directory=asset_folder)
                            self.pipe_data['sceneName'] = cmds.file(query=True, sceneName=True)
                            self.pipe_data['shortName'] = cmds.file(query=True, sceneName=True, shortName=True)
                elif mode == 1: #replaceData
                    # Open UI to select each desired module dpData to replace from
                    self.path_to_replace_from = asset_folder
                    self.get_datas_to_replace(self.path_to_replace_from)
                    if self.ios:
                        self.ar.pipeline_ui.replace_data_ui(file)
                    else:
                        # There's no data do replace from the selected asset
                        cmds.confirmDialog(title=self.ar.data.lang['i187_load']+" "+self.ar.data.lang['i303_asset'], message=self.ar.data.lang['r007_notExportedData']+": "+file, button="Ok")
        else:
            # There's no wip path to load assets
            cmds.confirmDialog(title=self.ar.data.lang['i187_load']+" "+self.ar.data.lang['i303_asset'], message=self.ar.data.lang['i352_notFoundWIPPath'], button="Ok")


    def get_save_version_preview_text(self, *args):
        """ Concatenate UI info to compose rig version file name to save.
        """
        modelVersionValue = cmds.textFieldGrp('save_version_model_tfg', query=True, text=True)
        rigVersionValue = cmds.textFieldGrp('save_version_rig_tfg', query=True, text=True)
        previewSaveVersionFileName = self.pipe_data['assetName']+self.pipe_data['s_model']+modelVersionValue.zfill(self.pipe_data['i_padding'])+self.pipe_data['s_rig']+rigVersionValue.zfill(self.pipe_data['i_padding'])+self.pipe_data['extension']
        self.saveVersionFile = self.pipe_data['assetPath']+"/"+previewSaveVersionFileName
        if self.saveVersionFile:
            cmds.text('save_version_preview_txt', edit=True, label=previewSaveVersionFileName)
        return 'save_version_preview_txt'


    def create_new_asset(self, asset_file=None, *args):
        """ Create a new asset context saving a maya file with the given asset file complete path.
        """
        if asset_file:
            self.new_asset_file = asset_file
        if self.new_asset_file:
            folder = self.new_asset_file[:self.new_asset_file.rfind("/")]
            if self.make_dir_if_not_exists(folder):
                cmds.file(rename=self.new_asset_file)
                cmds.workspace(directory=folder)
                cmds.file(save=True, type="mayaAscii", force=True)
                self.ar.utils.close_ui("dpNewAssetWindow")
                self.ar.data.rebuilding = False
                self.refresh_asset_data()
            else:
                cmds.confirmDialog(title=self.ar.data.lang['i158_create']+" "+self.ar.data.lang['i304_new']+" "+self.ar.data.lang['i303_asset'], message=self.ar.data.lang['i349_alreadyExistsAsset'], button="Ok")
        else:
            cmds.confirmDialog(title=self.ar.data.lang['i158_create']+" "+self.ar.data.lang['i304_new']+" "+self.ar.data.lang['i303_asset'], message=self.ar.data.lang['i307_fillFieldCorrectly'], button="Ok")


    def get_datas_to_replace(self, path, *args):
        """ Check if exists exported module data in the given path.
        """
        io_elements = [
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
        self.ios = []
        for item in io_elements:
            if os.path.exists(path+"/"+self.pipe_data["s_"+item]):
                self.ios.append(item)


    def replace_data(self, path=None, to_replace_items=None):
        """ Replace the dpData sub_folder with the given arguments.
        """
        if not path:
            path = self.path_to_replace_from
        if not to_replace_items:
            to_replace_items = self.ar.pipeline_ui.to_replace_datas
        if path and to_replace_items:
            for item in to_replace_items:
                source_path = path+"/"+self.pipe_data['s_'+item]
                dest_path = self.pipe_data['assetPath']+"/"+self.pipe_data['s_'+item]
                if os.path.exists(source_path):
                    if os.path.exists(dest_path):
                        for dest_file in next(os.walk(dest_path))[2]:
                            try:
                                os.remove(dest_path+"/"+dest_file)
                            except PermissionError as exc:
                                # use a brute force to delete without permission:
                                os.chmod(dest_path+"/"+dest_file, stat.S_IWUSR)
                                os.remove(dest_path+"/"+dest_file)
                    else:
                        self.make_dir_if_not_exists(dest_path)
                    source_item = next(os.walk(source_path))[2][-1]
                    ext = source_item[source_item.rfind("."):]
                    prefix = source_item[:source_item.find("_")+1]
                    dest_item = dest_path+"/"+prefix+self.pipe_data['assetName']+self.pipe_data['s_model']+"0".zfill(self.pipe_data['i_padding'])+self.pipe_data['s_rig']+"0".zfill(self.pipe_data['i_padding'])+ext
                    shutil.copy2(source_path+"/"+source_item, dest_item)
            # Concatenate done message
            sucess_message_text = self.ar.data.lang['r068_replacedDataSuccess']+"\n\n"+self.ar.data.lang['i036_from']+": "+path+"\n"+self.ar.data.lang['i037_to']+": "+self.pipe_data['assetName']+"\n\n"+" \n".join(to_replace_items)
            cmds.confirmDialog(title="dpAutoRigSystem", message=sucess_message_text, button="Ok")


    def confirm_save_this_scene(self, must_save_it=True, *args):
        """ Open a confirmDialog to user save or save as this file.
            Return the saved file path or False if canceled.
            If not must_save_it, the user can choose continue without saving, them it'll return True.
        """
        short_name = cmds.file(query=True, sceneName=True, shortName=True)
        save_name = self.ar.data.lang['i222_save']
        save_as_name = self.ar.data.lang['i223_saveAs']
        cancel_name = self.ar.data.lang['i132_cancel']
        continue_name = self.ar.data.lang['i174_continue']
        if must_save_it:
            confirm_result = cmds.confirmDialog(title="dpAutoRigSystem - Pipeliner "+str(self.ar.data.version), message=self.ar.data.lang['i201_saveScene'], button=[save_name, save_as_name, cancel_name], defaultButton=save_name, cancelButton=cancel_name, dismissString=cancel_name)
        else:
            confirm_result = cmds.confirmDialog(title="dpAutoRigSystem - Pipeliner "+str(self.ar.data.version), message=self.ar.data.lang['i201_saveScene'], button=[save_name, save_as_name, cancel_name, continue_name], defaultButton=save_name, cancelButton=cancel_name, dismissString=cancel_name)
        if confirm_result == cancel_name:
            return False
        if confirm_result == continue_name:
            return True
        else:
            if not short_name or confirm_result == save_as_name: #untitled or saveAs
                new_names = cmds.fileDialog2(fileFilter="Maya ASCII (*.ma);;Maya Binary (*.mb);;", fileMode=0, dialogStyle=2)
                if new_names:
                    new_name = new_names[0]
                    ext = self.ar.publisher.get_file_type_by_extension(new_name)
                    cmds.file(rename=new_name)
                    return cmds.file(save=True, type=ext)
                else:
                    return False
            else: #save
                cmds.file(rename=cmds.file(query=True, sceneName=True))
                ext = cmds.file(type=True, query=True)[0]
                return cmds.file(save=True, type=ext)
