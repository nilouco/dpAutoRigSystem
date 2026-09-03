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
    

    def run_action(self, first_mode=True, inputs=None, *args):
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
        if not self.ar.utils.get_all_grp():
            if not self.ar.utils.get_network_by_attr("dpGuideNet"):
                if not cmds.file(query=True, reference=True):
                    ignore_types = ["tweak", "file", "place2dTexture"]
                    if inputs:
                        to_clean_geos = inputs
                    else:
                        geos = []
                        transforms = self.get_mesh_transforms()
                        if transforms:
                            for transform in transforms:
                                # Filter which geometry has deformer history and groupLevels to pass through sets and shader
                                histories = cmds.listHistory(transform, pruneDagObjects=True, groupLevels=True)
                                if histories:
                                    for history in histories:
                                        # Pass through tweak and initialShading nodes
                                        if not cmds.nodeType(history) in ignore_types: 
                                            if history != "initialShadingGroup":
                                                geos.append(transform)
                        # Merge duplicated names
                        to_clean_geo_fullpaths = list(set(geos))
                        # Get shortName to better reading in display log
                        to_clean_geos = cmds.ls(to_clean_geo_fullpaths, long=False)
                    if to_clean_geos:
                        self.ar.ui_manager.set_progress(max=len(to_clean_geos), add_one=False, add_number=False)
                        for geo in to_clean_geos:
                            self.ar.ui_manager.set_progress(self.ar.data.lang[self.title])
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
