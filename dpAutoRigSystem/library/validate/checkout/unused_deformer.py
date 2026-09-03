# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "UnusedDeformer"
TITLE = "v148_unusedDeformer"
DESCRIPTION = "v149_unusedDeformerDesc"
WIKI = "07-‐-Validator#-unused-deformer-cleaner"



class UnusedDeformer(action.BaseAction):
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
        
        #mel.eval('scOpt_performOneCleanup({"deformerOption"});')

        # ---
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            unused_items = []
            #cmds.findDeformers("*")
            deformers = cmds.ls(type="geometryFilter") #deformers
            intermediates = cmds.ls(type="controlPoint", intermediateObjects=True)
            if inputs:
                check_items = inputs
            else:
                check_items = deformers.copy()
                check_items.extend(intermediates.copy())
            if check_items:
                self.ar.utils.set_progress(max=len(check_items), add_one=False, add_number=False)
                if deformers:
                    for def_node in deformers:
                        self.ar.utils.set_progress(self.ar.data.lang[self.title])
                        has_tags = False
                        indices = cmds.getAttr(def_node+".input", multiIndices=True)
                        if indices:
                            for i in indices:
                                if not cmds.getAttr(def_node+".input["+str(i)+"].groupId"):
                                    if cmds.getAttr(def_node+".input["+str(i)+"].componentTagExpression"):
                                        has_tags = True
                                        break
                        if not has_tags:
                            def_sets = cmds.listConnections(def_node+".message", type="objectSet")
                            if not def_sets:
                                unused_items.append(def_node)
                            else:
                                members = cmds.sets(def_sets[0], query=True)
                                if not members:
                                    unused_items.append(def_node)
                if intermediates:
                    for intermediate in intermediates:
                        self.ar.utils.set_progress(self.ar.data.lang[self.title])
                        outputs = cmds.listConnections(intermediate, source=False, destination=True, plugs=True)
                        if not outputs:
                            unused_items.append(intermediate)
                # conditional to check here
                if unused_items:
                    self.checked_items.append("\n".join(unused_items))
                    self.found_issues.append(True)
                    if self.first_mode:
                        self.good_results.append(False)
                    else: #fix
                        try:
                            # delete them
                            cmds.lockNode(unused_items, lock=False)
                            cmds.delete(unused_items)
                            self.good_results.append(True)
                            self.messages.append(self.ar.data.lang['v004_fixed']+": nodes = "+str(len(unused_items)))
                        except:
                            self.good_results.append(False)
                            self.messages.append(self.ar.data.lang['v005_cantFix']+": nodes = "+str(len(unused_items)))
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
