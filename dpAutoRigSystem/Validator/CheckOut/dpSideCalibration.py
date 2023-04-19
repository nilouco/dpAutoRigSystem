# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass
from importlib import reload
reload(dpBaseValidatorClass)

# global variables to this module:    
CLASS_NAME = "SideCalibration"
TITLE = "v044_sideCalibration"
DESCRIPTION = "v045_sideCalibrationDesc"
ICON = "/Icons/dp_sideCalibration.png"

dpSideCalibration_Version = 1.0

class SideCalibration(dpBaseValidatorClass.ValidatorStartClass):
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
            remainingList = toCheckList
            pairDic = {}
            progressAmount = 0
            maxProcess = len(toCheckList)
            for item in toCheckList:
                if self.verbose:
                    # Update progress window
                    progressAmount += 1
                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.langDic[self.dpUIinst.langName][self.title]+': '+repr(progressAmount)))
                # conditional to check here
                if cmds.objExists(item+".calibrationList"):
                    if item in remainingList:
                        remainingList.remove(item)

                        if item[1] == "_": #side: because L_CtrlName or R_CtrlName have "_" as second letter.
                            foundOtherSide = False
                            for node in remainingList:
                                if node[2:] == item[2:]: #other side found
                                    pairDic[item] = node
                                    remainingList.remove(node)
                                    foundOtherSide = True
                                    break
                            if foundOtherSide:
                                print(pairDic)
                                
                                calibrationAttr = cmds.getAttr(item+".calibrationList")
                                if calibrationAttr:
                                    calibrationList = calibrationAttr.split(";")
                                    print("item, calibrationList = ", item, calibrationList)
                                    if calibrationList:
                                        
                                        for attr in calibrationList:
                                            if not float(format(cmds.getAttr(item+"."+attr),".3f")) == float(format(cmds.addAttr(item+"."+attr, query=True, defaultValue=True),".3f")):
                                                print("not default")

                                        self.checkedObjList.append(item)
                                        self.foundIssueList.append(True)
                                        if self.verifyMode:
                                            self.resultOkList.append(False)
                                        else: #fix
                                            try:




                                                self.resultOkList.append(True)
                                                self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v004_fixed']+": "+item)
                                            except:
                                                self.resultOkList.append(False)
                                                self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v005_cantFix']+": "+item)
                else:
                    remainingList.remove(item)
            print(remainingList)
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