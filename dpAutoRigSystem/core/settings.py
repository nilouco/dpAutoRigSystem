import os
import sys
import json
import datetime
import getpass
import urllib.request
import socket
import platform
from maya import cmds
from maya import mel



class Configuration(object):
    def __init__(self, ar):
        self.ar = ar
        
        
        #
        # TODO: define verbose as il fault here
        #
        self.ar.data.verbose = self.ar.dev


        self.lib_folders = [
                            self.ar.data.standard_folder,
                            self.ar.data.integrated_folder,
                            self.ar.data.curve_simple_folder,
                            self.ar.data.curve_combined_folder,
                            self.ar.data.checkin_folder,
                            self.ar.data.checkout_folder,
                            self.ar.data.start_folder,
                            self.ar.data.source_folder,
                            self.ar.data.setup_folder,
                            self.ar.data.deforming_folder,
                            self.ar.data.custom_folder
                            ]
        self.today = str(datetime.datetime.now().date())
        self.load_path()
        self.load_version()
        self.load_language()
        self.load_validator_preset()
        self.load_curve_preset()
        self.load_curve_degree()
        self.load_menu_options()
        self.load_agree_terms()
        self.load_auto_check_update()
        self.load_icons()


    def load_path(self):
        path = str(os.path.join(os.path.dirname(sys._getframe(1).f_code.co_filename))).replace("\\", "/")
        self.ar.data.dp_auto_rig_path = path[:path.rfind("/")] #remove '/core'

        #
        # TODO test it in Mac to see if we need to correct the path
        #
        #correct_path = path[:path.rfind("/")] #remove '/core'
        #if os.name == "posix":
        #    self.ar.data.dp_auto_rig_path = stringPath[0:stringPath.rfind("/")]
        #else:
        #    self.ar.data.dp_auto_rig_path = correct_path[correct_path.find("/")-2:]
    

    def load_version(self):
        self.ar.data.version = self.ar.version.__version__
        self.ar.data.update_log = self.ar.version._update_log
        if cmds.text("loading_text", query=True, exists=True):
            cmds.text("loading_text", edit=True, label=f"Loading dpAutoRigSystem v{self.ar.data.version} ... ")
            cmds.refresh()


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


    def load_menu_options(self):
        values = []
        for item, option_var in zip([
                                        self.ar.data.colorize_curve, 
                                        self.ar.data.supplementary_attr,
                                        self.ar.data.display_joint,
                                        self.ar.data.display_temp_grp, 
                                        self.ar.data.integrate_all, 
                                        self.ar.data.default_render_layer 
                                   ], 
                                   [
                                        self.ar.data.colorize_curve_option_var,
                                        self.ar.data.supplementary_attr_option_var,
                                        self.ar.data.display_joint_option_var,
                                        self.ar.data.display_temp_grp_option_var,
                                        self.ar.data.integrate_all_option_var,
                                        self.ar.data.default_render_layer_option_var
                                   ]):
            values.append(self.check_last_option_var(
                                                        option_var, 
                                                        item, 
                                                        self.ar.data.booleans,
                                                        string=False
                                                    ))
        self.ar.data.colorize_curve = values[0]
        self.ar.data.supplementary_attr = values[1]
        self.ar.data.display_joint = values[2]
        self.ar.data.display_temp_grp = values[3]
        self.ar.data.integrate_all = values[4]
        self.ar.data.default_render_layer = values[5]


    def load_agree_terms(self):
        self.ar.data.agree_terms = self.check_last_option_var(
                                                                self.ar.data.terms_cond_option_var,
                                                                self.ar.data.agree_terms,
                                                                self.ar.data.booleans,
                                                                string=False
                                                                )


    def load_auto_check_update(self):
        self.ar.data.auto_check_update = self.check_last_option_var(
                                                                self.ar.data.check_update_option_var,
                                                                self.ar.data.auto_check_update,
                                                                self.ar.data.booleans,
                                                                string=False
                                                                )
    

    def load_icons(self):
        # TODO: review the 3: after renamed all images without the "dp_" prefix
        self.ar.data.icon = {i[3:-4]: self.ar.data.dp_auto_rig_path+"/"+self.ar.data.icons_folder+"/"+i for i in os.listdir(self.ar.data.dp_auto_rig_path+"/"+self.ar.data.icons_folder) if i.endswith(".png")}
        
        #print(self.ar.data.icon)


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
        folder = folder.replace(".", "/")
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
    

    def check_last_option_var(self, name, preferable, founds, string=True):
        """ Verify if there's an optionVar with this name or create it with the preferable given value.
            Returns the last_value found.
        """
        if not cmds.optionVar(exists=name):
            # if not exists a last optionVar, set it to preferable if it exists, or to the first value in the list:
            if preferable in founds:
                if string:
                    cmds.optionVar(stringValue=(name, preferable))
                else:
                    cmds.optionVar(intValue=(name, preferable))
            elif string:
                cmds.optionVar(stringValue=(name, founds[0]))
            else:
                cmds.optionVar(intValue=(name, preferable))
        # get its value puting in a variable to return it:
        result_value = cmds.optionVar(query=name)
        # if the last value in the system was different of json files, set it to preferable or to the first value in the list also:
        if not result_value in founds:
            if preferable in founds:
                result_value = preferable
            else:
                result_value = result_value[0]
        return result_value

        
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
            result_data = self.save_json_file(new_preset, preset_folder, '_preset')
            preset_name = result_data['_preset']
            # set this new preset as userDefined preset:
            if set_option_var:
                self.ar.opt.set_option_var(preset_option_var, preset_name)
            # show preset creation result window:
            button_label = self.ar.data.lang['c108_open']+" "+self.ar.data.lang['i298_folder']
            button_command = self.ar.packager.openFolder
            button_argument = os.path.join(self.ar.data.dp_auto_rig_path, preset_folder.replace(".", "/"))
            self.ar.logger.infoWin('i129_createPreset', 'i133_presetCreated', '\n'+preset_name+'\n\n'+self.ar.data.lang['i134_rememberPublish']+'\n\n'+self.ar.data.lang['i018_thanks'], 'center', 205, 270, buttonList=[button_label, button_command, button_argument])
            # close and reload dpAR UI in order to avoid Maya crash
            self.ar.ui_manager.reload_ui()


    def save_json_file(self, data, folder, file_name_id, *args):
        """ Load given string as a json dictionary and save it as a json file with the file_name_id in the folder.
            Returns the loaded json dictionary.
        """
        # json file:
        result_data = json.loads(data)
        # hack in order to avoid "\\" from os.sep, them we need to use the replace string method:
        path = os.path.join(self.ar.data.dp_auto_rig_path, folder.replace(".", "/"), "").replace("\\", "/")
        # write json file in the HD:
        with open(path+result_data[file_name_id]+'.json', 'w') as json_file:
            json.dump(result_data, json_file, indent=4, sort_keys=True)
        return result_data


    def get_validator_addons(self, path="addOnsPath"):
        """ Return a list of Validator's AddOns or Finishing to load.
        """
        if os.path.exists(self.ar.pipeliner.pipeData[path]):
            start_path = self.ar.pipeliner.pipeData[path][:self.ar.pipeliner.pipeData[path].rfind("/")]
            end_path = self.ar.pipeliner.pipeData[path][self.ar.pipeliner.pipeData[path].rfind("/")+1:]
            print("start_path = ", start_path)
            print("end_path = ", end_path)
            return self.ar.utils.findAllModules(start_path, end_path)
        

    def get_instance_info(self, name, folders, info="instances"):
        # TODO Temporary renaming before refacotry files renaming is done:
        if name.startswith("dp"):
            name = name[2:] #removes initial dp string
        
        for folder in folders:
            if folder in self.ar.data.lib.keys():
                for i, item in enumerate(self.ar.data.lib[folder]["instances"]):
                    if name == item.name:
                        return self.ar.data.lib[folder][info][i]
                    

    def get_validator_instances(self):
        validators = []
        if self.ar.data.checkaddon_folder:
            validators.extend(self.ar.data.lib[self.ar.data.checkaddon_folder]["instances"])
        validators.extend(self.ar.data.lib[self.ar.data.checkin_folder]["instances"])
        validators.extend(self.ar.data.lib[self.ar.data.checkout_folder]["instances"])
        if self.ar.data.checkfinishing_folder:
            validators.extend(self.ar.data.lib[self.ar.data.checkfinishing_folder]["instances"])
        return validators


    def get_rebuilder_instances(self):
        rebuilders = []
        for folder in self.ar.filler.rebuilder_folders:
            rebuilders.extend(self.ar.data.lib[folder]["instances"])
        return rebuilders


    def get_instance(self, name, folders=None):
        if not folders:
            folders = self.lib_folders
        for folder in folders:
            if folder in list(self.ar.data.lib.keys()):
                for i, item in enumerate(self.ar.data.lib[folder]["modules"]):
                    if item == name:
                        return self.ar.data.lib[folder]["instances"][i]


    def get_template_name(self, name):
        keys = self.ar.utils.get_keys_by_value(self.ar.data.lang_preset_data["English"], name.capitalize())
        if keys:
            for key in keys:
                if key.startswith("m") or key.startswith("i"):
                    return key
            return keys[0]
        return self.ar.data.template_default


