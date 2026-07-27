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
    

    def runAction(self, first_mode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If first_mode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checked_items = node list of checked item
                - found_issues = True if an issue was found, False if there isn't an issue for the checked node
                - good_results = True if well done, False if we got an error
                - messages = reported text
        """
        # starting
        self.first_mode = first_mode
        self.cleanup_to_start()
        self.pruneMinValue = 0.0005
        
        # ---
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            if objList:
                check_items = objList
            else:
                check_items = cmds.ls(selection=False, type='skinCluster')
            if check_items:
                self.ar.utils.setProgress(max=len(check_items), addOne=False, addNumber=False)
                for skinClusterNode in check_items:
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
                            self.checked_items.append(skinClusterNode)
                            self.found_issues.append(True)
                            if self.first_mode:
                                self.good_results.append(False)
                            else: #fix
                                try:
                                    #cmds.skinCluster(skinClusterNode, edit=True, prune=True)
                                    influenceList = cmds.skinCluster(skinClusterNode, query=True, influence=True)
                                    for jnt in influenceList:
                                        cmds.setAttr(jnt+".liw", 0) #unlock
                                    cmds.select(meshList[0])
                                    mel.eval('doPruneSkinClusterWeightsArgList 2 { "'+str(self.pruneMinValue)+'", "1" };')
                                    self.good_results.append(True)
                                    self.messages.append(self.ar.data.lang['v004_fixed']+": "+skinClusterNode+" = "+str(len(toPruneList))+" vertices")
                                except:
                                    self.good_results.append(False)
                                    self.messages.append(self.ar.data.lang['v005_cantFix']+": "+skinClusterNode)
                                cmds.select(clear=True)
            else:
                self.not_found_node()
        else:
            self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.end_progress()
        return self.log_data
