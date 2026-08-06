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
        cmds.evalDeferred("ar = main.Start("+str(self.ar.dev)+", intro=False); ar.ui();", lowestPriority=True)

    
    def reload_dev_mode_ui(self, *args):
        """ Reload the system code as development mode.
        """
        value = True
        if cmds.menuItem('dev_mode_mi', query=True, exists=True):
            value = cmds.menuItem('dev_mode_mi', query=True, checkBox=True)
        if value:
            cmds.evalDeferred("from importlib import reload; reload(dpAutoRigSystem); ar = main.Start(dev=True, intro=False); ar.ui();", lowestPriority=True)
        else:
            cmds.evalDeferred("ar = main.Start(); ar.ui();", lowestPriority=True)


    def refresh_ui(self, saved_scene=False, reset_buttons=True, clear_selection=False):
        """ Read guides, joints, geometries and refresh the UI without reload the script creating a new instance.
            Useful to rebuilding process when creating a new scene
        """
        if self.ar.data.ui_state:
            if saved_scene:
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
                if reset_buttons:
                    self.reset_button_colors()
                self.ar.pipeliner.refreshAssetData()
                for item in self.ar.config.get_rebuilder_instances():
                    item.update_action_buttons(color=False)
            self.ar.job.selection_change()
            if saved_scene:
                cmds.select(clear=True)
                if selected:
                    cmds.select(selected)
            if clear_selection:
                cmds.select(clear=True)


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
            quantity = len(self.ar.data.guide_instances)
            if quantity == 0:
                quantity = 'Zero'
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
        icon = self.ar.data.icon['tri_right']
        if layout == 0: #guide modules
            modules = self.ar.data.guide_instances
            if self.ar.data.modules_collapse_status:
                collapse_value = False
                icon = self.ar.data.icon['tri_down']
            self.ar.data.modules_collapse_status = collapse_value
        else: #rebuilder processes
            modules = self.ar.data.rebuilder_layouts
            if self.ar.data.rebuilders_collapse_status:
                collapse_value = False
                icon = self.ar.data.icon['tri_down']
            self.ar.data.rebuilders_collapse_status = collapse_value
        if modules:
            for item in modules:
                if layout == 0:
                    cmds.frameLayout(item.module_fl, edit=True, collapse=collapse_value)
                else:
                    cmds.frameLayout(item, edit=True, collapse=collapse_value)
        cmds.iconTextButton(iconTB, edit=True, image=icon)


    def get_icon_name(self, item, alternative="add_on"):
        icon_name = "ar"
        if hasattr(item, "name"):
            if item.name in self.ar.data.icon.keys():
                icon_name = item.name
            else:
                icon_name = self.ar.utils.to_snake_case(item.name)
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
                item.reset_button_colors()


    def change_active_modules(self, items, value, *args):
        """ Set all module instances active attribute as True or False.
            Used by validators and rebuilders.
        """
        if items:
            for item in items:
                item.change_active(value)

    
    def run_selected_actions(self, action_instances, first_mode, verbose=True, stop_if_found_block=False, publish_log=None, action_type="v000_validator", *args):
        """ Run the code for each active validator/rebuilder instance.
            first_mode = True for verify/export
                       = False for fix/import
        """
        if first_mode and action_type == "r000_rebuilder": #splitData
            if self.ar.utils.getDuplicatedNames():
                confirm = cmds.confirmDialog(title=self.ar.data.lang['v024_duplicatedName'], icon="question", message=self.ar.data.lang['i355_uniqueNameDependence'], button=[self.ar.data.lang['i071_yes'], self.ar.data.lang['i072_no']], defaultButton=self.ar.data.lang['i072_no'], cancelButton=self.ar.data.lang['i072_no'], dismissString=self.ar.data.lang['i072_no'])
                if confirm == self.ar.data.lang['i072_no']:
                    return
        self.reset_button_colors()
        action_result_data = {}
        log_text = ""
        if publish_log:
            log_text = f"\nPublisher"
            log_text += f"\nScene: {publish_log['scene']}"
            log_text += f"\nPublished: {publish_log['published']}"
            log_text += f"\nExported: {publish_log['exportPath']}"
            log_text += f"\nComments: {publish_log['comments']}\n"
        if action_instances:
            self.ar.utils.setProgress(self.ar.data.lang[action_type]+': '+self.ar.data.lang['c110_start'], self.ar.data.lang[action_type], len(action_instances))
            for a, action_instance in enumerate(action_instances):
                if action_instance.active:
                    self.ar.utils.setProgress(action_instance.name)
                    action_instance.verbose = False
                    action_result_data[action_instance.name] = action_instance.runAction(first_mode)
                    action_instance.verbose = True
                    if stop_if_found_block:
                        if True in action_instance.found_issues:
                            if False in action_instance.good_results:
                                return action_result_data, True, a
        if action_result_data:
            action_result_keys = list(action_result_data.keys())
            action_result_keys.sort()
            for i, item_data in enumerate(action_result_keys):
                log_text += action_result_data[item_data]["log_text"]
                if i != len(action_result_keys)-1:
                    log_text += "\n"
            height_size = len(action_result_keys)
        else:
            log_text += "\n"+self.ar.data.lang['i207_notMarked']
            height_size = 2
        log_text = self.ar.pipeliner.getToday(True)+"\n\n"+log_text+"\n"
        if verbose:
            self.ar.logger.infoWin('i019_log', action_type, log_text, "left", 250, (150+(height_size)*13))
            print("\n-------------\n"+self.ar.data.lang[action_type]+"\n"+log_text)
            if publish_log:
                action_result_data["Publisher"] = publish_log
            if not self.ar.utils.exportLogDicToJson(action_result_data, sub_folder=self.ar.data.dp_data+"/"+self.ar.data.dp_log):
                print(self.ar.data.lang['i201_saveScene'])
        self.ar.utils.setProgress(endIt=True)
        return action_result_data, False, 0
