# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "Outliner"
TITLE = "v076_outliner"
DESCRIPTION = "v077_outlinerDesc"
WIKI = "07-‐-Validator#-outliner-cleaner"



class Outliner(action.BaseAction):
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
        
        # ---
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            hiddenList = [self.ar.data.temp_grp, self.ar.data.guide_mirror_grp]
            
            
            #TODO = get node by attribute (dpTemp)


            if not objList:
                objList = cmds.ls(selection=False, type="transform")
            if objList:
                self.ar.utils.setProgress(max=len(hiddenList), addOne=False, addNumber=False)
                for item in hiddenList:
                    self.ar.utils.setProgress(self.ar.data.lang[self.title])
                    if item in objList:
                        self.checked_items.append(item)
                        if cmds.objExists(item):
                            self.found_issues.append(True)
                            if self.first_mode:
                                self.good_results.append(False)
                            else: #fix
                                try:    
                                    cmds.delete(item)
                                    self.good_results.append(True)
                                    self.messages.append(self.ar.data.lang['v004_fixed']+": "+item)
                                except:
                                    self.good_results.append(False)
                                    self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item)
                        else:
                            self.found_issues.append(False)
                            self.good_results.append(True)
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
