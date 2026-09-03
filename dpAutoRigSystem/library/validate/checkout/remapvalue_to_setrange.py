# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "RemapvalueToSetrange"
TITLE = "v136_remapValueToSetRange"
DESCRIPTION = "v137_remapValueToSetRangeDesc"
WIKI = "07-‐-Validator#-remapvalue-to-setrange"



class RemapvalueToSetrange(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.mapping_data = {
                            "inputMax"   : "oldMaxX",
                            "inputMin"   : "oldMinX",
                            "outputMax"  : "maxX",
                            "outputMin"  : "minX",
                            "inputValue" : "valueX",
                            "outValue"   : "outValueX"
                            }
    

    def run_action(self, first_mode=True, inputs=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If first_mode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checked_items = node list of checked items
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
                check_items = cmds.ls(inputs, type="remapValue")
            else:
                check_items = cmds.ls(selection=False, type="remapValue")
            if check_items:
                to_change_rmv_items = []
                for item in check_items:
                    indexes = cmds.getAttr(f"{item}.value", multiIndices=True)
                    # Check if color is used - if so, ignore it, since we only convert value remaps
                    if cmds.listConnections(f"{item}.outColor", source=False, destination=True):
                        continue
                    # Check if the remapValue node does more than just set min/max range (e.g. has
                    # a gradient curve being tweaked - if so, we skip it)
                    remapped_gradient = True
                    for index in indexes:
                        value_position, value_float, value_interp = cmds.getAttr(f"{item}.value[{index}]")[0]
                        if value_position != value_float: #there's curve
                            break
                        if value_interp != 1.0: #linear
                            break
                        if cmds.getAttr(item+".inputMin") > cmds.getAttr(item+".inputMax"): #setRange isn't able to work well with it as a remapValue
                            break
                        if cmds.getAttr(item+".outputMin") > cmds.getAttr(item+".outputMax"):
                            break
                    else:
                        remapped_gradient = False
                    if remapped_gradient:
                        continue
                    to_change_rmv_items.append(item)
                # conditional to check here
                if to_change_rmv_items:
                    self.ar.ui_manager.set_progress(max=len(to_change_rmv_items), add_one=False, add_number=False)
                    well_done = True
                    for rmv_node in to_change_rmv_items:
                        self.ar.ui_manager.set_progress(self.ar.data.lang[self.title])
                        self.found_issues.append(True)
                        if self.first_mode:
                            self.checked_items.append(rmv_node)
                            self.good_results.append(False)
                        else: #fix
                            try:
                                sr_node = cmds.createNode("setRange", name=rmv_node.replace("_RmV", "_SR"))
                                # Transfer values or connections
                                for rmv_attr, sr_attr in self.mapping_data.items():
                                    self.ar.ctrls.transfer_plug(f"{rmv_node}.{rmv_attr}", f"{sr_node}.{sr_attr}")
                                #clear Interpolation_PMA node
                                indexes = cmds.getAttr(f"{rmv_node}.value", multiIndices=True)
                                for index in indexes:
                                    connected_inputs = cmds.listConnections(rmv_node+".value["+str(index)+"].value_Interp", source=True, destination=False, plugs=False)
                                    if connected_inputs:
                                        cmds.delete(connected_inputs[0])
                                # delete the old remapValue node
                                cmds.delete(rmv_node)
                                self.checked_items.append(rmv_node+" -> "+sr_node)
                                self.good_results.append(True)
                            except:
                                self.good_results.append(False)
                                well_done = False
                                break
                    if self.first_mode:
                        self.messages.append(self.ar.data.lang['v006_foundIssue']+": "+str(len(to_change_rmv_items))+" remapValue nodes")
                    else:
                        if well_done:
                            self.messages.append(self.ar.data.lang['v004_fixed']+": "+str(len(to_change_rmv_items))+" remapValue nodes")
                        else:
                            self.messages.append(self.ar.data.lang['v005_cantFix']+": "+rmv_node)
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
