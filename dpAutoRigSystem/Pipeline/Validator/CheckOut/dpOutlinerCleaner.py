# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "OutlinerCleaner"
TITLE = "v076_outlinerCleaner"
DESCRIPTION = "v077_outlinerCleanerDesc"
ICON = "/Icons/dp_outlinerCleaner.png"

DP_OUTLINERCLEANER_VERSION = 1.03


class OutlinerCleaner(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_OUTLINERCLEANER_VERSION
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
            hiddenList = [self.dpUIinst.tempGrp, self.dpUIinst.guideMirrorGrp]
            if not objList:
                objList = cmds.ls(selection=False, type="transform")
            if objList:
                self.utils.setProgress(max=len(hiddenList), addOne=False, addNumber=False)
                for item in hiddenList:
                    self.utils.setProgress(self.dpUIinst.lang[self.title])
                    if item in objList:
                        self.checkedObjList.append(item)
                        if cmds.objExists(item):
                            self.foundIssueList.append(True)
                            if self.firstMode:
                                self.resultOkList.append(False)
                            else: #fix
                                try:    
                                    cmds.delete(item)
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
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic
