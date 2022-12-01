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
            toCheckList = list(set(cmds.listRelatives(cmds.ls(selection=False, type='mesh'), type="transform", parent=True, fullPath=False)))
        if toCheckList:
            progressAmount = 0
            maxProcess = len(toCheckList)
            # get exception list to keep nodes in the scene
            exceptionList = []
            deformersToKeepList = ["skinCluster", "blendShape", "wrap", "cluster", "ffd", "wire", "shrinkWrap", "sculpt", "morph"]
            renderGrp = dpUtils.getNodeByMessage("renderGrp")
            if renderGrp:
                renderNodeList = cmds.listRelatives(renderGrp, allDescendents=True, children=True, type="transform", fullPath=False)
                if renderNodeList:
                    exceptionList += renderNodeList
            toKeep = []
            for item in toCheckList:
                if self.verbose:
                    # Update progress window
                    progressAmount += 1
                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.langDic[self.dpUIinst.langName][self.title]+': '+repr(progressAmount)))
                if cmds.objExists(item):
                    needToKeepIt = False

                    #outputList = cmds.listConnections(item, source=True, destination=False)
                    #print("outputList =", item, outputList)

    #                histList = cmds.listHistory(item)
    #                print ("item, histList ===", item, histList)
    #                for histNode in histList:
    #                    print(cmds.objectType(histNode))

                    defList = cmds.findDeformers(item)
#                    print ("defList ======", item, defList)
                    if defList:
                        for deformerNode in defList:
#                            print("def type =", cmds.objectType(deformerNode))
                            if cmds.objectType(deformerNode) in deformersToKeepList:
                                if not item in exceptionList:
                                    exceptionList.append(item)

                                if cmds.objectType(deformerNode) == "wrap":

                                    #print("foundWrap here", item)
                                    basePointConnectedList = cmds.listConnections(deformerNode+".basePoints", source=True, destination=False)
                                    #print("WRAP Basepoints", basePointConnectedList)
                                    if basePointConnectedList:
                                        exceptionList.append(basePointConnectedList[0])#cmds.listRelatives(basePointConnectedList[0], type="transform", parent=True, fullPath=True)[0])
                                    diverPointConnectedList = cmds.listConnections(deformerNode+".driverPoints", source=True, destination=False)
                                    print("WRAP driverPoints", diverPointConnectedList)
                                    if diverPointConnectedList:
                                        exceptionList.append(diverPointConnectedList[0])#[0], type="transform", parent=True, fullPath=True)[0])
                                    #basePoints
                                    #driverPoints
                        #if not needToKeepIt:
#                       #     print("here not needToKeepIt", item)
                        #    if not item in exceptionList:
                        #        cmds.delete(item)
#                                print("here, after deleted....", item)
                        #if needTo:
                        #    toKeep.append(item)
#                        print("result =", item, needToKeepIt)

                    #else:
                    #    if not item in exceptionList:
                    #        # TODO need to dont remove wrap deformer setup meshes!!!
                    #        cmds.delete(item)
                    #        print("DELETED :::::", item)


            
                #print("toKeep         ", toKeep)
                #print("toCheckListMesh", toCheckListMesh)

                #WIP
            print("exceptionList = ", exceptionList)
            for item in toCheckList:
                if not item in exceptionList:
                    if cmds.objExists(item):
                        cmds.delete(item)
                        print("Deleted item:", item)



                
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