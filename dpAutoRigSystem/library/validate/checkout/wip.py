# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "Wip"
TITLE = "v009_wip"
DESCRIPTION = "v010_wipDesc"
WIKI = "07-‐-Validator#-wip-cleaner"



class Wip(action.BaseAction):
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
            wip_grp = None
            if inputs:
                wip_grp = inputs
            else:
                wip_grp = self.ar.utils.get_node_by_message("wipGrp")
                if not wip_grp:
                    if cmds.objExists("WIP_Grp"):
                        wip_grp = "WIP_Grp"
            if wip_grp:
                self.ar.ui_manager.set_progress(max=len(wip_grp), add_one=False, add_number=False)
                self.ar.ui_manager.set_progress(self.ar.data.lang[self.title])
                self.checked_items.append(wip_grp)
                children = cmds.listRelatives(wip_grp, allDescendents=True, children=True, fullPath=True)
                if children:
                    self.found_issues.append(True)
                    if self.first_mode:
                        self.good_results.append(False)
                    else: #fix    
                        try:
                            cmds.delete(children)
                            self.good_results.append(True)
                            self.messages.append(self.ar.data.lang['v004_fixed']+": "+wip_grp)
                        except:
                            self.good_results.append(False)
                            self.messages.append(self.ar.data.lang['v005_cantFix']+": "+wip_grp)
                else:
                    self.found_issues.append(False)
                    self.good_results.append(True)
            else:
                self.checked_items.append("")
                self.found_issues.append(False)
                self.good_results.append(True)
                self.messages.append(self.ar.data.lang['v011_notWIP'])
        else:
            self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.end_progress()
        return self.log_data
