# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "ImportReference"
TITLE = "v042_importReference"
DESCRIPTION = "v043_importReferenceDesc"
WIKI = "07-‐-Validator#-import-referenced-file"



class ImportReference(action.BaseAction):
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
        if inputs:
            references = inputs
        else:
            references = cmds.file(query=True, reference=True)
        if references:
            self.ar.ui_manager.set_progress(max=len(references), add_one=False, add_number=False)
            for reference in references:
                self.ar.ui_manager.set_progress(self.ar.data.lang[self.title])
                self.checked_items.append(reference)
                self.found_issues.append(True)
            if self.first_mode:
                self.good_results.append(False)
            else: #fix
                self.import_reference()
        else:
            self.not_found_node()
        # --- validator code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.end_progress()
        return self.log_data


    def import_reference(self):
        """ This function will import objects from referenced file.
        """
        refs = cmds.file(query=True, reference=True)
        if refs:
            for ref in refs:
                top_ref = cmds.referenceQuery(ref, referenceNode=True, topReference=True)
                if cmds.objExists(top_ref):
                    # Only import it if it's loaded, otherwise it would throw an error.
                    if cmds.referenceQuery(ref, isLoaded=True):
                        try:
                            cmds.file(ref, importReference=True)
                            self.good_results.append(True)
                            self.messages.append(self.ar.data.lang['v004_fixed']+": "+ref)
                            self.import_reference()
                            break
                        except:
                            self.good_results.append(False)
                            self.messages.append(self.ar.data.lang['v005_cantFix']+": "+ref)
                    else:
                        self.good_results.append(False)
                        self.messages.append(self.ar.data.lang['v005_cantFix']+": "+ref)
