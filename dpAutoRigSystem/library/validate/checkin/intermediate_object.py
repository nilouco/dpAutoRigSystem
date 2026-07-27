# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "IntermediateObject"
TITLE = "v142_intermediateObject"
DESCRIPTION = "v143_intermediateObjectDesc"
WIKI = "07-‐-Validator#-intermediate-object"



class IntermediateObject(action.BaseAction):
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
                toCheckList = cmds.ls(objList, type="mesh", intermediateObjects=True)
            else:
                toCheckList = cmds.ls(selection=False, type="mesh", intermediateObjects=True) #all intermediateObject meshes in the scene
            if toCheckList:
                self.ar.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                for item in toCheckList:
                    self.ar.utils.setProgress(self.ar.data.lang[self.title])
                    self.checked_items.append(item)
                    self.found_issues.append(True)
                    if self.first_mode:
                        self.good_results.append(False)
                    else: #fix
                        try:
                            cmds.lockNode(item, lock=False)
                            cmds.setAttr(item+".intermediateObject", 0)
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
