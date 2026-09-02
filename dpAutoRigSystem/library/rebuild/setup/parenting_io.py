# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "ParentingIO"
TITLE = "r019_parentingIO"
DESCRIPTION = "r020_parentingIODesc"
WIKI = "10-‐-Rebuilder#-parenting"



class ParentingIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_parentingIO"
        self.start_name = "dpParenting"
    

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
                    if self.first_mode: #export
                        transforms = None
                        if inputs:
                            transforms = inputs
                        else:
                            transforms = cmds.ls(selection=False, long=True, type="transform")
                        if transforms:
                            self.ar.utils.set_progress(max=len(transforms), add_one=False, add_number=False)
                            # define data to export
                            parent_data = self.get_parenting_data(transforms)
                            parent_data.update(self.get_broken_id_data())
                            parent_data.update(self.get_model_data())
                            self.export_json_file(parent_data)
                        else:
                            self.maybe_done_io(self.ar.data.lang['v014_notFoundNodes'])
                    else: #import
                        parent_data = self.import_latest_json_file(self.get_exported_items())
                        if parent_data:
                            try:
                                if self.import_broken_id(parent_data):
                                    self.import_parenting_data(parent_data) #double run to first put broken nodes in place
                                self.import_parenting_data(parent_data)
                            except Exception as e:
                                self.fail_io(self.ar.data.lang['r032_notImportedData']+": "+str(e))
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


    def get_parenting_data(self, transforms=None):
        """ Return a filtered dictionary of parenting hierarchy of current scene nodes.
        """
        if not transforms:
            transforms = cmds.ls(selection=False, long=True, type="transform")
        filtered_items = self.ar.utils.filter_transforms(transforms, verbose=self.ar.data.verbose, title=self.ar.data.lang[self.title])
        filtered_items = self.reorder_list(filtered_items)
        return {"Parent" : filtered_items}


    def get_model_data(self, *args):
        """ Check if there's a model list to include in the dictionary data to avoid change parenting from them.
        """
        model_data = {}
        models = self.get_models_to_export()
        if models:
            model_data["ModelList"] = models
        return model_data


    def import_broken_id(self, parent_data):
        """ If there are broken nodes, we try to recreate them if needed.
            Return True if there are broken nodes.
        """
        if "BrokenID" in parent_data.keys():
            self.ar.utils.set_progress(max=len(parent_data["BrokenID"]), add_one=False, add_number=False)
            for node_type in parent_data["BrokenID"].keys():
                if node_type == "transform":
                    self.ar.utils.set_progress(self.ar.data.lang[self.title])
                    for item in parent_data["BrokenID"][node_type].keys():
                        if not cmds.objExists(item):
                            if not self.check_its_from_modeling(parent_data, node_type, item):
                                cmds.createNode(node_type, name=item)
                                if parent_data["BrokenID"][node_type][item]:
                                    if cmds.objExists(parent_data["BrokenID"][node_type][item]):
                                        cmds.parent(item, parent_data["BrokenID"][node_type][item])
                                cmds.select(clear=True)
            return True


    def import_parenting_data(self, parent_data):
        """ Import parenting data and put the nodes as the correct hierarchy if needed.
        """
        if not self.get_parenting_data()["Parent"] == parent_data["Parent"]:
            self.ar.utils.set_progress(max=len(parent_data["Parent"]), add_one=False, add_number=False)
            # define lists to check result
            well_imported_items = []
            parent_issues = []
            not_found_nodes = []
            model_changed_items = []
            # check parenting shaders
            for item in parent_data["Parent"]:
                self.ar.utils.set_progress(self.ar.data.lang[self.title])
                if not cmds.objExists(item):
                    parent_issues.append(item)
                    short_item = item[item.rfind("|")+1:]
                    if cmds.objExists(short_item):
                        if len(cmds.ls(short_item)) == 1:
                            if not self.check_its_from_modeling(parent_data, "transform", item):
                                # get father name
                                long_father_node = item[:item.rfind("|")]
                                short_father_node = long_father_node[long_father_node.rfind("|")+1:]
                                current_fathers = cmds.listRelatives(short_item, parent=True)
                                if cmds.objExists(long_father_node):
                                    # simple parent to existing old father node in the ancient hierarchy
                                    cmds.parent(short_item, long_father_node)
                                    well_imported_items.append(short_item)
                                elif current_fathers:
                                    if current_fathers[0] == short_father_node:
                                        # already child of the father node
                                        well_imported_items.append(short_item)
                                elif cmds.objExists(short_father_node):
                                    if len(cmds.ls(short_father_node)) == 1:
                                        # found unique father node in another hierarchy to parent
                                        cmds.parent(short_item, short_father_node)
                                        well_imported_items.append(short_item)
                                    else:
                                        self.fail_io(self.ar.data.lang['i075_moreOne']+" "+self.ar.data.lang['i076_sameName']+" "+short_father_node)
                            else: #root here
                                model_changed_items.append(item)
                        else:
                            self.fail_io(self.ar.data.lang['i075_moreOne']+" "+self.ar.data.lang['i076_sameName']+" "+short_item)
                    else:
                        if not self.check_its_from_modeling(parent_data, "transform", item):
                            model_changed_items.append(item)
                        else:
                            not_found_nodes.append(short_item)
            if parent_issues:
                if model_changed_items:
                    self.maybe_done_io(', '.join(model_changed_items))
                elif well_imported_items:
                    self.well_done_io(self.latest_data_file)
                else:
                    self.fail_io(self.ar.data.lang['v014_notFoundNodes']+": "+', '.join(not_found_nodes))
            else:
                self.well_done_io(self.latest_data_file)
        else:
            self.well_done_io(self.latest_data_file)


    def check_its_from_modeling(self, parent_data, node_type, item):
        """ Returns True if the item is from modeling.
        """
        if "ModelList" in parent_data.keys():
            for model_node in parent_data["ModelList"]:
                if "BrokenID" in parent_data.keys() and node_type in parent_data["BrokenID"].keys() and item in parent_data["BrokenID"][node_type].keys():
                    if model_node in parent_data["BrokenID"][node_type][item]:
                        return True
