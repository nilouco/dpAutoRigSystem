#import libraries
from maya import cmds




class UIManager(object):
    def __init__(self, ar):
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
        if self.ar.data.ui_state:
            if savedScene:
                selected = cmds.ls(selection=True)
                self.ar.data.rebuilding = False
            #clear layouts
            self.clear_guide_layout()
            self.ar.filler.fill_created_guides()
            # guide checkers
            self.ar.filler.check_imported_guides()
            self.ar.filler.check_guide_nets()
            self.ar.filler.check_guide_versions()
            # populates
            self.ar.filler.populate_joints()
            self.ar.filler.populate_geometries()
            # update ui footers
            self.update_guide_footer()
            self.update_skinning_footer()
            # buttons
            if not self.ar.data.rebuilding:
                if resetButtons:
                    self.reset_button_colors()
                self.ar.pipeliner.refreshAssetData()
                for item in self.ar.config.get_rebuilder_instances():
                    item.updateActionButtons(color=False)
            try:
                self.ar.data.select_change_job_id = cmds.scriptJob(event=('SelectionChanged', self.ar.job.selected_guide), parent='main_menu_bar', replacePrevious=True, killWithScene=False, compressUndo=True)
            except:
                self.ar.data.select_change_job_id = cmds.scriptJob(event=('SelectionChanged', self.ar.job.selected_guide), parent='main_menu_bar', replacePrevious=False, killWithScene=False, compressUndo=True)
            if savedScene:
                cmds.select(clear=True)
                if selected:
                    cmds.select(selected)
            if clearSel:
                cmds.select(clear=True)
            self.ar.data.rebuilding = False


    def clear_guide_layout(self):
        if self.ar.data.ui_state:
            cmds.frameLayout('rig_edit_selected_module_fl', edit=True, label=self.ar.data.lang['i011_editSelected'], collapsable=True, collapse=False, parent='rigging_tab')
            if cmds.columnLayout("rig_guides_inst_cl", query=True, exists=True):
                cmds.deleteUI('rig_guides_inst_cl')
            if cmds.columnLayout("rig_selected_module_cl", query=True, exists=True):
                cmds.deleteUI('rig_selected_module_cl')
            cmds.columnLayout('rig_guides_inst_cl', adjustableColumn=True, width=200, parent='rig_guides_inst_sl')
            cmds.columnLayout('rig_selected_module_cl', adjustableColumn=True, parent='rig_edit_selected_module_fl')


    def update_guide_footer(self, text_name="rig_footer_txt",  message_id="i005_footerRigging", quantity=0):
        if not quantity:
            quantity = len(self.ar.data.created_guides)
        if self.ar.data.ui_state:
            cmds.text(text_name, edit=True, label=str(quantity)+" "+self.ar.data.lang[message_id])


    def update_skinning_footer(self, *args):
        """ Edit the label of skin footer text.
        """
        if self.ar.data.ui_state:
            # get the number of selected items for each textScrollLayout:
            n_selected_joints = cmds.textScrollList('skin_joint_tsl', query=True, numberOfSelectedItems=True)
            n_selected_geoms  = cmds.textScrollList('skin_geo_tcl', query=True, numberOfSelectedItems=True)
            
            # verify if there are not any selected items:
            if n_selected_joints == 0:
                n_joint_items = cmds.textScrollList('skin_joint_tsl', query=True, numberOfItems=True)
                if n_joint_items != 0:
                    n_selected_joints = n_joint_items
            if n_selected_geoms == 0:
                n_geom_items = cmds.textScrollList('skin_geo_tcl', query=True, numberOfItems=True)
                if n_geom_items != 0:
                    n_selected_geoms = n_geom_items
            
            # edit the footerB text:
            if n_selected_joints != 0 and n_selected_geoms != 0:
                cmds.text('skin_footer_txt', edit=True, label=str(n_selected_joints)+" "+self.ar.data.lang['i025_joints']+" "+str(n_selected_geoms)+" "+self.ar.data.lang['i024_geometries'])
            else:
                cmds.text('skin_footer_txt', edit=True, label=self.ar.data.lang['i029_skinNothing'])
        


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
                        "dpTermsCondWindow", 
                        'dpUpdateWindow',
                        'dpDonateWindow',
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
            if icon_name.split("_")[0] in self.ar.data.icon.keys():
                icon_name = icon_name.split("_")[0]
            else:
                icon_name = alternative
        return icon_name


    def ask_prompt_dialog(self, title, message, text="", buttons=None, *args):
        """ Prompt dialog to get the name of the root joint to receive all the web joints as children.
        """
        if not buttons:
            continue_button = self.ar.data.lang['i174_continue']
            cancel_button = self.ar.data.lang['i132_cancel']
            buttons = [continue_button, cancel_button]
        result = cmds.promptDialog(title=title, 
                                   message=message,
                                   text=text,
                                   button=buttons, 
                                   defaultButton=buttons[0], 
                                   cancelButton=buttons[0], 
                                   dismissString=buttons[0])
        if result == buttons[0]:
            return cmds.promptDialog(query=True, text=True)
        elif result is None:
            return None
    
    
    def reset_button_colors(self, *args):
        """ Just reset the button colors to default for each validator or rebuilder module.
        """
        items = self.ar.config.get_validator_instances()
        items.extend(self.ar.config.get_rebuilder_instances())
        if items:
            for item in items:
                item.resetButtonColors()


    def check_missing_modules(self, folder, check_modules):
        """ Verifies if the modules exists in the given folder.
            Returns a list of missing modules or []
        """
        return [m for m in check_modules if not m in self.ar.utils.findAllModules(self.ar.data.dp_auto_rig_path, folder.replace(".", "/"))]


    def changeActiveAllModules(self, items, value, *args):
        """ Set all module instances active attribute as True or False.
            Used by validators and rebuilders.
        """
        if items:
            for item in items:
                item.changeActive(value)

    
    def runSelectedActions(self, actionInstList, firstMode, verbose=True, stopIfFoundBlock=False, publishLog=None, actionType="v000_validator", *args):
        """ Run the code for each active validator/rebuilder instance.
            firstMode = True for verify/export
                      = False for fix/import
        """
        if firstMode and actionType == "r000_rebuilder": #splitData
            if self.ar.utils.getDuplicatedNames():
                confirm = cmds.confirmDialog(title=self.ar.data.lang['v024_duplicatedName'], icon="question", message=self.ar.data.lang['i355_uniqueNameDependence'], button=[self.ar.data.lang['i071_yes'], self.ar.data.lang['i072_no']], defaultButton=self.ar.data.lang['i072_no'], cancelButton=self.ar.data.lang['i072_no'], dismissString=self.ar.data.lang['i072_no'])
                if confirm == self.ar.data.lang['i072_no']:
                    return
        self.reset_button_colors()
        actionResultData = {}
        logText = ""
        if publishLog:
            logText = "\nPublisher"
            logText += "\nScene: "+publishLog["scene"]
            logText += "\nPublished: "+publishLog["published"]
            logText += "\nExported: "+publishLog["exportPath"]
            logText += "\nComments: "+publishLog["comments"]+"\n"
        if actionInstList:
            self.ar.utils.setProgress(self.ar.data.lang[actionType]+': '+self.ar.data.lang['c110_start'], self.ar.data.lang[actionType], len(actionInstList))
            for a, actionInst in enumerate(actionInstList):
                if actionInst.active:
                    self.ar.utils.setProgress(actionInst.name)
                    actionInst.verbose = False
                    actionResultData[actionInst.name] = actionInst.runAction(firstMode)
                    actionInst.verbose = True
                    if stopIfFoundBlock:
                        if True in actionInst.foundIssueList:
                            if False in actionInst.resultOkList:
                                return actionResultData, True, a
        if actionResultData:
            dataList = list(actionResultData.keys())
            dataList.sort()
            for i, dataItem in enumerate(dataList):
                logText += actionResultData[dataItem]["logText"]
                if i != len(dataList)-1:
                    logText += "\n"
            heightSize = len(dataList)
        else:
            logText += "\n"+self.ar.data.lang['i207_notMarked']
            heightSize = 2
        logText = self.ar.pipeliner.getToday(True)+"\n\n"+logText+"\n"
        if verbose:
            self.ar.logger.infoWin('i019_log', actionType, logText, "left", 250, (150+(heightSize)*13))
            print("\n-------------\n"+self.ar.data.lang[actionType]+"\n"+logText)
            if publishLog:
                actionResultData["Publisher"] = publishLog
            if not self.ar.utils.exportLogDicToJson(actionResultData, subFolder=self.ar.data.dp_data+"/"+self.ar.data.dp_log):
                print(self.ar.data.lang['i201_saveScene'])
        self.ar.utils.setProgress(endIt=True)
        return actionResultData, False, 0
