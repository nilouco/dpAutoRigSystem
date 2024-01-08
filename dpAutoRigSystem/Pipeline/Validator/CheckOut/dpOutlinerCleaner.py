# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass

# global variables to this module:
CLASS_NAME = "OutlinerCleaner"
TITLE = "v076_outlinerCleaner"
DESCRIPTION = "v077_outlinerCleanerDesc"
ICON = "/Icons/dp_outlinerCleaner.png"

DP_OUTLINERCLEANER_VERSION = 1.1


class OutlinerCleaner(dpBaseValidatorClass.ValidatorStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_OUTLINERCLEANER_VERSION
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
        hiddenList = ["dpAR_Temp_Grp", "dpAR_GuideMirror_Grp"]
        if not objList:
            objList = cmds.ls(selection=False, type="transform")
        if objList:
            for i, item in enumerate(objList):
                if cmds.objExists(item):
                    if self.verbose:
                        # Update progress window
                        cmds.progressWindow(edit=True, maxValue=len(objList), progress=i, status=(self.dpUIinst.lang[self.title]+': '+repr(i)))
                    for hidden in hiddenList:
                        self.checkedObjList.append(item)
                        if hidden in item:
                            self.foundIssueList.append(True)
                            if self.verifyMode:
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
        # --- validator code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        return self.dataLogDic
