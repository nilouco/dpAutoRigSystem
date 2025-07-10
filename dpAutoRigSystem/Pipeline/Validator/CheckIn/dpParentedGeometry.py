# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "ParentedGeometry"
TITLE = "v140_parentedGeometry"
DESCRIPTION = "v141_parentedGeometryDesc"
ICON = "/Icons/dp_parentedGeometry.png"

DP_PARENTEDGEOMETRY_VERSION = 1.0


class ParentedGeometry(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_PARENTEDGEOMETRY_VERSION
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
        if not cmds.file(query=True, reference=True):
            if objList:
                toCheckList = cmds.ls(objList, type="mesh")
            else:
                toCheckList = cmds.ls(selection=False, type="mesh") #all meshes in the scene
            if toCheckList:
                meshParentList = self.getMeshTransformList(toCheckList)
                if meshParentList:
                    meshParentList = self.reorderList(meshParentList)
                    self.utils.setProgress(max=len(meshParentList), addOne=False, addNumber=False)
                    # avoid reporting the same item multiple times
                    reportedChildren = set()
                    for mesh in meshParentList:
                        self.utils.setProgress(self.dpUIinst.lang[self.title])
                        # check if exists to avoid missing nodes
                        if cmds.objExists(mesh):
                            allDescendents = cmds.listRelatives(mesh, allDescendents=True, fullPath=True, type='transform') or []
                            # get all descendents and check if it's different than its parent
                            childrenList = self.utils.filterTransformList([d for d in allDescendents if cmds.objExists(d) and d != mesh])
                            if childrenList:
                                for item in childrenList:
                                    shortName = item.split("|")[-1] # get only the last part of the path
                                    # check to avoid multiple report
                                    if not shortName in reportedChildren:
                                        reportedChildren.add(shortName)
                                        self.checkedObjList.append(shortName)
                                        self.foundIssueList.append(True)
                                    if self.firstMode:
                                        self.resultOkList.append(False)
                                    else: #fix
                                        try:
                                            grandParent = cmds.listRelatives(mesh, parent=True, fullPath=True)
                                            if grandParent and cmds.objExists(grandParent[0]):
                                                # try to parent the item to the mesh grandparent
                                                cmds.parent(item, grandParent[0])
                                            else: 
                                                # if no parent, just unparent it to world
                                                cmds.parent(item, world=True)
                                            self.resultOkList.append(True)
                                            self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+item)
                                        except:
                                            self.resultOkList.append(False)
                                            self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item)
            else:
                self.notFoundNodes()
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic
