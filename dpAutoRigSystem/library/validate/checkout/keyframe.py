# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "Keyframe"
TITLE = "v040_keyframe"
DESCRIPTION = "v041_keyframeDesc"
WIKI = "07-‐-Validator#-keyframe-cleaner"



class Keyframe(action.BaseAction):
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
                check_items = cmds.ls(selection=False)
            if check_items:
                # get animation node list
                anim_curve_items = cmds.ls(type="animCurve")
                if anim_curve_items:
                    animated_items = []
                    for anim_crv in anim_curve_items:
                        connections = cmds.ls(cmds.listConnections(anim_crv), type=["transform", "blendShape", "nonLinear"])
                        if connections and not connections[0] in animated_items:
                            animated_items.append(connections[0])
                    if animated_items:
                        self.ar.ui_manager.set_progress(max=len(animated_items), add_one=False, add_number=False)
                        for item in animated_items:
                            self.ar.ui_manager.set_progress(self.ar.data.lang[self.title])
                            if item in check_items:
                                if cmds.objExists(item):
                                    connected_anim_curves = cmds.listConnections(item, source=True, destination=False, type="animCurve") #blendWeighted/pairBlend
                                    if connected_anim_curves:
                                        found_key = False
                                        for crv in connected_anim_curves:
                                            # conditional to check here
                                            if len(cmds.listConnections(crv, source=True)) >= 2:
                                                pass #drivenKey
                                            else: #normal key
                                                found_key = True
                                                break
                                        if found_key:
                                            self.checked_items.append(item)
                                            self.found_issues.append(True)
                                            if self.first_mode:
                                                self.good_results.append(False)
                                            else: #fix
                                                reported = False
                                                for crv in connected_anim_curves:
                                                    if len(cmds.listConnections(crv, source=True)) < 2:
                                                        try:
                                                            # delete animation curve (keyframe)
                                                            cmds.delete(crv)
                                                            if not reported:
                                                                self.good_results.append(True)
                                                                self.messages.append(self.ar.data.lang['v004_fixed']+": "+item)
                                                                reported = True
                                                        except:
                                                            if not reported:
                                                                self.good_results.append(False)
                                                                self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item)
                                                                reported = True
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
