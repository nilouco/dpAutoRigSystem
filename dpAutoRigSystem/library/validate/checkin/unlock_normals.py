# importing libraries:
from maya import cmds
from maya import OpenMaya
from ....library.base import action
from ....library.util import edge_normals
from importlib import reload


# global variables to this module:
CLASS_NAME = "UnlockNormals"
TITLE = "v078_unlockNormals"
DESCRIPTION = "v079_unlockNormalsDesc"
WIKI = "07-‐-Validator#-unlock-normals"



class UnlockNormals(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(edge_normals)
        self.softHardEdges = edge_normals.ConvertNormals(self.ar)
    

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
            if objList:
                allMeshList = objList
            else:
                allMeshList = cmds.ls(selection=False, type='mesh')
            if allMeshList:
                self.ar.utils.setProgress(max=len(allMeshList), addOne=False, addNumber=False)
                for mesh in allMeshList:
                    self.ar.utils.setProgress(self.ar.data.lang[self.title])
                    if cmds.objExists(mesh):
                        lockedList = cmds.polyNormalPerVertex(mesh+".vtx[*]", query=True, freezeNormal=True)
                        # check if there's any locked normal
                        if True in lockedList:
                            self.checkedObjList.append(mesh)
                            self.foundIssueList.append(True)
                            if self.firstMode:
                                self.resultOkList.append(False)
                            else: #fix
                                try:
                                    #cmds.polyNormalPerVertex(mesh+".vtx[*]", unFreezeNormal=True) #it doesn't keep the soft and hard edges when importing mesh
                                    self.softHardEdges.setSoftHard(mesh)
                                    self.resultOkList.append(True)
                                    self.messageList.append(self.ar.data.lang['v004_fixed']+": "+mesh)
                                except:
                                    self.resultOkList.append(False)
                                    self.messageList.append(self.ar.data.lang['v005_cantFix']+": "+mesh)
            else:
                self.notFoundNodes()
        else:
            self.notWorkedWellIO(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic