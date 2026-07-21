# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "ExitEditMode"
TITLE = "v034_exitEditMode"
DESCRIPTION = "v035_exitEditModeDesc"
WIKI = "07-‐-Validator#-exit-edit-mode"



class ExitEditMode(action.BaseAction):
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
                toCheckList = self.ar.ctrls.getControlList()
            if toCheckList:
                self.ar.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                for item in toCheckList:
                    self.ar.utils.setProgress(self.ar.data.lang[self.title])
                    # conditional to check here
                    if "editMode" in cmds.listAttr(item):
                        if cmds.getAttr(item+".editMode") == 1:
                            self.checkedObjList.append(item)
                            self.foundIssueList.append(True)
                            if self.firstMode:
                                self.resultOkList.append(False)
                            else: #fix
                                try:
                                    # delete the corrective script job
                                    self.ar.job.delete_old_job(item)
                                    # remove color override
                                    shapeList = cmds.listRelatives(item, shapes=True, children=True, fullPath=True)
                                    if shapeList:
                                        for shapeNode in shapeList:
                                            cmds.setAttr(shapeNode+".overrideRGBColors", 0)
                                    # set edit mode off
                                    cmds.setAttr(item+".editMode", 0)
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
