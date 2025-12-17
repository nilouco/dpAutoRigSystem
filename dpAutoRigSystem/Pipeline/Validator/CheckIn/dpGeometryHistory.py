# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "GeometryHistory"
TITLE = "v071_geometryHistory"
DESCRIPTION = "v072_geometryHistoryDesc"
ICON = "/Icons/dp_geometryHistory.png"
WIKI = "07-‐-Validator#-geometry-history"

DP_GEOMETRYHISTORY_VERSION = 1.06


class GeometryHistory(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_GEOMETRYHISTORY_VERSION
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
                    ignoreTypeList = ["tweak", "file", "place2dTexture"]
                    if objList:
                        geoToCleanList = objList
                    else:
                        geoList = []
                        transformList = self.getMeshTransformList()
                        if transformList:
                            for transform in transformList:
                                # Filter which geometry has deformer history and groupLevels to pass through sets and shader
                                historyList = cmds.listHistory(transform, pruneDagObjects=True, groupLevels=True)
                                if historyList:
                                    for history in historyList:
                                        # Pass through tweak and initialShading nodes
                                        if not cmds.nodeType(history) in ignoreTypeList: 
                                            if history != "initialShadingGroup":
                                                geoList.append(transform)
                        # Merge duplicated names
                        geoToCleanFullPathList = list(set(geoList))
                        # Get shortName to better reading in display log
                        geoToCleanList = cmds.ls(geoToCleanFullPathList, long=False)
                    if geoToCleanList:
                        self.utils.setProgress(max=len(geoToCleanList), addOne=False, addNumber=False)
                        for geo in geoToCleanList:
                            self.utils.setProgress(self.dpUIinst.lang[self.title])
                            if cmds.objExists(geo):
                                self.checkedObjList.append(geo)
                                self.foundIssueList.append(True)
                                if self.firstMode:
                                    self.resultOkList.append(False)
                                else: #fix
                                    try:
                                        # Delete history
                                        cmds.delete(geo, constructionHistory=True)
                                        self.resultOkList.append(True)
                                        self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+geo)
                                    except:
                                        self.resultOkList.append(False)
                                        self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+geo)
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
