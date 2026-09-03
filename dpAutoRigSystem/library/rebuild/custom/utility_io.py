# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "UtilityIO"
TITLE = "r054_utilityIO"
DESCRIPTION = "r055_utilityIODesc"
WIKI = "10-‐-Rebuilder#-utility"



class UtilityIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_utilityIO"
        self.start_name = "dpUtility"
    

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
                    utilities = None
                    if inputs:
                        utilities = inputs
                    else:
                        utilities = cmds.ls(selection=False, type=self.ar.utils.utility_types)
                    if self.first_mode: #export
                        if utilities:
                            self.export_json_file(self.get_utility_data(utilities))
                        else:
                            self.maybe_done_io("Utility nodes.")
                    else: #import
                        utility_data = self.import_latest_json_file(self.get_exported_items())
                        if utility_data:
                            self.import_utility_data(utility_data)
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


    def get_utility_data(self, utilities):
        """ Processes the given utility list to collect and mount the info data.
            Returns the dictionary to export.
        """
        data = {}
        self.ar.ui_manager.set_progress(max=len(utilities), add_one=False, add_number=False)
        for item in utilities:
            self.ar.ui_manager.set_progress(self.ar.data.lang[self.title])
            if not cmds.attributeQuery(self.ar.data.dp_id, node=item, exists=True) or not self.ar.utils.validate_id(item):
                # getting attributes values
                node_type = cmds.objectType(item)
                data[item] = {"attributes" : {},
                                "type"       : node_type,
                                "name"       : item
                            }
                for attr in self.ar.utils.type_attr_data[node_type]:
                    if cmds.attributeQuery(attr, node=item, exists=True):
                        data[item]["attributes"][attr] = cmds.getAttr(item+"."+attr)
                # compound attributes
                if node_type in self.ar.utils.type_multi_attr_data.keys():
                    for multi_attr in self.ar.utils.type_multi_attr_data[node_type].keys():
                        indexes = cmds.getAttr(item+"."+multi_attr, multiIndices=True)
                        if indexes:
                            dot = ""
                            attributes = [""]
                            if self.ar.utils.type_multi_attr_data[node_type][multi_attr]:
                                dot = "."
                                attributes = self.ar.utils.type_multi_attr_data[node_type][multi_attr]
                            for i in indexes:
                                for attr in attributes:
                                    attr_name = multi_attr+"["+str(i)+"]"+dot+attr
                                    attr_value = cmds.getAttr(item+"."+attr_name)
                                    data[item]["attributes"][attr_name] = attr_value
                                    if isinstance(attr_value, list):
                                        data[item]["attributes"][attr_name] = attr_value[0]
        return data


    def import_utility_data(self, utility_data):
        """ Import utility nodes from exported dictionary.
            Create missing utility nodes and set them values if they don't exists.
        """
        self.ar.ui_manager.set_progress(max=len(utility_data.keys()), add_one=False, add_number=False)
        # define lists to check result
        well_imported_items = []
        for item in utility_data.keys():
            existing_nodes = []
            self.ar.ui_manager.set_progress(self.ar.data.lang[self.title])
            # create utility node if it needs
            if not cmds.objExists(item):
                cmds.createNode(utility_data[item]["type"], name=utility_data[item]["name"])
                # set attribute values
                if utility_data[item]["attributes"]:
                    for attr in utility_data[item]["attributes"].keys():
                        #if isinstance(attr, list): 
                        if str(utility_data[item]["attributes"][attr]).count(",") > 1: #support vector attributes like color_Color
                            cmds.setAttr(item+"."+attr, utility_data[item]["attributes"][attr][0], utility_data[item]["attributes"][attr][1], utility_data[item]["attributes"][attr][2], type="double3")
                        else:
                            cmds.setAttr(item+"."+attr, utility_data[item]["attributes"][attr])
                well_imported_items.append(item)
            else:
                existing_nodes.append(item)
        if well_imported_items:
            self.well_done_io(self.latest_data_file)
        else:
            if existing_nodes:
                self.well_done_io(self.ar.data.lang['r032_notImportedData'])
            else:
                self.fail_io(self.ar.data.lang['v014_notFoundNodes']+": "+', '.join(existing_nodes))
