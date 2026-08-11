# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "JointEnd"
TITLE = "v111_jointEnd"
DESCRIPTION = "v112_jointEndDesc"
WIKI = "07-‐-Validator#-joint-end-cleaner"



class JointEnd(action.BaseAction):
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
                check_items = cmds.ls(selection=False, type="joint")
            if check_items:
                self.ar.utils.setProgress(max=len(check_items), add_one=False, add_number=False)
                # list joint ends
                jEndList = [j for j in check_items if self.ar.data.joint_end_attr in cmds.listAttr(j)] #by attribute
                jEndList.extend([j for j in cmds.ls(selection=False, type="joint") if j.endswith(self.ar.data.joint_end_attr)]) #by suffix
                if jEndList:
                    # check connection with skinCluster to avoid delete it and crash the setup
                    jEndList = list(set(jEndList)-set(self.ar.skin.getSkinnedJointList())) #remove duplicated and skinned joints
                    jEndList = [j for j in jEndList if not cmds.listRelatives(j, children=True)] #remove if there are children
                    if jEndList:
                        jEndList.sort()
                        for item in jEndList:
                            self.ar.utils.setProgress(self.ar.data.lang[self.title])
                            self.checked_items.append(item)
                            self.found_issues.append(True)
                            if self.first_mode:
                                self.good_results.append(False)
                            else: #fix
                                try:
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
