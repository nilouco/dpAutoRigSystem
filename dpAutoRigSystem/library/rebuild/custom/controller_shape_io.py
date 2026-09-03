# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "ControllerShapeIO"
TITLE = "r014_controllerShapeIO"
DESCRIPTION = "r015_controllerShapeIODesc"
WIKI = "10-‐-Rebuilder#-controller-shape"



class ControllerShapeIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_controlShapeIO"
        self.start_name = "dpControlShape"
    

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
                self.io_path = self.get_io_path(self.io_folder)
                if self.io_path:
                    controllers = None
                    if inputs:
                        controllers = inputs
                    else:
                        controllers = self.ar.ctrls.get_controllers()
                    if controllers:
                        self.ar.ui_manager.set_progress(max=len(controllers), add_one=False, add_number=False)
                        if self.first_mode: #export
                            try:
                                self.ar.pipeliner.make_dir_if_not_exists(self.io_path)
                                ctrl_filename = self.io_path+"/"+self.start_name+"_"+self.ar.pipeliner.pipe_data['currentFileName']+".ma"
                                self.ar.ctrls.export_shape(controllers, ctrl_filename, ui=False, verbose=True)
                                self.well_done_io(ctrl_filename)
                            except Exception as e:
                                self.fail_io(', '.join(controllers)+": "+str(e))
                        else: #import
                            exported_items = self.get_exported_items()
                            if exported_items:
                                try:
                                    exported_items.sort()
                                    to_import_ctrls = self.io_path+"/"+exported_items[-1]
                                    self.ar.ctrls.import_shape(controllers, to_import_ctrls, ui=False, verbose=True)
                                    self.well_done_io(exported_items[-1])
                                except Exception as e:
                                    self.fail_io(exported_items[-1]+": "+str(e))
                            else:
                                self.maybe_done_io(self.ar.data.lang['r007_notExportedData'])
                    else:
                        self.maybe_done_io("Ctrls_Grp")
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
