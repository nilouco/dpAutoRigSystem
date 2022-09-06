# importing libraries:
from maya import cmds
from maya import mel
from ..Modules.Library import dpControls
from ..Modules.Library import dpUtils

DEFAULT_COLOR = (0.5, 0.5, 0.5)
CHECKED_COLOR = (0.6, 0.8, 0.6)
WARNING_COLOR = (0.6, 0.6, 0.4)
ERROR_COLOR = (0.8, 0.6, 0.6)

class ValidatorStartClass:
    def __init__(self, dpUIinst, langDic, langName, presetDic, presetName, CLASS_NAME, TITLE, DESCRIPTION, ICON):
        """ Initialize the module class creating a button in createGuidesLayout in order to be used to start the guide module.
        """
        # defining variables:
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        self.presetDic = presetDic
        self.presetName = presetName
        self.guideModuleName = CLASS_NAME
        self.title = TITLE
        self.description = DESCRIPTION
        self.icon = ICON
        self.ctrls = dpControls.ControlClass(self.dpUIinst, self.presetDic, self.presetName)
        self.active = True
        self.validatorCB = None
        self.verifyBT = None
        self.fixBT = None

        self.verifiedStatus = None
        self.fixedStatus = None

        self.ui = True
        self.checked = False

    
    def somethingHereMethod(self, cvName='', *args):
        """ WHITE DESCRIPTION HERE
        """
        # do something
        print("merci")
    
    

    def changeActive(self, value, *args):
        self.active = value
        
        #WIP
        ui = True
        if ui:

            cmds.checkBox(self.validatorCB, edit=True, value=value)
            cmds.button(self.verifyBT, edit=True, enable=value)
            cmds.button(self.fixBT, edit=True, enable=value)

    
    def runVerify(self, *args):
        print("here start class main run....")
        #WIP
        
        if self.ui:
            
            if self.checked:
                cmds.button(self.verifyBT, edit=True, backgroundColor=WARNING_COLOR)
                cmds.button(self.fixBT, edit=True, backgroundColor=CHECKED_COLOR)
                print("HERE IN MAIN checked")
            else:
                cmds.button(self.verifyBT, edit=True, backgroundColor=ERROR_COLOR)
                cmds.button(self.fixBT, edit=True, backgroundColor=DEFAULT_COLOR)