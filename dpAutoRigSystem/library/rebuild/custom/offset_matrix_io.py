# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "OffsetMatrixIO"
TITLE = "r061_offsetMatrixIO"
DESCRIPTION = "r062_offsetMatrixIODesc"
WIKI = "10-‐-Rebuilder#-offset-matrix"



class OffsetMatrixIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_offsetMatrixIO"
        self.start_name = "dpOffsetMatrix"
        self.offset_matrix_attr = "offsetParentMatrix"
    

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
                    nodes = None
                    if inputs:
                        nodes = inputs
                    else:
                        nodes = cmds.ls(selection=False, type="transform")
                    if nodes:
                        if self.first_mode: #export
                            to_export_data = self.get_offset_matrix_data(nodes)
                            self.export_json_file(to_export_data)
                        else: #import
                            to_import_data = self.import_latest_json_file(self.get_exported_items())
                            if to_import_data:
                                self.import_offset_matrix_data(to_import_data)
                            else:
                                self.maybe_done_io(self.ar.data.lang['r007_notExportedData'])
                    else:
                        self.maybe_done_io(self.ar.data.lang['v014_notFoundNodes'])
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


    def get_offset_matrix_data(self, items):
        """ Processes the given list to collect the info about their parent offset matrix connections to rebuild.
            Returns a dictionary to export.
        """
        data = {}
        self.ar.utils.setProgress(max=len(items), add_one=False, add_number=False)
        for item in items:
            self.ar.utils.setProgress(self.ar.data.lang[self.title])
            if cmds.objExists(item):
                in_plugs = cmds.listConnections(item+"."+self.offset_matrix_attr, source=True, destination=False, plugs=True)
                if in_plugs:
                    data[item] = in_plugs[0]
        return data


    def import_offset_matrix_data(self, connection_data):
        """ Import connection data.
            Check if need to create an unitConversion node and set its conversionFactor value.
            Only redo the connection if it doesn't exists yet.
        """
        self.ar.utils.setProgress(max=len(connection_data.keys()), add_one=False, add_number=False)
        # define lists to check result
        well_imported_items = []
        for item in connection_data.keys():
            not_found_nodes = []
            self.ar.utils.setProgress(self.ar.data.lang[self.title])
            if cmds.objExists(item):
                om_attr = item+"."+self.offset_matrix_attr
                if not cmds.listConnections(om_attr, plugs=True, source=True, destination=False):
                    is_locked = cmds.getAttr(om_attr, lock=True)
                    cmds.setAttr(om_attr, lock=False)
                    cmds.connectAttr(connection_data[item]+"[0]", om_attr, force=True)
                    if is_locked:
                        cmds.setAttr(om_attr, lock=True)
                if not item in well_imported_items:
                    well_imported_items.append(item)
            else:
                not_found_nodes.append(item+"."+self.offset_matrix_attr)
        if not_found_nodes:
            self.fail_io(self.ar.data.lang['v014_notFoundNodes']+": "+', '.join(not_found_nodes))
        elif well_imported_items:
            self.well_done_io(self.latest_data_file)
