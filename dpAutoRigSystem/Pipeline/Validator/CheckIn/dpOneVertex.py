# importing libraries:
from maya import cmds
from maya import mel
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "OneVertex"
TITLE = "v132_oneVertex"
DESCRIPTION = "v133_oneVertexDesc"
ICON = "/Icons/dp_oneVertex.png"
WIKI = "07-‐-Validator#-one-vertex"

DP_ONEVERTEX_VERSION = 2.01


class OneVertex(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_ONEVERTEX_VERSION
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
        if not self.utils.getAllGrp():
            if not self.utils.getNetworkNodeByAttr("dpGuideNet"):
                if not cmds.file(query=True, reference=True):
                    if objList:
                        toCheckList = cmds.ls(objList, type="mesh")
                    else:
                        toCheckList = cmds.ls(selection=False, type="mesh")
                    if toCheckList:
                        self.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                        oneVertexList = self.checkNonManifoldVertex(toCheckList)
                        # conditional to check here
                        if oneVertexList:
                            oneVertexList.sort()
                            for item in oneVertexList:
                                self.checkedObjList.append(item)
                                self.foundIssueList.append(True)
                                if self.firstMode:
                                    self.resultOkList.append(False)
                                else: #fix
                                    self.resultOkList.append(False)
                                    self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item)
                            self.messageList.append("---\n"+self.dpUIinst.lang['v121_sharePythonSelect']+"\nmaya.cmds.select("+str(oneVertexList)+")\n---")
                            cmds.select(oneVertexList)
                    else:
                        self.notFoundNodes()
                else:
                    self.notWorkedWellIO(self.dpUIinst.lang['r072_noReferenceAllowed'])
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['v100_cantExistsGuides'])
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['v099_cantExistsAllGrp'])
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic


    def checkNonManifoldVertex(self, itemList, *args):
        """ Return a list of nonManifold vertex if exists.
        """
        nmVertexList, foundList = [], []
        for item in itemList:
            cmds.select(item)
            foundList.extend(mel.eval('polyCleanupArgList 4 { "0","2","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","1","0","0" };'))
        if foundList:
            for sel in foundList:
                if ".vtx[" in sel:
                    nmVertexList.append(sel)
        cmds.select(nmVertexList)
        return nmVertexList
