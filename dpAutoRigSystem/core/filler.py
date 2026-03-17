#import libraries
from maya import cmds
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

    
    def fill_libraries(self):
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
            module_layout = cmds.rowLayout(item.name+"_rl", numberOfColumns=columns, columnWidth3=(32, 55, 17), height=32, adjustableColumn=2, columnAlign=[(1, 'left'), (2, 'left'), (3, 'left'), (4, 'left'), (5, 'left')], columnAttach=[(1, 'both', 2), (2, 'both', 0), (3, 'both', 2), (4, 'both', 2), (5, 'left', 2)], parent=layout)
            cmds.image(item.name+"_img", image=self.ar.data.icon[icon_name], width=32, parent=module_layout)
            if folder == self.ar.data.standard_folder:
                cmds.button(item.name+'_bt', label=self.ar.data.lang[item.title], height=32, command=item.build_raw_guide, parent=module_layout)
            elif folder == self.ar.data.integrated_folder:
                cmds.button(item.name+'_bt', label=self.ar.data.lang[item.title], height=32, command=item.build_template, parent=module_layout)
            elif folder == self.ar.data.tools_folder:
                cmds.button(item.name+'_bt', label=self.ar.data.lang[item.title], height=32, width=200, command=item.build_tool, parent=module_layout)
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
            cmds.iconTextButton(item.name+"_itb", image=self.ar.data.icon['info'], height=30, width=30, style='iconOnly', command=partial(self.ar.logger.infoWin, item.title, item.description, None, 'center', 305, 250, wiki=item.wiki), parent=module_layout)


    def load_pipeline_validator_preset(self):
        cmds.menuItem(f"{self.ar.data.validator_preset['_preset']}_mi", label=self.ar.data.validator_preset["_preset"], radioButton=False, collection="validator_preset_rbc", parent="validator_preset_menu")
        cmds.menuItem(f"{self.ar.data.validator_preset['_preset']}_mi", edit=True, radioButton=True, collection="validator_preset_rbc")


    def fill_created_guides(self):
        """ Read all guide modules loaded in the scene and re-create the elements in the module_layout.
        """
        # create a new list in order to store all created guide modules in the scene and its userSpecNames:
        self.ar.data.created_guides = []
        self.ar.data.standard_instances = []
        # list all namespaces:
        cmds.namespace(setNamespace=":")
        namespaces = cmds.namespaceInfo(listOnlyNamespaces=True)
        # find all module names:
        module_name = self.ar.utils.findAllModuleNames(self.ar.data.dp_auto_rig_path, self.ar.data.standard_folder)
        valid_modules = module_name[0]
        valid_module_ames = module_name[1]
        
        # check if there is "__" (double undersore) in the namespaces:
        for n in namespaces:
            n_partitions = n.partition("__")
            if n_partitions[1] != "":
                module = n_partitions[0]
                userSpecName = n_partitions[2]
                if module in valid_module_ames:
                    index = valid_module_ames.index(module)
                    # check if there is this module guide base in the scene:
                    curGuideName = valid_module_ames[index]+"__"+userSpecName+":"+self.ar.data.guide_base_name
                    if cmds.objExists(curGuideName):
                        self.ar.data.created_guides.append([valid_modules[index], userSpecName, curGuideName])
                    else:
                        cmds.namespace(moveNamespace=(n, ':'), force=True)
                        cmds.namespace(removeNamespace=n, deleteNamespaceContent=True, force=True)

        # if exists any guide module in the scene, recreate its instance as objectClass:
        if self.ar.data.created_guides:
            sorted_guides = sorted(self.ar.data.created_guides, key=lambda userSpecName: userSpecName[1])
            # load again the modules:
            module_path = f"{self.ar.utils.findEnv('PYTHONPATH', 'dpAutoRigSystem')}.{self.ar.data.standard_folder.replace('/', '.')}"
            # this list will be used to rig all modules pressing the RIG button:
            for module in sorted_guides:
                imported_module = __import__(module_path+"."+module[0], {}, {}, [module[0]])
                if self.ar.dev:
                    reload(imported_module)
                # identify the guide modules and add to the moduleInstancesList:
                moduleClass = getattr(imported_module, imported_module.CLASS_NAME)
                if "rigType" in cmds.listAttr(module[2]):
                    curRigType = cmds.getAttr(module[2]+".rigType")
                    moduleInst = moduleClass(self.ar)#, module[1], curRigType)
                else:
                    if "Style" in cmds.listAttr(module[2]):
                        iStyle = cmds.getAttr(module[2]+".Style")
                        if (iStyle == 0 or iStyle == 1):
                            moduleInst = moduleClass(self.ar, module[1], self.ar.data.rig_type_biped)
                        else:
                            moduleInst = moduleClass(self.ar, module[1], self.ar.data.rig_type_quadruped)
                    else:
                        moduleInst = moduleClass(self.ar, module[1], self.ar.data.rig_type_default)
                self.ar.data.standard_instances.append(moduleInst)
                moduleInst.get_namespace_for_it(module[1])
                if self.ar.data.ui_state:
                    moduleInst.load_raw_guide(moduleInst.userGuideName)

                # reload pinGuide scriptJob:
                self.ar.ctrls.startPinGuide(module[2])
