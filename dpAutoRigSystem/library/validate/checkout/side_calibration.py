# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "SideCalibration"
TITLE = "v044_sideCalibration"
DESCRIPTION = "v045_sideCalibrationDesc"
WIKI = "07-‐-Validator#-side-calibration"



class SideCalibration(action.BaseAction):
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
                check_items = self.ar.ctrls.get_controllers()
            if check_items:
                pair_data = {}
                self.ar.ui_manager.set_progress(max=len(check_items), add_one=False, add_number=False)
                for item in check_items:
                    self.ar.ui_manager.set_progress(self.ar.data.lang[self.title])
                    # conditional to check here
                    if cmds.objExists(item+".calibrations"):
                        if item[1] == "_": #side: because L_CtrlName or R_CtrlName have "_" as second letter.
                            found_other_side = False
                            for node in check_items:
                                if node[2:] == item[2:]: #other side found
                                    pair_data[item] = node
                                    found_other_side = True
                                    break
                            if found_other_side:
                                calibrations = self.ar.ctrls.get_items_from_string_attr(item)
                                if calibrations:
                                    not_mirror_attrs = self.ar.ctrls.get_items_from_string_attr(item, "notMirrorList")
                                    if not_mirror_attrs:
                                        calibrations = list(set(calibrations) - set(not_mirror_attrs))
                                    for attr in calibrations:
                                        if cmds.objExists(item+"."+attr) and cmds.objExists(pair_data[item]+"."+attr):
                                            # current values
                                            item_current_value = float(format(cmds.getAttr(item+"."+attr),".3f"))
                                            pair_current_value = float(format(cmds.getAttr(pair_data[item]+"."+attr),".3f"))
                                            if not item_current_value == pair_current_value:
                                                # found issue here
                                                self.checked_items.append(item+"."+attr)
                                                self.found_issues.append(True)
                                                if self.first_mode:
                                                    self.good_results.append(False)
                                                else: #fix
                                                    try:
                                                        # default values (supposed to be the same for the two sides)
                                                        item_default_value = float(format(cmds.addAttr(item+"."+attr, query=True, defaultValue=True),".3f"))
                                                        if pair_current_value == item_default_value:
                                                            # pair current value is equal to its default value, so we set the pair value as item current value
                                                            cmds.setAttr(pair_data[item]+"."+attr, item_current_value)
                                                        else:
                                                            # check for left, top or front side to use it as priority node:
                                                            if item[0] == self.ar.data.lang['p002_left'] or item[0] == self.ar.data.lang['p004_top'] or item[0] == self.ar.data.lang['p006_front']:
                                                                cmds.setAttr(pair_data[item]+"."+attr, item_current_value)
                                                            else:
                                                                cmds.setAttr(item+"."+attr, pair_current_value)
                                                        self.good_results.append(True)
                                                        self.messages.append(self.ar.data.lang['v004_fixed']+": "+item+"."+attr)
                                                    except:
                                                        self.good_results.append(False)
                                                        self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item+"."+attr)
                                        else:
                                            self.good_results.append(True)
                                            self.messages.append(item+"."+attr+" "+self.ar.data.lang['i061_notExists'])
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
