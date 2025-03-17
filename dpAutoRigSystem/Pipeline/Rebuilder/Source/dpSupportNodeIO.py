# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "SupportNodeIO"
TITLE = "r023_supportNodeIO"
DESCRIPTION = "r024_supportNodeIODesc"
ICON = "/Icons/dp_supportNodeIO.png"

DP_SUPPORTNODEIO_VERSION = 1.1


class SupportNodeIO(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_SUPPORTNODEIO_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_supportNodeIO"
        self.startName = "dpSupportNode"
    

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
                            itemList = None
                            if objList:
                                itemList = objList
                            else:
                                itemList = self.getNodeToExportList()
                            if itemList:
                                self.utils.setProgress(self.dpUIinst.lang[self.title], addOne=False, addNumber=False)
                                self.exportAlembicFile(itemList, attr=False, curve=True)
                            else:
                                self.maybeDoneIO("Geometries")
                        else: #import
                            self.importLatestAlembicFile(self.getExportedList())
                    else:
                        self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
                else:
                    self.notWorkedWellIO(self.dpUIinst.lang['e022_notLoadedPlugin']+"AbcExport")
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


    def getNodeToExportList(self, *args):
        """ Returns a list of the first children node in base groups.
        """
        geoList = []
        geoGrpList = ["supportGrp", "blendShapesGrp", "wipGrp", "fxGrp"]
        for geoGrp in geoGrpList:
            grp = self.utils.getNodeByMessage(geoGrp)
            if grp:
                itemList = cmds.listRelatives(grp, allDescendents=True, fullPath=True, noIntermediate=True, type="mesh") or []
                itemList.extend(cmds.listRelatives(grp, allDescendents=True, fullPath=True, noIntermediate=True, type="nurbsCurve") or []) #include curves to export hair guides
                if itemList:
                    geoList.extend([n for n in cmds.listRelatives(grp, children=True, type="transform") if not "dpID" in cmds.listAttr(n) and not self.utils.getSuffixNumberList(n)[1].endswith("Base")] or [])
        return geoList
