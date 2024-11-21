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
                if self.firstMode: #export
                    if utilityList:
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
                    nodeType = cmds.objectType(item)
                    dic[item] = {"attributes" : {},
                                 "type"       : nodeType,
                                 "name"       : item
                                }
                    for attr in self.typeAttrDic[nodeType]:
                        if attr in cmds.listAttr(item):
                            dic[item]["attributes"][attr] = cmds.getAttr(item+"."+attr)
                    # compound attributes
                    if nodeType in self.typeMultiAttrDic.keys():
                        for multiAttr in self.typeMultiAttrDic[nodeType].keys():
                            indexList = cmds.getAttr(item+"."+multiAttr, multiIndices=True)
                            if indexList:
                                dot = ""
                                attrList = [""]
                                if self.typeMultiAttrDic[nodeType][multiAttr]:
                                    dot = "."
                                    attrList = self.typeMultiAttrDic[nodeType][multiAttr]
                                for i in indexList:
                                    for attr in attrList:
                                        attrName = multiAttr+"["+str(i)+"]"+dot+attr
                                        attrValue = cmds.getAttr(item+"."+attrName)
                                        dic[item]["attributes"][attrName] = attrValue
                                        if isinstance(attrValue, list):
                                            dic[item]["attributes"][attrName] = attrValue[0]
            return dic


    def importUtilityData(self, utilityDic, *args):
        """ Import utility nodes from exported dictionary.
            Create missing utility nodes and set them values if they don't exists.
        """
        self.utils.setProgress(max=len(utilityDic.keys()), addOne=False, addNumber=False)
        # define lists to check result
        wellImportedList = []
        for item in utilityDic.keys():
            existingNodesList = []
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            # create utility node if it needs
            if not cmds.objExists(item):
                cmds.createNode(utilityDic[item]["type"], name=utilityDic[item]["name"])
                # set attribute values
                if utilityDic[item]["attributes"]:
                    for attr in utilityDic[item]["attributes"].keys():
                        #if isinstance(attr, list): 
                        if str(utilityDic[item]["attributes"][attr]).count(",") > 1: #support vector attributes like color_Color
                            cmds.setAttr(item+"."+attr, utilityDic[item]["attributes"][attr][0], utilityDic[item]["attributes"][attr][1], utilityDic[item]["attributes"][attr][2], type="double3")
                        else:
                            cmds.setAttr(item+"."+attr, utilityDic[item]["attributes"][attr])
                wellImportedList.append(item)
            else:
                existingNodesList.append(item)
        if wellImportedList:
            self.wellDoneIO(', '.join(wellImportedList))
        else:
            if existingNodesList:
                self.wellDoneIO(self.dpUIinst.lang['r032_notImportedData'])
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+": "+', '.join(existingNodesList))
