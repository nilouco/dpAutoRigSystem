# importing libraries:
from maya import cmds
from ... import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "NamespaceCleaner"
TITLE = "v038_namespaceCleaner"
DESCRIPTION = "v039_namespaceCleanerDesc"
ICON = "/Icons/dp_namespaceCleaner.png"

DP_NAMESPACECLEANER_VERSION = 1.2


class NamespaceCleaner(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_NAMESPACECLEANER_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)


    def runAction(self, firstMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If firstMode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.firstMode = firstMode
        self.cleanUpToStart()

        # ---
        # --- validator code --- beginning
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
            self.utils.setProgress(max=len(namespaceMainList))
            for namespace in namespaceToCleanList:
                self.utils.setProgress(self.dpUIinst.lang[self.title])
                self.checkedObjList.append(namespace)
                self.foundIssueList.append(True)
            if self.firstMode:
                self.resultOkList.append(False)
            else: #fix
                try:
                    if namespaceWithGuidesList:
                        # call checkImportedGuides from dpAutoRig, to remove namespace when it's guide.
                        self.dpUIinst.checkImportedGuides(False)
                    elif namespaceWithoutGuidesList:
                        # call function inside validator to remove namespaces when it's not a guide.
                        self.removeNamespace()
                    self.resultOkList.append(True)
                    self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+namespace)
                except:
                    self.resultOkList.append(False)
                    self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+namespace)
        else:
            self.notFoundNodes()

        # --- validator code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic
    

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
