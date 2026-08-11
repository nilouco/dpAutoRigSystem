# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "Namespace"
TITLE = "v038_namespace"
DESCRIPTION = "v039_namespaceDesc"
WIKI = "07-‐-Validator#-namespace-cleaner"



class Namespace(action.BaseAction):
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
                namespaceToCleanList = objList
            else:
                namespaceWithGuidesMainList = []
                namespaceWithoutGuidesMainList = []
                cmds.namespace(setNamespace=':')
                namespaceMainList = cmds.namespaceInfo(listOnlyNamespaces=True)
                if namespaceMainList:
                    for namespace in namespaceMainList:
                        if namespace != "UI" and namespace != "shared":
                            # check if there's dpGuides in the list members
                            types = cmds.namespaceInfo(namespace, listNamespace=True)
                            for type in types:
                                # if dpGuides, append to list with Guides, else append to withouGuides
                                if type.find("_dpAR_") != -1:
                                    namespaceWithGuidesMainList.append(namespace)
                                else:
                                    namespaceWithoutGuidesMainList.append(namespace)
                    namespaceWithoutGuidesList = []
                    namespaceWithGuidesList = []
                    # append to new list in order to remove the namespace guide base
                    for namespace in namespaceWithGuidesMainList:
                        # it will only add to namespaceWithGuideList if it's not a guide base
                        if "_dpAR_" not in namespace:
                            namespaceWithGuidesList.append(namespace)
                    # append to a new list if not find the item from with guides in without guides
                    for item in namespaceWithoutGuidesMainList:
                        if item not in namespaceWithGuidesMainList:
                            namespaceWithoutGuidesList.append(item)
                    # set both list together, excluding the duplicated names
                    namespaceToCleanList = list(set(namespaceWithGuidesList)) + list(set(namespaceWithoutGuidesList))
            if namespaceToCleanList:
                self.ar.utils.setProgress(max=len(namespaceMainList), add_one=False, add_number=False)
                for namespace in namespaceToCleanList:
                    self.ar.utils.setProgress(self.ar.data.lang[self.title])
                    self.checked_items.append(namespace)
                    self.found_issues.append(True)
                if self.first_mode:
                    self.good_results.append(False)
                else: #fix
                    try:
                        if namespaceWithGuidesList:
                            # call check_imported_guides from dpAutoRig, to remove namespace when it's guide.
                            self.ar.filler.check_imported_guides(False)
                        elif namespaceWithoutGuidesList:
                            # call function inside validator to remove namespaces when it's not a guide.
                            self.removeNamespace()
                        self.good_results.append(True)
                        self.messages.append(self.ar.data.lang['v004_fixed']+": "+namespace)
                    except:
                        self.good_results.append(False)
                        self.messages.append(self.ar.data.lang['v005_cantFix']+": "+namespace)
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
    

    def removeNamespace(self, *args):
        """ This function will use recursive method to remove all namespace, 
            when it isn't a guide namespace
        """
        cmds.namespace(setNamespace=':')
        namespaceList = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
        for name in namespaceList:
            if name != "UI" and name != "shared":
                if name.find("_dpAR_") == -1:
                    cmds.namespace(removeNamespace=name, mergeNamespaceWithRoot=True)
                    self.removeNamespace()
                    break
