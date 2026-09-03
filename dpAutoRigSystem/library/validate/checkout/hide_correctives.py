# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "HideCorrectives"
TITLE = "v036_hideCorrectives"
DESCRIPTION = "v037_hideCorrectivesDesc"
WIKI = "07-‐-Validator#-hide-correctives"



class HideCorrectives(action.BaseAction):
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
            option_ctrl = self.ar.utils.get_node_by_message("optionCtrl")
            if option_ctrl:
                if inputs:
                    check_items = cmds.attributeQuery('correctiveCtrls', node=inputs[0], exists=True)
                else:
                    check_items = cmds.attributeQuery('correctiveCtrls', node=option_ctrl, exists=True)
                if check_items:
                    self.ar.utils.set_progress(max=1)
                    self.ar.utils.set_progress(self.ar.data.lang[self.title])
                    item = option_ctrl+".correctiveCtrls"
                    # conditional to check here
                    check_channel_box = cmds.getAttr(item, channelBox=True)
                    if check_channel_box:
                        self.checked_items.append(item)
                        self.found_issues.append(True)
                        if self.first_mode:
                            self.good_results.append(False)
                        else: #fix
                            try:
                                cmds.setAttr(item, 0)
                                cmds.setAttr(item, lock=True, channelBox=False)
                                self.good_results.append(True)
                                self.messages.append(self.ar.data.lang['v004_fixed']+": "+item)
                            except:
                                self.good_results.append(False)
                                self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item)
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
