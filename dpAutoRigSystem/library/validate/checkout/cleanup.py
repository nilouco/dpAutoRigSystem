# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "Cleanup"
TITLE = "v096_cleanup"
DESCRIPTION = "v097_cleanupDesc"
WIKI = "07-‐-Validator#-cleanup"



class Cleanup(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.cleanupAttr = "dpDeleteIt"
    

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
        
        # ---
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            if objList:
                toCheckList = objList
            else:
                toCheckList = cmds.ls() #all
            if toCheckList:
                self.ar.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                for item in toCheckList:
                    if cmds.objExists(item):
                        self.ar.utils.setProgress(self.ar.data.lang[self.title])
                        # conditional to check here
                        if self.cleanupAttr in cmds.listAttr(item):
                            if cmds.getAttr(item+"."+self.cleanupAttr) == 1:
                                self.checked_items.append(item)
                                self.found_issues.append(True)
                                if self.first_mode:
                                    self.good_results.append(False)
                                else: #fix
                                    try:
                                        # delete the node
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
        self.endProgress()
        return self.log_data
