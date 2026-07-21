# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "ModelIO"
TITLE = "r003_modelIO"
DESCRIPTION = "r004_modelIODesc"
WIKI = "10-‐-Rebuilder#-model"



class ModelIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
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
        self.cleanUpToStart(True)
        
        # ---
        # --- rebuilder code --- beginning
        if not cmds.file(query=True, reference=True):
            if self.ar.pipeliner.checkAssetContext():
                # load alembic plugin
                if self.ar.utils.checkLoadedPlugin("AbcExport") and self.ar.utils.checkLoadedPlugin("AbcImport"):
                    self.ioPath = self.getIOPath(self.ioDir)
                    if self.ioPath:
                        if self.firstMode: #export
                            meshList = None
                            if objList:
                                meshList = objList
                            else:
                                meshList = self.ar.utils.filterTransformList(self.getModelToExportList(), verbose=self.ar.data.verbose, title=self.ar.data.lang[self.title])
                            if meshList:
                                self.ar.utils.setProgress(max=len(meshList), addOne=False, addNumber=False)
                                constraintDataDic = self.removeConstraints(meshList)
                                self.exportAlembicFile(meshList)
                                if constraintDataDic:
                                    self.importConstraintData(constraintDataDic, False)
                            else:
                                self.maybeDoneIO("Render_Grp")
                        else: #import
                            self.importLatestAlembicFile(self.getExportedList())
                    else:
                        self.notWorkedWellIO(self.ar.data.lang['r010_notFoundPath'])
                else:
                    self.notWorkedWellIO(self.ar.data.lang['e018_notLoadedPlugin']+"AbcExport")
            else:
                self.notWorkedWellIO(self.ar.data.lang['r027_noAssetContext'])
        else:
            self.notWorkedWellIO(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        self.refreshView()
        return self.dataLogDic
