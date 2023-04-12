# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass
from importlib import reload
reload(dpBaseValidatorClass)

# global variables to this module:    
CLASS_NAME = "ReferenceCleaner"
TITLE = "v042_referenceCleaner"
DESCRIPTION = "v043_referenceCleanerDesc"
ICON = "/Icons/dp_referenceCleaner.png"

dpReferenceCleaner_Version = 1.0

class ReferenceCleaner(dpBaseValidatorClass.ValidatorStartClass):
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
            referenceList = objList
        else:
            referenceList = cmds.ls(references=True)
        if referenceList:
            progressAmount = 0
            maxProcess = len(referenceList)
            for item in referenceList:
                if self.verbose:
                    # Update progress window
                    progressAmount += 1
                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.langDic[self.dpUIinst.langName][self.title]+': '+repr(progressAmount)))
                path = cmds.referenceQuery(item, filename=True)
                self.checkedObjList.append(item)
                self.foundIssueList.append(True)
                if path:
                    if self.verifyMode:
                        self.resultOkList.append(False)
                    else: #fix
                        try:
                            #This comment bellow is to remove the reference. Check with the team if it's better remove/import or AskUser
                            #cmds.file(path, removeReference=True)
                            
                            # Import objects from referenced file.
                            cmds.file(path, importReference=True)

                            # The line bellow is to remove the namespaces after import reference. It can crash when there're
                            # a bunch of guides and geometry together in the file
                            self.removeNamespace()
                            self.resultOkList.append(True)
                            self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v004_fixed']+": "+item)
                        except:
                            self.resultOkList.append(False)
                            self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v005_cantFix']+": "+item)
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
                else:
                    self.dpUIinst.checkImportedGuides(False)