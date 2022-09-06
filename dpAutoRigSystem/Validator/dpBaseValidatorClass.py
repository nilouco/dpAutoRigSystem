# importing libraries:
from maya import cmds
from maya import mel
from ..Modules.Library import dpControls
from ..Modules.Library import dpUtils


DEFAULT_COLOR = (0.5, 0.5, 0.5)
CHECKED_COLOR = (0.7, 1.0, 0.7)
WARNING_COLOR = (1.0, 1.0, 0.5)
ERROR_COLOR = (1.0, 0.7, 0.7)


class ValidatorStartClass:
    def __init__(self, dpUIinst, langDic, langName, presetDic, presetName, CLASS_NAME, TITLE, DESCRIPTION, ICON, ui=True):
        """ Initialize the module class creating a button in createGuidesLayout in order to be used to start the guide module.
        """
        # defining variables:
        self.dpUIinst = dpUIinst
        self.guideModuleName = CLASS_NAME
        self.title = TITLE
        self.description = DESCRIPTION
        self.icon = ICON
        self.ui = ui
        self.ctrls = dpControls.ControlClass(self.dpUIinst, self.dpUIinst.presetDic, self.dpUIinst.presetName)
        self.active = True
        self.validatorCB = None
        self.verifyBT = None
        self.fixBT = None
        self.checked = False
        self.okVerified = None
        self.okFixed = None

    
    def changeActive(self, value, *args):
        ''' Set active attribute to given value.
            If there's an UI it will work to update the checkBox and buttons.
        '''
        self.active = value
        if self.ui:
            cmds.checkBox(self.validatorCB, edit=True, value=value)
            cmds.button(self.verifyBT, edit=True, enable=value)
            cmds.button(self.fixBT, edit=True, enable=value)

    
    def updateButtonColors(self, *args):
        ''' Base method to verify the validator instructions.
        '''
        # update UI button colors
        if self.ui:
            if self.checked:
                if self.okVerified:
                    cmds.button(self.verifyBT, edit=True, backgroundColor=CHECKED_COLOR)
                    cmds.button(self.fixBT, edit=True, backgroundColor=DEFAULT_COLOR)
                elif self.okFixed:
                    cmds.button(self.verifyBT, edit=True, backgroundColor=DEFAULT_COLOR)
                    cmds.button(self.fixBT, edit=True, backgroundColor=CHECKED_COLOR)
                else:
                    cmds.button(self.verifyBT, edit=True, backgroundColor=ERROR_COLOR)
                    cmds.button(self.fixBT, edit=True, backgroundColor=WARNING_COLOR)
            else:
                cmds.button(self.verifyBT, edit=True, backgroundColor=DEFAULT_COLOR)
                cmds.button(self.fixBT, edit=True, backgroundColor=DEFAULT_COLOR)
    

    def runFix(self, *args):
        ''' Base method to fix the validator instructions.
        '''
        # WIP 
        print("Running fix from baseClass")

