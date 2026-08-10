# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "ConstraintIO"
TITLE = "r050_constraintIO"
DESCRIPTION = "r051_constraintIODesc"
WIKI = "10-‐-Rebuilder#-constraint"



class ConstraintIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_constraintIO"
        self.start_name = "dpConstraint"
    

    def runAction(self, first_mode=True, objList=None, *args):
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
                self.io_path = self.get_io_path(self.io_folder)
                if self.io_path:
                    constraintList = None
                    if objList:
                        constraintList = objList
                    else:
                        constraintList = cmds.ls(selection=False, type=self.constraint_types)
                    if self.first_mode: #export
                        if constraintList:
                            self.export_json_file(self.get_constraint_data(constraintList))
                        else:
                            self.maybe_done_io("Constraints")
                    else: #import
                        constDic = self.import_latest_json_file(self.get_exported_items())
                        if constDic:
                            self.import_constraint_data(constDic)
                        else:
                            self.maybe_done_io(self.ar.data.lang['r007_notExportedData'])
                else:
                    self.fail_io(self.ar.data.lang['r010_notFoundPath'])
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