class Option(object):
    def __init__(self, ar):
        self.ar = ar

    
    def change_degree(self, value, *args):
        self.set_option_var(self.ar.data.degree_option_var, value)
        self.ar.data.degree_option = int(value[-1])
        for module_instance in self.ar.data.standard_instances:
            if "degree" in cmds.listAttr(module_instance.moduleGrp):
                cmds.setAttr(module_instance.moduleGrp+".degree", self.ar.data.degree_option)


    def check_use_default_render_layer(self):
        if self.ar.data.default_render_layer:
            self.set_default_render_layer(True)


    def set_option_var(self, opt_var, value, string=True):
        cmds.optionVar(remove=opt_var)
        if string:
            cmds.optionVar(stringValue=(opt_var, value))
        else:
            cmds.optionVar(intValue=(opt_var, value))


    def set_verbose(self, value):
        """ Set the dev verbose variable.
        """
        self.ar.data.verbose = value


    def set_colorize_curve(self, value):
        self.ar.data.colorize_curve = value
        self.set_option_var(self.ar.data.colorize_curve_option_var, value, False)


    def set_supplementary_attr(self, value):
        self.ar.data.supplementary_attr = value
        self.set_option_var(self.ar.data.supplementary_attr_option_var, value, False)


    def set_display_joint(self, value):
        self.ar.data.display_joint = value
        self.set_option_var(self.ar.data.display_joint_option_var, value, False)


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
        self.set_option_var(self.ar.data.display_temp_grp_option_var, value, False)


    def set_integrate_all(self, value):
        self.ar.data.integrate_all = value
        self.set_option_var(self.ar.data.integrate_all_option_var, value, False)


    def set_default_render_layer(self, value):
        """ Analisys if must use the Default Render Layer (masterLayer) checking the option in the UI.
            Set to use it if need.
        """
        self.ar.data.default_render_layer = value
        self.set_option_var(self.ar.data.default_render_layer_option_var, value, False)
        if value:
            cmds.editRenderLayerGlobals(currentRenderLayer='defaultRenderLayer')


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
                if self.ar.data.ui_state:
                    if cmds.text("rig_prefix_txt", query=True, exists=True):
                        cmds.text("rig_prefix_txt", edit=True, label=f"{self.ar.data.lang['i144_prefix']}: {prefix}", visible=True)
        else:
            self.reset_prefix()

        
    def reset_prefix(self):
        self.ar.data.prefix = ""
        if self.ar.data.ui_state:
            if cmds.text("rig_prefix_txt", query=True, exists=True):
                cmds.text("rig_prefix_txt", edit=True, label="", visible=False)


    def reset_options_to_default(self, *args):
        self.set_option_var(self.ar.data.language_option_var, self.ar.data.language_default)
        self.set_option_var(self.ar.data.validator_option_var, self.ar.data.validator_default)
        self.set_option_var(self.ar.data.curve_option_var, self.ar.data.curve_default)
        self.change_degree(self.ar.data.degree_default)
        # same hard coded number than variables dataclass
        self.set_colorize_curve(1)
        self.set_supplementary_attr(1)
        self.set_display_joint(1)
        self.set_display_temp_grp(0)
        self.set_integrate_all(1)
        self.set_default_render_layer(1)
        self.reset_prefix()
        self.set_agree_terms_cond(1)
        self.set_auto_check_update(1)
        # reload UI
        cmds.evalDeferred("ar = dpAutoRig.Start("+str(self.ar.dev)+", intro=False); ar.ui();", lowestPriority=True)


    def set_agree_terms_cond(self, value):
        self.ar.data.agree_terms = value
        self.set_option_var(self.ar.data.terms_cond_option_var, value, False)


    def set_auto_check_update(self, value):
        self.ar.data.auto_check_update = value
        self.set_option_var(self.ar.data.check_update_option_var, value, False)



