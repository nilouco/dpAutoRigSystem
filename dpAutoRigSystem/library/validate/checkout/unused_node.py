# importing libraries:
from maya import cmds
from maya import mel
from ....library.base import action

# global variables to this module:
CLASS_NAME = "UnusedNode"
TITLE = "v084_unusedNode"
DESCRIPTION = "v085_unusedNodeDesc"
WIKI = "07-‐-Validator#-unused-node-cleaner"



class UnusedNode(action.BaseAction):
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
                check_items = cmds.ls(selection=False, materials=True)
            if check_items:
                if len(check_items) > 3: #discarding default materials
                    # getting data to analyse
                    default_materials = ['lambert1', 'standardSurface1', 'particleCloud1', 'openPBR_shader1']
                    all_materials = list(set(check_items) - set(default_materials))
                    used_materials = list(set(self.get_used_materials()) - set(default_materials))
                    # conditional to check here
                    if not len(all_materials) == len(used_materials):
                        self.ar.ui_manager.set_progress(max=len(all_materials), add_one=False, add_number=False)
                        self.ar.ui_manager.set_progress(self.ar.data.lang[self.title])
                        issue_materials = sorted(list(set(all_materials) - set(used_materials)))
                        self.checked_items.append(str(", ".join(issue_materials)))
                        self.found_issues.append(True)
                        if self.first_mode:
                            self.good_results.append(False)
                        else: #fix
                            try:
                                fix_result = mel.eval("MLdeleteUnused;")
                                self.good_results.append(True)
                                self.messages.append(self.ar.data.lang['v004_fixed']+": "+str(fix_result)+" nodes = "+str(len(issue_materials))+" materials")
                            except:
                                self.good_results.append(False)
                                self.messages.append(self.ar.data.lang['v005_cantFix']+": materials")
                else:
                    self.not_found_node()
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
