# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "RemapValueToSetRange"
TITLE = "v136_remapValueToSetRange"
DESCRIPTION = "v137_remapValueToSetRangeDesc"
ICON = "/Icons/dp_remapValueToSetRange.png"

DP_REMAPVALUETOSETRANGE_VERSION = 1.00


class RemapValueToSetRange(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_REMAPVALUETOSETRANGE_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
    

    def runAction(self, firstMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If firstMode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.firstMode = firstMode
        self.cleanUpToStart()
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
            if objList:
                toCheckList = cmds.ls(objList, type="remapValue")
            else:
                toCheckList = cmds.ls(selection=False, type="remapValue")
            if toCheckList:
                remapValueToChangeList = []
                for item in toCheckList:
                    indexList = cmds.getAttr(f"{item}.value", multiIndices=True)
                    # Check if color is used - if so, ignore it, since we only convert value remaps
                    if cmds.listConnections(f"{item}.outColor", source=False, destination=True):
                        continue
                    # Check if the remapValue node does more than just set min/max range (e.g. has
                    # a gradient curve being tweaked - if so, we skip it)
                    remappedGradient = True
                    for index in indexList:
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
                    self.utils.setProgress(max=len(remapValueToChangeList), addOne=False, addNumber=False)
                    wellDone = True
                    for remapValueNode in remapValueToChangeList:
                        self.utils.setProgress(self.dpUIinst.lang[self.title])
                        self.foundIssueList.append(True)
                        if self.firstMode:
                            self.checkedObjList.append(remapValueNode)
                            self.resultOkList.append(False)
                        else: #fix
                            try:
                                setRangeNode = cmds.createNode("setRange", name=remapValueNode.replace("_RmV", "_SR"))
                                # Transfer values or connections
                                for remapAttr, setRangeAttr in self.mappingDic.items():
                                    self.dpUIinst.ctrls.transferPlug(f"{remapValueNode}.{remapAttr}", f"{setRangeNode}.{setRangeAttr}")
                                #clear Interpolation_PMA node
                                indexList = cmds.getAttr(f"{remapValueNode}.value", multiIndices=True)
                                for index in indexList:
                                    connectedInputList = cmds.listConnections(remapValueNode+".value["+str(index)+"].value_Interp", source=True, destination=False, plugs=False)
                                    if connectedInputList:
                                        cmds.delete(connectedInputList[0])
                                # delete the old remapValue node
                                cmds.delete(remapValueNode)
                                self.checkedObjList.append(remapValueNode+" -> "+setRangeNode)
                                self.resultOkList.append(True)
                            except:
                                self.resultOkList.append(False)
                                wellDone = False
                                break
                    if self.firstMode:
                        self.messageList.append(self.dpUIinst.lang['v006_foundIssue']+": "+str(len(remapValueToChangeList))+" remapValue nodes")
                    else:
                        if wellDone:
                            self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+str(len(remapValueToChangeList))+" remapValue nodes")
                        else:
                            self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+remapValueNode)
            else:
                self.notFoundNodes()
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic
