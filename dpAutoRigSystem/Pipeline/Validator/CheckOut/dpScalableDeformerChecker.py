# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "ScalableDeformerChecker"
TITLE = "v109_scalableDeformerChecker"
DESCRIPTION = "v110_scalableDeformerCheckerDesc"
ICON = "/Icons/dp_scalableDeformerChecker.png"
WIKI = "07-‐-Validator#-scalable-deformer-checker"

DP_SCALABLEDEFORMERCHECKER_VERSION = 1.01


class ScalableDeformerChecker(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_SCALABLEDEFORMERCHECKER_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
    

    def runAction(self, firstMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If firstMode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked item
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.firstMode = firstMode
        self.cleanUpToStart()
        self.rigScaleOutputAttr = "rigScaleOutput"
        
        # ---
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            if objList:
                toCheckList = objList
            else:
                toCheckList = cmds.ls(selection=False, type=['skinCluster', 'deltaMush'])
            if toCheckList:
                optionCtrl = self.utils.getNodeByMessage("optionCtrl")
                if optionCtrl:
                    self.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                    rigScaleOutput = [optionCtrl+"."+self.rigScaleOutputAttr]
                    itemAttrToFixList = []
                    for node in toCheckList:
                        self.utils.setProgress(self.dpUIinst.lang[self.title])
                        nodeType = cmds.objectType(node)
                        # check skinCluster nodes and connections
                        if nodeType == "skinCluster":
                            if cmds.getAttr(node+".skinningMethod") != 0: # If it's not "Classic Linear"
                                if cmds.getAttr(node+".dqsSupportNonRigid") == False:
                                    itemAttrToFixList.append(node+".dqsSupportNonRigid")
                                for attrDqs in ["dqsScaleX", "dqsScaleY", "dqsScaleZ"]:
                                    scConnection = cmds.listConnections(node+"."+attrDqs, source=True, destination=True, plugs=True)
                                    if scConnection != rigScaleOutput:
                                        itemAttrToFixList.append(node+"."+attrDqs)
                        # check deltaMush nodes and connections
                        elif nodeType == "deltaMush":
                            for attr in ["scaleX", "scaleY", "scaleZ"]:
                                dmConnection = cmds.listConnections(node+"."+attr, source=True, destination=True, plugs=True)
                                if dmConnection != rigScaleOutput:
                                    itemAttrToFixList.append(node+"."+attr)
                    if itemAttrToFixList:
                        for itemAttr in itemAttrToFixList:
                            self.checkedObjList.append(itemAttr)
                            self.foundIssueList.append(True)
                            if self.firstMode:
                                self.resultOkList.append(False)
                            else: #fix
                                try:
                                    if itemAttr.endswith("dqsSupportNonRigid"):
                                        # check non-rigid support attribute
                                        cmds.setAttr(itemAttr, True)
                                    else:
                                        # connect the rigScaleOutput to the deformer scale attributes
                                        cmds.connectAttr(rigScaleOutput[0], itemAttr, force=True)
                                    self.resultOkList.append(True)
                                    self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+itemAttr)
                                except:
                                    self.resultOkList.append(False)
                                    self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+itemAttr)
                                cmds.select(clear=True)
                else:
                    self.notFoundNodes("Option_Ctrl")
            else:
                self.notFoundNodes()
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic
