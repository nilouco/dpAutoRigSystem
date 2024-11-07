# importing libraries:
from maya import cmds
from ... import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "AttributeIO"
TITLE = "r043_attributeIO"
DESCRIPTION = "r044_attributeIODesc"
ICON = "/Icons/dp_attributeIO.png"

DP_ATTRIBUTEIO_VERSION = 1.0


class AttributeIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_ATTRIBUTEIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_attributeIO"
        self.startName = "dpAttribute"
        self.defaultValueTypeList = ["bool", "long",  "short",  "byte",  "char",  "enum",  "'float'",  "double",  "doubleAngle",  "doubleLinear"]
    

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
                ctrlList = None
                if objList:
                    ctrlList = objList
                else:
                    ctrlList = self.dpUIinst.ctrls.getControlList()
                if ctrlList:
                    if self.firstMode: #export
                        toExportDataDic = self.getAttributeDataDic(ctrlList)
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
                                attrDic = self.pipeliner.getJsonContent(self.ioPath+"/"+exportedList[-1])
                                if attrDic:
                                    self.importAttributeData(attrDic)
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


    def getAttributeDataDic(self, ctrlList, *args):
        """ Processes the given controller list to collect and mount the attributes data.
            Returns the dictionary to export.
        """
        if ctrlList:
            dic = {}
            self.utils.setProgress(max=len(ctrlList), addOne=False, addNumber=False)
            for ctrl in ctrlList:
                self.utils.setProgress(self.dpUIinst.lang[self.title])
                attrList = cmds.listAttr(ctrl, userDefined=True)
                if attrList:
                    dic[ctrl] = {"attributes" : {},
                                 "order" : attrList}
                    for attr in attrList:
                        if not cmds.getAttr(ctrl+"."+attr, type=True) == "message":
                            attrType = cmds.getAttr(ctrl+"."+attr, type=True)
                            dic[ctrl]["attributes"][attr] = {
                                                "type" : attrType,
                                                "value" : cmds.getAttr(ctrl+"."+attr),
                                                "locked" : cmds.getAttr(ctrl+"."+attr, lock=True),
                                                "keyable" : cmds.getAttr(ctrl+"."+attr, keyable=True),
                                                "channelBox" : cmds.getAttr(ctrl+"."+attr, channelBox=True)
                                                }
                            if attrType in self.defaultValueTypeList:
                                if attrType == "enum":
                                    dic[ctrl]["attributes"][attr]["enumName"] = cmds.attributeQuery(attr, node=ctrl, listEnum=True)[0]
                                dic[ctrl]["attributes"][attr]["default"] = cmds.addAttr(ctrl+"."+attr, query=True, defaultValue=True)
                                dic[ctrl]["attributes"][attr]["maxExists"] = cmds.attributeQuery(attr, node=ctrl, maxExists=True) or False
                                if dic[ctrl]["attributes"][attr]["maxExists"]:
                                    dic[ctrl]["attributes"][attr]["maximum"] = cmds.attributeQuery(attr, node=ctrl, maximum=True)[0]
                                dic[ctrl]["attributes"][attr]["minExists"] = cmds.attributeQuery(attr, node=ctrl, minExists=True) or False
                                if dic[ctrl]["attributes"][attr]["minExists"]:
                                    dic[ctrl]["attributes"][attr]["minimum"] = cmds.attributeQuery(attr, node=ctrl, minimum=True)[0]
            return dic


    def importAttributeData(self, attrDic, *args):
        """ Import attributes from exported dictionary.
            Add missing attributes and set them values if they don't exists.
        """
        self.utils.setProgress(max=len(attrDic.keys()), addOne=False, addNumber=False)
        # define lists to check result
        wellImportedList = []
        for item in attrDic.keys():
            notFoundNodesList = []
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            # check attributes
            if not cmds.objExists(item):
                item = item[item.rfind("|")+1:] #short name (after last "|")
            if cmds.objExists(item):
                for attr in attrDic[item]["attributes"].keys():
                    if not cmds.objExists(item+"."+attr):
                        try:
                            # add and set attribute value
                            if attrDic[item]["attributes"][attr]['type'] == "string":
                                cmds.addAttr(item, longName=attr, dataType="string")
                                cmds.setAttr(item+"."+attr, attrDic[item]["attributes"][attr]['value'], type="string")
                            elif attrDic[item]["attributes"][attr]['type'] == "enum":
                                cmds.addAttr(item, longName=attr, attributeType="enum", enumName=attrDic[item]["attributes"][attr]['enumName'])
                            else:
                                if attrDic[item]["attributes"][attr]['minExists']:
                                    if attrDic[item]["attributes"][attr]['maxExists']:
                                        cmds.addAttr(item, longName=attr, attributeType=attrDic[item]["attributes"][attr]['type'], minValue=attrDic[item]["attributes"][attr]['minimum'], maxValue=attrDic[item]["attributes"][attr]['maximum'], defaultValue=attrDic[item]["attributes"][attr]['default'])
                                    else:
                                        cmds.addAttr(item, longName=attr, attributeType=attrDic[item]["attributes"][attr]['type'], minValue=attrDic[item]["attributes"][attr]['minimum'], defaultValue=attrDic[item]["attributes"][attr]['default'])
                                elif attrDic[item]["attributes"][attr]['maxExists']:
                                    cmds.addAttr(item, longName=attr, attributeType=attrDic[item]["attributes"][attr]['type'], maxValue=attrDic[item]["attributes"][attr]['maximum'], defaultValue=attrDic[item]["attributes"][attr]['default'])
                                else:
                                    cmds.addAttr(item, longName=attr, attributeType=attrDic[item]["attributes"][attr]['type'], defaultValue=attrDic[item]["attributes"][attr]['default'])
                            if attrDic[item]["attributes"][attr]['type'] in self.defaultValueTypeList:
                                cmds.setAttr(item+"."+attr, attrDic[item]["attributes"][attr]['value'])
                                cmds.setAttr(item+"."+attr, keyable=attrDic[item]["attributes"][attr]['keyable'])
                                if not attrDic[item]["attributes"][attr]['keyable']:
                                    cmds.setAttr(item+"."+attr, channelBox=attrDic[item]["attributes"][attr]['channelBox'])
                                cmds.setAttr(item+"."+attr, lock=attrDic[item]["attributes"][attr]['locked'])
                            if not item in wellImportedList:
                                wellImportedList.append(item)
                        except Exception as e:
                            self.notWorkedWellIO(item+" - "+str(e))
                    else:
                        wellImportedList.append(item)
                # reorder attr
                self.dpUIinst.reorderAttributes([item], attrDic[item]["order"], False)
            else:
                notFoundNodesList.append(item)
        if wellImportedList:
            self.wellDoneIO(', '.join(wellImportedList))
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+": "+', '.join(notFoundNodesList))
