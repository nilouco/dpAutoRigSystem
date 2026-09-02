# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "ExitEditMode"
TITLE = "v034_exitEditMode"
DESCRIPTION = "v035_exitEditModeDesc"
WIKI = "07-‐-Validator#-exit-edit-mode"



class ExitEditMode(action.BaseAction):
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
                check_items = self.ar.ctrls.get_controllers()
            if check_items:
                self.ar.utils.set_progress(max=len(check_items), add_one=False, add_number=False)
                for item in check_items:
                    self.ar.utils.set_progress(self.ar.data.lang[self.title])
                    # conditional to check here
                    if "editMode" in cmds.listAttr(item):
                        if cmds.getAttr(item+".editMode") == 1:
                            self.checked_items.append(item)
                            self.found_issues.append(True)
                            if self.first_mode:
                                self.good_results.append(False)
                            else: #fix
                                try:
                                    # delete the corrective script job
                                    self.ar.job.delete_old_job(item)
                                    # remove color override
                                    shapes = cmds.listRelatives(item, shapes=True, children=True, fullPath=True)
                                    if shapes:
                                        for shape in shapes:
                                            cmds.setAttr(shape+".overrideRGBColors", 0)
                                    # set edit mode off
                                    cmds.setAttr(item+".editMode", 0)
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
