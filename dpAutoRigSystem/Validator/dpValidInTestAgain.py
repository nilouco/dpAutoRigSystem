# importing libraries:
from maya import cmds
from . import dpBaseValidatorClass
from importlib import reload
reload(dpBaseValidatorClass)

# global variables to this module:    
CLASS_NAME = "ValidInTestAgain"
TITLE = "i155_upDesc"
DESCRIPTION = "m099_cvControlDesc"
ICON = "/Icons/dp_limb.png"

dpValidInTestVersion = 0.1

class ValidInTestAgain(dpBaseValidatorClass.ValidatorStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseValidatorClass.ValidatorStartClass.__init__(self, *args, **kwargs)
    
    
    

    def runVerify(self, *args):
        print("Logistica Verify")

    def runFix(self, *args):
        print("Logistica fix")

    