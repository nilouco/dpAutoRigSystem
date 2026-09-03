# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "EmptyTransform"
TITLE = "v138_emptyTransform"
DESCRIPTION = "v139_emptyTransformDesc"
WIKI = "07-‐-Validator#-empty-transform-cleaner"



class EmptyTransform(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.keep_attr = 'dpKeepIt'
    

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
                check_items = inputs
            else:
                check_items = cmds.ls(selection=False, long=True, type="transform") #list all transforms in the scene
            if check_items:
                self.ar.ui_manager.set_progress(max=len(check_items), add_one=False, add_number=False)
                empty_transforms = self.filter_empty_transforms(check_items)
                empty_transforms.extend(self.filter_empty_transforms(self.get_ignore_connected(), True))
                # conditional to check here
                if empty_transforms:
                    for item in empty_transforms:
                        self.ar.ui_manager.set_progress(self.ar.data.lang[self.title])
                        self.checked_items.append(self.ar.naming.get_short_name(item, False))
                        self.found_issues.append(True)
                        if self.first_mode:
                            self.good_results.append(False)
                        else: #fix
                            try:
                                if self.keep_attr in cmds.listAttr(item) and cmds.getAttr(item+"."+self.keep_attr) == True:
                                    pass
                                else:
                                    cmds.lockNode(item, lock=False)
                                    cmds.delete(item)
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
    
    
    def filter_empty_transforms(self, transforms=None, connected=False, *args):
        """ Filter the transform list to remove those without children or connections.
            Returns a list of transforms that are empty.
        """
        filtered_items = self.ar.utils.filter_transforms(transforms, verbose=self.ar.data.verbose, title=self.ar.data.lang[self.title])
        filtered_items = self.reorder_list(filtered_items)
        empty_transforms = []
        for transform in filtered_items:
            if connected:
                has_connection = False
            else:
                has_connection = cmds.listConnections(transform)
                if has_connection:
                    node_graphs = cmds.listConnections(transform, type="nodeGraphEditorInfo") or []
                    has_connection = set(has_connection)-set(node_graphs)
            if not has_connection:
                children = cmds.listRelatives(transform, children=True, fullPath=True)
                if not children:
                    empty_transforms.append(transform)
                elif len(list(set(children).intersection(empty_transforms))) == len(children):
                    empty_transforms.append(transform)
        return empty_transforms
    

    def get_ignore_connected(self, *args):
        """ Ignore dpAr default nodes
        """
        ignored_items = ["supportGrp", "renderGrp", "proxyGrp", "fxGrp", "blendShapesGrp", "wipGrp"]
        nodes = []
        for item in ignored_items:
            got_node = self.ar.utils.get_node_by_message(item)
            if got_node:
                nodes.append(got_node)
        return nodes
    