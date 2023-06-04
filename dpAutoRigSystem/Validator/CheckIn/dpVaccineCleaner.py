# importing libraries:
from maya import cmds
import os
from .. import dpBaseValidatorClass

# global variables to this module:    
CLASS_NAME = "VaccineCleaner"
TITLE = "v052_vaccineCleaner"
DESCRIPTION = "v053_vaccineCleanerDesc"
ICON = "/Icons/dp_vaccineCleaner.png"

DP_VACCINECLEANER_VERSION = 1.1


class VaccineCleaner(dpBaseValidatorClass.ValidatorStartClass):
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
        self.cleanUpToStart()
        
        # ---
        # --- validator code --- beginning
        if objList:
            toCheckList = objList
        else:
            toCheckList = cmds.ls(selection=False, type='script')
        if toCheckList:
            progressAmount = 0
            maxProcess = len(toCheckList)
            for item in toCheckList:
                if self.verbose:
                    # Update progress window
                    progressAmount += 1
                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                # conditional to check here
                    scriptdata = cmds.scriptNode(item, beforeScript=True, query=True)
                    #if "fuck_All_U" in scriptdata:
                    if "_gene" in scriptdata:
                        self.checkedObjList.append(item)
                        self.foundIssueList.append(True)
                        if self.verifyMode:
                            self.resultOkList.append(False)
                        else: #fix
                            try:
                                cmds.delete(item)
                                path = cmds.internalVar(userAppDir=True)+"/scripts/"
                                vaccineList = ["vaccine.py", "vaccine.pyc"]
                                for vaccine in vaccineList:
                                    if os.path.exists(path+vaccine):
                                        os.remove(path+vaccine)
                                if os.path.exists(path+"userSetup.py"):
                                    self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item+"\n    - "+path+"userSetup.py")
                                else:
                                    self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+item)
                                cmds.select(clear=True)
                                self.resultOkList.append(True)
                            except:
                                self.resultOkList.append(False)
                                self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item)
        else:
            self.notFoundNodes()
        # --- validator code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        return self.dataLogDic
