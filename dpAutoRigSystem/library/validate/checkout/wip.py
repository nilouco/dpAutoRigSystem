# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "Wip"
TITLE = "v009_wip"
DESCRIPTION = "v010_wipDesc"
WIKI = "07-‐-Validator#-wip-cleaner"



class Wip(action.ActionStartClass):
    def __init__(self, ar):
        action.ActionStartClass.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
    

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
            wipGrp = None
            if objList:
                wipGrp = objList
            else:
                wipGrp = self.ar.utils.getNodeByMessage("wipGrp")
                if not wipGrp:
                    if cmds.objExists("WIP_Grp"):
                        wipGrp = "WIP_Grp"
            if wipGrp:
                self.ar.utils.setProgress(max=len(wipGrp), addOne=False, addNumber=False)
                self.ar.utils.setProgress(self.ar.data.lang[self.title])
                self.checkedObjList.append(wipGrp)
                wipChildrenList = cmds.listRelatives(wipGrp, allDescendents=True, children=True, fullPath=True)
                if wipChildrenList:
                    self.foundIssueList.append(True)
                    if self.firstMode:
                        self.resultOkList.append(False)
                    else: #fix    
                        try:
                            cmds.delete(wipChildrenList)
                            self.resultOkList.append(True)
                            self.messageList.append(self.ar.data.lang['v004_fixed']+": "+wipGrp)
                        except:
                            self.resultOkList.append(False)
                            self.messageList.append(self.ar.data.lang['v005_cantFix']+": "+wipGrp)
                else:
                    self.foundIssueList.append(False)
                    self.resultOkList.append(True)
            else:
                self.checkedObjList.append("")
                self.foundIssueList.append(False)
                self.resultOkList.append(True)
                self.messageList.append(self.ar.data.lang['v011_notWIP'])
        else:
            self.notWorkedWellIO(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic
