# importing libraries:
from maya import cmds
from .. import dpBaseActionClass

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
#                    ctrlList = cmds.ls(selection=False)
                if ctrlList:
                    if self.firstMode: #export
                        toExportDataDic = self.getAttributeDataDic(ctrlList, True)
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
                                attributeDic = self.pipeliner.getJsonContent(self.ioPath+"/"+exportedList[-1])
                                if attributeDic:
                                    progressAmount = 0
                                    maxProcess = len(attributeDic.keys())
                                    # define lists to check result
                                    wellImportedList = []
                                    for item in attributeDic.keys():
                                        notFoundNodesList = []
                                        progressAmount += 1
                                        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)+" "+item[item.rfind("|"):]))
                                        # check attributes
                                        if not cmds.objExists(item):
                                            item = item[item.rfind("|")+1:] #short name (after last "|")
                                        if cmds.objExists(item):
                                            for attr in attributeDic[item].keys():
                                                if not cmds.objExists(item+"."+attr):
                                                    if not cmds.listConnections(item+"."+attr, destination=False, source=True):
                                                        # unlock attribute
                                                        wasLocked = cmds.getAttr(item+"."+attr, lock=True)
                                                        cmds.setAttr(item+"."+attr, lock=False)
                                                        try:
                                                            # add and set attribute value
#                                                            cmds.addAttr()
                                                            cmds.setAttr(item+"."+attr, attributeDic[item][attr]['value'])
                                                            # lock attribute again if it was locked
                                                            cmds.setAttr(item+"."+attr, lock=wasLocked)
                                                            if not item in wellImportedList:
                                                                wellImportedList.append(item)
                                                        except Exception as e:
                                                            self.notWorkedWellIO(item+" - "+str(e))
                                        else:
                                            notFoundNodesList.append(item)
                                    if wellImportedList:
                                        self.wellDoneIO(', '.join(wellImportedList))
                                    else:
                                        self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+": "+', '.join(notFoundNodesList))
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
        self.endProgressBar()
        self.refreshView()
        return self.dataLogDic


    def getAttributeDataDic(self, ctrlList, filterUserDefined=False, *args):
        """ Processes the given controller list to collect and mount the attributes data.
            Returns the dictionary to export.
            {ctrl : {attr : [attrType, [attrDefaultValue, attrEnumValues], attrValue]}}
        """
        defaultValueTypeList = ["bool", "long",  "short",  "byte",  "char",  "enum",  "'float'",  "double",  "doubleAngle",  "doubleLinear"]
        if ctrlList:
            dic = {}
            progressAmount = 0
            maxProcess = len(ctrlList)
            if self.verbose:
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
            for ctrl in ctrlList:
                attrList = cmds.listAttr(ctrl, userDefined=filterUserDefined)
                if attrList:
                    dic[ctrl] = {}
                    for attr in attrList:
                        if not cmds.getAttr(ctrl+"."+attr, type=True) == "message":
                            attrType = cmds.getAttr(ctrl+"."+attr, type=True)
                            dic[ctrl][attr] = {
                                                "type" : attrType,
                                                "value" : cmds.getAttr(ctrl+"."+attr),
                                                "channelBox" : cmds.getAttr(ctrl+"."+attr, channelBox=True),
                                                "keyable" : cmds.getAttr(ctrl+"."+attr, keyable=True),
                                                "lock" : cmds.getAttr(ctrl+"."+attr, lock=True)
                            }
                            attrDefaultValue = [None, None]
                            if attrType in defaultValueTypeList:
                                if attrType == "enum":
                                    attrDefaultValue = [cmds.addAttr(ctrl+"."+attr, query=True, defaultValue=True), cmds.attributeQuery(attr, node=ctrl, listEnum=True)]
                                else:
                                    attrDefaultValue = [cmds.addAttr(ctrl+"."+attr, query=True, defaultValue=True), None]
                                dic[ctrl][attr]["defaultValue"] = attrDefaultValue
                                maxExists = cmds.attributeQuery(attr, node=ctrl, maxExists=True) or None
                                if maxExists:
                                    dic[ctrl][attr]["maxExists"] = maxExists
                                    dic[ctrl][attr]["maximum"] = cmds.attributeQuery(attr, node=ctrl, maximum=True)

                                minExists = cmds.attributeQuery(attr, node=ctrl, minExists=True) or None
                                if minExists:
                                    dic[ctrl][attr]["minExists"] = minExists
                                    dic[ctrl][attr]["minimum"] = cmds.attributeQuery(attr, node=ctrl, minimum=True)
            return dic
