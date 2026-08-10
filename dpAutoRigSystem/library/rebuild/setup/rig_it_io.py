# importing libraries:
from ....library.base import action

# global variables to this module:
CLASS_NAME = "RigItIO"
TITLE = "r028_rigItIO"
DESCRIPTION = "r029_rigItIODesc"
WIKI = "10-‐-Rebuilder#-rig-it"



class RigItIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.start_name = "dpRigIt"
        self.first_bt_enable = False
        self.first_bt_custom_label = self.ar.data.lang['i305_none']
        self.second_bt_custom_label = self.ar.data.lang['i306_run']
        self.set_action_type("r000_rebuilder")
    

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
        if self.ar.pipeliner.check_asset_context():
            if self.first_mode: #export
                self.well_done_io(self.ar.data.lang['v007_allOk'])
            else: #import
                try:
                    self.ar.maker.rig_all()
                except Exception as e:
                    self.fail_io(str(e))
        else:
            self.fail_io(self.ar.data.lang['r027_noAssetContext'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.end_progress(True)
        self.refresh_view()
        return self.log_data
