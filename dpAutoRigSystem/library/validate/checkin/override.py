# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = 'Override'
TITLE = 'v090_override'
DESCRIPTION = 'v091_overrideDesc'
WIKI = "07-‐-Validator#-override-cleaner"



class Override(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)


    def runAction(self, first_mode=True, objList=None, *args):
        ''' Main method to process this validator instructions.
            It's in verify mode by default.
            If first_mode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checked_items = node list of checked items
                - found_issues = True if an issue was found, False if there isn't an issue for the checked node
                - good_results = True if well done, False if we got an error
                - messages = reported text
        '''
        # starting
        self.first_mode = first_mode
        self.cleanup_to_start()

        # ---
        # --- validator code --- beginning
        if not self.ar.utils.getAllGrp():
            if not self.ar.utils.getNetworkNodeByAttr("dpGuideNet"):
                if not cmds.file(query=True, reference=True):
                    nodes = cmds.ls(selection=False)
                    if objList:
                        nodes = objList
                    if nodes:
                        overridedList = []
                        self.ar.utils.setProgress(max=len(nodes), add_one=False, add_number=False)
                        for item in nodes:
                            self.ar.utils.setProgress(self.ar.data.lang[self.title])
                            if cmds.objExists(item+".overrideEnabled"):
                                if cmds.getAttr(item+".overrideEnabled") == 1:
                                    overridedList.append(item)
                        # conditional to check here
                        if overridedList:
                            for item in overridedList:
                                self.checked_items.append(item)
                                self.found_issues.append(True)
                                if self.first_mode:
                                    self.good_results.append(False)
                                else: #fix
                                    try:
                                        cmds.lockNode(item, lock=False, lockUnpublished=False)
                                        cmds.setAttr(item+".overrideEnabled", lock=False)
                                        cmds.setAttr(item+".overrideEnabled", 0)
                                        self.good_results.append(True)
                                        self.messages.append(self.ar.data.lang['v004_fixed']+": "+item)
                                    except:
                                        self.good_results.append(False)
                                        self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item)
                    else:
                        self.not_found_node()
                else:
                    self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
            else:
                self.fail_io(self.ar.data.lang['v100_cantExistsGuides'])
        else:
            self.fail_io(self.ar.data.lang['v099_cantExistsAllGrp'])
        # --- validator code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.end_progress()
        return self.log_data
