# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "Cleanup"
TITLE = "v096_cleanup"
DESCRIPTION = "v097_cleanupDesc"
ICON = "/Icons/dp_cleanup.png"
WIKI = "07-‐-Validator#-cleanup"

DP_CLEANUP_VERSION = 1.01


class Cleanup(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_CLEANUP_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
        self.cleanupAttr = "dpDeleteIt"
    

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
                toCheckList = cmds.ls() #all
            if toCheckList:
                self.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                for item in toCheckList:
                    if cmds.objExists(item):
                        self.utils.setProgress(self.dpUIinst.lang[self.title])
                        # conditional to check here
                        if self.cleanupAttr in cmds.listAttr(item):
                            if cmds.getAttr(item+"."+self.cleanupAttr) == 1:
                                self.checkedObjList.append(item)
                                self.foundIssueList.append(True)
                                if self.firstMode:
                                    self.resultOkList.append(False)
                                else: #fix
                                    try:
                                        # delete the node
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
