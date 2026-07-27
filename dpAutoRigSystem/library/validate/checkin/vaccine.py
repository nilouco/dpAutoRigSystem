# importing libraries:
from maya import cmds
from ....library.base import action
from importlib import reload
import os

# global variables to this module:
CLASS_NAME = "Vaccine"
TITLE = "v052_vaccine"
DESCRIPTION = "v053_vaccineDesc"
WIKI = "07-‐-Validator#-vaccine-cleaner"



class Vaccine(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(action)
    

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
                check_items = objList
            else:
                check_items = cmds.ls(selection=False, type='script')
            if check_items:
                self.ar.utils.setProgress(max=len(check_items), addOne=False, addNumber=False)
                for item in check_items:
                    self.ar.utils.setProgress(self.ar.data.lang[self.title])
                    # conditional to check here
                    scriptdata = cmds.scriptNode(item, beforeScript=True, query=True)
                    #if "fuck_All_U" in scriptdata:
                    if "_gene" in scriptdata:
                        self.checked_items.append(item)
                        self.found_issues.append(True)
                        if self.first_mode:
                            self.good_results.append(False)
                        else: #fix
                            try:
                                cmds.delete(item)
                                path = cmds.internalVar(userAppDir=True)+"/scripts/"
                                vaccineList = ["vaccine.py", "vaccine.pyc"]
                                for vaccine in vaccineList:
                                    if os.path.exists(path+vaccine):
                                        os.remove(path+vaccine)
                                if os.path.exists(path+"userSetup.py"):
                                    self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item+"\n    - "+path+"userSetup.py")
                                else:
                                    self.messages.append(self.ar.data.lang['v004_fixed']+": "+item)
                                cmds.select(clear=True)
                                self.good_results.append(True)
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
