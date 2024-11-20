# importing libraries:
from maya import cmds
from ... import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "ExitEditMode"
TITLE = "v034_exitEditMode"
DESCRIPTION = "v035_exitEditModeDesc"
ICON = "/Icons/dp_exitEditMode.png"

DP_EXITEDITMODE_VERSION = 1.2


class ExitEditMode(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_EXITEDITMODE_VERSION
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
            toCheckList = self.dpUIinst.ctrls.getControlList()
        if toCheckList:
            self.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
            for item in toCheckList:
                self.utils.setProgress(self.dpUIinst.lang[self.title])
                # conditional to check here
                if cmds.objExists(item+".editMode"):
                    if cmds.getAttr(item+".editMode") == 1:
                        self.checkedObjList.append(item)
                        self.foundIssueList.append(True)
                        if self.firstMode:
                            self.resultOkList.append(False)
                        else: #fix
                            try:
                                # delete the corrective script job
                                self.dpUIinst.ctrls.deleteOldCorrectiveJobs(item)
                                # remove color override
                                shapeList = cmds.listRelatives(item, shapes=True, children=True, fullPath=True)
                                if shapeList:
                                    for shapeNode in shapeList:
                                        cmds.setAttr(shapeNode+".overrideRGBColors", 0)
                                # set edit mode off
                                cmds.setAttr(item+".editMode", 0)
                                self.resultOkList.append(True)
                                self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+item)
                            except:
                                self.resultOkList.append(False)
                                self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item)
        else:
            self.notFoundNodes()
        # --- validator code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic