# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "BlendshapeTarget"
TITLE = "v012_blendshapeTarget"
DESCRIPTION = "v013_blendshapeTargetDesc"
WIKI = "07-‐-Validator#-blendshape-target-cleaner"

DPKEEPITATTR = "dpKeepIt"



class BlendshapeTarget(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
    

    def runAction(self, first_mode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If first_mode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checked_items = node list of checked items
                - found_issues = True if an issue was found, False if there isn't an issue for the checked node
                - good_results = True if well done, False if we got an error
                - messages = reported text
        """
        # starting
        self.first_mode = first_mode
        self.cleanup_to_start()
        
        # ---
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            if objList:
                toCheckList = objList
            else:
                toCheckList = None
                meshList = cmds.ls(selection=False, type='mesh')
                if meshList:
                    toCheckList = list(set(cmds.listRelatives(meshList, type="transform", parent=True, fullPath=False)))
            if toCheckList:
                self.ar.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                # get exception list to keep nodes in the scene
                deformersToKeepList = ["skinCluster", "blendShape", "wrap", "cluster", "ffd", "wire", "shrinkWrap", "sculpt", "morph"]
                exceptionList = self.keepGrp(["supportGrp", "renderGrp", "proxyGrp"])
                for item in toCheckList:
                    if cmds.objExists(item):
                        if cmds.objExists(item+"."+DPKEEPITATTR) and cmds.getAttr(item+"."+DPKEEPITATTR):
                            if not item in exceptionList:
                                exceptionList.append(item)
                        elif self.ar.utils.getSuffixNumberList(item)[1].endswith("Base"):
                            exceptionList.append(item)
                        else:
                            try:
                                inputDeformerList = cmds.findDeformers(item)
                            except:
                                self.messages.append(self.ar.data.lang['i075_moreOne']+": "+item)
                                inputDeformerList = False
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
                    self.ar.utils.setProgress(self.ar.data.lang[self.title])
                    if cmds.objExists(item):
                        self.checked_items.append(item)
                        if not item in exceptionList:
                            self.found_issues.append(True)
                            if self.first_mode:
                                self.good_results.append(False)
                            else: #fix        
                                try:
                                    fatherItemList = cmds.listRelatives(item, parent=True, type="transform")
                                    cmds.delete(item)
                                    if fatherItemList:
                                        brotherList = cmds.listRelatives(fatherItemList[0], allDescendents=True, children=True)
                                        if not brotherList:
                                            cmds.delete(fatherItemList[0])
                                    self.good_results.append(True)
                                    self.messages.append(self.ar.data.lang['v004_fixed']+": "+item)
                                except:
                                    self.good_results.append(False)
                                    self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item)
                        else:
                            self.found_issues.append(False)
                            self.good_results.append(True)
            else:
                self.not_found_node()
        else:
            self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.endProgress()
        return self.log_data


    def keepGrp(self, grpList, *args):
        """ Check if there're some nodes in the given group to return them.
        """
        resultList = []
        if grpList:
            for item in grpList:
                nodeGrp = self.ar.utils.getNodeByMessage(item)
                if nodeGrp:
                    nodeList = cmds.listRelatives(nodeGrp, allDescendents=True, children=True, type="transform", fullPath=False)
                    if nodeList:
                        resultList.extend(nodeList)
        return resultList