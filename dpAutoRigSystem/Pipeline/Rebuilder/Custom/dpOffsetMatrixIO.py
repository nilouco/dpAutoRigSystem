# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "OffsetMatrixIO"
TITLE = "r061_offsetMatrixIO"
DESCRIPTION = "r062_offsetMatrixIODesc"
ICON = "/Icons/dp_offsetMatrixIO.png"

DP_OFFSETMATRIXIO_VERSION = 1.0


class OffsetMatrixIO(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_OFFSETMATRIXIO_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_offsetMatrixIO"
        self.startName = "dpOffsetMatrix"
        self.offsetMatrixAttr = "offsetParentMatrix"
    

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
                    nodeList = cmds.ls(selection=False, type="transform")
                if nodeList:
                    if self.firstMode: #export
                        toExportDataDic = self.getOffsetMatrixDataDic(nodeList)
                        self.exportDicToJsonFile(toExportDataDic)
                    else: #import
                        toImportDic = self.importLatestJsonFile(self.getExportedList())
                        if toImportDic:
                            self.importOffsetMatrixData(toImportDic)
                        else:
                            self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
                else:
                    self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes'])
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


    def getOffsetMatrixDataDic(self, itemList, *args):
        """ Processes the given list to collect the info about their parent offset matrix connections to rebuild.
            Returns a dictionary to export.
        """
        dic = {}
        self.utils.setProgress(max=len(itemList), addOne=False, addNumber=False)
        for item in itemList:
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            if cmds.objExists(item):
                inPlugList = cmds.listConnections(item+"."+self.offsetMatrixAttr, source=True, destination=False, plugs=True)
                if inPlugList:
                    dic[item] = inPlugList[0]
        return dic


    def importOffsetMatrixData(self, connectDic, *args):
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
                omAttr = item+"."+self.offsetMatrixAttr
                if not cmds.listConnections(omAttr, plugs=True, source=True, destination=False):
                    isLocked = cmds.getAttr(omAttr, lock=True)
                    cmds.setAttr(omAttr, lock=False)
                    cmds.connectAttr(connectDic[item]+"[0]", omAttr, force=True)
                    if isLocked:
                        cmds.setAttr(omAttr, lock=True)
                if not item in wellImportedList:
                    wellImportedList.append(item)
            else:
                notFoundNodesList.append(item+"."+self.offsetMatrixAttr)
        if notFoundNodesList:
            self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+": "+', '.join(notFoundNodesList))
        elif wellImportedList:
            self.wellDoneIO(self.latestDataFile)
