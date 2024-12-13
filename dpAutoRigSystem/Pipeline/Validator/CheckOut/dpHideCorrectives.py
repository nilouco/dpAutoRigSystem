# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "HideCorrectives"
TITLE = "v036_hideCorrectives"
DESCRIPTION = "v037_hideCorrectivesDesc"
ICON = "/Icons/dp_hideCorrectives.png"

DP_HIDECORRECTIVES_VERSION = 1.3


class HideCorrectives(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_HIDECORRECTIVES_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
    

    def runAction(self, firstMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If firstMode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.firstMode = firstMode
        self.cleanUpToStart()
        
        # ---
        # --- validator code --- beginning
        optionCtrl = self.utils.getNodeByMessage("optionCtrl")
        if optionCtrl:
            if objList:
                toCheckList = cmds.attributeQuery('correctiveCtrls', node=objList[0], exists=True)
            else:
                toCheckList = cmds.attributeQuery('correctiveCtrls', node=optionCtrl, exists=True)
            if toCheckList:
                self.utils.setProgress(max=1)
                self.utils.setProgress(self.dpUIinst.lang[self.title])
                item = optionCtrl+".correctiveCtrls"
                # conditional to check here
                checkChannelBox = cmds.getAttr(item, channelBox=True)
                if checkChannelBox:
                    self.checkedObjList.append(item)
                    self.foundIssueList.append(True)
                    if self.firstMode:
                        self.resultOkList.append(False)
                    else: #fix
                        try:
                            cmds.setAttr(item, 0)
                            cmds.setAttr(item, lock=True, channelBox=False)
                            self.resultOkList.append(True)
                            self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+item)
                        except:
                            self.resultOkList.append(False)
                            self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item)
                else:
                    self.notFoundNodes()
        else:
            self.notFoundNodes()

        # --- validator code --- end
        # ---


        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic
    

    
