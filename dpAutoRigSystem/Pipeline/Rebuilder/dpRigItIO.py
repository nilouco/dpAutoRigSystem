# importing libraries:
from .. import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "RigItIO"
TITLE = "r028_rigItIO"
DESCRIPTION = "r029_rigItIODesc"
ICON = "/Icons/dp_rigItIO.png"

DP_RIGITIO_VERSION = 1.0


class RigItIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_RIGITIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.startName = "dpRigIt"
        self.firstBTEnable = False
        self.firstBTCustomLabel = self.dpUIinst.lang['i305_none']
        self.secondBTCustomLabel = self.dpUIinst.lang['i306_run']
    

    def runAction(self, firstMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in export mode by default.
            If firstMode parameter is False, it'll run in import mode.
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
        # --- rebuilder code --- beginning
        if self.pipeliner.checkAssetContext():
            if self.firstMode: #export
                self.wellDoneIO(self.dpUIinst.lang['v007_allOk'])
            else: #import
                try:
                    self.dpUIinst.rebuilding = True
                    self.dpUIinst.rigAll()
                except Exception as e:
                    self.notWorkedWellIO(str(e))
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r027_noAssetContext'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        self.refreshView()
        return self.dataLogDic
