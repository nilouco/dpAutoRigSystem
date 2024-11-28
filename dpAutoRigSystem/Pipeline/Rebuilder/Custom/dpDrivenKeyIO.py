# importing libraries:
from maya import cmds
from ... import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "DrivenKeyIO"
TITLE = "r052_drivenKeyIO"
DESCRIPTION = "r053_drivenKeyIODesc"
ICON = "/Icons/dp_drivenKeyIO.png"

DP_DRIVENKEYIO_VERSION = 1.0


class DrivenKeyIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_DRIVENKEYIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_drivenKeyIO"
        self.startName = "dpDrivenKey"
        self.drivenKeyTypeList = ["animCurveUA", "animCurveUL", "animCurveUT", "animCurveUU"]


    def runAction(self, firstMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in export mode by default.
            If firstMode parameter is False, it'll run in import mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.firstMode = firstMode
        self.cleanUpToStart()
        
        # ---
        # --- rebuilder code --- beginning
        if self.pipeliner.checkAssetContext():
            self.ioPath = self.getIOPath(self.ioDir)
            if self.ioPath:
                nodeList = None
                if objList:
                    nodeList = objList
                else:
                    nodeList = cmds.ls(selection=False, type=self.drivenKeyTypeList)
                if self.firstMode: #export
                    if nodeList:
                        self.exportDicToJsonFile(self.getDrivenKeyDataDic(nodeList))
                else: #import
                    try:
                        exportedList = self.getExportedList()
                        if exportedList:
                            exportedList.sort()
                            drivenKeyDic = self.pipeliner.getJsonContent(self.ioPath+"/"+exportedList[-1])
                            if drivenKeyDic:
                                self.importDrivenKeyData(drivenKeyDic)
                            else:
                                self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
                        else:
                            self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
                    except Exception as e:
                        self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData']+": "+str(e))
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r027_noAssetContext'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgress()
        self.refreshView()
        return self.dataLogDic


    def getDrivenKeyDataDic(self, nodeList, *args):
        """ Processes the given set driven key node list to collect and mount the info data.
            Returns the dictionary to export.
        """
        dic = {}
        attrList = ["preInfinity", "postInfinity", "useCurveColor", "stipplePattern", "outStippleThreshold", "stippleReverse"]
        keyAttrList = ["keyBreakdown", "keyTickDrawSpecial"]
        keyTimeAttrList = ["keyTime", "keyValue"]
        self.utils.setProgress(max=len(nodeList), addOne=False, addNumber=False)
        for item in nodeList:
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            if not cmds.attributeQuery(self.dpID, node=item, exists=True) or not self.utils.validateID(item):
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
        self.utils.setProgress(max=len(drivenKeyDic.keys()), addOne=False, addNumber=False)
        # define lists to check result
        wellImportedList = []
        for item in drivenKeyDic.keys():
            existingNodesList = []
            self.utils.setProgress(self.dpUIinst.lang[self.title])
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
            self.wellDoneIO(', '.join(wellImportedList))
        else:
            if existingNodesList:
                self.wellDoneIO(self.dpUIinst.lang['r032_notImportedData'])
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+": "+', '.join(existingNodesList))
