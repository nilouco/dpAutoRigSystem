# importing libraries:
from maya import cmds
from collections import defaultdict
from ....library.base import action

# global variables to this module:
CLASS_NAME = "DuplicatedName"
TITLE = "v024_duplicatedName"
DESCRIPTION = "v025_duplicatedNameDesc"
WIKI = "07-‐-Validator#-duplicated-name"



class DuplicatedName(action.BaseAction):
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
                check_items = inputs
            else:
                check_items = cmds.ls(dag=True, long=True)
            if check_items:
                self.ar.ui_manager.set_progress(max=len(check_items), add_one=False, add_number=False)
                # Dictionary {shortName: [Full paths]}
                names = defaultdict(list)
                for item in check_items:
                    short = item.split("|")[-1]
                    names[short].append(item)
                # Filter only duplicates
                duplicates = {k:v for k,v in names.items() if len(v) > 1}
                if duplicates:
                    for name, paths in duplicates.items():
                        self.ar.ui_manager.set_progress(self.ar.data.lang[self.title])
                        # found issue here
                        self.checked_items.append(name)
                        self.found_issues.append(True)
                        if self.first_mode:
                            self.good_results.append(False)
                        else: #fix
                            try:
                                for p, path in enumerate(paths):
                                    if p == 0:
                                        continue
                                    if cmds.objExists(path):
                                        for i in range(1, len(paths)+1):
                                            if not cmds.objExists(name+"_"+str(i)):
                                                self.rename_node_and_children(path, i)
                                    self.good_results.append(True)
                                    self.messages.append(self.ar.data.lang['v004_fixed']+": "+name)
                            except:
                                self.good_results.append(False)
                                self.messages.append(self.ar.data.lang['v005_cantFix']+": "+name)
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


    def rename_node_and_children(self, item, i):
        """ Rename the given item node and it's children with the given number as suffix.
        """
        if cmds.objExists(item):
            if cmds.objectType(item) == "transform":
                children = cmds.listRelatives(item, allDescendents=True, children=True, fullPath=True, type="transform")
                if children:
                    children = self.reorder_list(children)
                    for child in children:
                        if cmds.objExists(child):
                            cmds.rename(child, child[child.rfind("|")+1:]+"_"+str(i))
                cmds.rename(item, item[item.rfind("|")+1:]+"_"+str(i))
            return True
