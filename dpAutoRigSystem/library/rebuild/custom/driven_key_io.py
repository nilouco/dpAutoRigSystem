# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "DrivenKeyIO"
TITLE = "r052_drivenKeyIO"
DESCRIPTION = "r053_drivenKeyIODesc"
WIKI = "10-‐-Rebuilder#-driven-key"



class DrivenKeyIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_drivenKeyIO"
        self.start_name = "dpDrivenKey"
        self.drivenKeyTypeList = ["animCurveUA", "animCurveUL", "animCurveUT", "animCurveUU"]


    def runAction(self, first_mode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in export mode by default.
            If first_mode parameter is False, it'll run in import mode.
            Returns dataLog with the validation result as:
                - checked_items = node list of checked items
                - found_issues = True if an issue was found, False if there isn't an issue for the checked node
                - good_results = True if well done, False if we got an error
                - messages = reported text
        """
        # starting
        self.first_mode = first_mode
        self.cleanup_to_start(True)
        
        # ---
        # --- rebuilder code --- beginning
        if not cmds.file(query=True, reference=True):
            if self.ar.pipeliner.checkAssetContext():
                self.io_path = self.get_io_path(self.io_folder)
                if self.io_path:
                    nodeList = None
                    if objList:
                        nodeList = objList
                    else:
                        nodeList = cmds.ls(selection=False, type=self.drivenKeyTypeList)
                    if self.first_mode: #export
                        if nodeList:
                            self.export_json_file(self.getDrivenKeyDataDic(nodeList))
                        else:
                            self.maybe_done_io("Set Driven Keys")
                    else: #import
                        drivenKeyDic = self.import_latest_json_file(self.get_exported_items())
                        if drivenKeyDic:
                            self.importDrivenKeyData(drivenKeyDic)
                        else:
                            self.maybe_done_io(self.ar.data.lang['r007_notExportedData'])
                else:
                    self.fail_io(self.ar.data.lang['r010_notFoundPath'])
            else:
                self.fail_io(self.ar.data.lang['r027_noAssetContext'])
        else:
            self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.end_progress()
        self.refresh_view()
        return self.log_data


    def getDrivenKeyDataDic(self, nodeList, *args):
        """ Processes the given set driven key node list to collect and mount the info data.
            Returns the dictionary to export.
        """
        dic = {}
        attrList = ["preInfinity", "postInfinity", "useCurveColor", "stipplePattern", "outStippleThreshold", "stippleReverse"]
        keyAttrList = ["keyBreakdown", "keyTickDrawSpecial"]
        keyTimeAttrList = ["keyTime", "keyValue"]
        self.ar.utils.setProgress(max=len(nodeList), addOne=False, addNumber=False)
        for item in nodeList:
            self.ar.utils.setProgress(self.ar.data.lang[self.title])
            if not cmds.attributeQuery(self.ar.data.dp_id, node=item, exists=True) or not self.ar.utils.validateID(item):
                # getting attributes if they exists
                dic[item] = { "attributes"     : {},
                            "keys"             : {},
                            "keyTimeValue"     : {},
                            "keyTanInType"     : {},
                            "keyTanOutType"    : {},
                            "keyTanInX"        : {},
                            "keyTanInY"        : {},
                            "keyTanOutX"       : {},
                            "keyTanOutY"       : {},
                            "keyTanLocked"     : {},
                            "keyWeightLocked"  : {},
                            "inAngle"          : {},
                            "inWeight"         : {},
                            "outAngle"         : {},
                            "outWeight"        : {},
                            "input"            : cmds.listConnections(item+".input", source=True, destination=False, plugs=True),
                            "output"           : cmds.listConnections(item+".output", source=False, destination=True, plugs=True),
                            "curveColor"       : cmds.getAttr(item+".curveColor")[0],
                            "weightedTangents" : cmds.getAttr(item+".weightedTangents"),
                            "type"             : cmds.objectType(item),
                            "size"             : cmds.getAttr(item+".keyTimeValue", multiIndices=True, size=True),
                            "name"             : item
                            }
                for attr in attrList:
                    if cmds.objExists(item+"."+attr):
                        dic[item]["attributes"][attr] = cmds.getAttr(item+"."+attr)
                # storage the keys
                if cmds.getAttr(item+".keyTimeValue", multiIndices=True):
                    for i, index in enumerate(cmds.getAttr(item+".keyTimeValue", multiIndices=True)):
                        dic[item]["keyTimeValue"][index] = {}
                        dic[item]["keys"][index] = {}
                        for ktAttr in keyTimeAttrList:
                            dic[item]["keyTimeValue"][index][ktAttr] = cmds.getAttr(item+".keyTimeValue["+str(i)+"]."+ktAttr)
                        for kAttr in keyAttrList:
                            dic[item]["keys"][index][kAttr] = cmds.getAttr(item+"."+kAttr+"["+str(i)+"]")
                        dic[item]["keyTanInType"][index]    = cmds.keyTangent(item, query=True, index=(i, i), inTangentType=True)[0]
                        dic[item]["keyTanOutType"][index]   = cmds.keyTangent(item, query=True, index=(i, i), outTangentType=True)[0]
                        dic[item]["keyTanInX"][index]       = cmds.keyTangent(item, query=True, index=(i, i), ix=True)[0]
                        dic[item]["keyTanInY"][index]       = cmds.keyTangent(item, query=True, index=(i, i), iy=True)[0]
                        dic[item]["keyTanOutX"][index]      = cmds.keyTangent(item, query=True, index=(i, i), ox=True)[0]
                        dic[item]["keyTanOutY"][index]      = cmds.keyTangent(item, query=True, index=(i, i), oy=True)[0]
                        dic[item]["keyTanLocked"][index]    = cmds.keyTangent(item, query=True, index=(i, i), lock=True)[0]
                        dic[item]["keyWeightLocked"][index] = cmds.keyTangent(item, query=True, index=(i, i), weightLock=True)[0]
                        dic[item]["inAngle"][index]         = cmds.keyTangent(item, query=True, index=(i, i), inAngle=True)[0]
                        dic[item]["inWeight"][index]        = cmds.keyTangent(item, query=True, index=(i, i), inWeight=True)[0]
                        dic[item]["outAngle"][index]        = cmds.keyTangent(item, query=True, index=(i, i), outAngle=True)[0]
                        dic[item]["outWeight"][index]       = cmds.keyTangent(item, query=True, index=(i, i), outWeight=True)[0]
        return dic


    def importDrivenKeyData(self, drivenKeyDic, *args):
        """ Import set driven key nodes from exported dictionary.
            Create missing set driven key nodes and set them values if they don't exists.
        """
        self.ar.utils.setProgress(max=len(drivenKeyDic.keys()), addOne=False, addNumber=False)
        # define lists to check result
        wellImportedList = []
        for item in drivenKeyDic.keys():
            existingNodesList = []
            self.ar.utils.setProgress(self.ar.data.lang[self.title])
            # create set driven key node if it needs
            if not cmds.objExists(item):
                drivenKeyType = drivenKeyDic[item]["type"]
                node = cmds.createNode(drivenKeyType, name=drivenKeyDic[item]["name"])
                # set attribute values
                for attr in drivenKeyDic[item]["attributes"].keys():
                    if cmds.objExists(node+"."+attr):
                        cmds.setAttr(node+"."+attr, drivenKeyDic[item]["attributes"][attr])
                cmds.setAttr(node+".curveColor", drivenKeyDic[item]["curveColor"][0], drivenKeyDic[item]["curveColor"][1], drivenKeyDic[item]["curveColor"][2], type="double3")
                cmds.keyTangent(node, edit=True, weightedTangents=drivenKeyDic[item]["weightedTangents"])
                # set driven keys
                for i in range(0, drivenKeyDic[item]["size"]):
                    cmds.setKeyframe(item, float=drivenKeyDic[item]["keyTimeValue"][str(i)]["keyTime"], value=drivenKeyDic[item]["keyTimeValue"][str(i)]["keyValue"])
                    for kAttr in drivenKeyDic[item]["keys"][str(i)].keys():
                        cmds.setAttr(item+"."+kAttr+"["+str(i)+"]", drivenKeyDic[item]["keys"][str(i)][kAttr])
                    cmds.keyTangent(node, edit=True, index=(int(i), int(i)), inTangentType=drivenKeyDic[item]["keyTanInType"][str(i)])
                    cmds.keyTangent(node, edit=True, index=(int(i), int(i)), outTangentType=drivenKeyDic[item]["keyTanOutType"][str(i)])
                    cmds.keyTangent(node, edit=True, index=(int(i), int(i)), ix=drivenKeyDic[item]["keyTanInX"][str(i)])
                    cmds.keyTangent(node, edit=True, index=(int(i), int(i)), iy=drivenKeyDic[item]["keyTanInY"][str(i)])
                    cmds.keyTangent(node, edit=True, index=(int(i), int(i)), ox=drivenKeyDic[item]["keyTanOutX"][str(i)])
                    cmds.keyTangent(node, edit=True, index=(int(i), int(i)), oy=drivenKeyDic[item]["keyTanOutX"][str(i)])
                    cmds.keyTangent(node, edit=True, index=(int(i), int(i)), lock=drivenKeyDic[item]["keyTanLocked"][str(i)])
                    cmds.keyTangent(node, edit=True, index=(int(i), int(i)), inAngle=drivenKeyDic[item]["inAngle"][str(i)])
                    cmds.keyTangent(node, edit=True, index=(int(i), int(i)), inWeight=drivenKeyDic[item]["inWeight"][str(i)])
                    cmds.keyTangent(node, edit=True, index=(int(i), int(i)), outAngle=drivenKeyDic[item]["outAngle"][str(i)])
                    cmds.keyTangent(node, edit=True, index=(int(i), int(i)), outWeight=drivenKeyDic[item]["outWeight"][str(i)])
                    if drivenKeyDic[item]["weightedTangents"]:
                        cmds.keyTangent(node, edit=True, index=(int(i), int(i)), weightLock=drivenKeyDic[item]["keyWeightLocked"][str(i)])
                # reconnect node
                if drivenKeyDic[item]["input"]:
                    if cmds.objExists(drivenKeyDic[item]["input"][0]):
                        cmds.connectAttr(drivenKeyDic[item]["input"][0], node+".input", force=True)
                if drivenKeyDic[item]["output"]:
                    for c, outputNode in enumerate(drivenKeyDic[item]["output"]):
                        if cmds.objExists(drivenKeyDic[item]["output"][c]):
                            lockedStatus = cmds.getAttr(drivenKeyDic[item]["output"][c], lock=True)
                            cmds.setAttr(drivenKeyDic[item]["output"][c], lock=False)
                            cmds.connectAttr(node+".output", drivenKeyDic[item]["output"][c], force=True)
                            if lockedStatus:
                                cmds.setAttr(drivenKeyDic[item]["output"][c], lock=True)
                wellImportedList.append(node)
            else:
                existingNodesList.append(item)
        if wellImportedList:
            self.well_done_io(self.latest_data_file)
        else:
            if existingNodesList:
                self.well_done_io(self.ar.data.lang['r032_notImportedData'])
            else:
                self.fail_io(self.ar.data.lang['v014_notFoundNodes']+": "+', '.join(existingNodesList))
