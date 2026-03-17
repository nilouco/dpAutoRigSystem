#import libraries
import os
import sys
from maya import cmds
from maya import mel
from functools import partial
from importlib import reload



class UIFiller(object):
    def __init__(self, ar):
        self.ar = ar
        self.validator_folders = [self.ar.data.checkin_folder, 
                                  self.ar.data.checkout_folder]
        self.rebuilder_folders = [ self.ar.data.rebuilder_folder,
                                   self.ar.data.start_folder,
                                   self.ar.data.source_folder,
                                   self.ar.data.setup_folder,
                                   self.ar.data.deforming_folder,
                                   self.ar.data.custom_folder]


    def start_library(self):
        self.start_modules()
        self.load_pipeline_validator()
        self.set_validator_preset()


    def start_modules(self):
        # rigging
        self.start_modules_by_folder(self.ar.data.standard_folder)
        self.start_modules_by_folder(self.ar.data.integrated_folder)
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
                    cmds.menuItem(f"{self.ar.data.validator_preset['_preset']}_mi", label=self.ar.data.validator_preset["_preset"], radioButton=False, collection="validator_preset_rbc", parent="validator_preset_menu")
                    cmds.menuItem(f"{self.ar.data.validator_preset['_preset']}_mi", edit=True, radioButton=True, collection="validator_preset_rbc")

    
    def set_validator_preset(self):
        check_instances = self.ar.data.lib[self.ar.data.checkin_folder]["instances"] + self.ar.data.lib[self.ar.data.checkout_folder]["instances"]
        if self.ar.data.checkaddon_folder in self.ar.data.lib.keys():
            check_instances = check_instances + self.ar.data.lib[self.ar.data.checkaddon_folder]["instances"]
        if self.ar.data.checkfinishing_folder in self.ar.data.lib.keys():
            check_instances = check_instances + self.ar.data.lib[self.ar.data.checkfinishing_folder]["instances"]
        if check_instances:
            for validator_name in self.ar.data.validator_preset:
                for validator_instance in check_instances:
                    if validator_name == validator_instance.name:
                        validator_instance.changeActive(self.ar.data.validator_preset_data[self.ar.data.validator_preset["_preset"]][validator_instance.name])
    
    
    def fill_library(self):
        # rigging
        for item in self.ar.data.lib[self.ar.data.standard_folder]["instances"]:
            self.populate_library(item, self.ar.data.standard_folder, "rig_guides_standard_cl")
        for item in self.ar.data.lib[self.ar.data.integrated_folder]["instances"]:
            self.populate_library(item, self.ar.data.integrated_folder, "rig_guides_integrated_cl")
        # controllers
        for item in self.ar.data.lib[self.ar.data.curve_simple_folder]["instances"]:
            self.populate_library(item, self.ar.data.curve_simple_folder, "ctr_simple_module_gl")
        for item in self.ar.data.lib[self.ar.data.curve_combined_folder]["instances"]:
            self.populate_library(item, self.ar.data.curve_combined_folder, "ctr_combined_module_gl")
        # tools
        for item in self.ar.data.lib[self.ar.data.tools_folder]["instances"]:
            self.populate_library(item, self.ar.data.tools_folder, "tools_module_cl")
        # validators
        for item in self.ar.data.lib[self.ar.data.checkin_folder]["instances"]:
            self.populate_library(item, self.ar.data.checkin_folder, "i208_checkin_module_cl")
        for item in self.ar.data.lib[self.ar.data.checkout_folder]["instances"]:
            self.populate_library(item, self.ar.data.checkout_folder, "i209_checkout_module_cl")
        if self.ar.data.checkaddon_folder:
            for item in self.ar.data.lib[self.ar.data.checkaddon_folder]["instances"]:
                cmds.frameLayout('i212_addOns_fl', edit=True, visible=True)
                self.populate_library(item, "", "i212_addOns_module_cl")
        if self.ar.data.checkfinishing_folder:
            for item in self.ar.data.lib[self.ar.data.checkfinishing_folder]["instances"]:
                cmds.frameLayout('i354_finishing_fl', edit=True, visible=True)
                self.populate_library(item, "", "i354_finishing_module_cl")
        # rebuilders
        for item in self.ar.data.lib[self.ar.data.start_folder]["instances"]:
            self.populate_library(item, self.ar.data.start_folder, "rebuilder_start_fl", 6)
        for item in self.ar.data.lib[self.ar.data.source_folder]["instances"]:
            self.populate_library(item, self.ar.data.source_folder, "rebuilder_source_fl", 6)
        for item in self.ar.data.lib[self.ar.data.setup_folder]["instances"]:
            self.populate_library(item, self.ar.data.setup_folder, "rebuilder_setup_fl", 6)
        for item in self.ar.data.lib[self.ar.data.deforming_folder]["instances"]:
            self.populate_library(item, self.ar.data.deforming_folder, "rebuilder_deforming_fl", 6)
        for item in self.ar.data.lib[self.ar.data.custom_folder]["instances"]:
            self.populate_library(item, self.ar.data.custom_folder, "rebuilder_custom_fl", 6)


    def populate_library(self, item, folder, layout, columns=5):
        if cmds.layout(layout, query=True, exists=True):
            icon_name = self.ar.ui_manager.get_icon_name(item)
            if folder == self.ar.data.curve_simple_folder or folder == self.ar.data.curve_combined_folder:
                cmds.iconTextButton(image=self.ar.data.icon[icon_name], label=item.name, annotation=item.name, height=32, width=32, command=partial(item.cvMain, True), parent=layout)
                return
            module_layout = cmds.rowLayout(item.title+"_rl", numberOfColumns=columns, columnWidth3=(32, 55, 17), height=32, adjustableColumn=2, columnAlign=[(1, 'left'), (2, 'left'), (3, 'left'), (4, 'left'), (5, 'left')], columnAttach=[(1, 'both', 2), (2, 'both', 0), (3, 'both', 2), (4, 'both', 2), (5, 'left', 2)], parent=layout)
            cmds.image(item.title+"_img", image=self.ar.data.icon[icon_name], width=32, parent=module_layout)
            if folder == self.ar.data.standard_folder:
                cmds.button(item.title+'_bt', label=self.ar.data.lang[item.title], height=32, command=item.build_raw_guide, parent=module_layout)
            elif folder == self.ar.data.integrated_folder:
                cmds.button(item.title+'_bt', label=self.ar.data.lang[item.title], height=32, command=item.build_template, parent=module_layout)
            elif folder == self.ar.data.tools_folder:
                cmds.button(item.title+'_bt', label=self.ar.data.lang[item.title], height=32, width=200, command=item.build_tool, parent=module_layout)
            else:
                item.actionCB = cmds.checkBox(label=self.ar.data.lang[item.title], value=item.active, changeCommand=item.changeActive, parent=module_layout)
                item.firstBT = cmds.button(label=item.firstBTLabel, width=45, command=partial(item.runAction, True), backgroundColor=(0.5, 0.5, 0.5), enable=item.firstBTEnable, parent=module_layout)
                item.secondBT = cmds.button(label=item.secondBTLabel.capitalize(), width=45, command=partial(item.runAction, False), backgroundColor=(0.5, 0.5, 0.5), enable=item.secondBTEnable, parent=module_layout)
                if folder == "" or folder in self.validator_folders:
                    if item.customName:
                        cmds.checkBox(item.actionCB, edit=True, label=item.customName)
                        item.title = item.customName
                if folder in self.rebuilder_folders:
                    item.deleteDataITB = cmds.iconTextButton(image=self.ar.data.icon['xDelete'], height=30, width=30, style='iconOnly', command=item.deleteData, enable=item.deleteDataBTEnable, annotation=self.ar.data.lang['r058_deleteDataAnn'], parent=module_layout)
                    item.updateActionButtons(color=False)
            cmds.iconTextButton(item.title+"_itb", image=self.ar.data.icon['info'], height=30, width=30, style='iconOnly', command=partial(self.ar.logger.infoWin, item.title, item.description, None, 'center', 305, 250, wiki=item.wiki), parent=module_layout)

