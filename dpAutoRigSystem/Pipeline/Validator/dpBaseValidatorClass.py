# importing libraries:
from maya import cmds
import time
import getpass

# global variables to this module:
DEFAULT_COLOR = (0.5, 0.5, 0.5)
CHECKED_COLOR = (0.7, 1.0, 0.7)
WARNING_COLOR = (1.0, 1.0, 0.5)
ISSUE_COLOR = (1.0, 0.7, 0.7)

DP_VALIDATORSTARTCLASS_VERSION = 2.3


class ValidatorStartClass(object):
    def __init__(self, dpUIinst, CLASS_NAME, TITLE, DESCRIPTION, ICON, ui=True, verbose=True):
        """ Initialize the module class creating a button in createGuidesLayout in order to be used to start the guide module.
        """
        # defining variables:
        self.dpUIinst = dpUIinst
        self.utils = dpUIinst.utils
        self.guideModuleName = CLASS_NAME
        self.title = TITLE
        self.description = DESCRIPTION
        self.icon = ICON
        self.ui = ui
        self.verbose = verbose
        self.active = True
        self.validatorCB = None
        self.verifyBT = None
        self.fixBT = None
        # returned lists
        self.checkedObjList = []
        self.foundIssueList = []
        self.resultOkList = []
        self.messageList = []
        self.dataLogDic = {}


    def changeActive(self, value, *args):
        """ Set active attribute to given value.
            If there's an UI it will work to update the checkBox and buttons.
        """
        self.active = value
        if self.ui:
            cmds.checkBox(self.validatorCB, edit=True, value=value)
            cmds.button(self.verifyBT, edit=True, enable=value)
            cmds.button(self.fixBT, edit=True, enable=value)


    def cleanUpToStart(self, *args):
        """ Just redeclare variables and close openned window to run the code properly.
        """
        # redeclare variables
        self.checkedObjList = []
        self.foundIssueList = []
        self.resultOkList = []
        self.messageList = []
        self.dataLogDic = {}
        # close info log window if it exists
        if cmds.window('dpInfoWindow', query=True, exists=True):
            cmds.deleteUI('dpInfoWindow', window=True)
        if self.verbose:
            # Starting progress window
            cmds.progressWindow(title="dpValidator", progress=0, status=self.dpUIinst.lang[self.title]+': 0%', isInterruptable=False)


    def updateButtonColors(self, *args):
        """ Update button background colors if using UI.
        """
        if self.ui:
            if cmds.button(self.verifyBT, exists=True):
                if self.checkedObjList:
                    if self.verifyMode:
                        if True in self.foundIssueList:
                            cmds.button(self.verifyBT, edit=True, backgroundColor=ISSUE_COLOR)
                            cmds.button(self.fixBT, edit=True, backgroundColor=WARNING_COLOR)
                        else:
                            cmds.button(self.verifyBT, edit=True, backgroundColor=CHECKED_COLOR)
                            cmds.button(self.fixBT, edit=True, backgroundColor=DEFAULT_COLOR)
                    else: #fix
                        if False in self.resultOkList:
                            cmds.button(self.verifyBT, edit=True, backgroundColor=WARNING_COLOR)
                            cmds.button(self.fixBT, edit=True, backgroundColor=ISSUE_COLOR)
                        else:
                            cmds.button(self.verifyBT, edit=True, backgroundColor=DEFAULT_COLOR)
                            cmds.button(self.fixBT, edit=True, backgroundColor=CHECKED_COLOR)
                else:
                    if self.verifyMode:
                        cmds.button(self.verifyBT, edit=True, backgroundColor=CHECKED_COLOR)
                        cmds.button(self.fixBT, edit=True, backgroundColor=DEFAULT_COLOR)
                    else: #fix
                        cmds.button(self.verifyBT, edit=True, backgroundColor=DEFAULT_COLOR)
                        cmds.button(self.fixBT, edit=True, backgroundColor=CHECKED_COLOR)
    

    def reportLog(self, *args):
        """ Prepare the log output text and data dictionary for this checked validator.
        """
        thisTime = str(time.asctime(time.localtime(time.time())))
        # texts
        nameText = self.dpUIinst.lang['m006_name']
        titleText = self.dpUIinst.lang[self.title]
        modeText = self.dpUIinst.lang['v003_mode']
        fixText = self.dpUIinst.lang['c052_fix'].upper()
        verifyText = self.dpUIinst.lang['i210_verify'].upper()
        foundIssueText = self.dpUIinst.lang['v006_foundIssue']
        everythingOkText = self.dpUIinst.lang['v007_allOk']
        # header
        logText = "\n"+nameText+": "+titleText+"\n"
        # mode
        logText += modeText+": "
        checkText = fixText
        if self.verifyMode:
            checkText = verifyText
        logText += checkText+"\n"
        # issues
        if True in self.foundIssueList:
            logText += foundIssueText+":\n"
            for i, item in enumerate(self.foundIssueList):
                if item == True:
                    logText += self.checkedObjList[i]
                    if i != len(self.checkedObjList)-1:
                        logText += "\n"
        else:
            logText += everythingOkText
        # messages
        if self.messageList:
            for msg in self.messageList:
                logText += "\n"+msg
        # dataLog
        self.dataLogDic["user"] = getpass.getuser()
        self.dataLogDic["time"] = thisTime
        self.dataLogDic["validator"] = self.guideModuleName
        self.dataLogDic["name"] = self.title
        self.dataLogDic["mode"] = checkText
        self.dataLogDic["checkedObjList"] = self.checkedObjList
        self.dataLogDic["foundIssueList"] = self.foundIssueList
        self.dataLogDic["resultOkList"] = self.resultOkList
        self.dataLogDic["messageList"] = self.messageList
        self.dataLogDic["logText"] = logText
        # verbose call info window
        if self.verbose:
            self.dpUIinst.infoWin('i019_log', 'v000_validator', thisTime+"\n"+logText, "left", 250, 250)
            print("\n-------------\n"+self.dpUIinst.lang['v000_validator']+"\n"+thisTime+"\n"+logText)
            if not self.utils.exportLogDicToJson(self.dataLogDic, subFolder=self.dpUIinst.dpData+"/"+self.dpUIinst.dpLog):
                print(self.dpUIinst.lang['i201_saveScene'])


    def endProgressBar(self, *args):
        if self.verbose:
            cmds.progressWindow(endProgress=True)

    
    def notFoundNodes(self, item=None, *args):
        """ Set dataLog when don't have any objects to verify.
        """
        self.checkedObjList.append(item)
        self.foundIssueList.append(False)
        self.resultOkList.append(True)
        self.messageList.append(self.dpUIinst.lang['v014_notFoundNodes'])
