# importing libraries:
from maya import cmds
from maya import mel
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "ScalableDeformerChecker"
TITLE = "v109_scalableDeformerChecker"
DESCRIPTION = "v110_scalableDeformerCheckerDesc"
ICON = "/Icons/dp_scalableDeformerChecker.png"

DP_SCALABLEDEFORMERCHECKER_VERSION = 1.0


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
        
        # ---
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            if objList:
                toCheckList = objList
            else:
                toCheckList = cmds.ls(selection=False, type=['skinCluster', 'deltaMush'])
            if toCheckList:
                self.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                rigScaleOutput = ['Option_Ctrl.rigScaleOutput']          
                itemAttrToFixList = []
                for node in toCheckList:
                    nodeType = cmds.objectType(node)
                    # check skinCluster nodes and connections
                    if nodeType == "skinCluster":
                        skinMethod = cmds.getAttr(node + ".skinningMethod")
                        if skinMethod != 0: # If it's not "Classic Linear"
                            if cmds.getAttr(node + ".dqsSupportNonRigid") == False:
                                itemAttrToFixList.append(node+".dqsSupportNonRigid")
                            for attrDqs in ["dqsScaleX", "dqsScaleY", "dqsScaleZ"]:
                                scConnection = cmds.listConnections(node+"."+attrDqs, source=True, destination=True, plugs=True)
                                if scConnection != rigScaleOutput:
                                    itemAttrToFixList.append(node+"."+attrDqs)
                    # check deltaMush nodes and connections
                    elif nodeType == "deltaMush":
                        for attr in ["scaleX", "scaleY", "scaleZ"]:
                            dmConection = cmds.listConnections(node+"."+attr, source=True, destination=True, plugs=True)
                            if dmConection != rigScaleOutput:
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
