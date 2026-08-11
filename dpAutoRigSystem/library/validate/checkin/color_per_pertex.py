# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "ColorPerVertex"
TITLE = "v117_colorPerVertex"
DESCRIPTION = "v118_colorPerVertexDesc"
WIKI = "07-‐-Validator#-colorpervertex-cleaner"



class ColorPerVertex(action.BaseAction):
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
                check_items = cmds.ls(objList, type="polyColorPerVertex")
            else:
                check_items = cmds.ls(selection=False, type='polyColorPerVertex')
            if check_items:
                self.ar.utils.setProgress(max=len(check_items), add_one=False, add_number=False)
                for item in check_items:
                    self.ar.utils.setProgress(self.ar.data.lang[self.title])
                    self.checked_items.append(item)
                    self.found_issues.append(True)
                    if self.first_mode:
                        self.good_results.append(False)
                    else: #fix
                        try:
                            meshList = cmds.ls(cmds.listHistory(item, future=True), long=True, type="mesh")
                            cmds.lockNode(item, lock=False)
                            cmds.delete(item)
                            if meshList:
                                for mesh in meshList:
                                    cmds.setAttr(mesh+".displayColors", 0)
                            else:
                                meshList = ["None"]
                            cmds.select(clear=True)
                            self.good_results.append(True)
                            self.messages.append(self.ar.data.lang['v004_fixed']+": "+item+" - Mesh: "+", ".join(meshList))
                        except:
                            self.good_results.append(False)
                            self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item+" - Mesh: "+", ".join(meshList))
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
