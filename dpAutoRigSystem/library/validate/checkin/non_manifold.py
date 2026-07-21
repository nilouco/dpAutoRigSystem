# importing libraries:
from maya import cmds
from maya import mel
from ....library.base import action

# global variables to this module:
CLASS_NAME = "NonManifold"
TITLE = "v101_nonManifold"
DESCRIPTION = "v102_nonManifoldDesc"
WIKI = "07-‐-Validator#-nonmanifold-cleaner"



class NonManifold(action.BaseAction):
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
        if not self.ar.utils.getAllGrp():
            if not self.ar.utils.getNetworkNodeByAttr("dpGuideNet"):
                if not cmds.file(query=True, reference=True):
                    if objList:
                        geoToCleanList = objList
                    else:
                        geoToCleanList = cmds.ls(list(set(self.checkNonManifold(self.getMeshTransformList()))), long=False)
                    if geoToCleanList:
                        self.ar.utils.setProgress(max=len(geoToCleanList), addOne=False, addNumber=False)
                        for geo in geoToCleanList:
                            self.ar.utils.setProgress(self.ar.data.lang[self.title])
                            if cmds.objExists(geo):
                                self.checkedObjList.append(geo)
                                self.foundIssueList.append(True)
                                if self.firstMode:
                                    self.resultOkList.append(False)
                                else: #fix
                                    try:
                                        cmds.select(geo)
                                        # Cleanup non manifolds
                                        mel.eval('polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","1","0","0" };')
                                        self.resultOkList.append(True)
                                        self.messageList.append(self.ar.data.lang['v004_fixed']+": "+geo)
                                        mel.eval('changeSelectMode -object;')
                                        cmds.select(clear=True)
                                    except:
                                        self.resultOkList.append(False)
                                        self.messageList.append(self.ar.data.lang['v005_cantFix']+": "+geo)
                    else:
                        self.notFoundNodes()
                else:
                    self.notWorkedWellIO(self.ar.data.lang['r072_noReferenceAllowed'])
            else:
                self.notWorkedWellIO(self.ar.data.lang['v100_cantExistsGuides'])
        else:
            self.notWorkedWellIO(self.ar.data.lang['v099_cantExistsAllGrp'])
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic


    def checkNonManifold(self, itemList, *args):
        """ Verify if there are non manifold meshes and return them if exists.
        """
        nonManifoldList = []
        if itemList:
            for item in itemList:
                if cmds.polyInfo(item, nonManifoldEdges=True, nonManifoldUVEdges=True, nonManifoldUVs=True, nonManifoldVertices=True):
                    nonManifoldList.append(item)
        return nonManifoldList
