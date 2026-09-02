# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "ControllersHierarchy"
TITLE = "v060_controllersHierarchy"
DESCRIPTION = "v061_controllerssHierarchyDesc"
WIKI = "07-‐-Validator#-controls-hierarchy"



class ControllersHierarchy(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.io_folder = "s_hierarchyIO"
        self.start_name = "dpHierarchy"


    def check_nurbs(self, transform):
        try:
            shapes = cmds.listRelatives(transform, shapes=True)
        except Exception as e:
            print(e)
            self.messages.append(f"{self.ar.data.lang['v070_duplicateName']} {transform}")
            return False
        if shapes:
            for shape in shapes:
                if "nurbsCurve" not in cmds.objectType(shape):
                    return False
        else:
            return False
        return True
    

    def find_nurbs_parent(self, node):
        parents = cmds.listRelatives(node, parent=True)
        while parents != None:
            for parent in parents:
                if self.check_nurbs(parent):
                    return parent
            parents = cmds.listRelatives(parents, parent=True)
        return None
    

    def add_to_tree(self, node, data):
        nurbs_parent = self.find_nurbs_parent(node)
        if nurbs_parent != None:
            if nurbs_parent in data:
                data[nurbs_parent].append(node)
            else:
                data[nurbs_parent] = [node]
        if node not in data:
            data[node] = []


    def raise_hierarchy(self, root_node):
        hierarchy_data = {}
        self.add_to_tree(root_node, hierarchy_data)
        transform_descendents = cmds.listRelatives(root_node, allDescendents=True, type="transform")
        if transform_descendents != None:
            for node in transform_descendents:
                if self.check_nurbs(node):
                    self.add_to_tree(node, hierarchy_data)
        return hierarchy_data
    

    def find_diff_in_hierarchy(self, diff, new_hierarchy):
        for list in new_hierarchy:
            if diff in new_hierarchy[list]:
                return list
        return None
    

    def check_hierarchy_change(self, original_hierarchy, new_hierarchy):
        # This data is in a way wich each key is the changed control and first value is a list in wich index 0 is the original Father and index 1 is the new Father. 
        hierarchy_change_ctrls_set = {}
        for key in original_hierarchy:
            if (key in new_hierarchy):
                if (original_hierarchy[key] != new_hierarchy[key]):
                    diff_set = set(original_hierarchy[key]) ^ set(new_hierarchy[key])
                    for diff in diff_set:
                        if diff in original_hierarchy[key]:
                            last_parent = key
                        else:
                            last_parent = self.find_diff_in_hierarchy(diff, original_hierarchy)
                        new_dad = self.find_diff_in_hierarchy(diff, new_hierarchy)
                        hierarchy_change_ctrls_set[diff] = [last_parent, new_dad]
        return hierarchy_change_ctrls_set
    

    def log_info(self, info_data):
        for ctrl in info_data:
            if info_data[ctrl][0] == None:
                self.messages.append(f"{ctrl} {self.ar.data.lang['v065_addedSonOf']} {info_data[ctrl][1]}")
            elif info_data[ctrl][1] == None:
                self.messages.append(f"{ctrl} {self.ar.data.lang['v066_wasRemoved']}")
            else:
                self.messages.append(f"{ctrl} {self.ar.data.lang['v067_changedParent']} {info_data[ctrl][0]}, new parent: {info_data[ctrl][1]}")


    def compare_hierarchy(self, original_hierarchy, new_hierarchy):
        if original_hierarchy != new_hierarchy:
            info_data = self.check_hierarchy_change(original_hierarchy, new_hierarchy)
            self.log_info(info_data)
            return False
        else:
            self.messages.append(self.ar.data.lang['v068_matchingHierarchies'])
            return True


    def run_action(self, first_mode=True, inputs=None, *args):
        """ Main method to process this validator instructions.
            It"s in verify mode by default.
            If first_mode parameter is False, it"ll run in fix mode.
            Returns dataLog with the validation result as:
                - checked_items = node list of checked items
                - found_issues = True if an issue was found, False if there isn"t an issue for the checked node
                - good_results = True if well done, False if we got an error
                - messages = reported text
        """
        # starting
        self.first_mode = first_mode
        self.cleanup_to_start()
        
        # ---
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            root_node = None
            global_ctrl = self.ar.utils.get_node_by_message("globalCtrl")
            # Verify if another Ctrl was sent via code to check hierarchy from.
            if inputs and cmds.objExists(inputs[0]) and self.check_nurbs(inputs[0]):
                root_node = inputs[0]
            elif cmds.objExists(global_ctrl) and self.check_nurbs(global_ctrl):
                root_node = global_ctrl
            else:
                self.checked_items.append(str(root_node))
                self.found_issues.append(False)
                self.good_results.append(True)
                self.messages.append(self.ar.data.lang['v062_globalMissing'])
            if root_node:
                is_hierarchy_same = True
                self.io_path = self.get_io_path(self.io_folder)
                if self.io_path:
                    current_file_hierarchy_data = self.raise_hierarchy(root_node)
                    last_hierarchy_data = self.import_latest_json_file(self.get_exported_items(get_any=True))
                    if last_hierarchy_data:
                        is_hierarchy_same = self.compare_hierarchy(last_hierarchy_data, current_file_hierarchy_data)
                        self.checked_items.append(str(last_hierarchy_data))
                    else:
                        self.checked_items.append("Controls Hierarchy")
                        self.messages.append(self.ar.data.lang['v063_firstHierarchy'])
                    if self.first_mode: #verify
                        if is_hierarchy_same:
                            self.found_issues.append(False)
                            self.good_results.append(True)
                        else:
                            self.found_issues.append(True)
                            self.good_results.append(False)
                    else: #fix
                        if cmds.file(query=True, sceneName=True) != "":
                            if last_hierarchy_data == None or not is_hierarchy_same:
                                self.export_json_file(current_file_hierarchy_data)
                            self.found_issues.append(False)
                            self.good_results.append(True)
                        else:
                            self.checked_items.append("Scene")
                            self.found_issues.append(True)
                            self.good_results.append(False)
                            self.messages.append(self.ar.data.lang['v005_cantFix']+" "+self.ar.data.lang['v064_hierarchy'])
                            self.messages.append(self.ar.data.lang['i201_saveScene'])
                    self.maybe_done = False
                else:
                    self.fail_io(self.ar.data.lang['r010_notFoundPath'])
            else:
                self.maybe_done = True
                self.not_found_node()
        else:
            self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.end_progress()
        return self.log_data
