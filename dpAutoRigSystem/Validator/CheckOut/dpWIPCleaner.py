# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass
from ...Modules.Library import dpUtils

# global variables to this module:
CLASS_NAME = "WIPCleaner"
TITLE = "v009_wipCleaner"
DESCRIPTION = "v010_wipCleanerDesc"
ICON = "/Icons/dp_wipCleaner.png"

DP_WIPCLEANER_VERSION = 1.2


class WIPCleaner(dpBaseValidatorClass.ValidatorStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseValidatorClass.ValidatorStartClass.__init__(self, *args, **kwargs)
    

    def runValidator(self, verifyMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If verifyMode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.verifyMode = verifyMode
        self.cleanUpToStart()
        
        # ---
        # --- validator code --- beginning
        wipGrp = None
        if objList:
            wipGrp = objList
        else:
            wipGrp = dpUtils.getNodeByMessage("wipGrp")
            if not wipGrp:
                if cmds.objExists("WIP_Grp"):
                    wipGrp = "WIP_Grp"
        if wipGrp:
            progressAmount = 0
            maxProcess = len(wipGrp)
            if self.verbose:
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
            self.checkedObjList.append(wipGrp)
            wipChildrenList = cmds.listRelatives(wipGrp, allDescendents=True, children=True, fullPath=True)
            if wipChildrenList:
                self.foundIssueList.append(True)
                if self.verifyMode:
                    self.resultOkList.append(False)
                else: #fix    
                    try:
                        cmds.delete(wipChildrenList)
                        self.resultOkList.append(True)
                        self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+wipGrp)
                    except:
                        self.resultOkList.append(False)
                        self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+wipGrp)
            else:
                self.foundIssueList.append(False)
                self.resultOkList.append(True)
        else:
            self.checkedObjList.append("")
            self.foundIssueList.append(False)
            self.resultOkList.append(True)
            self.messageList.append(self.dpUIinst.lang['v011_notWIP'])
        # --- validator code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        return self.dataLogDic
