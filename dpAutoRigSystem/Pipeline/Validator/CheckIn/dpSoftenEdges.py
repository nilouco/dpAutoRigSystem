# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "SoftenEdges"
TITLE = "v088_softenEdges"
DESCRIPTION = "v089_softenEdgesDesc"
ICON = "/Icons/dp_softenEdges.png"

DP_SOFTENEDGES_VERSION = 1.2


class SoftenEdges(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_SOFTENEDGES_VERSION
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
        if objList:
            allMeshList = objList
        else:
            allMeshList = cmds.ls(selection=False, type="mesh")
        if allMeshList:
            self.utils.setProgress(max=len(allMeshList), addOne=False, addNumber=False)
            for mesh in allMeshList:
                self.utils.setProgress(self.dpUIinst.lang[self.title])
                if cmds.objExists(mesh):
                    cmds.select(mesh)
                    # set selection only non-smoothed edges
                    cmds.polySelectConstraint(type=0x8000, mode=3, smoothness=1)
                    hardenEdges = cmds.ls(selection=True)
                    cmds.polySelectConstraint(mode=0)
                    if hardenEdges:
                        # converts the selected edges to faces
                        toFace = cmds.polyListComponentConversion(hardenEdges, toFace=True, internal=True)
                        # check if there's any non-smoothed edges
                        if toFace:
                            self.checkedObjList.append(mesh)
                            self.foundIssueList.append(True)
                            if self.firstMode:
                                self.resultOkList.append(False)
                            else: #fix
                                try:
                                    cmds.polySoftEdge(mesh, angle=180, constructionHistory=False)
                                    self.resultOkList.append(True)
                                    self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+mesh)
                                except:
                                    self.resultOkList.append(False)
                                    self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+mesh)
                    cmds.select(clear=True)
    
        else:
            self.notFoundNodes()
        # --- validator code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic