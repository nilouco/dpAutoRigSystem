# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "GeometryHistory"
TITLE = "v071_geometryHistory"
DESCRIPTION = "v072_geometryHistoryDesc"
WIKI = "07-‐-Validator#-geometry-history"



class GeometryHistory(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
    

    def runAction(self, first_mode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If first_mode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checked_items = node list of checked items
                - found_issues = True if an issue was found, False if there isn't an issue for the checked node
                - good_results = True if well done, False if we got an error
                - messages = reported text
        """
        # starting
        self.first_mode = first_mode
        self.cleanup_to_start()

        # ---
        # --- validator code --- beginning
        if not self.ar.utils.getAllGrp():
            if not self.ar.utils.getNetworkNodeByAttr("dpGuideNet"):
                if not cmds.file(query=True, reference=True):
                    ignoreTypeList = ["tweak", "file", "place2dTexture"]
                    if objList:
                        geoToCleanList = objList
                    else:
                        geoList = []
                        transformList = self.get_mesh_transforms()
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
                        self.ar.utils.setProgress(max=len(geoToCleanList), addOne=False, addNumber=False)
                        for geo in geoToCleanList:
                            self.ar.utils.setProgress(self.ar.data.lang[self.title])
                            if cmds.objExists(geo):
                                self.checked_items.append(geo)
                                self.found_issues.append(True)
                                if self.first_mode:
                                    self.good_results.append(False)
                                else: #fix
                                    try:
                                        # Delete history
                                        cmds.delete(geo, constructionHistory=True)
                                        self.good_results.append(True)
                                        self.messages.append(self.ar.data.lang['v004_fixed']+": "+geo)
                                    except:
                                        self.good_results.append(False)
                                        self.messages.append(self.ar.data.lang['v005_cantFix']+": "+geo)
                    else:
                        self.not_found_node()
                else:
                    self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
            else:
                self.fail_io(self.ar.data.lang['v100_cantExistsGuides'])
        else:
            self.fail_io(self.ar.data.lang['v099_cantExistsAllGrp'])
        # --- validator code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.end_progress()
        return self.log_data
