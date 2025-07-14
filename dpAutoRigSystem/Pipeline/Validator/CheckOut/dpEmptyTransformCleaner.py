# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "EmptyTransformCleaner"
TITLE = "v138_emptyTransformCleaner"
DESCRIPTION = "v139_emptyTransformCleanerDesc"
ICON = "/Icons/dp_emptyTransformCleaner.png"

DP_EMPTYTRANSFORMCLEANER_VERSION = 1.0


class EmptyTransformCleaner(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_EMPTYTRANSFORMCLEANER_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
    

    def runAction(self, firstMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If firstMode parameter is False, it'll run in fix mode.
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
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            if objList:
                toCheckList = objList
            else:
                toCheckList =  cmds.ls(selection=False, long=True, type="transform") #list all transforms in the scene
            if toCheckList:
                self.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                emptyTransformList = self.filterEmptyTransformList(toCheckList)
                emptyTransformList.extend(self.filterEmptyTransformList(self.getIgnoreConnected(), True))
                # conditional to check here
                if emptyTransformList:
                    for item in emptyTransformList:
                        self.utils.setProgress(self.dpUIinst.lang[self.title])
                        self.checkedObjList.append(self.utils.getShortName(item, False))
                        self.foundIssueList.append(True)
                        if self.firstMode:
                            self.resultOkList.append(False)
                        else: #fix
                            try:
                                cmds.lockNode(item, lock=False)
                                cmds.delete(item)
                                self.resultOkList.append(True)
                                self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+item)
                            except:
                                self.resultOkList.append(False)
                                self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item)
            else:
                self.notFoundNodes()
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic
    
    
    def filterEmptyTransformList(self, transformList=None, connected=False, *args):
        """ Filter the transform list to remove those without children or connections.
            Returns a list of transforms that are empty.
        """
        filteredList = self.utils.filterTransformList(transformList, verbose=self.verbose, title=self.dpUIinst.lang[self.title])
        filteredList = self.reorderList(filteredList)
        emptyTransforms = []
        for transform in filteredList:
            if connected:
                hasConnection = False
            else:
                hasConnection = cmds.listConnections(transform)
                if hasConnection:
                    nodeGraphList = cmds.listConnections(transform, type="nodeGraphEditorInfo") or []
                    hasConnection = set(hasConnection)-set(nodeGraphList)
            if not hasConnection:
                childrenList = cmds.listRelatives(transform, children=True, fullPath=True)
                if not childrenList:
                    emptyTransforms.append(transform)
                elif len(list(set(childrenList).intersection(emptyTransforms))) == len(childrenList):
                    emptyTransforms.append(transform)
        return emptyTransforms
    

    def getIgnoreConnected(self, *args):
        """ Ignore dpAr default nodes
        """
        ignoredList = ["supportGrp", "renderGrp", "proxyGrp", "fxGrp", "blendShapesGrp", "wipGrp"]
        nodeList = []
        for item in ignoredList:
            gotNode = self.utils.getNodeByMessage(item)
            if gotNode:
                nodeList.append(gotNode)
        return nodeList
    