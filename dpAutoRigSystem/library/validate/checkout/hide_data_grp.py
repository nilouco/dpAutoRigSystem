# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "HideDataGrp"
TITLE = "v028_hideDataGrp"
DESCRIPTION = "v029_hideDataGrpDesc"
WIKI = "07-‐-Validator#-hide-data_grp"



class HideDataGrp(action.BaseAction):
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
            dataGrp = None
            if objList:
                dataGrp = objList[0]
            else:
                dataGrp = self.ar.utils.getNodeByMessage("dataGrp")
                if not dataGrp:
                    if cmds.objExists("Data_Grp"):
                        dataGrp = "Data_Grp"
            if dataGrp:
                self.ar.utils.setProgress(max=1)
                self.ar.utils.setProgress(self.ar.data.lang[self.title])
                self.checked_items.append(dataGrp)
                visibilityStatus = cmds.getAttr(dataGrp+".visibility")
                if visibilityStatus:
                    self.found_issues.append(True)
                    if self.first_mode:
                        self.good_results.append(False)
                    else: #fix
                        try:
                            cmds.setAttr(dataGrp+".visibility", 0)
                            self.good_results.append(True)
                            self.messages.append(self.ar.data.lang['v004_fixed']+": "+dataGrp)
                        except:
                            self.good_results.append(False)
                            self.messages.append(self.ar.data.lang['v005_cantFix']+": "+dataGrp)
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
