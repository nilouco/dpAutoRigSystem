#import libraries
import os
import sys
from maya import mel
from importlib import reload
from ..Modules.Base import dpBaseTemplate



class Lib(object):
    def __init__(self, ar):
        self.ar = ar
        if self.ar.dev:
            reload(dpBaseTemplate)


    def start_library(self):
        self.start_modules()
        self.start_templates()
        self.load_pipeline_validator()
        self.set_validator_preset()


    def start_modules(self):
        # rigging
        self.start_modules_by_folder(self.ar.data.standard_folder)
        # controllers
        self.start_modules_by_folder(self.ar.data.curve_simple_folder)
        self.start_modules_by_folder(self.ar.data.curve_combined_folder)
        # tools
        self.start_modules_by_folder(self.ar.data.tools_folder)
        # validators
        self.start_modules_by_folder(self.ar.data.checkin_folder)
        self.start_modules_by_folder(self.ar.data.checkout_folder)
        if self.ar.pipeliner.pipeData['addOnsPath'] and self.ar.config.get_validator_addons():
            self.start_modules_by_folder("", path=self.ar.pipeliner.pipeData['addOnsPath'])
            self.ar.data.checkaddon_folder = self.ar.pipeliner.pipeData['addOnsPath']
        if self.ar.pipeliner.pipeData['finishingPath'] and self.ar.config.get_validator_addons("finishingPath"):
            self.start_modules_by_folder("", path=self.ar.pipeliner.pipeData['finishingPath'])
            self.ar.data.checkfinishing_folder = self.ar.pipeliner.pipeData['finishingPath']
        # rebuilders
        self.start_modules_by_folder(self.ar.data.start_folder)
        self.start_modules_by_folder(self.ar.data.source_folder)
        self.start_modules_by_folder(self.ar.data.setup_folder)
        self.start_modules_by_folder(self.ar.data.deforming_folder)
        self.start_modules_by_folder(self.ar.data.custom_folder)


    def start_modules_by_folder(self, folder, path=None):
        libs, imported_modules = [], []
        if not path:
            path = self.ar.data.dp_auto_rig_path
        if not self.ar.data.loaded_path:
            if self.ar.data.verbose:
                print(f"dpAutoRigPath: {path}")
            self.ar.data.loaded_path = True
        
        # find all guide modules:
        modules = self.ar.utils.findAllModules(path, folder)
        if modules:
            for module in modules:
                lib_instance, imported_module = self.initialize_library(module, folder, path)
                self.ar.data.lib_instances.append(lib_instance)
                libs.append(lib_instance)
                imported_modules.append(imported_module)
        
            # avoid print again the same message:
            if folder == "":
                folder = path
            if not folder in self.ar.data.lib.keys():
                self.ar.data.lib[folder] = { 
                                            "modules" : modules,
                                            "instances": libs,
                                            "imported" : imported_modules
                                            }
                if self.ar.data.verbose:
                    print(folder+" : "+str(modules))
        return modules
    

    def start_templates(self):
        templates, content = self.ar.config.get_json_file_content(self.ar.data.template_folder)
        if templates:
            libs = self.initialize_templates(templates, content)
            self.ar.data.lib[self.ar.data.template_folder] = {
                                                                "templates" : templates,
                                                                "content" : content,
                                                                "instances" : libs
                                                              }
            if self.ar.data.verbose:
                print(self.ar.data.template_folder+" : "+str(templates))

    
    def initialize_templates(self, templates, content):
        libs = []
        for item in templates:
            base_name = item
            if "_" in item:
                base_name = item.split("_")[0]
            name = self.ar.config.get_template_name(base_name)
            lib = dpBaseTemplate.BaseTemplate(self.ar, item, name, "v002_templateDesc", item, f"03-‐-Guides#-{base_name}")
            lib.template_data = content[item]
            lib.base_name = base_name
            libs.append(lib)
        return libs


    def initialize_library(self, module, folder, path=None):
        """ Returns the started instance and the imported module objects.
        """
        imported_module = self.import_library(module, folder, path)
        if imported_module:
            return [self.create_instance(imported_module), imported_module]


    def import_library(self, module, folder, path=None):
        imported_module = None
        basePath = self.ar.utils.findEnv("PYTHONPATH", "dpAutoRigSystem")
        try:
            if folder:
                folder = folder.replace("/", ".")
                imported_module = __import__(f"{basePath}.{folder}.{module}", {}, {}, [module])
            elif path:
                sys.path.append(path)
                imported_module = __import__(module, {}, {}, [module])
            if self.ar.dev:
                reload(imported_module)
        except Exception as e:
            errorString = self.ar.data.lang['e017_loadingExtension']+" "+module+" : "+str(e.args)
            mel.eval('warning \"'+errorString+'\";')
            return
        return imported_module


    def create_instance(self, imported_module):
        """ Returns the initialized module instance.
        """
        return getattr(imported_module, imported_module.CLASS_NAME)(self.ar)
    

    def load_pipeline_validator(self):
        """ Load the Validator's presets from the pipeline path.
        """
        if self.ar.pipeliner.pipeData['presetsPath']:
            if os.path.exists(self.ar.pipeliner.pipeData['presetsPath']):
                studio_preset, studio_preset_data = self.ar.config.get_json_file_content(self.ar.pipeliner.pipeData['presetsPath']+"/", True)
                if studio_preset:
                    self.ar.data.validator_preset = studio_preset_data[studio_preset[0]]
                    self.ar.data.validator_preset_data.update(studio_preset_data)
                    if self.ar.data.ui_state:
                        self.ar.filler.load_pipeline_validator_preset()

    
    def set_validator_preset(self):
        check_instances = self.ar.config.get_validator_instances()
        if check_instances:
            for validator_name in self.ar.data.validator_preset:
                for validator_instance in check_instances:
                    if validator_name == validator_instance.name:
                        validator_instance.changeActive(self.ar.data.validator_preset_data[self.ar.data.validator_preset["_preset"]][validator_instance.name])
