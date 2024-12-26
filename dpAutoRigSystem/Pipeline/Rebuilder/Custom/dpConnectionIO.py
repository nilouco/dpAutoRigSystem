# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "ConnectionIO"
TITLE = "r045_connectionIO"
DESCRIPTION = "r046_connectionIODesc"
ICON = "/Icons/dp_connectionIO.png"

DP_CONNECTIONIO_VERSION = 1.0


class ConnectionIO(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_CONNECTIONIO_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_connectionIO"
        self.startName = "dpConnection"
    

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
                        toExportDataDic = self.getConnectionDataDic(ctrlList)
                        toExportDataDic.update(self.getUtilitiesDataDic(cmds.ls(selection=False, type=self.utils.utilityTypeList))) #utilityNodes without dpID
                        self.exportDicToJsonFile(toExportDataDic)
                    else: #import
                        connectDic = self.importLatestJsonFile(self.getExportedList())
                        if connectDic:
                            self.importConnectionData(connectDic)
                        else:
                            self.maybeDoneIO(self.dpUIinst.lang['r007_notExportedData'])
                else:
                    self.maybeDoneIO("Ctrls_Grp")
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r027_noAssetContext'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        self.refreshView()
        return self.dataLogDic


    def getConnectionDataDic(self, itemList, *args):
        """ Processes the given list to collect the info about their connections to rebuild.
            Returns a dictionary to export.
        """
        dic = {}
        self.utils.setProgress(max=len(itemList), addOne=False, addNumber=False)
        for item in itemList:
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            if cmds.objExists(item):
                attrList = self.dpUIinst.transformAttrList.copy()
                userDefList = cmds.listAttr(item, userDefined=True)
                if userDefList:
                    attrList.extend(userDefList)
                connectedAttrList = []
                for attr in attrList:
                    if cmds.objExists(item+"."+attr):
                        if cmds.listConnections(item+"."+attr):
                            connectedAttrList.append(attr)
                if connectedAttrList:
                    dic[item] = {}
                    for attr in connectedAttrList:
                        dic[item][attr] = self.getConnectionIODic(item, attr)
        return dic


    def getConnectionInfoList(self, item, sourceConnection, destinationConnection, *args):
        """ Return a list of plugged nodes and their attributes of the given item.
        """
        resultList = []
        if cmds.listConnections(item, plugs=True, source=sourceConnection, destination=destinationConnection):
            infoList = cmds.listConnections(item, plugs=True, source=sourceConnection, destination=destinationConnection)
            if infoList:
                for info in infoList:
                    if cmds.objectType(info[:info.find(".")]) == "unitConversion":
                        if sourceConnection:
                            connectionInfo = self.getConnectionInfoList(info[:info.find(".")]+".input", sourceConnection, destinationConnection) or [None]
                            resultList.append({info : connectionInfo})
                        else:
                            connectionInfo = self.getConnectionInfoList(info[:info.find(".")]+".output", sourceConnection, destinationConnection) or [None]
                            resultList.append({info : connectionInfo})
                        resultList[-1][list(resultList[-1].keys())[0]].append(cmds.getAttr(info[:info.find(".")]+".conversionFactor"))
                    else:
                        resultList.append(info)
        return resultList


    def getAttrConnections(self, item, attrDic, multi=False, *args):
        """ Return a dictionary with the connections for the attributes.
        """
        dic = {}
        nodeType = cmds.objectType(item)
        if nodeType in attrDic.keys():
            connectedAttrList = []
            for attr in attrDic[nodeType]:
                if cmds.listConnections(item+"."+attr):
                    connectedAttrList.append(attr)
            if connectedAttrList:
                for attr in connectedAttrList:
                    if multi:
                        indexList = cmds.getAttr(item+"."+attr, multiIndices=True)
                        if indexList:
                            dot = ""
                            multiAttrList = [""]
                            if attrDic[nodeType][attr]:
                                dot = "."
                                multiAttrList = attrDic[nodeType][attr]
                            for i in indexList:
                                for multiAttr in multiAttrList:
                                    attrName = attr+"["+str(i)+"]"+dot+multiAttr
                                    dic[attrName] = self.getConnectionIODic(item, attrName)
                    else:
                        dic[attr] = self.getConnectionIODic(item, attr)
        return dic
    

    def getUtilitiesDataDic(self, itemList, *args):
        """ Return the connection data from given utility nodes list.
        """
        dic = {}
        self.utils.setProgress(max=len(itemList), addOne=False, addNumber=False)
        for item in itemList:
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            if cmds.objExists(item):
                if not cmds.attributeQuery(self.dpID, node=item, exists=True) or not self.utils.validateID(item):
                    for attrDic, multi in zip([self.utils.typeAttrDic, self.utils.typeOutAttrDic, self.utils.typeMultiAttrDic, self.utils.typeOutMultiAttrDic], [False, False, True, True]):
                        gotDic = self.getAttrConnections(item, attrDic, multi)
                        if gotDic:
                            if not item in dic.keys():
                                dic[item] = gotDic
                            else:
                                dic[item].update(gotDic)
        return dic
        

    def getConnectionIODic(self, item, attr, *args):
        """ Return the connection from and to the given item and its attribute.
        """
        return {
                "in"  : self.getConnectionInfoList(item+"."+attr, sourceConnection=True, destinationConnection=False),
                "out" : self.getConnectionInfoList(item+"."+attr, sourceConnection=False, destinationConnection=True)
                }


    def importConnectionData(self, connectDic, *args):
        """ Import connection data.
            Check if need to create an unitConversion node and set its conversionFactor value.
            Only redo the connection if it doesn't exists yet.
        """
        self.utils.setProgress(max=len(connectDic.keys()), addOne=False, addNumber=False)
        # define lists to check result
        wellImportedList = []
        for item in connectDic.keys():
            notFoundNodesList = []
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            if cmds.objExists(item):
                # check connections
                for attr in connectDic[item].keys():
                    #if attr in cmds.listAttr(item): #can't have this conditional because multiIndices doesn't exists before connect them
                    for i, io in enumerate(["in", "out"]): #input and output
                        if connectDic[item][attr][io]: #there's connection
                            for ioInfo in connectDic[item][attr][io]:
                                if isinstance(ioInfo, dict): #is dictionary, so there's an unitConversion node
                                    plug = list(ioInfo.keys())[0]
                                    if not cmds.objExists(plug):
                                        uc = cmds.createNode("unitConversion", name=plug.split(".")[0])
                                        cmds.setAttr(uc+".conversionFactor", ioInfo[plug][1])
                                    else:
                                        uc = plug.split(".")[0]
                                    if not ioInfo[plug][0] == None:
                                        if i == 0: #in
                                            if not cmds.listConnections(item+"."+attr, plugs=True, source=True, destination=False) or not uc+".output" in cmds.listConnections(item+"."+attr, plugs=True, source=True, destination=False):
                                                isLocked = cmds.getAttr(item+"."+attr, lock=True)
                                                cmds.setAttr(item+"."+attr, lock=False)
                                                cmds.connectAttr(uc+".output", item+"."+attr, force=True)
                                                if isLocked:
                                                    cmds.setAttr(item+"."+attr, lock=True)
                                            if not cmds.listConnections(uc+".input", plugs=True, source=True, destination=False) or not ioInfo[plug][0] in cmds.listConnections(uc+".input", plugs=True, source=True, destination=False):
                                                cmds.connectAttr(ioInfo[plug][0], uc+".input", force=True)
                                        else: #out
                                            if not cmds.listConnections(item+"."+attr, plugs=True, source=False, destination=True) or not uc+".input" in cmds.listConnections(item+"."+attr, plugs=True, source=False, destination=True):
                                                cmds.connectAttr(item+"."+attr, uc+".input", force=True)
                                            if not cmds.listConnections(uc+".output", plugs=True, source=False, destination=True) or not ioInfo[plug][0] in cmds.listConnections(uc+".output", plugs=True, source=False, destination=True):
                                                isLocked = cmds.getAttr(ioInfo[plug][0], lock=True)
                                                cmds.setAttr(ioInfo[plug][0], lock=False)
                                                cmds.connectAttr(uc+".output", ioInfo[plug][0], force=True)
                                                if isLocked:
                                                    cmds.setAttr(ioInfo[plug][0], lock=True)
                                    else: #there is a not connected unitConversion node
                                        self.notWorkedWellIO(self.dpUIinst.lang['r047_notConnectedUC']+": "+uc)
                                elif cmds.objExists(ioInfo[:ioInfo.find(".")]):
                                    if i == 0: #in
                                        if not cmds.listConnections(item+"."+attr, plugs=True, source=True, destination=False) or not ioInfo in cmds.listConnections(item+"."+attr, plugs=True, source=True, destination=False):
                                            isLocked = cmds.getAttr(item+"."+attr, lock=True)
                                            cmds.setAttr(item+"."+attr, lock=False)
                                            cmds.connectAttr(ioInfo, item+"."+attr, force=True)
                                            if isLocked:
                                                cmds.setAttr(item+"."+attr, lock=True)
                                    else: #out
                                        if not cmds.listConnections(item+"."+attr, plugs=True, source=False, destination=True) or not ioInfo in cmds.listConnections(item+"."+attr, plugs=True, source=False, destination=True):
                                            isLocked = cmds.getAttr(ioInfo, lock=True)
                                            cmds.setAttr(ioInfo, lock=False)
                                            cmds.connectAttr(item+"."+attr, ioInfo, force=True)
                                            if isLocked:
                                                cmds.setAttr(ioInfo, lock=True)
                                else:
                                     self.maybeDoneIO(ioInfo[:ioInfo.find(".")])
                                if not item in wellImportedList:
                                    wellImportedList.append(item)
            else:
                notFoundNodesList.append(item)
        if notFoundNodesList:
            self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+": "+', '.join(notFoundNodesList))
        elif wellImportedList:
            self.wellDoneIO(self.latestDataFile)
