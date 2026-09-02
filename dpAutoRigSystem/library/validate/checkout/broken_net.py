# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "BrokenNet"
TITLE = "v046_brokenNet"
DESCRIPTION = "v047_brokenNetDesc"
WIKI = "07-‐-Validator#-broken-network-cleaner"



class BrokenNet(action.BaseAction):
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
                check_items = cmds.ls(selection=False, type='network')
            if check_items:
                self.ar.utils.set_progress(max=len(check_items), add_one=False, add_number=False)
                for item in check_items:
                    self.ar.utils.set_progress(self.ar.data.lang[self.title])
                    # conditional to check here
                    if 'originalLoc' in cmds.listAttr(item) and 'actionLoc' in cmds.listAttr(item): #correctionManater
                        if not cmds.listConnections(item+".originalLoc", source=True, destination=False) or not cmds.listConnections(item+".actionLoc", source=True, destination=False):
                            self.cleanup_network(item)
                    elif 'worldRef' in cmds.listAttr(item): #ikFkSnap
                        if not cmds.listConnections(item+".worldRef", source=True, destination=False):
                            self.cleanup_network(item)
                    elif 'follicle' in cmds.listAttr(item): #rivet
                        if not cmds.listConnections(item+".follicle", source=True, destination=False):
                            self.cleanup_network(item)
                    elif 'linkedNode' in cmds.listAttr(item): #guide
                        if not cmds.listConnections(item+".linkedNode", source=True, destination=False):
                            self.cleanup_network(item)
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


    def cleanup_network(self, item):
        self.checked_items.append(item)
        self.found_issues.append(True)
        if self.first_mode:
            self.good_results.append(False)
        else: #fix
            try:
                cmds.lockNode(item, lock=False)
                cmds.delete(item)
                cmds.select(clear=True)
                self.good_results.append(True)
                self.messages.append(self.ar.data.lang['v004_fixed']+": "+item)
            except:
                self.good_results.append(False)
                self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item)
