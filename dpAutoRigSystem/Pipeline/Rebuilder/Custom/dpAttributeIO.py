# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "AttributeIO"
TITLE = "r043_attributeIO"
DESCRIPTION = "r044_attributeIODesc"
ICON = "/Icons/dp_attributeIO.png"

DP_ATTRIBUTEIO_VERSION = 1.0


class AttributeIO(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_ATTRIBUTEIO_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
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
        if not cmds.file(query=True, reference=True):
            if self.pipeliner.checkAssetContext():
                self.ioPath = self.getIOPath(self.ioDir)
                if self.ioPath:
                    itemList = None
                    if objList:
                        itemList = objList
                    else:
                        itemList = self.dpUIinst.ctrls.getControlList()
                        itemList.extend(self.getModelToExportList())
                    if itemList:
                        if self.firstMode: #export
                            self.exportDicToJsonFile(self.getAttributeDataDic(itemList))
                        else: #import
                            attrDic = self.importLatestJsonFile(self.getExportedList())
                            if attrDic:
                                self.importAttributeData(attrDic)
                            else:
                                self.maybeDoneIO(self.dpUIinst.lang['r007_notExportedData'])
                    else:
                        self.maybeDoneIO("Ctrls_Grp")
                else:
                    self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['r027_noAssetContext'])
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r072_noReferenceAllowed'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        self.refreshView()
        return self.dataLogDic


    def getAttributeDataDic(self, objList, *args):
        """ Processes the given controller list to collect and mount the attributes data.
            Also works with meshes.
            Returns the dictionary to export.
        """
        dic = {}
        itemList = objList.copy()
        self.utils.setProgress(max=len(itemList), addOne=False, addNumber=False)
        for node in objList:
            meshList = cmds.listRelatives(node, allDescendents=True, children=True, type="mesh")
            if meshList:
                itemList.extend([m for m in meshList if not cmds.getAttr(m+".intermediateObject")] or [])
                itemList.extend([t for t in cmds.listRelatives(node, allDescendents=True, children=True, type="transform") or [] if cmds.listRelatives(t, children=True, type="mesh")] or [])
        itemList = list(set(itemList))
        itemList.sort()
        for item in itemList:
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            attrList = cmds.listAttr(item, userDefined=True)
            if attrList:
                dic[item] = {"attributes" : {},
                                "order" : attrList}
                for attr in attrList:
                    if not cmds.getAttr(item+"."+attr, type=True) == "message":
                        attrType = cmds.getAttr(item+"."+attr, type=True)
                        dic[item]["attributes"][attr] = {
                                            "type" : attrType,
                                            "value" : cmds.getAttr(item+"."+attr),
                                            "locked" : cmds.getAttr(item+"."+attr, lock=True),
                                            "keyable" : cmds.getAttr(item+"."+attr, keyable=True),
                                            "channelBox" : cmds.getAttr(item+"."+attr, channelBox=True)
                                            }
                        if attrType in self.defaultValueTypeList:
                            if attrType == "enum":
                                dic[item]["attributes"][attr]["enumName"] = cmds.attributeQuery(attr, node=item, listEnum=True)[0]
                            dic[item]["attributes"][attr]["default"] = cmds.addAttr(item+"."+attr, query=True, defaultValue=True)
                            dic[item]["attributes"][attr]["maxExists"] = cmds.attributeQuery(attr, node=item, maxExists=True) or False
                            if dic[item]["attributes"][attr]["maxExists"]:
                                dic[item]["attributes"][attr]["maximum"] = cmds.attributeQuery(attr, node=item, maximum=True)[0]
                            dic[item]["attributes"][attr]["minExists"] = cmds.attributeQuery(attr, node=item, minExists=True) or False
                            if dic[item]["attributes"][attr]["minExists"]:
                                dic[item]["attributes"][attr]["minimum"] = cmds.attributeQuery(attr, node=item, minimum=True)[0]
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
                        # TODO: should we set the attribute value here?
                # reorder attr
                self.dpUIinst.reorderAttributes([item], attrDic[item]["order"], False)
            else:
                notFoundNodesList.append(item)
        if wellImportedList:
            self.wellDoneIO(self.latestDataFile)
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+": "+', '.join(notFoundNodesList))
