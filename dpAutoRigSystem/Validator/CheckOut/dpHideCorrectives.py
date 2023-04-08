# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass
from importlib import reload
reload(dpBaseValidatorClass)

# global variables to this module:    
CLASS_NAME = "HideCorrectives"
TITLE = "v034_hideCorrectives"
DESCRIPTION = "v035_hideCorrectivesDesc"
ICON = "/Icons/dp_validatorTemplate.png"

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
        if objList:
            toCheckList = objList
        else:
            # toCheckList = cmds.ls(selection=False, type='mesh')
            toCheckList = cmds.attributeQuery('correctiveCtrls', node='Option_Ctrl', exists=True)
            
            print("toCheckList =", toCheckList)


        if toCheckList:
            progressAmount = 0
            maxProcess = 1
            #for item in toCheckList:
            if self.verbose:
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.langDic[self.dpUIinst.langName][self.title]+': '+repr(progressAmount)))
            #parentNode = cmds.listRelatives(item, parent=True)[0]
            parentNode = "Option_Ctrl.correctiveCtrls"
            # conditional to check here
            
            checkChannelBox= cmds.getAttr(parentNode, channelBox=True)
            print("#########___checkChannelBox = ", checkChannelBox)

            checkLocked= cmds.getAttr(parentNode, lock=True)
            print("#########_____checkLocked = ", checkLocked)
            

            if checkChannelBox:
                print("*****passei aqui de kombi*****")
                self.checkedObjList.append(parentNode)
                self.foundIssueList.append(True)
                if self.verifyMode:
                    self.resultOkList.append(False)
                else: #fix
                    try:
                        #WIP: (index to fix error OMG!)
                        parentNode = "Option_Ctrl.correctiveCtrls"     #cmds.listRelatives(item, parent=True)[0] # change index here to test
                        #raise Exception("Carreto trombado na pista")
                        print("Passei aqui")
                        cmds.setAttr(parentNode, lock=True, channelBox=False)

                        self.resultOkList.append(True)
                        self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v004_fixed']+": "+parentNode)
                    except:
                        self.resultOkList.append(False)
                        self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v005_cantFix']+": "+parentNode)
            elif not checkLocked:
                print("*****passei aqui de Carreto*****")
                self.checkedObjList.append(parentNode)
                self.foundIssueList.append(True)
                if self.verifyMode:
                    self.resultOkList.append(False)
                else: #fix
                    try:
                        #WIP: (index to fix error OMG!)
                        parentNode = "Option_Ctrl.correctiveCtrls"     #cmds.listRelatives(item, parent=True)[0] # change index here to test
                        #raise Exception("Carreto trombado na pista")
                        print("Passei aqui")
                        cmds.setAttr(parentNode, lock=True, channelBox=False)

                        self.resultOkList.append(True)
                        self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v004_fixed']+": "+parentNode)
                    except:
                        self.resultOkList.append(False)
                        self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v005_cantFix']+": "+parentNode)
                    # else:
                    #     self.foundIssueList.append(False)
                    #     self.resultOkList.append(True)

            
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