# importing libraries:
from maya import cmds
from maya import mel
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "PruneSkinWeights"
TITLE = "v103_pruneSkinWeights"
DESCRIPTION = "v104_pruneSkinWeightsDesc"
ICON = "/Icons/dp_pruneSkinWeights.png"

DP_PRUNESKINWEIGHTS_VERSION = 1.0


class PruneSkinWeights(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_PRUNESKINWEIGHTS_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
    

    def runAction(self, firstMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If firstMode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.firstMode = firstMode
        self.cleanUpToStart()
        pruneMinValue = 0.01
        
        # ---
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            if objList:
                toCheckList = objList
            else:
                toCheckList = cmds.ls(selection=False, type='skinCluster')
            if toCheckList:
                self.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                for item in toCheckList:
                    self.utils.setProgress(self.dpUIinst.lang[self.title])
                    # conditional to check here

                    #WIP

                    mesh = cmds.skinCluster(item, query=True, geometry=True)[0]
                    print("mesh =", mesh)
                    weightsDic = self.dpUIinst.skin.getSkinWeights(mesh, item)
                    print("weightsDic =", weightsDic)
                    
                    verticesList = []
                    influenceList = cmds.skinCluster(item, query=True, influence=True)
                    weightedInfluenceList = cmds.skinCluster(item, query=True, weightedInfluence=True)
                    if not len(influenceList) == len(weightedInfluenceList):
                    


                        self.checkedObjList.append(item)
                        self.foundIssueList.append(True)
                        if self.firstMode:
                            self.resultOkList.append(False)
                        else: #fix
                            try:
                                cmds.skinCluster(item, edit=True, prune=True)
                                mel.eval('doPruneSkinClusterWeightsArgList 2 { "'+str(pruneMinValue)+'", "1" };')
                                self.resultOkList.append(True)
                                self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+item+" = "+str(len(verticesList))+" vertices")
                            except:
                                self.resultOkList.append(False)
                                self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item)
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
