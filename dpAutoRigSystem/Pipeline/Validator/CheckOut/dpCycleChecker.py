# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "CycleChecker"
TITLE = "v105_cycleChecker"
DESCRIPTION = "v106_cycleCheckerDesc"
ICON = "/Icons/dp_cycleChecker.png"
WIKI = "07-‐-Validator#-cycle-checker"

DP_CYCLECHECKER_VERSION = 1.01


class CycleChecker(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_CYCLECHECKER_VERSION
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
            self.utils.setProgress(max=1, addOne=False, addNumber=False)
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            cycles = None
            if objList:
                cycles = cmds.cycleCheck(objList, list=True)
                self.checkedObjList.append(objList)
            else:
                cycles = cmds.cycleCheck(all=False, list=True)
                if cycles:
                    self.checkedObjList.append("\n".join(cycles))
            if cycles:
                self.foundIssueList.append(True)
                if self.firstMode:
                    self.resultOkList.append(False)
                else: #fix = can't do it automatically, sorry
                    self.resultOkList.append(False)
                    self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+", ".join(cycles))
            else:
                self.foundIssueList.append(False)
                self.resultOkList.append(True)
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic
