# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "DataSet"
TITLE = "v144_dataSet"
DESCRIPTION = "v145_dataSetDesc"
WIKI = "07-‐-Validator#-data_grp-set-cleaner"



class DataSet(action.BaseAction):
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
                dataGrp = inputs[0]
            else:
                dataGrp = self.ar.utils.get_node_by_message("dataGrp")
                if not dataGrp:
                    if cmds.objExists("Data_Grp"):
                        dataGrp = "Data_Grp"
            if dataGrp:
                check_items = cmds.listRelatives(dataGrp, children=True, allDescendents=True)
                if check_items:
                    self.ar.utils.set_progress(max=len(check_items), add_one=False, add_number=False)
                    for item in check_items:
                        self.ar.utils.set_progress(self.ar.data.lang[self.title])
                        plugList = cmds.listConnections(item+".instObjGroups[0]", source=False, destination=True, plugs=True)
                        if plugList:
                            for plug in plugList:
                                if cmds.objectType(plug.split(".")[0]) == "objectSet":
                                    itemDone = False
                                    if item in self.checked_items:
                                        itemDone = True
                                    if not itemDone:
                                        self.checked_items.append(item)
                                        self.found_issues.append(True)
                                    if self.first_mode:
                                        if not itemDone:
                                            self.good_results.append(False)
                                    else: #fix
                                        try:
                                            cmds.disconnectAttr(item+".instObjGroups[0]", plug)
                                            if not itemDone:
                                                self.good_results.append(True)
                                                self.messages.append(self.ar.data.lang['v004_fixed']+": "+item)
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
