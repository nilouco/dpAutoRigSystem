# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass
from importlib import reload
reload(dpBaseValidatorClass)

# global variables to this module:    
CLASS_NAME = "ValidInTest2"
TITLE = "v001_test"
DESCRIPTION = "v002_testDesc"
ICON = "/Icons/dp_validatorTest.png"

dpValidInTest2_Version = 0.1

class ValidInTest2(dpBaseValidatorClass.ValidatorStartClass):
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
            Returns dataLog with the validation result.
        """
        # starting
        self.verifyMode = verifyMode
        self.startValidation()
        
        # -- validator code -- beginning
        if objList:
            toCheckList = objList
        else:
            toCheckList = cmds.ls(selection=False, type='mesh')
        if toCheckList:
            for item in toCheckList:
                parentNode = cmds.listRelatives(item, parent=True)[0]
                self.checkedObjList.append(parentNode)
                if not '_Mesh' in item:
                    self.foundIssueList.append(True)
                    if self.verifyMode:
                        self.resultOkList.append(False)
                    else: #fix
                        try:
                            #WIP: (index to fix error OMG!)
                            parentNode = cmds.listRelatives(item, parent=True)[0] # change index here to test
                            #
                            cmds.rename(parentNode, parentNode+"_Mesh")
                            self.resultOkList.append(True)
                            self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v004_fixed']+": "+parentNode)
                        except:
                            self.resultOkList.append(False)
                            self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v005_cantFix']+": "+parentNode)
                else:
                    self.foundIssueList.append(False)
                    self.resultOkList.append(True)
        # -- validator code -- end

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