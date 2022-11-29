# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass
from ...Modules.Library import dpUtils
from importlib import reload
reload(dpBaseValidatorClass)

# global variables to this module:    
CLASS_NAME = "TargetCleaner"
TITLE = "v012_targetCleaner"
DESCRIPTION = "v013_targetCleanerDesc"
ICON = "/Icons/dp_targetCleaner.png"

dpTargetCleaner_Version = 1.0

class TargetCleaner(dpBaseValidatorClass.ValidatorStartClass):
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
            #toCheckList = cmds.listRelatives(cmds.ls(selection=False, type='mesh'), type="transform", parent=True, fullPath=True)
            toCheckList = cmds.ls(selection=False, type='mesh')
        if toCheckList:
            progressAmount = 0
            maxProcess = len(toCheckList)
            # get exception list to keep nodes in the scene
            exceptionList = []
            renderGrp = dpUtils.getNodeByMessage("renderGrp")
            if renderGrp:
                renderNodeList = cmds.listRelatives(renderGrp, allDescendents=True, children=True, type="transform", fullPath=True)
                if renderNodeList:
                    exceptionList += renderNodeList
            
            for item in toCheckList:
                #outputList = cmds.listConnections(item, source=True, destination=False)
                #print("outputList =", item, outputList)

#                histList = cmds.listHistory(item)
#                print ("item, histList ===", item, histList)
#                for histNode in histList:
#                    print(cmds.objectType(histNode))

                defList = cmds.findDeformers(item)
                print (item, defList)
                if defList:
                    for deformerNode in defList:
                        print("def type =", cmds.objectType(deformerNode))


            print("exceptionList ===", exceptionList)


            for item in toCheckList:
                if self.verbose:
                    # Update progress window
                    progressAmount += 1
                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.langDic[self.dpUIinst.langName][self.title]+': '+repr(progressAmount)))
                
                #WIP
                if not item in exceptionList:
                    print("to clean up node:", item)




                
                parentNode = item
                self.checkedObjList.append(parentNode)
                if not '_Mesh' in item:
                    self.foundIssueList.append(True)
                    if self.verifyMode:
                        self.resultOkList.append(False)
                    else: #fix
                        try:
                            #WIP: (index to fix error OMG!)
                            parentNode = cmds.listRelatives(item, parent=True)[0] # change index here to test
                            #raise Exception("Carreto trombado na pista")
                            cmds.rename(parentNode, parentNode+"_Mesh")
                            self.resultOkList.append(True)
                            self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v004_fixed']+": "+parentNode)
                        except:
                            self.resultOkList.append(False)
                            self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v005_cantFix']+": "+parentNode)
                else:
                    self.foundIssueList.append(False)
                    self.resultOkList.append(True)
        else:
            self.checkedObjList.append("")
            self.foundIssueList.append(True)
            self.resultOkList.append(False)
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