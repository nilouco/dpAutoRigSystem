# importing libraries:
from maya import cmds
from ....library.base import action
from importlib import reload

# global variables to this module:
CLASS_NAME = "NewSceneIO"
TITLE = "r025_newSceneIO"
DESCRIPTION = "r026_newSceneIODesc"
WIKI = "10-‐-Rebuilder#-new-scene"



class NewSceneIO(action.ActionStartClass):
    def __init__(self, ar):
        action.ActionStartClass.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(action)
        self.startName = "dpNewScene"
        self.firstBTEnable = False
        self.firstBTCustomLabel = self.ar.data.lang['i305_none']
        self.secondBTCustomLabel = self.ar.data.lang['i306_run']
        self.setActionType("r000_rebuilder")


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
        self.cleanUpToStart(True)
        
        # ---
        # --- rebuilder code --- beginning
        if self.ar.pipeliner.checkAssetContext():
            if self.firstMode: #export
                self.wellDoneIO(self.ar.data.lang['v007_allOk'])
            else: #import
                try:
                    # start a new clean scene and keep the same asset context
                    cmds.file(newFile=True, force=True)
                    self.wellDoneIO(self.ar.pipeliner.pipeData["assetName"])
                except Exception as e:
                    self.notWorkedWellIO(str(e))
        else:
            self.notWorkedWellIO(self.ar.data.lang['r027_noAssetContext'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress(True)
        self.refreshView()
        return self.dataLogDic
