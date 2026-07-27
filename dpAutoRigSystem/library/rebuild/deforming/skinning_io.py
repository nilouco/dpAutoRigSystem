# importing libraries:
from maya import cmds
from ....library.base import action
import os

# global variables to this module:
CLASS_NAME = "SkinningIO"
TITLE = "r016_skinningIO"
DESCRIPTION = "r017_skinningIODesc"
WIKI = "10-‐-Rebuilder#-skinning"



class SkinningIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_skinningIO"
        self.startName = "skinning"
        self.importRefName = "dpSkinningIO_Import"
    

    def runAction(self, first_mode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in export mode by default.
            If first_mode parameter is False, it'll run in import mode.
            Returns dataLog with the validation result as:
                - checked_items = node list of checked items
                - found_issues = True if an issue was found, False if there isn't an issue for the checked node
                - good_results = True if well done, False if we got an error
                - messages = reported text
        """
        # starting
        self.first_mode = first_mode
        self.cleanup_to_start(True)
        
        # ---
        # --- rebuilder code --- beginning
        if not cmds.file(query=True, reference=True):
            if self.ar.pipeliner.checkAssetContext():
                self.io_path = self.get_io_path(self.io_folder)
                if self.io_path:
                    if self.first_mode: #export
                        itemList = None
                        if objList:
                            itemList = objList
                        else:
                            itemList = self.ar.skin.getDeformedItemList(deformerTypeList=["skinCluster"], ignoreAttr=self.ar.skin.ignoreSkinningAttr)
                        if itemList:
                            self.exportDicToJsonFile(self.ar.skin.getSkinWeightData(itemList))
                        else:
                            self.maybe_done_io("Render_Grp")
                    else: #import
                        skinWeightDic = self.importLatestJsonFile(self.get_exported_items())
                        if skinWeightDic:
                            self.importSkinning(skinWeightDic)
                        else:
                            self.maybe_done_io(self.ar.data.lang['r007_notExportedData'])
                else:
                    self.fail_io(self.ar.data.lang['r010_notFoundPath'])
            else:
                self.fail_io(self.ar.data.lang['r027_noAssetContext'])
        else:
            self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.endProgress()
        self.refresh_view()
        return self.log_data


    def referOldWipFile(self, *args):
        """ Reference the latest wip rig file before the current, and return it's tranform elements, if there.
        """
        refNodeList = []
        wipFilesList = next(os.walk(self.ar.pipeliner.pipeData['assetPath']))[2]
        if len(wipFilesList) > 1:
            wipFilesList.sort()
            if len(self.exportedList) > 1:
                self.refPathName = self.exportedList[-2][len(self.startName)+1:-5]
                if os.path.isfile(self.ar.pipeliner.pipeData['assetPath']+"/"+self.refPathName+".ma"):
                    self.refPathName = self.refPathName+".ma"
                else:
                    self.refPathName = self.refPathName+".mb"
                self.refPathName = self.ar.pipeliner.pipeData['assetPath']+"/"+wipFilesList[-2]
                cmds.file(self.refPathName, reference=True, namespace=self.importRefName)
                refNode = cmds.file(self.refPathName, referenceNode=True, query=True)
                refNodeList = cmds.referenceQuery(refNode, nodes=True)
                if refNodeList:
                    refNodeList = cmds.ls(refNodeList, type="transform")
        return refNodeList


    def importSkinning(self, skinWeightDic, *args):
        """ Import the skinning from exported skin weight dictionary.
        """
        wellImported = True
        toImportList, notFoundMeshList, changedTopoMeshList, changedShapeMeshList = [], [], [], []
        
        # reference old wip rig version to compare meshes changes
        #refNodeList = self.referOldWipFile()
        refNodeList = None

        for item in skinWeightDic.keys():
            if cmds.objExists(item):
                if refNodeList: #disable at the momment
                    for refNodeName in refNodeList:
                        if refNodeName[refNodeName.rfind(":")+1:] == self.ar.skin.getIOFileName(item):
                            if cmds.polyCompare(item, refNodeName, vertices=True) > 0 or cmds.polyCompare(item, refNodeName, edges=True) > 0: #check if shape changes
                                changedShapeMeshList.append(item)
                                wellImported = False
                            elif not len(cmds.ls(item+".vtx[*]", flatten=True)) == len(cmds.ls(refNodeName+".vtx[*]", flatten=True)): #check if poly count changes
                                changedTopoMeshList.append(item)
                                wellImported = False
                            else:
                                toImportList.append(item)
                else:
                    toImportList.append(item)
            else:
                notFoundMeshList.append(item)
        if refNodeList:
            cmds.file(self.refPathName, removeReference=True)
        if toImportList:
            try:
                # import skin weights
                self.ar.skin.importSkinWeightsFromFile(toImportList, self.io_path, self.latestDataFile, False)
                self.well_done_io(self.latestDataFile)
            except Exception as e:
                self.fail_io(self.latestDataFile+": "+str(e))
        else:
            self.fail_io(self.ar.data.lang['v014_notFoundNodes']+" "+str(', '.join(skinWeightDic.keys())))
        if not wellImported:
            if changedShapeMeshList:
                self.fail_io(self.ar.data.lang['r018_changedMesh']+" shape "+str(', '.join(changedShapeMeshList)))
            elif changedTopoMeshList:
                self.fail_io(self.ar.data.lang['r018_changedMesh']+" topology "+str(', '.join(changedTopoMeshList)))
            elif notFoundMeshList:
                self.fail_io(self.ar.data.lang['v014_notFoundNodes']+" "+str(', '.join(notFoundMeshList)))
