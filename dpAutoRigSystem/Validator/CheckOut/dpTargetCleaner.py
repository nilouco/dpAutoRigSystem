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

dpTargetCleaner_Version = 1.2

DPKEEPITATTR = "dpKeepIt"

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
            toCheckList = None
            meshList = cmds.ls(selection=False, type='mesh')
            if meshList:
                toCheckList = list(set(cmds.listRelatives(meshList, type="transform", parent=True, fullPath=False)))
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
            for item in toCheckList:
                if cmds.objExists(item):
                    if cmds.objExists(item+"."+DPKEEPITATTR) and cmds.getAttr(item+"."+DPKEEPITATTR):
                        if not item in exceptionList:
                            exceptionList.append(item)
                    else:
                        inputDeformerList = cmds.findDeformers(item)
                        if inputDeformerList:
                            for deformerNode in inputDeformerList:
                                if cmds.objectType(deformerNode) in deformersToKeepList:
                                    if not item in exceptionList:
                                        exceptionList.append(item)
                                    if cmds.objectType(deformerNode) == "wrap":
                                        wrapAttrList = ["basePoints", "driverPoints"]
                                        for wrapAttr in wrapAttrList:
                                            wrapConnectedList = cmds.listConnections(deformerNode+"."+wrapAttr, source=True, destination=False)
                                            if wrapConnectedList:
                                                exceptionList.append(wrapConnectedList[0])
                                        
            # run validation tasks
            for item in toCheckList:
                if self.verbose:
                    # Update progress window
                    progressAmount += 1
                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.langDic[self.dpUIinst.langName][self.title]+': '+repr(progressAmount)))
                if cmds.objExists(item):
                    self.checkedObjList.append(item)
                    if not item in exceptionList:
                        self.foundIssueList.append(True)
                        if self.verifyMode:
                            self.resultOkList.append(False)
                        else: #fix        
                            try:
                                cmds.delete(item)
                                self.resultOkList.append(True)
                                self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v004_fixed']+": "+item)
                            except:
                                self.resultOkList.append(False)
                                self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v005_cantFix']+": "+item)
                    else:
                        self.foundIssueList.append(False)
                        self.resultOkList.append(True)
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