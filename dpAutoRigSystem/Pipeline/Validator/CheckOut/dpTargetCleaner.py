# importing libraries:
from maya import cmds
from ... import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "TargetCleaner"
TITLE = "v012_targetCleaner"
DESCRIPTION = "v013_targetCleanerDesc"
ICON = "/Icons/dp_targetCleaner.png"

DPKEEPITATTR = "dpKeepIt"

DP_TARGETCLEANER_VERSION = 1.8


class TargetCleaner(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_TARGETCLEANER_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
    

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
        if objList:
            toCheckList = objList
        else:
            toCheckList = None
            meshList = cmds.ls(selection=False, type='mesh')
            if meshList:
                toCheckList = list(set(cmds.listRelatives(meshList, type="transform", parent=True, fullPath=False)))
        if toCheckList:
            self.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
            # get exception list to keep nodes in the scene
            deformersToKeepList = ["skinCluster", "blendShape", "wrap", "cluster", "ffd", "wire", "shrinkWrap", "sculpt", "morph"]
            exceptionList = self.keepGrp(["renderGrp", "proxyGrp"])
            for item in toCheckList:
                if cmds.objExists(item):
                    if cmds.objExists(item+"."+DPKEEPITATTR) and cmds.getAttr(item+"."+DPKEEPITATTR):
                        if not item in exceptionList:
                            exceptionList.append(item)
                    else:
                        try:
                            inputDeformerList = cmds.findDeformers(item)
                        except:
                            self.messageList.append(self.dpUIinst.lang['i075_moreOne']+": "+item)
                            inputDeformerList = False
                        if inputDeformerList:
                            for deformerNode in inputDeformerList:
                                if cmds.objectType(deformerNode) in deformersToKeepList:
                                    if not item in exceptionList:
                                        exceptionList.append(item)
                                    if cmds.objectType(deformerNode) == "wrap":
                                        wrapAttrList = ["basePoints", "driverPoints"]
                                        for wrapAttr in wrapAttrList:
                                            wrapConnectedList = cmds.listConnections(deformerNode+"."+wrapAttr, source=True, destination=False)
                                            if wrapConnectedList:
                                                exceptionList.append(wrapConnectedList[0])
                                        
            # run validation tasks
            for item in toCheckList:
                self.utils.setProgress(self.dpUIinst.lang[self.title])
                if cmds.objExists(item):
                    self.checkedObjList.append(item)
                    if not item in exceptionList:
                        self.foundIssueList.append(True)
                        if self.firstMode:
                            self.resultOkList.append(False)
                        else: #fix        
                            try:
                                fatherItemList = cmds.listRelatives(item, parent=True, type="transform")
                                cmds.delete(item)
                                if fatherItemList:
                                    brotherList = cmds.listRelatives(fatherItemList[0], allDescendents=True, children=True)
                                    if not brotherList:
                                        cmds.delete(fatherItemList[0])
                                self.resultOkList.append(True)
                                self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+item)
                            except:
                                self.resultOkList.append(False)
                                self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item)
                    else:
                        self.foundIssueList.append(False)
                        self.resultOkList.append(True)
        else:
            self.notFoundNodes()
        # --- validator code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic


    def keepGrp(self, grpList, *args):
        """ Check if there're some nodes in the given group to return them.
        """
        resultList = []
        if grpList:
            for item in grpList:
                nodeGrp = self.utils.getNodeByMessage(item)
                if nodeGrp:
                    nodeList = cmds.listRelatives(nodeGrp, allDescendents=True, children=True, type="transform", fullPath=False)
                    if nodeList:
                        resultList.extend(nodeList)
        return resultList