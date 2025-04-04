# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "HideDataGrp"
TITLE = "v028_hideDataGrp"
DESCRIPTION = "v029_hideDataGrpDesc"
ICON = "/Icons/dp_hideDataGrp.png"

DP_HIDEDATAGRP_VERSION = 1.2


class HideDataGrp(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_HIDEDATAGRP_VERSION
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
            dataGrp = None
            if objList:
                dataGrp = objList[0]
            else:
                dataGrp = self.utils.getNodeByMessage("dataGrp")
                if not dataGrp:
                    if cmds.objExists("Data_Grp"):
                        dataGrp = "Data_Grp"
            if dataGrp:
                self.utils.setProgress(max=1)
                self.utils.setProgress(self.dpUIinst.lang[self.title])
                self.checkedObjList.append(dataGrp)
                visibilityStatus = cmds.getAttr(dataGrp+".visibility")
                if visibilityStatus:
                    self.foundIssueList.append(True)
                    if self.firstMode:
                        self.resultOkList.append(False)
                    else: #fix
                        try:
                            cmds.setAttr(dataGrp+".visibility", 0)
                            self.resultOkList.append(True)
                            self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+dataGrp)
                        except:
                            self.resultOkList.append(False)
                            self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+dataGrp)
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
