# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "CalibrationIO"
TITLE = "r041_calibrationIO"
DESCRIPTION = "r042_calibrationIODesc"
WIKI = "10-‐-Rebuilder#-calibration"



class CalibrationIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_calibrationIO"
        self.start_name = "dpCalibration"
    

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
                        if self.first_mode: #export
                            self.export_json_file(self.get_calibration_data(controllers))
                        else: #import
                            calibration_data = self.import_latest_json_file(self.get_exported_items())
                            if calibration_data:
                                self.import_calibration_data(calibration_data)
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


    def get_calibration_data(self, controllers):
        """ Processes the given controller list to collect and mount the calibration data.
            Returns the dictionary to export.
        """
        data = {}
        self.ar.utils.setProgress(max=len(controllers), add_one=False, add_number=False)
        for ctrl in controllers:
            self.ar.utils.setProgress(self.ar.data.lang[self.title])
            calibrations = self.ar.ctrls.get_items_from_string_attr(ctrl)
            if calibrations:
                data[ctrl] = {}
                for attr in calibrations:
                    data[ctrl][attr] = cmds.getAttr(ctrl+"."+attr)
        return data


    def import_calibration_data(self, calibration_data):
        """ Import the calibration setup from the given calibration data dictionary.
        """
        self.ar.utils.setProgress(max=len(calibration_data.keys()), add_one=False, add_number=False)
        # define lists to check result
        well_imported_items = []
        for item in calibration_data.keys():
            self.ar.utils.setProgress(self.ar.data.lang[self.title])
            not_found_nodes = []
            # check transformations
            if not cmds.objExists(item):
                item = item[item.rfind("|")+1:] #short name (after last "|")
            if cmds.objExists(item):
                for attr in calibration_data[item].keys():
                    if not cmds.listConnections(item+"."+attr, destination=False, source=True):
                        # unlock attribute
                        was_locked = cmds.getAttr(item+"."+attr, lock=True)
                        cmds.setAttr(item+"."+attr, lock=False)
                        try:
                            # set calibration value
                            cmds.setAttr(item+"."+attr, calibration_data[item][attr])
                            # lock attribute again if it was locked
                            cmds.setAttr(item+"."+attr, lock=was_locked)
                            if not item in well_imported_items:
                                well_imported_items.append(item)
                        except Exception as e:
                            self.fail_io(item+" - "+str(e))
            else:
                not_found_nodes.append(item)
        if well_imported_items:
            self.well_done_io(self.latest_data_file)
        else:
            self.fail_io(self.ar.data.lang['v014_notFoundNodes']+": "+', '.join(not_found_nodes))
