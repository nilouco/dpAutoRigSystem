# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass
from importlib import reload
reload(dpBaseValidatorClass)

# global variables to this module:    
CLASS_NAME = "ImportReference"
TITLE = "v042_importReference"
DESCRIPTION = "v043_importReferenceDesc"
ICON = "/Icons/dp_importReference.png"

dpImportReference_Version = 1.0

class ImportReference(dpBaseValidatorClass.ValidatorStartClass):
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
            for reference in referenceList:
                if self.verbose:
                    # Update progress window
                    progressAmount += 1
                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.langDic[self.dpUIinst.langName][self.title]+': '+repr(progressAmount)))
                self.checkedObjList.append(reference)
                self.foundIssueList.append(True)
                if self.verifyMode:
                    self.resultOkList.append(False)
                else: #fix
                    try:
                        # Import objects from referenced file.
                        self.importRefence()
                        self.resultOkList.append(True)
                        self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v004_fixed']+": "+reference)
                    except:
                        self.resultOkList.append(False)
                        self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v005_cantFix']+": "+reference)
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

    def importRefence(self, *args):
        """ This function will use recursive method to import referenced file, 
        """
        referenceList = cmds.ls(references=True)
        print(referenceList)
        if referenceList:
            print("===REF LIST===", referenceList)
            for ref in referenceList:
                topReference = cmds.referenceQuery(ref, referenceNode=True, topReference=True)
                print(topReference)
                if topReference:
                    print("^^^TOP REF^^^", topReference)
                    path = cmds.referenceQuery(topReference, filename=True)
                    if path:
                        print(">>> PATH >>>", path)
                        cmds.file(path, importReference=True)
                        self.importRefence()
                        break
                        