# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass
from ... Modules.Library import dpUtils
from importlib import reload
reload(dpBaseValidatorClass)

# global variables to this module:    
CLASS_NAME = "HideCorrectives"
TITLE = "v036_hideCorrectives"
DESCRIPTION = "v037_hideCorrectivesDesc"
ICON = "/Icons/dp_hideCorrectives.png"

dpHideCorrective = 1.0

class HideCorrectives(dpBaseValidatorClass.ValidatorStartClass):
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
        optionCtrl = dpUtils.getNodeByMessage("optionCtrl")
        if optionCtrl:
            if objList:
                toCheckList = cmds.attributeQuery('correctiveCtrls', node=objList[0], exists=True)
            else:
                toCheckList = cmds.attributeQuery('correctiveCtrls', node=optionCtrl, exists=True)
            if toCheckList:
                progressAmount = 0
                maxProcess = 1
                if self.verbose:
                    # Update progress window
                    progressAmount += 1
                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.langDic[self.dpUIinst.langName][self.title]+': '+repr(progressAmount)))
                item = optionCtrl+".correctiveCtrls"
                # conditional to check here
                checkChannelBox = cmds.getAttr(item, channelBox=True)
                if checkChannelBox:
                    self.checkedObjList.append(item)
                    self.foundIssueList.append(True)
                    if self.verifyMode:
                        self.resultOkList.append(False)
                    else: #fix
                        try:
                            cmds.setAttr(item, lock=True, channelBox=False)
                            self.resultOkList.append(True)
                            self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v004_fixed']+": "+item)
                        except:
                            self.resultOkList.append(False)
                            self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v005_cantFix']+": "+item)
                else:
                    self.noFoundNodes()
        else:
            self.noFoundNodes()

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


    def noFoundNodes(self, *args):
        """ Set dataLog when don't have any objects to verify.
        """
        self.checkedObjList.append("")
        self.foundIssueList.append(False)
        self.resultOkList.append(True)
        self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v014_notFoundNodes'])
