# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = 'UnlockAttributes'
TITLE = 'v092_unlockAttributes'
DESCRIPTION = 'v093_unlockAttributesDesc'
WIKI = "07-‐-Validator#-unlock-attributes"



class UnlockAttributes(action.BaseAction):
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
                        lockedAttrDic = {}
                        self.ar.utils.setProgress(max=len(nodes), add_one=False, add_number=False)
                        for item in nodes:
                            self.ar.utils.setProgress(self.ar.data.lang[self.title])
                            lockedAttrList = cmds.listAttr(item, locked=True)
                            if lockedAttrList:
                                lockedAttrDic[item] = lockedAttrList
                        # conditional to check here
                        if lockedAttrDic:
                            for item in lockedAttrDic.keys():
                                self.checked_items.append(item)
                                self.found_issues.append(True)
                                if self.first_mode:
                                    self.good_results.append(False)
                                else: #fix
                                    try:
                                        cmds.lockNode(item, lock=False, lockUnpublished=False)
                                        for attr in lockedAttrDic[item]:
                                            cmds.setAttr(item+"."+attr, lock=False)
                                        self.good_results.append(True)
                                        self.messages.append(self.ar.data.lang['v004_fixed']+": "+item+" = "+str(lockedAttrDic[item]))
                                    except:
                                        self.good_results.append(False)
                                        self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item+" = "+attr)
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
