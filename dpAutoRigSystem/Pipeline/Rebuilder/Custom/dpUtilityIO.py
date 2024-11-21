# importing libraries:
from maya import cmds
from ... import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "UtilityIO"
TITLE = "r054_utilityIO"
DESCRIPTION = "r055_utilityIODesc"
ICON = "/Icons/dp_utilityIO.png"

DP_UTILITYIO_VERSION = 1.0


class UtilityIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_UTILITYIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_utilityIO"
        self.startName = "dpUtility"
        self.utilityTypeList = ["multiplyDivide", "reverse", "plusMinusAverage", "condition", "clamp", "blendColors", "remapValue"]
    

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
                utilityList = None
                if objList:
                    utilityList = objList
                else:
                    utilityList = cmds.ls(selection=False, type=self.utilityTypeList)
                if utilityList:
                    if self.firstMode: #export
                        toExportDataDic = self.getUtilityDataDic(utilityList)
                        if toExportDataDic:
                            try:
                                # export json file
                                self.pipeliner.makeDirIfNotExists(self.ioPath)
                                jsonName = self.ioPath+"/"+self.startName+"_"+self.pipeliner.pipeData['currentFileName']+".json"
                                self.pipeliner.saveJsonFile(toExportDataDic, jsonName)
                                self.wellDoneIO(jsonName)
                            except Exception as e:
                                self.notWorkedWellIO(jsonName+": "+str(e))
                    else: #import
                        try:
                            exportedList = self.getExportedList()
                            if exportedList:
                                exportedList.sort()
                                utilityDic = self.pipeliner.getJsonContent(self.ioPath+"/"+exportedList[-1])
                                if utilityDic:
                                    self.importUtilityData(utilityDic)

                                    # TODO: self.importUtilityConnections(utilityDic)


                                else:
                                    self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
                            else:
                                self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
                        except Exception as e:
                            self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData']+": "+str(e))
                else:
                    self.notWorkedWellIO("Ctrls_Grp")
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


    def getUtilityDataDic(self, utilityList, *args):
        """ Processes the given utility list to collect and mount the info data.
            Returns the dictionary to export.
        """
        if utilityList:
            dic = {}

            self.typeAttrDic = {
                            "multiplyDivide"   : ["operation", "input1X", "input1Y", "input1Z", "input2X", "input2Y", "input2Z"],
                            "reverse"          : ["inputX", "inputY", "inputZ"],
                            "plusMinusAverage" : ["operation"],
                            "condition"        : ["operation", "firstTerm", "secondTerm", "colorIfTrueR", "colorIfTrueG", "colorIfTrueB", "colorIfFalseR", "colorIfFalseG", "colorIfFalseB"],
                            "clamp"            : ["minR", "minG", "minB", "maxR", "maxG", "maxB", "inputR", "inputG", "inputB"],
                            "blendColors"      : ["blender", "color1R", "color1G", "color1B", "color2R", "color2G", "color2B"],
                            "remapValue"       : ["inputValue", "inputMin", "inputMax", "outputMin", "outputMax"]
                        }
            self.typeMultiAttrDic = {
                                "plusMinusAverage" : {"input1D" : [],
                                                      "input2D" : ["input2Dx", "input2Dy"],
                                                      "input3D" : ["input3Dx", "input3Dy", "input3Dz"]
                                                      },
                                "remapValue"       : {"value" : ["value_Position", "value_FloatValue", "value_Interp"],
                                                      "color" : ["color_Position", "color_Color", "color_ColorR", "color_ColorG", "color_ColorB", "color_Position"]
                                                      }
                            }

            self.utils.setProgress(max=len(utilityList), addOne=False, addNumber=False)
            for item in utilityList:
                self.utils.setProgress(self.dpUIinst.lang[self.title])
                if not self.dpID in cmds.listAttr(item):
                    # getting attributes values
                    itemType = cmds.objectType(item)
                    dic[item] = {"attributes" : {},
                                 "type"       : itemType,
                                 "name"       : item
                                }
                    for attr in self.typeAttrDic[itemType]:
                        if attr in cmds.listAttr(item):
                            dic[item]["attributes"][attr] = cmds.getAttr(item+"."+attr)
                    # compound attributes
                    if itemType in self.typeMultiAttrDic.keys():
                        for multiAttr in self.typeMultiAttrDic[itemType].keys():
                            indexList = cmds.getAttr(item+"."+multiAttr, multiIndices=True)
                            if indexList:
                                dot = ""
                                attrList = [""]
                                if self.typeMultiAttrDic[itemType][multiAttr]:
                                    dot = "."
                                    attrList = self.typeMultiAttrDic[itemType][multiAttr]
                                for i in indexList:
                                    for attr in attrList:
                                        attrName = multiAttr+"["+str(i)+"]"+dot+attr
                                        dic[item]["attributes"][attrName] = cmds.getAttr(item+"."+attrName)
            return dic


    def importUtilityData(self, utilityDic, *args):
        """ Import constraints from exported dictionary.
            Create missing constraints and set them values if they don't exists.
        """
        self.utils.setProgress(max=len(utilityDic.keys()), addOne=False, addNumber=False)
        # define lists to check result
        wellImportedList = []
        for item in utilityDic.keys():
            existingNodesList = []
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            # create constraint node if it needs
            if not cmds.objExists(item):
                constType = utilityDic[item]["type"]
                targetList, valueList = [], []
                if utilityDic[item]["target"]:
                    targetAttr = list(utilityDic[item]["target"].keys())[0]
                    keyList = list(utilityDic[item]["target"][targetAttr].keys())
                    keyList.sort()
                    for k in keyList:
                        targetList.append(utilityDic[item]["target"][targetAttr][k][0])
                        valueList.append(utilityDic[item]["target"][targetAttr][k][1])
                toNodeList = utilityDic[item]["constraintParentInverseMatrix"]
                # create the missing constraint
                if targetList and toNodeList:
                    if constType == "parentConstraint":
                        item = cmds.parentConstraint(targetList, toNodeList[0], maintainOffset=True, name=item)[0]
                    elif constType == "pointConstraint":
                        item = cmds.pointConstraint(targetList, toNodeList[0], maintainOffset=True, name=item)[0]
                    elif constType == "orientConstraint":
                        item = cmds.orientConstraint(targetList, toNodeList[0], maintainOffset=True, name=item)[0]
                    elif constType == "scaleConstraint":
                        item = cmds.scaleConstraint(targetList, toNodeList[0], maintainOffset=True, name=item)[0]
                    elif constType == "aimConstraint":
                        item = cmds.aimConstraint(targetList, toNodeList[0], maintainOffset=True, name=item)[0]
                    elif constType == "pointOnPolyConstraint":
                        item = cmds.pointOnPolyConstraint(targetList, toNodeList[0], maintainOffset=True, name=item)[0]
                    elif constType == "geometryConstraint":
                        item = cmds.geometryConstraint(targetList, toNodeList[0], name=item)[0]
                    elif constType == "normalConstraint":
                        item = cmds.normalConstraint(targetList, toNodeList[0], name=item)[0]
                    elif constType == "poleVectorConstraint":
                        item = cmds.poleVectorConstraint(targetList, toNodeList[0], name=item)[0]
                    elif constType == "tangentConstraint":
                        item = cmds.tangentConstraint(targetList, toNodeList[0], name=item)[0]
                    # set attribute values
                    if utilityDic[item]["attributes"]:
                        for attr in utilityDic[item]["attributes"].keys():
                            cmds.setAttr(item+"."+attr, utilityDic[item]["attributes"][attr])
                    # set weight values
                    for v, value in enumerate(valueList):
                        cmds.setAttr(item+"."+targetList[v]+"W"+str(v), value)
                    if utilityDic[item]["worldUpMatrix"]:
                        cmds.connectAttr(utilityDic[item]["worldUpMatrix"][0]+".worldMatrix", item+".worldUpMatrix", force=True)
                    # disconnect to keep the same exported skip option
                    for outAttr in utilityDic[item]["output"].keys():
                        if cmds.objExists(item+"."+outAttr):
                            if not utilityDic[item]["output"][outAttr]:
                                connectedList = cmds.listConnections(item+"."+outAttr, source=False, destination=True, plugs=True)
                                if connectedList:
                                    cmds.disconnectAttr(item+"."+outAttr, connectedList[0])
                    wellImportedList.append(item)
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
