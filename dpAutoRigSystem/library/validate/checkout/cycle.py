# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "Cycle"
TITLE = "v105_cycle"
DESCRIPTION = "v106_cycleDesc"
WIKI = "07-‐-Validator#-cycle-checker"



class Cycle(action.BaseAction):
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
            self.ar.utils.setProgress(max=1, add_one=False, add_number=False)
            self.ar.utils.setProgress(self.ar.data.lang[self.title])
            cycles = None
            if inputs:
                cycles = cmds.cycleCheck(inputs, list=True)
                self.checked_items.append(inputs)
            else:
                cycles = cmds.cycleCheck(all=False, list=True)
                if cycles:
                    self.checked_items.append("\n".join(cycles))
            if cycles:
                self.found_issues.append(True)
                if self.first_mode:
                    self.good_results.append(False)
                else: #fix = can't do it automatically, sorry
                    self.good_results.append(False)
                    self.messages.append(self.ar.data.lang['v005_cantFix']+": "+", ".join(cycles))
            else:
                self.found_issues.append(False)
                self.good_results.append(True)
        else:
            self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.end_progress()
        return self.log_data
