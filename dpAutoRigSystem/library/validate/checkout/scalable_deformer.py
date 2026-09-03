# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "ScalableDeformer"
TITLE = "v109_scalableDeformer"
DESCRIPTION = "v110_scalableDeformerDesc"
WIKI = "07-‐-Validator#-scalable-deformer-checker"



class ScalableDeformer(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.rig_scale_output_attr = "rig_scale_output"
    

    def run_action(self, first_mode=True, inputs=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If first_mode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checked_items = node list of checked item
                - found_issues = True if an issue was found, False if there isn't an issue for the checked node
                - good_results = True if well done, False if we got an error
                - messages = reported text
        """
        # starting
        self.first_mode = first_mode
        self.cleanup_to_start()
        
        # ---
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            if inputs:
                check_items = inputs
            else:
                check_items = cmds.ls(selection=False, type=['skinCluster', 'deltaMush'])
            if check_items:
                option_ctrl = self.ar.utils.get_node_by_message("optionCtrl")
                if option_ctrl:
                    self.ar.utils.set_progress(max=len(check_items), add_one=False, add_number=False)
                    rig_scale_output = [option_ctrl+"."+self.rig_scale_output_attr]
                    to_fix_item_attrs = []
                    for node in check_items:
                        self.ar.utils.set_progress(self.ar.data.lang[self.title])
                        node_type = cmds.objectType(node)
                        # check skinCluster nodes and connections
                        if node_type == "skinCluster":
                            if cmds.getAttr(node+".skinningMethod") != 0: # If it's not "Classic Linear"
                                if cmds.getAttr(node+".dqsSupportNonRigid") == False:
                                    to_fix_item_attrs.append(node+".dqsSupportNonRigid")
                                for dqs_attr in ["dqsScaleX", "dqsScaleY", "dqsScaleZ"]:
                                    sc_connections = cmds.listConnections(node+"."+dqs_attr, source=True, destination=True, plugs=True)
                                    if sc_connections != rig_scale_output:
                                        to_fix_item_attrs.append(node+"."+dqs_attr)
                        # check deltaMush nodes and connections
                        elif node_type == "deltaMush":
                            for attr in ["scaleX", "scaleY", "scaleZ"]:
                                dm_connection = cmds.listConnections(node+"."+attr, source=True, destination=True, plugs=True)
                                if dm_connection != rig_scale_output:
                                    to_fix_item_attrs.append(node+"."+attr)
                    if to_fix_item_attrs:
                        for item_attr in to_fix_item_attrs:
                            self.checked_items.append(item_attr)
                            self.found_issues.append(True)
                            if self.first_mode:
                                self.good_results.append(False)
                            else: #fix
                                try:
                                    if item_attr.endswith("dqsSupportNonRigid"):
                                        # check non-rigid support attribute
                                        cmds.setAttr(item_attr, True)
                                    else:
                                        # connect the rig_scale_output to the deformer scale attributes
                                        cmds.connectAttr(rig_scale_output[0], item_attr, force=True)
                                    self.good_results.append(True)
                                    self.messages.append(self.ar.data.lang['v004_fixed']+": "+item_attr)
                                except:
                                    self.good_results.append(False)
                                    self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item_attr)
                                cmds.select(clear=True)
                else:
                    self.not_found_node("Option_Ctrl")
            else:
                self.not_found_node()
        else:
            self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.end_progress()
        return self.log_data
