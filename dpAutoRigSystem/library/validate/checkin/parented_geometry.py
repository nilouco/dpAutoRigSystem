# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "ParentedGeometry"
TITLE = "v140_parentedGeometry"
DESCRIPTION = "v141_parentedGeometryDesc"
WIKI = "07-‐-Validator#-parented-geometry"



class ParentedGeometry(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
    

    def run_action(self, first_mode=True, inputs=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If first_mode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checked_items = node list of checked items
                - found_issues = True if an issue was found, False if there isn't an issue for the checked node
                - good_results = True if well done, False if we got an error
                - messages = reported text
        """
        # starting
        self.first_mode = first_mode
        self.cleanup_to_start()
        
        # ---
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            if inputs:
                check_items = cmds.ls(inputs, type="mesh")
            else:
                check_items = cmds.ls(selection=False, type="mesh") #all meshes in the scene
            if check_items:
                mesh_transforms = self.get_mesh_transforms(check_items)
                if mesh_transforms:
                    mesh_transforms = self.reorder_list(mesh_transforms)
                    self.ar.ui_manager.set_progress(max=len(mesh_transforms), add_one=False, add_number=False)
                    # avoid reporting the same item multiple times
                    for mesh in mesh_transforms:
                        self.ar.ui_manager.set_progress(self.ar.data.lang[self.title])
                        # check if exists to avoid missing nodes
                        if cmds.objExists(mesh):
                            all_children = cmds.listRelatives(mesh, allDescendents=True, fullPath=True, type='transform') or []
                            # get all descendents and check if it's different than its parent
                            children = self.ar.utils.filter_transforms([d for d in all_children if cmds.objExists(d) and d != mesh])
                            if children:
                                for item in children:
                                    if not self.ar.naming.get_short_name(item, False) in self.checked_items:
                                        self.checked_items.append(self.ar.naming.get_short_name(item, False)) # get only the last part of the path
                                        self.found_issues.append(True)
                                    if self.first_mode:
                                        self.good_results.append(False)
                                    else: #fix
                                        try:
                                            grand_parents = cmds.listRelatives(mesh, parent=True, fullPath=True)
                                            if grand_parents and cmds.objExists(grand_parents[0]):
                                                # try to parent the item to the mesh grandparent
                                                if cmds.objExists(item):
                                                    cmds.parent(item, grand_parents[0])
                                            else: 
                                                # if no parent, just unparent it to world
                                                cmds.parent(item, world=True)
                                            self.good_results.append(True)
                                            self.messages.append(self.ar.data.lang['v004_fixed']+": "+item)
                                        except:
                                            self.good_results.append(False)
                                            self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item)
            else:
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
