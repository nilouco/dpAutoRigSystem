#import libraries
from maya import cmds
from importlib import reload



class UIManager(object):
    def __init__(self, ar):
#        print("init manager")
        self.ar = ar


    def reload_ui(self, opt_var=None, item=None, *args):
        """ This method will set the given optionVar and reload the dpAutoRigSystem UI.
        """
        if opt_var and item:
            self.ar.opt.set_option_var(opt_var, item)
        cmds.evalDeferred("ar = dpAutoRig.Start("+str(self.ar.dev)+", intro=False); ar.ui();", lowestPriority=True)

    
    def reload_dev_mode_ui(self, *args):
        """ Reload the system code as development mode.
        """
        value = True
        if cmds.menuItem('dev_mode_mi', query=True, exists=True):
            value = cmds.menuItem('dev_mode_mi', query=True, checkBox=True)
        if value:
            cmds.evalDeferred("from importlib import reload; reload(dpAutoRigSystem); ar = dpAutoRig.Start(dev=True, intro=False); ar.ui();", lowestPriority=True)
        else:
            cmds.evalDeferred("ar = dpAutoRig.Start(); ar.ui();", lowestPriority=True)


    def refresh_ui(self, savedScene=False, resetButtons=True, clearSel=False):
        """ Read guides, joints, geometries and refresh the UI without reload the script creating a new instance.
            Useful to rebuilding process when creating a new scene
        """
        
        #
        # WIP
        #
        #
        # TODO: delete main frame layout and call the loadUI again?
        #       or just clear filled layouts and fill them again?
        #
        # TODO: check all validators active checkboxes?
        #

#            def refreshMainUI(self, savedScene=False, resetButtons=True, clearSel=False, *args):

        if savedScene:
            self.selList = cmds.ls(selection=True)
            self.ar.data.rebuilding = False
        #clear layouts
        self.clear_guide_layout()
        self.fill_created_guides()

