# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "InputOrderIO"
TITLE = "r035_inputOrderIO"
DESCRIPTION = "r036_inputOrderIODesc"
ICON = "/Icons/dp_inputOrderIO.png"

DP_INPUTORDERIO_VERSION = 1.1


class InputOrderIO(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_INPUTORDERIO_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_inputOrderIO"
        self.startName = "dpInputOrder"
    

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
                if self.firstMode: #export
                    deformedList = None
                    if objList:
                        deformedList = objList
                    else:
                        deformedList = self.dpUIinst.skin.getDeformedItemList(deformerTypeList=self.dpUIinst.skin.getAllDeformerTypeList(), ignoreAttr=self.dpUIinst.skin.ignoreSkinningAttr)
                    if deformedList:
                        self.exportDicToJsonFile(self.getOrderDataDic(deformedList))
                    else:
                        self.maybeDoneIO(self.dpUIinst.lang['v014_notFoundNodes']+" - meshes")
                else: #import
                    orderDic = self.importLatestJsonFile(self.getExportedList())
                    if orderDic:
                        self.importInputOrder(orderDic)
                    else:
                        self.maybeDoneIO(self.dpUIinst.lang['r007_notExportedData'])
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


    def getOrderDataDic(self, deformedList, *args):
        """ Return the deformer order data dictionary to export.
        """
        orderDic = {}
        self.utils.setProgress(max=len(deformedList), addOne=False, addNumber=False)
        for item in deformedList:
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            orderDic[item] = self.dpUIinst.skin.getOrderList(item)
        return orderDic
    

    def importInputOrder(self, orderDic, *args):
        """ Import the input order data from given dictionary.
        """
        self.utils.setProgress(max=len(orderDic.keys()), addOne=False, addNumber=False)
        wellImported = True
        toImportList, notFoundMeshList, = [], []
        for item in orderDic.keys():
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            if cmds.objExists(item):
                toImportList.append(item)
            else:
                notFoundMeshList.append(item)
        if toImportList:
            warningStatus = cmds.scriptEditorInfo(query=True, suppressWarnings=True)
            cmds.scriptEditorInfo(edit=True, suppressWarnings=True)
            for item in toImportList:
                try:
                    # reorder deformers
                    deformerList = orderDic[item]
                    if deformerList:
                        if len(deformerList) > 1:
                            self.dpUIinst.skin.setOrderList(item, deformerList)
                except Exception as e:
                    wellImported = False
                    print(e)
                    self.notWorkedWellIO(self.latestDataFile)
            cmds.scriptEditorInfo(edit=True, suppressWarnings=warningStatus)
            if wellImported:
                self.wellDoneIO(self.latestDataFile)
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+" "+str(', '.join(notFoundMeshList)))
