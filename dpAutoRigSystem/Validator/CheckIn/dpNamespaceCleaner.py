# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass
from importlib import reload
reload(dpBaseValidatorClass)

# global variables to this module:    
CLASS_NAME = "NamespaceCleaner"
TITLE = "v032_namespaceCleaner"
DESCRIPTION = "v033_namespaceCleanerDesc"
ICON = "/Icons/dp_namespaceCleaner.png"

dpNamespaceCleaner_Version = 1.0

class NamespaceCleaner(dpBaseValidatorClass.ValidatorStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseValidatorClass.ValidatorStartClass.__init__(self, *args, **kwargs)

    def runValidator(self, verifyMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If verifyMode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.verifyMode = verifyMode
        self.startValidation()
    
        
        # ---
        # --- validator code --- beginning
        if objList:
            namespaceListToClean = objList
        else:
            namespaceWithGuidesListMain = []
            namespaceWithoutGuidesListMain = []
            cmds.namespace(setNamespace=':')
            namespaceListMain = cmds.namespaceInfo(listOnlyNamespaces=True)
            if namespaceListMain:
                for namespace in namespaceListMain:
                    if namespace != "UI" and namespace != "shared":
                        # check if there's dpGuides in the list members
                        types = cmds.namespaceInfo(namespace, listNamespace=True)
                        for type in types:
                            # if dpGuides, append to list with Guides, else append to withouGuides
                            if type.find("_dpAR_") != -1:
                                namespaceWithGuidesListMain.append(namespace)
                            else:
                                namespaceWithoutGuidesListMain.append(namespace)
                namespaceWithoutGuidesList = []
                namespaceWithGuidesList = []
                # append to new list in order to remove the namespace guide base
                for namespace in namespaceWithGuidesListMain:
                    # it will only add to namespaceWithGuideList if it's not a guide base
                    if "_dpAR_" not in namespace:
                        namespaceWithGuidesList.append(namespace)
                # append to a new list if not find the item from with guides in without guides
                for item in namespaceWithoutGuidesListMain:
                    if item not in namespaceWithGuidesListMain:
                        namespaceWithoutGuidesList.append(item)
                # set both list together, excluding the duplicated names
                namespaceListToClean = list(set(namespaceWithGuidesList)) + list(set(namespaceWithoutGuidesList))
        if namespaceListToClean:
            progressAmount = 0
            maxProcess = len(namespaceListMain)
            for namespace in namespaceListToClean:
                if self.verbose:
                    # Update progress window
                    progressAmount += 1
                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.langDic[self.dpUIinst.langName][self.title]+': '+repr(progressAmount)))
                self.checkedObjList.append(namespace)
                self.foundIssueList.append(True)
                if self.verifyMode:
                    self.resultOkList.append(False)
                else: #fix
                    try:
                        if namespace in namespaceWithGuidesList:
                            # call checkImportedGuides from dpAutoRig, to remove namespace when it's guide.
                            self.dpUIinst.checkImportedGuides(False)
                        else:
                            # call function inside validator to remove namespaces when it's not a guide.
                            self.removeNamespace()
                            
                        self.resultOkList.append(True)
                        self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v004_fixed']+": "+namespace)
                    except:
                        self.resultOkList.append(False)
                        self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v005_cantFix']+": "+namespace)
        else:
            self.checkedObjList.append("")
            self.foundIssueList.append(False)
            self.resultOkList.append(True)
            self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v014_notFoundNodes'])

        # --- validator code --- end
        # ---



        # finishing
        self.finishValidation()
        return self.dataLogDic
    
    def startValidation(self, *args):
        """ Procedures to start the validation cleaning old data.
        """
        dpBaseValidatorClass.ValidatorStartClass.cleanUpToStart(self)


    def finishValidation(self, *args):
        """ Call main base methods to finish the validation of this class.
        """
        dpBaseValidatorClass.ValidatorStartClass.updateButtonColors(self)
        dpBaseValidatorClass.ValidatorStartClass.reportLog(self)
        dpBaseValidatorClass.ValidatorStartClass.endProgressBar(self)

    
    def removeNamespace(self, *args):
        """ This function will use recursive method to remove all namespace, 
            when it's not a guide namespace
        """
        cmds.namespace(setNamespace=':')
        namespaceList = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
        for name in namespaceList:
            if name != "UI" and name != "shared":
                if name.find("_dpAR_") == -1:
                        cmds.namespace(removeNamespace=name, mergeNamespaceWithRoot=True)
                        self.removeNamespace()
                        break
