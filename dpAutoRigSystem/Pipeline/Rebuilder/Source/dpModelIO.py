# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "ModelIO"
TITLE = "r003_modelIO"
DESCRIPTION = "r004_modelIODesc"
ICON = "/Icons/dp_modelIO.png"
WIKI = "10-‐-Rebuilder#-model"

DP_MODELIO_VERSION = 1.02


class ModelIO(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_MODELIO_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_modelIO"
        self.startName = "dpModel"
    

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
                # load alembic plugin
                if self.utils.checkLoadedPlugin("AbcExport") and self.utils.checkLoadedPlugin("AbcImport"):
                    self.ioPath = self.getIOPath(self.ioDir)
                    if self.ioPath:
                        if self.firstMode: #export
                            meshList = None
                            if objList:
                                meshList = objList
                            else:
                                meshList = self.utils.filterTransformList(self.getModelToExportList(), verbose=self.verbose, title=self.dpUIinst.lang[self.title])
                            if meshList:
                                self.utils.setProgress(max=len(meshList), addOne=False, addNumber=False)
                                constraintDataDic = self.removeConstraints(meshList)
                                self.exportAlembicFile(meshList)
                                if constraintDataDic:
                                    self.importConstraintData(constraintDataDic, False)
                            else:
                                self.maybeDoneIO("Render_Grp")
                        else: #import
                            self.importLatestAlembicFile(self.getExportedList())
                    else:
                        self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
                else:
                    self.notWorkedWellIO(self.dpUIinst.lang['e018_notLoadedPlugin']+"AbcExport")
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
