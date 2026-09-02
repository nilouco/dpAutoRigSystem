# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "RenameIO"
TITLE = "r056_renameIO"
DESCRIPTION = "r057_renameIODesc"
WIKI = "10-‐-Rebuilder#-rename"



class RenameIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_renameIO"
        self.start_name = "dpRename"
    

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
                    items = None
                    if inputs:
                        items = inputs
                    else:
                        items = [n for n in cmds.ls(selection=False, noIntermediate=True) if cmds.attributeQuery(self.ar.data.dp_id, node=n, exists=True)]
                    if items:
                        if self.first_mode: #export
                            self.export_json_file(self.get_node_id_data(items))
                        else: #import
                            node_id_data = self.import_latest_json_file(self.get_exported_items())
                            if node_id_data:
                                self.import_node_id_data(node_id_data)
                            else:
                                self.maybe_done_io(self.ar.data.lang['r007_notExportedData'])
                    else:
                        self.fail_io("Ctrls_Grp")
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


    def get_node_id_data(self, items):
        """ Processes the given item list to collect and mount the dpID attribute dictionary.
            Returns the dictionary to export.
        """
        data = {}
        self.ar.utils.set_progress(max=len(items), add_one=False, add_number=False)
        for item in items:
            self.ar.utils.set_progress(self.ar.data.lang[self.title])
            if cmds.objExists(item):
                data[item] = cmds.getAttr(item+"."+self.ar.data.dp_id)
        return data


    def import_node_id_data(self, node_id_data):
        """ Import data from exported dictionary.
            Check if nodes exist in the scene, otherwise try to find in the dpID if it was probably renamed.
        """
        self.ar.utils.set_progress(max=len(node_id_data.keys()), add_one=False, add_number=False)
        # define lists to check result
        well_imported_items = []
        not_found_nodes = []
        maybe_items = []
        for item in node_id_data.keys():
            self.ar.utils.set_progress(self.ar.data.lang[self.title])
            # check item
            if not cmds.objExists(item):
                old_id_data = self.ar.utils.get_decomposed_ids(node_id_data[item])
                if old_id_data:
                    if cmds.objExists(old_id_data[1]):
                        cmds.rename(old_id_data[1], item)
                        well_imported_items.append(item)
                    elif item.endswith("Shape"):
                        maybe_items.append(item)
                    else:
                        not_found_nodes.append(item)
        if well_imported_items:
            self.well_done_io(self.latest_data_file)
        elif not_found_nodes:
            self.fail_io(self.ar.data.lang['v014_notFoundNodes']+": "+', '.join(not_found_nodes))
        elif maybe_items:
            self.maybe_done_io(self.ar.data.lang['r066_shapeToReplace']+" "+', '.join(maybe_items))
        else:
            self.maybe_done_io(self.ar.data.lang['r032_notImportedData'])
