#import libraries
from maya import cmds
from functools import partial
from importlib import reload



class UIFiller(object):
    def __init__(self, ar):
        self.ar = ar
        self.validator_folders = [ self.ar.data.checkin_folder, 
                                   self.ar.data.checkout_folder]
        self.rebuilder_folders = [ self.ar.data.start_folder,
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
        valid_module_names = module_name[1]
        
        # check if there is "__" (double undersore) in the namespaces:
        for n in namespaces:
            n_partitions = n.partition("__")
            if n_partitions[1] != "":
                module = n_partitions[0]
                userSpecName = n_partitions[2]
                if module in valid_module_names:
                    index = valid_module_names.index(module)
                    # check if there is this module guide base in the scene:
                    curGuideName = valid_module_names[index]+"__"+userSpecName+":"+self.ar.data.guide_base_name
                    if cmds.objExists(curGuideName):
                        self.ar.data.created_guides.append([valid_modules[index], userSpecName, curGuideName])
                    else:
                        cmds.namespace(moveNamespace=(n, ':'), force=True)
                        cmds.namespace(removeNamespace=n, deleteNamespaceContent=True, force=True)

        # if exists any guide module in the scene, recreate its instance as objectClass:
        if self.ar.data.created_guides:
            sorted_guides = sorted(self.ar.data.created_guides, key=lambda userSpecName: userSpecName[1])
            # load again the modules:
            for module in sorted_guides:
                mod = self.start_module(module, self.ar.data.standard_folder)
                self.ar.data.standard_instances.append(mod)
                mod.get_namespace_for_it(module[1])
                if self.ar.data.ui_state:
                    mod.load_raw_guide(mod.userGuideName)

                # reload pinGuide scriptJob:
                self.ar.ctrls.startPinGuide(module[2])


    def start_module(self, module, folder):
        path = f"{self.ar.utils.findEnv('PYTHONPATH', 'dpAutoRigSystem')}.{folder.replace('/', '.')}"
        imported_module = __import__(path+"."+module[0], {}, {}, [module[0]])
        if self.ar.dev:
            reload(imported_module)
        # identify the guide modules and add to the moduleInstancesList:
        moduleClass = getattr(imported_module, imported_module.CLASS_NAME)
        if "rigType" in cmds.listAttr(module[2]):
            curRigType = cmds.getAttr(module[2]+".rigType")
            mod = moduleClass(self.ar)#, module[1], curRigType)
        else:
            if "Style" in cmds.listAttr(module[2]):
                iStyle = cmds.getAttr(module[2]+".Style")
                if (iStyle == 0 or iStyle == 1):
                    mod = moduleClass(self.ar, module[1], self.ar.data.rig_type_biped)
                else:
                    mod = moduleClass(self.ar, module[1], self.ar.data.rig_type_quadruped)
            else:
                mod = moduleClass(self.ar, module[1], self.ar.data.rig_type_default)
        return mod


    def populate_joints(self, *args):
        """ This function is responsable to list all joints or only dpAR joints in the interface in order to use in skinning.
        """
        # get current jointType (all or just dpAutoRig joints):
        choose_joint = cmds.radioButton(cmds.radioCollection('skin_joint_rc', query=True, select=True), query=True, annotation=True)
        
        # list joints to be populated:
        joints, sorted_joints = [], []
        all_joints = cmds.ls(selection=False, type="joint")
        if choose_joint == "allJoints":
            joints = all_joints
            cmds.checkBox('skin_jnt_cb', edit=True, enable=False)
            cmds.checkBox('skin_jar_cb', edit=True, enable=False)
            cmds.checkBox('skin_jad_cb', edit=True, enable=False)
            cmds.checkBox('skin_jcr_cb', edit=True, enable=False)
            cmds.checkBox('skin_jis_cb', edit=True, enable=False)
        elif choose_joint == "dpARJoints":
            cmds.checkBox('skin_jnt_cb', edit=True, enable=True)
            cmds.checkBox('skin_jar_cb', edit=True, enable=True)
            cmds.checkBox('skin_jad_cb', edit=True, enable=True)
            cmds.checkBox('skin_jcr_cb', edit=True, enable=True)
            cmds.checkBox('skin_jis_cb', edit=True, enable=True)
            display_jnt = cmds.checkBox('skin_jnt_cb', query=True, value=True)
            display_jar = cmds.checkBox('skin_jar_cb', query=True, value=True)
            diaplay_jad = cmds.checkBox('skin_jad_cb', query=True, value=True)
            display_jcr = cmds.checkBox('skin_jcr_cb', query=True, value=True)
            display_jis = cmds.checkBox('skin_jis_cb', query=True, value=True)
            for joint_node in all_joints:
                if cmds.objExists(joint_node+'.'+self.ar.data.base_name+'joint'):
                    if display_jnt:
                        if joint_node.endswith("_Jnt"):
                            joints.append(joint_node)
                    if display_jar:
                        if joint_node.endswith("_Jar"):
                            joints.append(joint_node)
                    if diaplay_jad:
                        if joint_node.endswith("_Jad"):
                            joints.append(joint_node)
                    if display_jcr:
                        if joint_node.endswith("_Jcr"):
                            joints.append(joint_node)
                    if display_jis:
                        if joint_node.endswith("_Jis"):
                            joints.append(joint_node)
        
        # sort joints by name filter:
        joint_name = cmds.textField('skin_joint_name_tf', query=True, text=True)
        if joints:
            if joint_name:
                sorted_joints = self.ar.utils.filterName(joint_name, joints, " ")
            else:
                sorted_joints = joints
        
        # populate the list:
        cmds.textScrollList('skin_joint_tsl', edit=True, removeAll=True)
        cmds.textScrollList('skin_joint_tsl', edit=True, append=sorted_joints)
        # atualize of footerB text:
        self.ar.ui_manager.update_skinning_footer()


    def populate_geometries(self, *args):
        """ This function is responsable to list all geometries or only selected geometries in the interface in order to use in skinning.
        """
        # get current geo_type (all or just selected):
        choose_geo = cmds.radioButton(cmds.radioCollection('skin_geo_rc', query=True, select=True), query=True, annotation=True)
        
        # get user preference as long or short name:
        display_long_name = cmds.checkBox('skin_geo_long_name_cb', query=True, value=True)
        
        # list geometries to be populated:
        geos, same_names, sorted_geos = [], [], []
        
        selecteds = cmds.ls(selection=True, long=True)
        for geo_type in ["mesh", "nurbsSurface", "subdiv"]:
            all_geos = cmds.ls(selection=False, type=geo_type, long=True)
            if all_geos:
                for mesh in all_geos:
                    if cmds.getAttr(mesh+".intermediateObject") == 0:
                        transforms = cmds.listRelatives(mesh, parent=True, fullPath=True, type="transform")
                        if transforms:
                            # do not add ribbon nurbs plane to the list:
                            if not cmds.objExists(transforms[0]+"."+self.ar.skin.ignoreSkinningAttr):
                                if not transforms[0] in geos:
                                    if choose_geo == "allGeoms":
                                        geos.append(transforms[0])
                                        cmds.checkBox('skin_geo_long_name_cb', edit=True, value=True, enable=False)
                                    elif choose_geo == "selGeoms":
                                        cmds.checkBox('skin_geo_long_name_cb', edit=True, enable=True)
                                        if transforms[0] in selecteds or mesh in selecteds:
                                            if display_long_name:
                                                geos.append(transforms[0])
                                            else:
                                                geos.append(transforms[0][transforms[0].rfind("|")+1:]) #short name

        # check if we have same short name:
        if geos:
            for g, geo in enumerate(geos):
                if geo in geos[:g]:
                    same_names.append(geo)
        if same_names:
            geos.insert(0, "*")
            geos.append(" ")
            geos.append("-------")
            geos.append(self.ar.data.lang['i074_attention'])
            geos.append(self.ar.data.lang['i075_moreOne'])
            geos.append(self.ar.data.lang['i076_sameName'])
            for sameName in same_names:
                geos.append(sameName)
        
        # sort geometries by name filter:
        geo_name = cmds.textField('skin_geo_name_tf', query=True, text=True)
        if geos:
            if geo_name:
                sorted_geos = self.ar.utils.filterName(geo_name, geos, " ")
            else:
                sorted_geos = geos
        
        # populate the list:
        cmds.textScrollList('skin_geo_tcl', edit=True, removeAll=True)
        if same_names:
            cmds.textScrollList('skin_geo_tcl', edit=True, lineFont=[(len(sorted_geos)-len(same_names)-2, 'boldLabelFont'), (len(sorted_geos)-len(same_names)-1, 'obliqueLabelFont'), (len(sorted_geos)-len(same_names), 'obliqueLabelFont')], append=sorted_geos)
        else:
            cmds.textScrollList('skin_geo_tcl', edit=True, append=sorted_geos)
        # atualize of footerB text:
        self.ar.ui_manager.update_skinning_footer()
        
    
    def check_imported_guides(self, ask_user=True, *args):
        """ This method will check if there's imported dpGuides in the scene and ask if the user wants to delete the namespace.
            If there isn't an UI it runs as ask_user=False, removing the namespace automacally.
            It uses a recursive method to remove imported of imported guides.
        """
        imported_namespaces = []
        current_custom_names = list(map(lambda guideModule : cmds.getAttr(guideModule.moduleGrp+".customName"), self.ar.utils.getModulesToBeRigged(self.ar.data.standard_instances)))
        cmds.namespace(setNamespace=':')
        namespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
        if namespaces:
            for n, name in enumerate(namespaces):
                if name != "UI" and name != "shared":
                    if name.count(":") > 0:
                        if name.find("_dpAR_") != -1:
                            if ask_user and self.ar.data.ui_state:
                                # open dialog to confirm merge namespaces:
                                yes_text = self.ar.data.lang['i071_yes']
                                no_text = self.ar.data.lang['i072_no']
                                result = cmds.confirmDialog(title=self.ar.data.lang['i205_guide'], message=self.ar.data.lang['i206_removeNamespace'], 
                                                            button=[yes_text, no_text], defaultButton=yes_text, cancelButton=no_text, dismissString=no_text)
                                if result == yes_text:
                                    ask_user = False
                                else:
                                    return
                            imported_namespaces.append(name)
            if imported_namespaces:
                # review guide custom name before remove namespaces
                for name in imported_namespaces:
                    if cmds.objExists(name+":Guide_Base.customName"):
                        n = 1
                        old_custom_name = cmds.getAttr(name+":Guide_Base.customName")
                        if old_custom_name:
                            base_name = old_custom_name
                            while old_custom_name in current_custom_names:
                                old_custom_name = base_name+str(n)
                                n += 1
                            cmds.setAttr(name+":Guide_Base.customName", old_custom_name, type="string")
                            current_custom_names.append(old_custom_name)
                # remove namespaces
                for name in imported_namespaces:
                    if ":" in name:
                        if cmds.namespace(exists=name):
                            namespace_string = name.split(":")[0]
                            cmds.namespace(removeNamespace=namespace_string, mergeNamespaceWithRoot=True)
                            print(f"{self.ar.data.lang['m206_mergeNamespace']}: {namespace_string}")
                            self.check_imported_guides(False)
                            break


    def check_guide_nets(self, *args):
        """ Verify if there are guideNet nodes to existing guides, otherwise it'll call the updatedGuides tool to fix it.
        """
        for item in self.ar.utils.getModulesToBeRigged(self.ar.data.standard_instances):
            if not item.guideNet:
                item.createGuideNetwork()
                print(self.ar.data.lang["v004_fixed"]+" guideNet: "+item.moduleGrp)


    def check_guide_versions(self, *args):
        """ Verify if there are guides with different version of the current dpAutoRig version.
        """
        for item in self.ar.utils.getModulesToBeRigged(self.ar.data.standard_instances):
            if not self.ar.data.version == cmds.getAttr(item.moduleGrp+'.dpARVersion'):
                self.ar.config.get_instance_info("dpUpdateGuides", [self.ar.data.tools_folder]).build_tool()
                break
