# importing libraries:
from maya import cmds
from ... import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "RenameIO"
TITLE = "r056_renameIO"
DESCRIPTION = "r057_renameIODesc"
ICON = "/Icons/dp_renameIO.png"

DP_RENAMEIO_VERSION = 1.0


class RenameIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_RENAMEIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_renameIO"
        self.startName = "dpRename"
    

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
                itemList = None
                if objList:
                    itemList = objList
                else:
                    itemList = [n for n in cmds.ls(selection=False, noIntermediate=True) if cmds.attributeQuery(self.dpID, node=n, exists=True)]
                if itemList:
                    if self.firstMode: #export
                        self.exportDicToJsonFile(self.getNodeIDDataDic(itemList))
                    else: #import
                        nodeIDDic = self.importLatestJsonFile(self.getExportedList())
                        if nodeIDDic:
                            self.importNodeIDData(nodeIDDic)
                        else:
                            self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
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


    def getNodeIDDataDic(self, itemList, *args):
        """ Processes the given item list to collect and mount the dpID attribute dictionary.
            Returns the dictionary to export.
        """
        dic = {}
        self.utils.setProgress(max=len(itemList), addOne=False, addNumber=False)
        for item in itemList:
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            if cmds.objExists(item):
                dic[item] = cmds.getAttr(item+"."+self.dpID)
        return dic


    def importNodeIDData(self, nodeIDDic, *args):
        """ Import data from exported dictionary.
            Check if nodes exist in the scene, otherwise try to find in the dpID if it was probably renamed.
        """
        self.utils.setProgress(max=len(nodeIDDic.keys()), addOne=False, addNumber=False)
        # define lists to check result
        wellImportedList = []
        notFoundNodesList = []
        for item in nodeIDDic.keys():
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            # check attributes
            if not cmds.objExists(item):
                oldIDList = self.utils.getDecomposedIDList(nodeIDDic[item])
                if oldIDList:
                    if cmds.objExists(oldIDList[1]):
                        cmds.rename(oldIDList[1], item)
                        wellImportedList.append(item)
                    else:
                        notFoundNodesList.append(item)
        if wellImportedList:
            self.wellDoneIO(self.latestDataFile)
        elif notFoundNodesList:
            self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+": "+', '.join(notFoundNodesList))
