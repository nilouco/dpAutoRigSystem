# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "BindPose"
TITLE = "v113_bindPose"
DESCRIPTION = "v114_bindPoseDesc"
WIKI = "07-‐-Validator#-bindpose-cleaner"



class BindPose(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
    

    def runAction(self, first_mode=True, objList=None, *args):
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
        self.bindPoseName = "dpAR_BP"
        
        # ---
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            if objList:
                check_items = cmds.ls(objList, type="dagPose")
            else:
                check_items = cmds.ls(selection=False, type="dagPose") #bindPose nodes
            if check_items:
                self.ar.utils.setProgress(max=len(check_items), addOne=False, addNumber=False)
                # conditional to check here
                if len(check_items) > 1:
                    self.ar.utils.setProgress(self.ar.data.lang[self.title])
                    self.checked_items.append(", ".join(check_items))
                    self.found_issues.append(True)
                    if self.first_mode:
                        self.good_results.append(False)
                    else: #fix
                        try:
                            for item in check_items:
                                cmds.lockNode(item, lock=False)
                                cmds.delete(item)
                            jntList = self.ar.skin.getSkinnedJointList()
                            if jntList:
                                cmds.dagPose(jntList, save=True, bindPose=True, name=self.bindPoseName)
                            self.good_results.append(True)
                            self.messages.append(self.ar.data.lang['v004_fixed']+": "+self.bindPoseName)
                        except:
                            self.good_results.append(False)
                            self.messages.append(self.ar.data.lang['v005_cantFix']+": "+", ".join(check_items))
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