class Agreement(object):
    def __init__(self, ar):
        self.ar = ar

    
    def load_terms_cond(self):
        if self.ar.data.ui_state and not self.ar.dev:
            if cmds.optionVar(exists=self.ar.data.terms_cond_option_var):
                if cmds.optionVar(query=self.ar.data.terms_cond_option_var):
                    if not cmds.optionVar(query=self.ar.data.terms_cond_last_option_var) == self.ar.config.today:
                        self.get_local_data()
            else:
                self.ar.opt.set_option_var(self.ar.data.terms_cond_option_var, 1, False)
                self.ask_terms_cond()
                self.get_local_data()
            self.ar.opt.set_option_var(self.ar.data.terms_cond_last_option_var, self.ar.config.today)


    def get_local_data(self):
        """ Collect info for statistical purposes.
        """
        local_data = False
        try:
            local_response = urllib.request.urlopen(self.ar.data.location_url)
            local_data = json.loads(local_response.read())
        except:
            pass
        if local_data:
            local_info = {}
            local_info['country'] = local_data['country']
            local_info['region'] = local_data['region']
            local_info['city'] = local_data['city']
            local_info['user'] = getpass.getuser()
            local_info['host'] = socket.gethostname()
            local_info['os'] = platform.system()
            local_info['lang'] = self.ar.data.lang['_preset']
            local_info['Maya'] = cmds.about(version=True)
            local_info['dpAR'] = self.ar.data.version
            #print(local_info)
            if local_info:
                wh = self.ar.utils.mountWH(self.ar.data.discord_url, self.ar.pipeliner.pipeData['h000_location'])
                self.ar.packager.toDiscord(wh, str(local_info))


    def ask_terms_cond(self, *args):
        """ Create a window to ask user if agree to terms and conditions.
        """
        if self.ar.data.ui_state:
            terms_width  = 205
            terms_height = 200
            # creating Terms and Conditions Window:
            self.ar.utils.closeUI('dpTermsCondWindow')
            cmds.window('dpTermsCondWindow', title='dpAutoRigSystem - '+self.ar.data.lang['i281_termsCond'], iconName='dpInfo', widthHeight=(terms_width, terms_height), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False)
            # creating text layout:
            cmds.columnLayout("terms_cl", adjustableColumn=True, columnOffset=['both', 20], rowSpacing=5, parent="dpTermsCondWindow")
            cmds.text("\n"+self.ar.data.lang['i282_termsCondDesc'], align="center", parent="terms_cl")
            # agreement:
            cmds.separator(height=30)
            cmds.checkBox('terms_cond_cb', label=self.ar.data.lang['i280_iAgreeTermsCond'], align="left", value=self.ar.data.agree_terms, changeCommand=self.ar.opt.set_agree_terms_cond, parent="terms_cl")
            cmds.separator(height=30)
            # call window:
            cmds.showWindow("dpTermsCondWindow")
