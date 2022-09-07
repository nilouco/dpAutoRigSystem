# importing libraries:
from maya import cmds
from maya import mel
from ..Modules.Library import dpControls
from ..Modules.Library import dpUtils


DEFAULT_COLOR = (0.5, 0.5, 0.5)
CHECKED_COLOR = (0.7, 1.0, 0.7)
WARNING_COLOR = (1.0, 1.0, 0.5)
ISSUE_COLOR = (1.0, 0.7, 0.7)


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
        self.ctrls = dpControls.ControlClass(self.dpUIinst, self.dpUIinst.presetDic, self.dpUIinst.presetName)
        self.ui = ui
        self.verbose = False
        self.active = True
        self.validatorCB = None
        self.verifyBT = None
        self.fixBT = None
        # returned lists
        self.checkedObjList = []
        self.foundIssueList = []
        self.resultList = []
        self.messageList = []
        self.dataDic = {}


    
    def changeActive(self, value, *args):
        """ Set active attribute to given value.
            If there's an UI it will work to update the checkBox and buttons.
        """
        self.active = value
        if self.ui:
            cmds.checkBox(self.validatorCB, edit=True, value=value)
            cmds.button(self.verifyBT, edit=True, enable=value)
            cmds.button(self.fixBT, edit=True, enable=value)

    
    def updateButtonColors(self, *args):
        """ Update button background colors if using UI.
        """
        # update UI button colors
        if self.ui:
            if self.checkedObjList:
                if self.verifyMode:
                    if True in self.foundIssueList:
                        cmds.button(self.verifyBT, edit=True, backgroundColor=ISSUE_COLOR)
                        cmds.button(self.fixBT, edit=True, backgroundColor=WARNING_COLOR)
                    else:
                        cmds.button(self.verifyBT, edit=True, backgroundColor=CHECKED_COLOR)
                        cmds.button(self.fixBT, edit=True, backgroundColor=DEFAULT_COLOR)
                else: #fix
                    if True in self.foundIssueList:
                        cmds.button(self.verifyBT, edit=True, backgroundColor=WARNING_COLOR)
                        cmds.button(self.fixBT, edit=True, backgroundColor=ISSUE_COLOR)
                    else:
                        cmds.button(self.verifyBT, edit=True, backgroundColor=DEFAULT_COLOR)
                        cmds.button(self.fixBT, edit=True, backgroundColor=CHECKED_COLOR)
            else:
                cmds.button(self.verifyBT, edit=True, backgroundColor=DEFAULT_COLOR)
                cmds.button(self.fixBT, edit=True, backgroundColor=DEFAULT_COLOR)
    

    def reportLog(self, *args):
        """ Prepare the log output for this checked validator.
        """
        # WIP 
        print("\nReporting LOG.....")
        logText = self.dpUIinst.langDic[self.dpUIinst.langName]['v000_validatorHeader']

        if self.verifyMode:
            print("Mode = VERIFY")
            logText += "\nMode = VERIFY"
        else:
            print("Mode = FIX")
            logText += "\nMode = FIX"
        if self.verbose:
            print("self.checkedObjList = ", self.checkedObjList)
            print("self.foundIssueList = ", self.foundIssueList)
            print(logText)
        

