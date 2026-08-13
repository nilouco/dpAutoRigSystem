# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "SupportNodeIO"
TITLE = "r023_supportNodeIO"
DESCRIPTION = "r024_supportNodeIODesc"
WIKI = "10-‐-Rebuilder#-support-node"



class SupportNodeIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_supportNodeIO"
        self.start_name = "dpSupportNode"
    

    def run_action(self, first_mode=True, inputs=None, *args):
        """ Main method to process this validator instructions.
            It's in export mode by default.
            If first_mode parameter is False, it'll run in import mode.
            Returns dataLog with the validation result as:
                - checked_items = node list of checked items
                - found_issues = True if an issue was found, False if there isn't an issue for the checked node
                - good_results = True if well done, False if we got an error
                - messages = reported text
        """
        # starting
        self.first_mode = first_mode
        self.cleanup_to_start(True)
        
        # ---
        # --- rebuilder code --- beginning
        if not cmds.file(query=True, reference=True):
            if self.ar.pipeliner.check_asset_context():
                # load alembic plugin
                if self.ar.utils.checkLoadedPlugin("AbcExport") and self.ar.utils.checkLoadedPlugin("AbcImport"):
                    self.io_path = self.get_io_path(self.io_folder)
                    if self.io_path:
                        if self.first_mode: #export
                            items = None
                            if inputs:
                                items = inputs
                            else:
                                items = self.getNodeToExportList()
                            if items:
                                self.ar.utils.setProgress(self.ar.data.lang[self.title], add_one=False, add_number=False)
                                self.export_alembic_file(items, attr=False, curve=True)
                            else:
                                self.maybe_done_io("Geometries")
                        else: #import
                            self.import_latest_alembic_file(self.get_exported_items())
                    else:
                        self.fail_io(self.ar.data.lang['r010_notFoundPath'])
                else:
                    self.fail_io(self.ar.data.lang['e018_notLoadedPlugin']+"AbcExport")
            else:
                self.fail_io(self.ar.data.lang['r027_noAssetContext'])
        else:
            self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.end_progress()
        self.refresh_view()
        return self.log_data


    def getNodeToExportList(self, *args):
        """ Returns a list of the first children node in base groups.
        """
        geoList = []
        geoGrpList = ["supportGrp", "blendShapesGrp", "wipGrp", "fxGrp"]
        for geoGrp in geoGrpList:
            grp = self.ar.utils.getNodeByMessage(geoGrp)
            if grp:
                items = cmds.listRelatives(grp, allDescendents=True, fullPath=True, noIntermediate=True, type="mesh") or []
                items.extend(cmds.listRelatives(grp, allDescendents=True, fullPath=True, noIntermediate=True, type="nurbsCurve") or []) #include curves to export hair guides
                if items:
                    geoList.extend([n for n in cmds.listRelatives(grp, children=True, type="transform") if not "dpID" in cmds.listAttr(n) and not self.ar.utils.getSuffixNumberList(n)[1].endswith("Base")] or [])
        if cmds.objExists("Zipper_Curves_Grp"):
            geoList.extend(cmds.listRelatives("Zipper_Curves_Grp", children=True))
        return geoList
