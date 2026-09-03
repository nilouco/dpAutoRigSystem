# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "TweakNode"
TITLE = "v130_tweakNode"
DESCRIPTION = "v131_tweakNodeDesc"
WIKI = "07-‐-Validator#-tweak-node-cleaner"



class TweakNode(action.BaseAction):
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
                check_items = cmds.ls(inputs, type='tweak')
            else:
                check_items = cmds.ls(selection=False, type='tweak') #tweakNodes
            if check_items:
                self.ar.utils.set_progress(max=len(check_items), add_one=False, add_number=False)
                for item in check_items:
                    self.ar.utils.set_progress(self.ar.data.lang[self.title])
                    # check for edited control shape
                    if not self.check_edited_control_points(item):
                        self.checked_items.append(item)
                        self.found_issues.append(True)
                        if self.first_mode:
                            self.good_results.append(False)
                        else: #fix
                            try:
                                if cmds.objExists(item):
                                    cmds.lockNode(item, lock=False)
                                    cmds.delete(item)
                                cmds.select(clear=True)
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


    def check_edited_control_points(self, item):
        """ Check if there are edited control point in the given tweak node and return them.
        """
        if cmds.objExists(item):
            p_items = cmds.getAttr(item+".plist", multiIndices=True)
            if p_items:
                for idx in p_items:
                    cp_items = cmds.getAttr(item+".plist["+str(idx)+"].controlPoints", multiIndices=True)
                    if cp_items:
                        for cp in cp_items:
                            if not cmds.getAttr(item+".plist["+str(idx)+"].controlPoints["+str(cp)+"]") == [0.0, 0.0, 0.0]:
                                return True
