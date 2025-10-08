# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "ParentingIO"
TITLE = "r019_parentingIO"
DESCRIPTION = "r020_parentingIODesc"
ICON = "/Icons/dp_parentingIO.png"

DP_PARENTINGIO_VERSION = 1.02


class ParentingIO(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_PARENTINGIO_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_parentingIO"
        self.startName = "dpParenting"
    

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
                    if self.firstMode: #export
                        transformList = None
                        if objList:
                            transformList = objList
                        else:
                            transformList = cmds.ls(selection=False, long=True, type="transform")
                        if transformList:
                            self.utils.setProgress(max=len(transformList), addOne=False, addNumber=False)
                            # define data to export
                            parentDic = self.getParentingDataDic(transformList)
                            parentDic.update(self.getBrokenIDDataDic())
                            parentDic.update(self.getModelDataDic())
                            self.exportDicToJsonFile(parentDic)
                        else:
                            self.maybeDoneIO(self.dpUIinst.lang['v014_notFoundNodes'])
                    else: #import
                        parentDic = self.importLatestJsonFile(self.getExportedList())
                        if parentDic:
                            try:
                                if self.importBrokenIDData(parentDic):
                                    self.importParentingData(parentDic) #double run to first put broken nodes in place
                                self.importParentingData(parentDic)
                            except Exception as e:
                                self.notWorkedWellIO(self.dpUIinst.lang['r032_notImportedData']+": "+str(e))
                        else:
                            self.maybeDoneIO(self.dpUIinst.lang['r007_notExportedData'])
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


    def getParentingDataDic(self, transformList=None, *args):
        """ Return a filtered dictionary of parenting hierarchy of current scene nodes.
        """
        if not transformList:
            transformList = cmds.ls(selection=False, long=True, type="transform")
        filteredList = self.utils.filterTransformList(transformList, verbose=self.verbose, title=self.dpUIinst.lang[self.title])
        filteredList = self.reorderList(filteredList)
        return {"Parent" : filteredList}


    def getModelDataDic(self, *args):
        """ Check if there's a model list to include in the dictionary data to avoid change parenting from them.
        """
        modelDataDic = {}
        modelList = self.getModelToExportList()
        if modelList:
            modelDataDic["ModelList"] = modelList
        return modelDataDic


    def importBrokenIDData(self, parentDic, *args):
        """ If there are broken nodes, we try to recreate them if needed.
            Return True if there are broken nodes.
        """
        if "BrokenID" in parentDic.keys():
            self.utils.setProgress(max=len(parentDic["BrokenID"]), addOne=False, addNumber=False)
            for nodeType in parentDic["BrokenID"].keys():
                if nodeType == "transform":
                    self.utils.setProgress(self.dpUIinst.lang[self.title])
                    for item in parentDic["BrokenID"][nodeType].keys():
                        if not cmds.objExists(item):
                            if not self.checkIsFromModeling(parentDic, nodeType, item):
                                cmds.createNode(nodeType, name=item)
                                if parentDic["BrokenID"][nodeType][item]:
                                    if cmds.objExists(parentDic["BrokenID"][nodeType][item]):
                                        cmds.parent(item, parentDic["BrokenID"][nodeType][item])
                                cmds.select(clear=True)
            return True


    def importParentingData(self, parentDic, *args):
        """ Import parenting data and put the nodes as the correct hierarchy if needed.
        """
        if not self.getParentingDataDic()["Parent"] == parentDic["Parent"]:
            self.utils.setProgress(max=len(parentDic["Parent"]), addOne=False, addNumber=False)
            # define lists to check result
            wellImportedList = []
            parentIssueList = []
            notFoundNodesList = []
            modelChangedList = []
            # check parenting shaders
            for item in parentDic["Parent"]:
                self.utils.setProgress(self.dpUIinst.lang[self.title])
                if not cmds.objExists(item):
                    parentIssueList.append(item)
                    shortItem = item[item.rfind("|")+1:]
                    if cmds.objExists(shortItem):
                        if len(cmds.ls(shortItem)) == 1:
                            if not self.checkIsFromModeling(parentDic, "transform", item):
                                # get father name
                                longFatherNode = item[:item.rfind("|")]
                                shortFatherNode = longFatherNode[longFatherNode.rfind("|")+1:]
                                currentFatherList = cmds.listRelatives(shortItem, parent=True)
                                if cmds.objExists(longFatherNode):
                                    # simple parent to existing old father node in the ancient hierarchy
                                    cmds.parent(shortItem, longFatherNode)
                                    wellImportedList.append(shortItem)
                                elif currentFatherList:
                                    if currentFatherList[0] == shortFatherNode:
                                        # already child of the father node
                                        wellImportedList.append(shortItem)
                                elif cmds.objExists(shortFatherNode):
                                    if len(cmds.ls(shortFatherNode)) == 1:
                                        # found unique father node in another hierarchy to parent
                                        cmds.parent(shortItem, shortFatherNode)
                                        wellImportedList.append(shortItem)
                                    else:
                                        self.notWorkedWellIO(self.dpUIinst.lang['i075_moreOne']+" "+self.dpUIinst.lang['i076_sameName']+" "+shortFatherNode)
                            else: #root here
                                modelChangedList.append(item)
                        else:
                            self.notWorkedWellIO(self.dpUIinst.lang['i075_moreOne']+" "+self.dpUIinst.lang['i076_sameName']+" "+shortItem)
                    else:
                        if not self.checkIsFromModeling(parentDic, "transform", item):
                            modelChangedList.append(item)
                        else:
                            notFoundNodesList.append(shortItem)
            if parentIssueList:
                if modelChangedList:
                    self.maybeDoneIO(', '.join(modelChangedList))
                elif wellImportedList:
                    self.wellDoneIO(self.latestDataFile)
                else:
                    self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+": "+', '.join(notFoundNodesList))
            else:
                self.wellDoneIO(self.latestDataFile)
        else:
            self.wellDoneIO(self.latestDataFile)


    def checkIsFromModeling(self, parentDic, nodeType, item, *args):
        """ Returns True if the item is from modeling.
        """
        if "ModelList" in parentDic.keys():
            for modelNode in parentDic["ModelList"]:
                if "BrokenID" in parentDic.keys() and nodeType in parentDic["BrokenID"].keys() and item in parentDic["BrokenID"][nodeType].keys():
                    if modelNode in parentDic["BrokenID"][nodeType][item]:
                        return True
