# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "ControllerTag"
TITLE = "v073_controllerTag"
DESCRIPTION = "v074_controllerTagDesc"
WIKI = "07-‐-Validator#-controller-tag"



class ControllerTag(action.BaseAction):
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
                check_items = self.ar.ctrls.getControlList()
            if check_items:
                self.ar.utils.setProgress(max=len(check_items), add_one=False, add_number=False)
                for item in check_items:
                    self.ar.utils.setProgress(self.ar.data.lang[self.title])
                    if not "controlID" in cmds.listAttr(item):
                        continue
                    if not cmds.getAttr(item+".controlID") == "id_092_Correctives":
                        if self.first_mode:
                            # conditional to check here
                            if not cmds.controller(item, query=True, isController=True):
                                self.checked_items.append(item+" + controllers")
                                self.found_issues.append(True)
                                self.good_results.append(False)
                                self.messages.append(self.ar.data.lang['v075_missingControllerTags'])
                                break
                        else: #fix
                            try:
                                # tag as controller
                                cmds.controller(item, isController=True)
                                result = self.addParentControllerTag(item)
                                self.good_results.append(True)
                                if result:
                                    self.messages.append(self.ar.data.lang['v004_fixed']+": "+result)
                                else:
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


    def addParentControllerTag(self, item, *args):
        """ Add parent controller tag to the given item.
        """
        if "parentTag" in cmds.listAttr(item):
            parentCtrlList = cmds.listConnections(item+".parentTag", source=True, destination=False)
            if parentCtrlList:
                cmds.controller(item, parentCtrlList[0], parent=True)
                return ("Tagged parent = "+item+" --> "+parentCtrlList[0])
