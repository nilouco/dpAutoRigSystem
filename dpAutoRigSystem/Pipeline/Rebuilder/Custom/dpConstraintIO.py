# importing libraries:
from maya import cmds
from ... import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "ConstraintIO"
TITLE = "r050_constraintIO"
DESCRIPTION = "r051_constraintIODesc"
ICON = "/Icons/dp_constraintIO.png"

DP_CONSTRAINTIO_VERSION = 1.0


class ConstraintIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_CONSTRAINTIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_constraintIO"
        self.startName = "dpConstraint"
        self.constraintTypeList = ["parentConstraint", "pointConstraint", "orientConstraint", "scaleConstraint", "aimConstraint", "pointOnPolyConstraint", "geometryConstraint", "normalConstraint", "poleVectorConstraint", "tangentConstraint"]
    

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
                constraintList = None
                if objList:
                    constraintList = objList
                else:
                    constraintList = cmds.ls(selection=False, type=self.constraintTypeList)
                if self.firstMode: #export
                    if constraintList:
                        self.exportDicToJsonFile(self.getConstraintDataDic(constraintList))
                else: #import
                    try:
                        exportedList = self.getExportedList()
                        if exportedList:
                            exportedList.sort()
                            constDic = self.pipeliner.getJsonContent(self.ioPath+"/"+exportedList[-1])
                            if constDic:
                                self.importConstraintData(constDic)
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


    def getConstraintDataDic(self, constraintList, *args):
        """ Processes the given constraint list to collect and mount the info data.
            Returns the dictionary to export.
        """
        if constraintList:
            dic = {}
            attrList = ["interpType", "constraintOffsetPolarity", "aimVectorX", "aimVectorY", "aimVectorZ", "upVectorX", "upVectorY", "upVectorZ", "worldUpType", "worldUpVectorX", "worldUpVectorY", "worldUpVectorZ"]
            outputAttrList = ["constraintTranslateX", "constraintTranslateY",  "constraintTranslateZ",  "constraintRotateX",  "constraintRotateY",  "constraintRotateZ",  "constraintScaleX",  "constraintScaleY",  "constraintScaleZ"]
            #typeAttrDic = {
            #                "parentConstraint" : ["interpType"],
            #                "orientConstraint" : ["interpType"],
            #                "pointConstraint"  : ["constraintOffsetPolarity"],
            #                "normalConstraint" : ["aimVectorX", "aimVectorY", "aimVectorZ", "upVectorX", "upVectorY", "upVectorZ", "worldUpType", "worldUpVectorX", "worldUpVectorY", "worldUpVectorZ"],
            #                "aimConstraint"    : ["aimVectorX", "aimVectorY", "aimVectorZ", "upVectorX", "upVectorY", "upVectorZ", "worldUpType", "worldUpVectorX", "worldUpVectorY", "worldUpVectorZ"]
            #            }
            self.utils.setProgress(max=len(constraintList), addOne=False, addNumber=False)
            for const in constraintList:
                self.utils.setProgress(self.dpUIinst.lang[self.title])
                if not cmds.attributeQuery(self.dpID, node=const, exists=True):
                    # getting attributes if they exists
                    dic[const] = {"attributes" : {},
                                "output"     : {},
                                "type"       : cmds.objectType(const)
                                }
                    for attr in attrList:
                        if cmds.objExists(const+"."+attr):
                            dic[const]["attributes"][attr] = cmds.getAttr(const+"."+attr)
                    dic[const]["worldUpMatrix"] = []
                    if cmds.objExists(const+".worldUpMatrix"):
                        dic[const]["worldUpMatrix"] = cmds.listConnections(const+".worldUpMatrix", source=True, destination=False)
                    dic[const]["constraintParentInverseMatrix"] = cmds.listConnections(const+".constraintParentInverseMatrix", source=True, destination=False)
                    dic[const]["target"] = {}
                    if cmds.objExists(const+".target"):
                        targetAttr = None
                        if cmds.objExists(const+".target[0].targetParentMatrix"):
                            targetAttr = "targetParentMatrix"
                        elif cmds.objExists(const+".target[0].targetGeometry"):
                            targetAttr = "targetGeometry"
                        elif cmds.objExists(const+".target[0].targetMesh"):
                            targetAttr = "targetMesh"
                        if targetAttr:
                            dic[const]["target"][targetAttr] = {}
                            targetList = cmds.getAttr(const+".target", multiIndices=True)
                            for t in targetList:
                                dic[const]["target"][targetAttr][t] = [cmds.listConnections(const+".target["+str(t)+"]."+targetAttr, source=True, destination=False)[0], cmds.getAttr(const+".target["+str(t)+"].targetWeight")]
                    # store connection info to disconnect when import if need to skip the constraint driving
                    for outAttr in outputAttrList:
                        dic[const]["output"][outAttr] = None
                        if cmds.objExists(const+"."+outAttr):
                            if cmds.listConnections(const+"."+outAttr, source=False, destination=True):
                                dic[const]["output"][outAttr] = True
                            else:
                                dic[const]["output"][outAttr] = False
            return dic


    def importConstraintData(self, constDic, *args):
        """ Import constraints from exported dictionary.
            Create missing constraints and set them values if they don't exists.
        """
        self.utils.setProgress(max=len(constDic.keys()), addOne=False, addNumber=False)
        # define lists to check result
        wellImportedList = []
        for item in constDic.keys():
            existingNodesList = []
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            # create constraint node if it needs
            if not cmds.objExists(item):
                constType = constDic[item]["type"]
                targetList, valueList = [], []
                if constDic[item]["target"]:
                    targetAttr = list(constDic[item]["target"].keys())[0]
                    keyList = list(constDic[item]["target"][targetAttr].keys())
                    keyList.sort()
                    for k in keyList:
                        targetList.append(constDic[item]["target"][targetAttr][k][0])
                        valueList.append(constDic[item]["target"][targetAttr][k][1])
                toNodeList = constDic[item]["constraintParentInverseMatrix"]
                # create the missing constraint
                if targetList and toNodeList:
                    if constType == "parentConstraint":
                        const = cmds.parentConstraint(targetList, toNodeList[0], maintainOffset=True, name=item)[0]
                    elif constType == "pointConstraint":
                        const = cmds.pointConstraint(targetList, toNodeList[0], maintainOffset=True, name=item)[0]
                    elif constType == "orientConstraint":
                        const = cmds.orientConstraint(targetList, toNodeList[0], maintainOffset=True, name=item)[0]
                    elif constType == "scaleConstraint":
                        const = cmds.scaleConstraint(targetList, toNodeList[0], maintainOffset=True, name=item)[0]
                    elif constType == "aimConstraint":
                        const = cmds.aimConstraint(targetList, toNodeList[0], maintainOffset=True, name=item)[0]
                    elif constType == "pointOnPolyConstraint":
                        const = cmds.pointOnPolyConstraint(targetList, toNodeList[0], maintainOffset=True, name=item)[0]
                    elif constType == "geometryConstraint":
                        const = cmds.geometryConstraint(targetList, toNodeList[0], name=item)[0]
                    elif constType == "normalConstraint":
                        const = cmds.normalConstraint(targetList, toNodeList[0], name=item)[0]
                    elif constType == "poleVectorConstraint":
                        const = cmds.poleVectorConstraint(targetList, toNodeList[0], name=item)[0]
                    elif constType == "tangentConstraint":
                        const = cmds.tangentConstraint(targetList, toNodeList[0], name=item)[0]
                    # set attribute values
                    if constDic[item]["attributes"]:
                        for attr in constDic[item]["attributes"].keys():
                            cmds.setAttr(const+"."+attr, constDic[item]["attributes"][attr])
                    # set weight values
                    for v, value in enumerate(valueList):
                        cmds.setAttr(item+"."+targetList[v]+"W"+str(v), value)
                    if constDic[item]["worldUpMatrix"]:
                        cmds.connectAttr(constDic[item]["worldUpMatrix"][0]+".worldMatrix", const+".worldUpMatrix", force=True)
                    # disconnect to keep the same exported skip option
                    for outAttr in constDic[item]["output"].keys():
                        if cmds.objExists(const+"."+outAttr):
                            if not constDic[item]["output"][outAttr]:
                                connectedList = cmds.listConnections(const+"."+outAttr, source=False, destination=True, plugs=True)
                                if connectedList:
                                    cmds.disconnectAttr(const+"."+outAttr, connectedList[0])
                    wellImportedList.append(const)
                else:
                    cmds.createNode(constType, name=item) #broken node
                    self.notWorkedWellIO(self.dpUIinst.lang['i329_broken']+" node - "+item)
            else:
                existingNodesList.append(item)
        if wellImportedList:
            self.wellDoneIO(', '.join(wellImportedList))
        else:
            if existingNodesList:
                self.wellDoneIO(self.dpUIinst.lang['r032_notImportedData'])
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+": "+', '.join(existingNodesList))
