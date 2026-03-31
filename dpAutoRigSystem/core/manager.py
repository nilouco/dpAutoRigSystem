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

        if savedScene:
            self.selList = cmds.ls(selection=True)
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
            icon_name = alternative
        return icon_name
