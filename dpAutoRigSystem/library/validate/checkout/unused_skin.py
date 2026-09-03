# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "UnusedSkin"
TITLE = "v082_unusedSkin"
DESCRIPTION = "v083_unusedSkinDesc"
WIKI = "07-‐-Validator#-unused-skin-cleaner"



class UnusedSkin(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
    

    def run_action(self, first_mode=True, inputs=None, *args):
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
            if inputs:
                check_items = inputs
            else:
                check_items = cmds.ls(selection=False, type="skinCluster")
            if check_items:
                self.ar.utils.set_progress(max=len(check_items), add_one=False, add_number=False)
                for item in check_items:
                    self.ar.utils.set_progress(self.ar.data.lang[self.title])
                    # conditional 1 to check here if there's an influenced node, otherwise delete the unused skinCluster
                    meshes = cmds.skinCluster(item, query=True, geometry=True)
                    if meshes:
                        # conditional 2 to check here if there's weighted vertices by influencer
                        influences = cmds.skinCluster(item, query=True, influence=True)
                        weighted_influences = cmds.skinCluster(item, query=True, weightedInfluence=True)
                        if not len(influences) == len(weighted_influences):
                            self.checked_items.append(item)
                            self.found_issues.append(True)
                            if self.first_mode:
                                self.good_results.append(False)
                            else: #fix
                                try:
                                    to_remove_joints = []
                                    for joint_node in influences:
                                        if not joint_node in weighted_influences:
                                            if not joint_node in to_remove_joints:
                                                to_remove_joints.append(joint_node)
                                    if to_remove_joints:
                                        cmds.skinCluster(item, edit=True, removeInfluence=to_remove_joints, toSelectedBones=True)
                                    self.good_results.append(True)
                                    self.messages.append(self.ar.data.lang['v004_fixed']+": "+item+" = "+str(len(to_remove_joints))+" joints")
                                except:
                                    self.good_results.append(False)
                                    self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item)
                    else:
                        self.checked_items.append(item)
                        self.found_issues.append(True)
                        if self.first_mode:
                            self.good_results.append(False)
                        else: #fix
                            try:
                                cmds.lockNode(item, lock=False)
                                cmds.delete(item)
                                self.good_results.append(True)
                                self.messages.append(self.ar.data.lang['v004_fixed']+": "+item+" = deleted")
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
