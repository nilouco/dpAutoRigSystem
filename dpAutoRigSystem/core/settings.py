import os
import json
from maya import cmds

class Configuration(object):
    def __init__(self, dpUIinst):
        self.ar = dpUIinst
        self.load_language()

        # TODO
            # get_language()
            # get_update()
            # get_terms_cond()


    def load_language(self, name=None):
        founds, self.ar.data.lang_data = self.get_json_file_content(self.ar.data.language_folder)
        if founds and self.ar.data.lang_data:
            if name and name in founds:
                self.ar.lang = self.ar.data.lang_data[name]
            elif self.ar.data.language_default in founds:
                self.ar.lang = self.ar.data.lang_data[self.ar.data.language_default]
        # WIP
        print("defining language =", self.ar.lang)


    def get_json_file_content(self, folder, absolute=False):
        
        """ Find all json files in the given path and get contents used for each file.
            Create a dictionary with dictionaries of all file found.
            Return a list with the name of the found files.
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
    

    def open_pipeliner(self, *args):
        print("WIP opening piliener UI", args)
        self.ar.pipeliner.mainUI(self.ar)



    def create_preset(self, preset_type="controls", preset_folder="Modules/Curves/Presets", set_option_var=True, *args):
        """ Just call ctrls create preset and set it as userDefined preset.
        """
        print("WIP creating preset here, preset_type =", preset_type)
        if preset_type == "controls":
            preset_option_var = self.ar.data.controller_option_var
            newPresetString = self.ar.ctrls.dpCreateControlsPreset()
        elif preset_type == "validator":
            preset_option_var = self.ar.data.validator_option_var
            newPresetString = self.ar.utils.dpCreateValidatorPreset()
        if newPresetString:
            # create json file:
            resultDic = self.ar.createJsonFile(newPresetString, preset_folder, '_preset')
            preset_name = resultDic['_preset']
            # set this new preset as userDefined preset:
            if set_option_var:
                self.ar.opt.set_option_var(preset_option_var, preset_name)

            # show preset creation result window:
            self.ar.logger.infoWin('i129_createPreset', 'i133_presetCreated', '\n'+self.preset_name+'\n\n'+self.ar.lang['i134_rememberPublish']+'\n\n'+self.ar.lang['i018_thanks'], 'center', 205, 270)
            # close and reload dpAR UI in order to avoid Maya crash
            self.reloadMainUI()



class Option(object):
    def __init__(self, dpUIinst):
        self.ar = dpUIinst

    
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
    

    def set_option_var(self, opt_var, item):
        cmds.optionVar(remove=opt_var)
        cmds.optionVar(stringValue=(opt_var, item))
