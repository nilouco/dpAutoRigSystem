# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "UnusedSkinCleaner"
TITLE = "v082_unusedSkinCleaner"
DESCRIPTION = "v083_unusedSkinCleanerDesc"
ICON = "/Icons/dp_unusedSkinCleaner.png"

DP_UNUSEDSKINCLEANER_VERSION = 1.03


class UnusedSkinCleaner(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_UNUSEDSKINCLEANER_VERSION
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
                toCheckList = cmds.ls(selection=False, type="skinCluster")
            if toCheckList:
                self.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                for item in toCheckList:
                    self.utils.setProgress(self.dpUIinst.lang[self.title])
                    # conditional 1 to check here if there's an influenced node, otherwise delete the unused skinCluster
                    meshList = cmds.skinCluster(item, query=True, geometry=True)
                    if meshList:
                        # conditional 2 to check here if there's weighted vertices by influencer
                        influenceList = cmds.skinCluster(item, query=True, influence=True)
                        weightedInfluenceList = cmds.skinCluster(item, query=True, weightedInfluence=True)
                        if not len(influenceList) == len(weightedInfluenceList):
                            self.checkedObjList.append(item)
                            self.foundIssueList.append(True)
                            if self.firstMode:
                                self.resultOkList.append(False)
                            else: #fix
                                try:
                                    toRemoveJointList = []
                                    for jointNode in influenceList:
                                        if not jointNode in weightedInfluenceList:
                                            if not jointNode in toRemoveJointList:
                                                toRemoveJointList.append(jointNode)
                                    if toRemoveJointList:
                                        cmds.skinCluster(item, edit=True, removeInfluence=toRemoveJointList, toSelectedBones=True)
                                    self.resultOkList.append(True)
                                    self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+item+" = "+str(len(toRemoveJointList))+" joints")
                                except:
                                    self.resultOkList.append(False)
                                    self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item)
                    else:
                        self.checkedObjList.append(item)
                        self.foundIssueList.append(True)
                        if self.firstMode:
                            self.resultOkList.append(False)
                        else: #fix
                            try:
                                cmds.lockNode(item, lock=False)
                                cmds.delete(item)
                                self.resultOkList.append(True)
                                self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+item+" = deleted")
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
