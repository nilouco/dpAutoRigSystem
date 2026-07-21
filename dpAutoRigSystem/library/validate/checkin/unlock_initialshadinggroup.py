# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "UnlockInitialshadinggroup"
TITLE = "v048_unlockIniShadGrp"
DESCRIPTION = "v049_unlockIniShadGrpDesc"
WIKI = "07-‐-Validator#-unlock-initialshadinggroup"



class UnlockInitialshadinggroup(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
    

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
                toCheckList = ["initialShadingGroup"]
            if toCheckList:
                self.ar.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                for item in toCheckList:
                    self.ar.utils.setProgress(self.ar.data.lang[self.title])
                    if cmds.objExists(item):
                        if item == "initialShadingGroup":
                            # conditional to check here
                            if cmds.lockNode(item, query=True, lockUnpublished=True):
                                if cmds.getAttr(item+".nodeState", lock=True):
                                    self.checkedObjList.append(item)
                                    self.foundIssueList.append(True)
                                    if self.firstMode:
                                        self.resultOkList.append(False)
                                    else: #fix
                                        try:
                                            cmds.lockNode(item, lock=False, lockUnpublished=False)
                                            cmds.setAttr(item+".nodeState", lock=False)
                                            self.resultOkList.append(True)
                                            self.messageList.append(self.ar.data.lang['v004_fixed']+": "+item)
                                        except:
                                            self.resultOkList.append(False)
                                            self.messageList.append(self.ar.data.lang['v005_cantFix']+": "+item)
            else:
                self.notFoundNodes()
        else:
            self.notWorkedWellIO(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic
