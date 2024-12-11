# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "ModelIO"
TITLE = "r003_modelIO"
DESCRIPTION = "r004_modelIODesc"
ICON = "/Icons/dp_modelIO.png"

DP_MODELIO_VERSION = 1.0


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
                            meshList = self.getModelToExportList()
                        if meshList:
                            self.utils.setProgress(max=len(meshList), addOne=False, addNumber=False)
                            self.exportAlembicFile(meshList)
                        else:
                            self.notWorkedWellIO("Render_Grp")
                    else: #import
                        self.importLatestAlembicFile(self.getExportedList())
                else:
                    self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['e022_notLoadedPlugin']+"AbcExport")
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r027_noAssetContext'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgress()
        self.refreshView()
        return self.dataLogDic


    def getModelToExportList(self, *args):
        """ Returns a list of higher father mesh node list or the children nodes in Render_Grp.
        """
        meshList, tempList = [], []
        renderGrp = self.utils.getNodeByMessage("renderGrp")
        if renderGrp:
            meshList = cmds.listRelatives(renderGrp, allDescendents=True, fullPath=True, noIntermediate=True, type="mesh") or []
            if meshList:
                return cmds.listRelatives(renderGrp, children=True, type="transform")
        if not meshList:
            unparentedMeshList = cmds.ls(selection=False, noIntermediate=True, long=True, type="mesh")
            if unparentedMeshList:
                for item in unparentedMeshList:
                    if not cmds.objExists(item+".masterGrp"):
                        fatherNode = item[:item[1:].find("|")+1]
                        if fatherNode:
                            if not cmds.objExists(fatherNode+".masterGrp"):
                                if not fatherNode in tempList:
                                    tempList.append(fatherNode)
        if tempList:
            for node in tempList:
                isCleaned = True
                if not cmds.objExists(node+".guideBase") and not cmds.objExists(node+".dpGuide"):
                    childrenList = cmds.listRelatives(node, children=True, allDescendents=True)
                    if childrenList:
                        for child in childrenList:
                            if cmds.objExists(child+".guideBase") or cmds.objExists(child+".dpGuide"):
                                isCleaned = False
                else:
                    isCleaned = False
                if isCleaned:
                    meshList.append(node)
        return meshList
