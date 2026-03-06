import os
import sys
import json
from maya import cmds
from maya import mel



class Configuration(object):
    def __init__(self, ar):
        self.ar = ar
        self.ar.data.verbose = self.ar.dev

        self.load_path()

        self.load_language()
        self.load_validator_preset()
        self.load_curve_preset()
        self.load_curve_degree()

        self.load_icons()

        

        # TODO
            # get_language()
            # get_update()
            # get_terms_cond()
            # get_icon()
            #
            # load_updater() ===== settings. class Update


    def load_path(self):
        path = str(os.path.join(os.path.dirname(sys._getframe(1).f_code.co_filename))).replace("\\", "/")
        self.ar.data.dp_auto_rig_path = path[:path.rfind("/")] #remove '/core'

        #correct_path = path[:path.rfind("/")] #remove '/core'
        #if os.name == "posix":
        #    self.ar.data.dp_auto_rig_path = stringPath[0:stringPath.rfind("/")]
        #else:
        #    self.ar.data.dp_auto_rig_path = correct_path[correct_path.find("/")-2:]
    


    def load_language(self):
        self.ar.data.lang, self.ar.data.lang_preset_data = self.check_option_data(
                                                                                    self.ar.data.language_option_var,
                                                                                    self.ar.data.language_default,
                                                                                    self.ar.data.language_folder
                                                                                    )
        if not self.ar.data.lang:
            raise FileExistsError("Language")


    def load_validator_preset(self):
        self.ar.data.validator_preset, self.ar.data.validator_preset_data = self.check_option_data(
                                                                                                    self.ar.data.validator_option_var,
                                                                                                    self.ar.data.validator_default,
                                                                                                    self.ar.data.validator_preset_folder
                                                                                                    )
        

    def load_curve_preset(self):
        self.ar.data.curve_preset, self.ar.data.curve_preset_data = self.check_option_data(
                                                                                            self.ar.data.curve_option_var,
                                                                                            self.ar.data.curve_default,
                                                                                            self.ar.data.curve_preset_folder
                                                                                            )

    
    def load_curve_degree(self):
        self.ar.data.degree = self.check_last_option_var(
                                                            self.ar.data.degree_option_var, 
                                                            self.ar.data.degree_default, 
                                                            self.ar.data.degrees
                                                         )
        self.ar.data.degree_option = int(self.ar.data.degree[-1])
#        if cmds.objectExists()


    def check_option_data(self, name, default, folder):
        founds, datas = self.get_json_file_content(folder)
        if founds and datas:
            last_name = self.check_last_option_var(name, default, founds)
            return datas[last_name], datas


    def get_json_file_content(self, folder, absolute=False):
        """ Find all json files in the given path and get contents used for each file.
            Create a dictionary with dictionaries of all file found.
            Return a list with the name of the found files and a dictionary with the content.
        """
        # declare the resulted list:
        items = []
        content = {}
        path = folder
        if not absolute:
            # find path where 'dpAutoRig.py' is been executed:
            path = os.path.dirname(__file__)
            # hack in order to avoid "\\" from os.sep, them we need to use the replace string method:
            path = os.path.join(path.split("core")[0], folder, "").replace("\\", "/")
        # list all files in this directory:
        found_files = os.listdir(path)
        for file in found_files:
            # verify if there is the extension ".json"
            if file.endswith(".json"):
                # get the name of the type from the file name:
                name = file.partition(".json")[0]
                # clear the old variable content and open the json file as read:
                loaded_content = None
                opened_file = open(path + file, "r", encoding='utf-8')
                try:
                    # read the json file content and store it in a dictionary:
                    loaded_content = json.loads(opened_file.read())
                    content[name] = loaded_content
                    items.append(name)
                except:
                    print("Error: corrupted json file:", file)
                # close the json file:
                opened_file.close()
        return items, content
    

    def check_last_option_var(self, name, preferable_name, founds):
        """ Verify if there's an optionVar with this name or create it with the preferable given value.
            Returns the last_value found.
        """
        last_value_exists = cmds.optionVar(exists=name)
        if not last_value_exists:
            # if not exists a last optionVar, set it to preferable_name if it exists, or to the first value in the list:
            if preferable_name in founds:
                cmds.optionVar(stringValue=(name, preferable_name))
            else:
                cmds.optionVar(stringValue=(name, founds[0]))
        # get its value puting in a variable to return it:
        result_value = cmds.optionVar(query=name)
        # if the last value in the system was different of json files, set it to preferable_name or to the first value in the list also:
        if not result_value in founds:
            if preferable_name in founds:
                result_value = preferable_name
            else:
                result_value = result_value[0]
        return result_value


    def load_icons(self):
        # TODO: review the 3: after renamed all images without the "dp_" prefix
        self.ar.data.icon = {i[3:-4]: self.ar.data.dp_auto_rig_path+"/"+self.ar.data.icons_folder+"/"+i for i in os.listdir(self.ar.data.dp_auto_rig_path+"/"+self.ar.data.icons_folder) if i.endswith(".png")}

        
        
    def open_pipeliner(self, *args):
       print("WIP opening piliener UI", args)
       self.ar.pipeliner.mainUI(self.ar)



    def create_preset(self, preset_type="curve", preset_folder="Modules/Curves/Presets", set_option_var=True, *args):
        """ Just call ctrls create preset and set it as userDefined preset.
        """
        if preset_type == "curve":
            preset_option_var = self.ar.data.curve_option_var
            new_preset = self.ar.ctrls.create_curve_preset()
        elif preset_type == "validator":
            preset_option_var = self.ar.data.validator_option_var
            new_preset = self.ar.utils.dpCreateValidatorPreset()
        if new_preset:
            # create json file:
            resultDic = self.ar.createJsonFile(new_preset, preset_folder, '_preset')
            preset_name = resultDic['_preset']
            # set this new preset as userDefined preset:
            if set_option_var:
                self.ar.opt.set_option_var(preset_option_var, preset_name)
            # show preset creation result window:
            self.ar.logger.infoWin('i129_createPreset', 'i133_presetCreated', '\n'+preset_name+'\n\n'+self.ar.data.lang['i134_rememberPublish']+'\n\n'+self.ar.data.lang['i018_thanks'], 'center', 205, 270)
            # close and reload dpAR UI in order to avoid Maya crash
            self.ar.ui_manager.reload_ui()


    def get_validator_addons(self, path="addOnsPath"):
        """ Return a list of Validator's AddOns or Finishing to load.
        """
        if os.path.exists(self.ar.pipeliner.pipeData[path]):
            return self.ar.startGuideModules("", "exists", None, path=self.ar.pipeliner.pipeData[path])


class Option(object):
    def __init__(self, ar):
        self.ar = ar
        self.set_use_default_render_layer(True)
        
        
        # TODO: getters and setters...


    def change_degree(self, value, *args):
        self.set_option_var(self.ar.data.degree_option_var, value)
        self.ar.data.degree_option = int(value[-1])
        for module_instance in self.ar.moduleInstancesList:
            if "degree" in cmds.listAttr(module_instance.moduleGrp):
                cmds.setAttr(module_instance.moduleGrp+".degree", self.ar.data.degree_option)


    def check_use_default_render_layer(self):
        if self.ar.data.use_default_render_layer:
            self.set_use_default_render_layer(True)


    def set_option_var(self, opt_var, item):
        cmds.optionVar(remove=opt_var)
        cmds.optionVar(stringValue=(opt_var, item))


    def set_verbose(self, value):
        """ Set the dev verbose variable.
        """
        self.ar.data.verbose = value


    def set_display_joint(self, value):
        self.ar.data.display_joint = value


    def set_integrate_module(self, value):
        self.ar.data.integrate_module = value


    def set_colorize_curve(self, value):
        self.ar.data.colorize_curve = value

    
    def set_add_supplementary_attr(self, value):
        self.ar.data.add_supplementary_attr = value


    def set_prefix(self, prefix=False):
        if not prefix:
            result_dialog = cmds.promptDialog(
                                                title=self.ar.data.lang['i144_prefix'],
                                                message=self.ar.data.lang['i003_prefixAll'],
                                                button=[self.ar.data.lang['i131_ok'], self.ar.data.lang['i132_cancel']],
                                                defaultButton=self.ar.data.lang['i131_ok'],
                                                cancelButton=self.ar.data.lang['i132_cancel'],
                                                dismissString=self.ar.data.lang['i132_cancel'])
            if result_dialog == self.ar.data.lang['i131_ok']:
                prefix = cmds.promptDialog(query=True, text=True)
        if prefix:
            prefix = self.ar.utils.normalizeText(prefix, prefixMax=10)
            if not prefix:
                self.ar.data.prefix = ""
                if self.ar.data.verbose:
                    mel.eval('warning \"'+self.ar.data.lang["p001_prefixText"]+'\";')
            else:
                if not prefix.endswith("_"):
                    prefix = f"{prefix}_"
                self.ar.data.prefix = prefix
                if cmds.text("rig_prefix_txt", query=True, exists=True):
                    cmds.text("rig_prefix_txt", edit=True, label=f"{self.ar.data.lang['i144_prefix']}: {prefix}", visible=True)
        else:
            self.ar.data.prefix = ""
            if cmds.text("rig_prefix_txt", query=True, exists=True):
                cmds.text("rig_prefix_txt", edit=True, label="", visible=False)


    def set_display_temp_grp(self, value):
        """ Change display hidden guide groups in the Outliner:
            dpAR_Temp_Grp
            dpAR_GuideMirror_Grp
        """
        self.ar.data.display_temp_grp = not value #invert value (True -> False or False -> True)
        if cmds.objExists(self.ar.data.temp_grp):
            cmds.setAttr(self.ar.data.temp_grp+".hiddenInOutliner", self.ar.data.display_temp_grp)
        if cmds.objExists(self.ar.data.guide_mirror_grp):
            cmds.setAttr(self.ar.data.guide_mirror_grp+".hiddenInOutliner", self.ar.data.display_temp_grp)
        mel.eval('source AEdagNodeCommon;')
        mel.eval('AEdagNodeCommonRefreshOutliners();')


    def set_use_default_render_layer(self, value):
        """ Analisys if must use the Default Render Layer (masterLayer) checking the option in the UI.
            Set to use it if need.
        """
        self.ar.data.use_default_render_layer = value
        if value:
            cmds.editRenderLayerGlobals(currentRenderLayer='defaultRenderLayer')





class Update(object):
    print("WIP... update")
    # TODO: bring update setting to here