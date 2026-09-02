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
        self.mappingDic = {
                            "inputMax"   : "oldMaxX",
                            "inputMin"   : "oldMinX",
                            "outputMax"  : "maxX",
                            "outputMin"  : "minX",
                            "inputValue" : "valueX",
                            "outValue"   : "outValueX"
                            }
        
        # ---
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            if inputs:
                check_items = cmds.ls(inputs, type="remapValue")
            else:
                check_items = cmds.ls(selection=False, type="remapValue")
            if check_items:
                remapValueToChangeList = []
                for item in check_items:
                    indexes = cmds.getAttr(f"{item}.value", multiIndices=True)
                    # Check if color is used - if so, ignore it, since we only convert value remaps
                    if cmds.listConnections(f"{item}.outColor", source=False, destination=True):
                        continue
                    # Check if the remapValue node does more than just set min/max range (e.g. has
                    # a gradient curve being tweaked - if so, we skip it)
                    remappedGradient = True
                    for index in indexes:
                        valuePosition, valueFloat, valueInterp = cmds.getAttr(f"{item}.value[{index}]")[0]
                        if valuePosition != valueFloat: #there's curve
                            break
                        if valueInterp != 1.0: #linear
                            break
                        if cmds.getAttr(item+".inputMin") > cmds.getAttr(item+".inputMax"): #setRange isn't able to work well with it as a remapValue
                            break
                        if cmds.getAttr(item+".outputMin") > cmds.getAttr(item+".outputMax"):
                            break
                    else:
                        remappedGradient = False
                    if remappedGradient:
                        continue
                    remapValueToChangeList.append(item)
                # conditional to check here
                if remapValueToChangeList:
                    self.ar.utils.set_progress(max=len(remapValueToChangeList), add_one=False, add_number=False)
                    wellDone = True
                    for remapValueNode in remapValueToChangeList:
                        self.ar.utils.set_progress(self.ar.data.lang[self.title])
                        self.found_issues.append(True)
                        if self.first_mode:
                            self.checked_items.append(remapValueNode)
                            self.good_results.append(False)
                        else: #fix
                            try:
                                setRangeNode = cmds.createNode("setRange", name=remapValueNode.replace("_RmV", "_SR"))
                                # Transfer values or connections
                                for remapAttr, setRangeAttr in self.mappingDic.items():
                                    self.ar.ctrls.transfer_plug(f"{remapValueNode}.{remapAttr}", f"{setRangeNode}.{setRangeAttr}")
                                #clear Interpolation_PMA node
                                indexes = cmds.getAttr(f"{remapValueNode}.value", multiIndices=True)
                                for index in indexes:
                                    connectedInputList = cmds.listConnections(remapValueNode+".value["+str(index)+"].value_Interp", source=True, destination=False, plugs=False)
                                    if connectedInputList:
                                        cmds.delete(connectedInputList[0])
                                # delete the old remapValue node
                                cmds.delete(remapValueNode)
                                self.checked_items.append(remapValueNode+" -> "+setRangeNode)
                                self.good_results.append(True)
                            except:
                                self.good_results.append(False)
                                wellDone = False
                                break
                    if self.first_mode:
                        self.messages.append(self.ar.data.lang['v006_foundIssue']+": "+str(len(remapValueToChangeList))+" remapValue nodes")
                    else:
                        if wellDone:
                            self.messages.append(self.ar.data.lang['v004_fixed']+": "+str(len(remapValueToChangeList))+" remapValue nodes")
                        else:
                            self.messages.append(self.ar.data.lang['v005_cantFix']+": "+remapValueNode)
            else:
                self.not_found_node()
        else:
            self.notWorkedWellIO(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.end_progress()
        return self.log_data
