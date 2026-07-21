# importing libraries:
from maya import cmds
from maya import mel
from ....library.base import action

# global variables to this module:
CLASS_NAME = "PruneSkinWeights"
TITLE = "v103_pruneSkinWeights"
DESCRIPTION = "v104_pruneSkinWeightsDesc"
WIKI = "07-‐-Validator#-prune-skin-weights"



class PruneSkinWeights(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
    

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
        self.pruneMinValue = 0.0005
        
        # ---
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            if objList:
                toCheckList = objList
            else:
                toCheckList = cmds.ls(selection=False, type='skinCluster')
            if toCheckList:
                self.ar.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                for skinClusterNode in toCheckList:
                    self.ar.utils.setProgress(self.ar.data.lang[self.title])
                    meshList = cmds.skinCluster(skinClusterNode, query=True, geometry=True)
                    if meshList:
                        weightsList = self.ar.skin.getSkinWeights(meshList[0], skinClusterNode)
                        toPruneList = []
                        # check low weights
                        for v, weightDic in enumerate(weightsList):
                            for w in weightDic.keys():
                                if weightDic[w] < self.pruneMinValue:
                                    toPruneList.append(v)
                                    break
                        # conditional to check here
                        if toPruneList:
                            self.checkedObjList.append(skinClusterNode)
                            self.foundIssueList.append(True)
                            if self.firstMode:
                                self.resultOkList.append(False)
                            else: #fix
                                try:
                                    #cmds.skinCluster(skinClusterNode, edit=True, prune=True)
                                    influenceList = cmds.skinCluster(skinClusterNode, query=True, influence=True)
                                    for jnt in influenceList:
                                        cmds.setAttr(jnt+".liw", 0) #unlock
                                    cmds.select(meshList[0])
                                    mel.eval('doPruneSkinClusterWeightsArgList 2 { "'+str(self.pruneMinValue)+'", "1" };')
                                    self.resultOkList.append(True)
                                    self.messageList.append(self.ar.data.lang['v004_fixed']+": "+skinClusterNode+" = "+str(len(toPruneList))+" vertices")
                                except:
                                    self.resultOkList.append(False)
                                    self.messageList.append(self.ar.data.lang['v005_cantFix']+": "+skinClusterNode)
                                cmds.select(clear=True)
            else:
                self.notFoundNodes()
        else:
            self.notWorkedWellIO(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic
