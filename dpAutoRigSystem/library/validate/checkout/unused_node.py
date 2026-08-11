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
                check_items = cmds.ls(selection=False, materials=True)
            if check_items:
                if len(check_items) > 3: #discarding default materials
                    # getting data to analyse
                    defaultMatList = ['lambert1', 'standardSurface1', 'particleCloud1', 'openPBR_shader1']
                    allMatList = list(set(check_items) - set(defaultMatList))
                    usedMatList = list(set(self.get_used_materials()) - set(defaultMatList))
                    # conditional to check here
                    if not len(allMatList) == len(usedMatList):
                        self.ar.utils.setProgress(max=len(allMatList), add_one=False, add_number=False)
                        self.ar.utils.setProgress(self.ar.data.lang[self.title])
                        issueMatList = sorted(list(set(allMatList) - set(usedMatList)))
                        self.checked_items.append(str(", ".join(issueMatList)))
                        self.found_issues.append(True)
                        if self.first_mode:
                            self.good_results.append(False)
                        else: #fix
                            try:
                                fixResult = mel.eval("MLdeleteUnused;")
                                self.good_results.append(True)
                                self.messages.append(self.ar.data.lang['v004_fixed']+": "+str(fixResult)+" nodes = "+str(len(issueMatList))+" materials")
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
