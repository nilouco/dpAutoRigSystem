# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass
from importlib import reload
reload(dpBaseValidatorClass)

# global variables to this module:    
CLASS_NAME = "ValidInTest"
TITLE = "v001_test"
DESCRIPTION = "v002_testDesc"
ICON = "/Icons/dp_validatorTest.png"

dpValidInTestVersion = 0.1

class ValidInTest(dpBaseValidatorClass.ValidatorStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseValidatorClass.ValidatorStartClass.__init__(self, *args, **kwargs)
    

    



    def runValidator(self, verifyMode=True, objList=None, verbose=False, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If verifyMode parameter is False, it'll run in fix mode.
        """
        #self.verbose = verbose
        self.verbose = True

        self.verifyMode = verifyMode
        
        self.checkedObjList = []
        self.foundIssueList = []

        
        
        
        if objList:
            varList = objList
        else:
            varList = cmds.ls(selection=False, type='transform')
        if varList:
            for item in varList:
                self.checkedObjList.append(item)
                if self.verifyMode:
                    if 'pCube1' in varList:
                        self.foundIssueList.append(False)
                    else:
                        self.foundIssueList.append(True)
                else: #fix
                    if not cmds.objExists('pCube1'):
                        try:
                            cmds.polyCube()
                            self.foundIssueList.append(False)
                            print("Fixed pCube1")
                        except:
                            self.foundIssueList.append(True)
                            print("some fix error")
                    else:
                        self.foundIssueList.append(False)
                    
        
        
        # WIP
        #TODO
        # ### put code here...

        # if well done
        
        
        
        self.finishValidation()




    def finishValidation(self, *args):
        """ Call main base methods to finish the validation of this class.
        """
        dpBaseValidatorClass.ValidatorStartClass.updateButtonColors(self)
        dpBaseValidatorClass.ValidatorStartClass.reportLog(self)