#        self.checkImportedGuides()
#        self.checkGuideNets()
#        self.populateJoints()
#        self.populateGeoms()
#        if not self.ar.data.rebuilding:
#            if resetButtons:
#                self.resetAllButtonColors()
#            self.pipeliner.refreshAssetData()
#            for rebuildInstance in self.rebuilderInstanceList:
#                rebuildInstance.updateActionButtons(color=False)
#        try:
#            self.ar.data.select_change_job_id = cmds.scriptJob(event=('SelectionChanged', self.jobSelectedGuide), parent='languageMenu', replacePrevious=True, killWithScene=False, compressUndo=True)
#        except:
#            self.ar.data.select_change_job_id = cmds.scriptJob(event=('SelectionChanged', self.jobSelectedGuide), parent='languageMenu', replacePrevious=False, killWithScene=False, compressUndo=True)
#        if savedScene:
#            cmds.select(clear=True)
#            if self.selList:
#                cmds.select(self.selList)
#        if clearSel:
#            cmds.select(clear=True)
#        self.ar.data.rebuilding = False


    def clear_guide_layout(self):
        if self.ar.data.ui_state:
            cmds.frameLayout('rig_edit_selected_module_fl', edit=True, label=self.ar.data.lang['i011_editSelected'], collapsable=True, collapse=False, parent='rigging_tab')
            if cmds.columnLayout("rig_guides_inst_cl", query=True, exists=True):
                cmds.deleteUI('rig_guides_inst_cl')
            if cmds.columnLayout("rig_selected_module_cl", query=True, exists=True):
                cmds.deleteUI('rig_selected_module_cl')
            cmds.columnLayout('rig_guides_inst_cl', adjustableColumn=True, width=200, parent='rig_guides_inst_sl')
            cmds.columnLayout('rig_selected_module_cl', adjustableColumn=True, parent='rig_edit_selected_module_fl')


    def fill_created_guides(self, *args):
        """ Read all guide modules loaded in the scene and re-create the elements in the module_layout.
        """
        # create a new list in order to store all created guide modules in the scene and its userSpecNames:
        self.ar.data.created_guides = []
        self.ar.data.standard_instances = []
        # list all namespaces:
        cmds.namespace(setNamespace=":")
        namespaceList = cmds.namespaceInfo(listOnlyNamespaces=True)
        # find path where 'dpAutoRig.py' is been executed:
        path = self.ar.data.dp_auto_rig_path
        guideDir = self.ar.data.standard_folder
        # find all module names:
        moduleNameInfo = self.ar.utils.findAllModuleNames(path, guideDir)
        validModules = moduleNameInfo[0]
        validModuleNames = moduleNameInfo[1]
        
        # check if there is "__" (double undersore) in the namespaces:
        for n in namespaceList:
            divString = n.partition("__")
            if divString[1] != "":
                module = divString[0]
                userSpecName = divString[2]
                if module in validModuleNames:
                    index = validModuleNames.index(module)
                    # check if there is this module guide base in the scene:
                    curGuideName = validModuleNames[index]+"__"+userSpecName+":"+self.ar.data.guide_base_name
                    if cmds.objExists(curGuideName):
                        self.ar.data.created_guides.append([validModules[index], userSpecName, curGuideName])
                    else:
                        cmds.namespace(moveNamespace=(n, ':'), force=True)
                        cmds.namespace(removeNamespace=n, deleteNamespaceContent=True, force=True)

        # if exists any guide module in the scene, recreate its instance as objectClass:
        if self.ar.data.created_guides:
            sortedAllGuidesList = sorted(self.ar.data.created_guides, key=lambda userSpecName: userSpecName[1])
            # load again the modules:
            guideFolder = self.ar.utils.findEnv("PYTHONPATH", "dpAutoRigSystem")+"."+self.ar.data.standard_folder.replace("/", ".")
            # this list will be used to rig all modules pressing the RIG button:
            for module in sortedAllGuidesList:
                mod = __import__(guideFolder+"."+module[0], {}, {}, [module[0]])
                if self.ar.dev:
                    reload(mod)
                # identify the guide modules and add to the moduleInstancesList:
                moduleClass = getattr(mod, mod.CLASS_NAME)
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
        self.update_footer_ui()



    def update_footer_ui(self, text_name="rig_footer_txt",  message_id="i005_footerRigging", quantity=0):
        if not quantity:
            quantity = len(self.ar.data.created_guides)
        if self.ar.data.ui_state:
            cmds.text(text_name, edit=True, label=str(quantity)+" "+self.ar.data.lang[message_id])



    def delete_exist_window(self, *args):
        """ Check if there are the dpAutoRigWindow and a control element to delete the UI.
        """
        if cmds.workspaceControl(self.ar.data.workspace_control_name, query=True, exists=True):
            cmds.workspaceControl(self.ar.data.workspace_control_name, edit=True, close=True)
            #cmds.deleteUI("dpAutoRigSystemWC", control=True)
        win_names = [
                        "dpARLoadWin", 
                        "dpInfoWindow", 
                        "dpNewAssetWindow", 
                        "dpReplaceDPDataWindow", 
                        "dpSelectAssetWindow", 
                        "dpSaveVersionWindow", 
                        self.ar.data.plus_info_win_name, 
                        self.ar.data.color_override_win_name
                       ]
        for win_name in win_names:
            self.ar.utils.closeUI(win_name)
        self.set_ui_state(False)

    
    def set_ui_state(self, value):
        self.ar.data.ui_state = value


    def collapse_all_fl(self, iconTB="rig_tri_collapse_guides_itb", layout=0, *args):
        """ Edit the current module frame layout collapse and icon.
            Layout number:
            0 = guide module frame layouts
            1 = rebuilder processes frame layouts
        """
        collapse_value = True
        icon = self.ar.data.icon['triRight']
        if layout == 0: #guide modules
            modules = self.ar.data.standard_instances
            if self.ar.data.modules_collapse_status:
                collapse_value = False
                icon = self.ar.data.icon['triDown']
            self.ar.data.modules_collapse_status = collapse_value
        else: #rebuilder processes
            modules = self.ar.data.rebuilder_layouts
            if self.ar.data.rebuilders_collapse_status:
                collapse_value = False
                icon = self.ar.data.icon['triDown']
            self.ar.data.rebuilders_collapse_status = collapse_value
        if modules:
            for item in modules:
                if layout == 0:
                    cmds.frameLayout(item.moduleFrameLayout, edit=True, collapse=collapse_value)
                else:
                    cmds.frameLayout(item, edit=True, collapse=collapse_value)
        cmds.iconTextButton(iconTB, edit=True, image=icon)


    def get_icon_name(self, item, alternative="addOn"):
        icon_name = "AR"
        if hasattr(item, "name"):
            icon_name = item.name[0].lower()+item.name[1:]
        if not icon_name in self.ar.data.icon.keys():
            icon_name = alternative
        return icon_name
