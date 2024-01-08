# importing libraries:
from maya import cmds
from ... import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "GeometryHistory"
TITLE = "v071_geometryHistory"
DESCRIPTION = "v072_geometryHistoryDesc"
ICON = "/Icons/dp_geometryHistory.png"

DP_GEOMETRYHISTORY_VERSION = 1.3


class GeometryHistory(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_GEOMETRYHISTORY_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
    

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
        ignoreTypeList = ["tweak", "file", "place2dTexture"]
        if objList:
            geoToCleanList = objList
        else:
            shapeList = cmds.ls(selection=False, type='mesh')
            geoList = []
            if shapeList:
                # Get only transform nodes
                transformList = list(set(cmds.listRelatives(shapeList, type="transform", parent=True, fullPath=True)))
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
            for geo in geoToCleanList:
                if cmds.objExists(geo):
                    progressAmount = 0
                    maxProcess = len(geoToCleanList)
                    if self.verbose:
                    # Update progress window
                        progressAmount += 1
                        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
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
        # --- validator code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        return self.dataLogDic
