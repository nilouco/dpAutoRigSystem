# importing libraries:
from maya import cmds
from maya import mel
from ....library.base import action

# global variables to this module:
CLASS_NAME = "PruneSkinWeights"
TITLE = "v103_pruneSkinWeights"
DESCRIPTION = "v104_pruneSkinWeightsDesc"
WIKI = "07-‐-Validator#-prune-skin-weights"



class PruneSkinWeights(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.prune_min_value = 0.0005
    

    def run_action(self, first_mode=True, inputs=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If first_mode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checked_items = node list of checked item
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
                check_items = cmds.ls(selection=False, type='skinCluster')
            if check_items:
                self.ar.utils.set_progress(max=len(check_items), add_one=False, add_number=False)
                for skincluster_node in check_items:
                    self.ar.utils.set_progress(self.ar.data.lang[self.title])
                    meshes = cmds.skinCluster(skincluster_node, query=True, geometry=True)
                    if meshes:
                        weights = self.ar.skin.get_skin_weights(meshes[0], skincluster_node)
                        to_prune_items = []
                        # check low weights
                        for v, weight_data in enumerate(weights):
                            for w in weight_data.keys():
                                if weight_data[w] < self.prune_min_value:
                                    to_prune_items.append(v)
                                    break
                        # conditional to check here
                        if to_prune_items:
                            self.checked_items.append(skincluster_node)
                            self.found_issues.append(True)
                            if self.first_mode:
                                self.good_results.append(False)
                            else: #fix
                                try:
                                    #cmds.skinCluster(skincluster_node, edit=True, prune=True)
                                    influences = cmds.skinCluster(skincluster_node, query=True, influence=True)
                                    for jnt in influences:
                                        cmds.setAttr(jnt+".liw", 0) #unlock
                                    cmds.select(meshes[0])
                                    mel.eval('doPruneSkinClusterWeightsArgList 2 { "'+str(self.prune_min_value)+'", "1" };')
                                    self.good_results.append(True)
                                    self.messages.append(self.ar.data.lang['v004_fixed']+": "+skincluster_node+" = "+str(len(to_prune_items))+" vertices")
                                except:
                                    self.good_results.append(False)
                                    self.messages.append(self.ar.data.lang['v005_cantFix']+": "+skincluster_node)
                                cmds.select(clear=True)
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
