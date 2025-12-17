# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "ConstraintIO"
TITLE = "r050_constraintIO"
DESCRIPTION = "r051_constraintIODesc"
ICON = "/Icons/dp_constraintIO.png"
WIKI = "10-‐-Rebuilder#-constraint"

DP_CONSTRAINTIO_VERSION = 1.02


class ConstraintIO(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_CONSTRAINTIO_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_constraintIO"
        self.startName = "dpConstraint"
    

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
        if not cmds.file(query=True, reference=True):
            if self.pipeliner.checkAssetContext():
                self.ioPath = self.getIOPath(self.ioDir)
                if self.ioPath:
                    constraintList = None
                    if objList:
                        constraintList = objList
                    else:
                        constraintList = cmds.ls(selection=False, type=self.constraintTypeList)
                    if self.firstMode: #export
                        if constraintList:
                            self.exportDicToJsonFile(self.getConstraintDataDic(constraintList))
                        else:
                            self.maybeDoneIO("Constraints")
                    else: #import
                        constDic = self.importLatestJsonFile(self.getExportedList())
                        if constDic:
                            self.importConstraintData(constDic)
                        else:
                            self.maybeDoneIO(self.dpUIinst.lang['r007_notExportedData'])
                else:
                    self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['r027_noAssetContext'])
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r072_noReferenceAllowed'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        self.refreshView()
        return self.dataLogDic
