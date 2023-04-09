# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass
from importlib import reload
reload(dpBaseValidatorClass)

# global variables to this module:    
CLASS_NAME = "ExitEditMode"
TITLE = "v034_exitEditMode"
DESCRIPTION = "v035_exitEditModeDesc"
ICON = "/Icons/dp_exitEditMode.png"

dpExitEditMode_Version = 1.0

class ExitEditMode(dpBaseValidatorClass.ValidatorStartClass):
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
            toCheckList = objList
        else:
            toCheckList = self.dpUIinst.ctrls.getControlList()
        if toCheckList:
            progressAmount = 0
            maxProcess = len(toCheckList)
            for item in toCheckList:
                if self.verbose:
                    # Update progress window
                    progressAmount += 1
                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.langDic[self.dpUIinst.langName][self.title]+': '+repr(progressAmount)))
                # conditional to check here
                if cmds.objExists(item+".editMode"):
                    if cmds.getAttr(item+".editMode") == 1:
                        self.checkedObjList.append(item)
                        self.foundIssueList.append(True)
                        if self.verifyMode:
                            self.resultOkList.append(False)
                        else: #fix
                            try:
                                # delete the corrective script job
                                self.dpUIinst.ctrls.deleteOldCorrectiveJobs(item)
                                # remove color override
                                shapeList = cmds.listRelatives(item, shapes=True, children=True, fullPath=True)
                                if shapeList:
                                    for shapeNode in shapeList:
                                        cmds.setAttr(shapeNode+".overrideRGBColors", 0)
                                # set edit mode off
                                cmds.setAttr(item+".editMode", 0)
                                self.resultOkList.append(True)
                                self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v004_fixed']+": "+item)
                            except:
                                self.resultOkList.append(False)
                                self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v005_cantFix']+": "+item)
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