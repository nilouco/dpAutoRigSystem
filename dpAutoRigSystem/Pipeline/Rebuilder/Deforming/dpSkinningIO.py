# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction
import os

# global variables to this module:
CLASS_NAME = "SkinningIO"
TITLE = "r016_skinningIO"
DESCRIPTION = "r017_skinningIODesc"
ICON = "/Icons/dp_skinningIO.png"

DP_SKINNINGIO_VERSION = 1.0


class SkinningIO(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_SKINNINGIO_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_skinningIO"
        self.startName = "dpSkinning"
        self.importRefName = "dpSkinningIO_Import"
    

    def runAction(self, firstMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in export mode by default.
            If firstMode parameter is False, it'll run in import mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.firstMode = firstMode
        self.cleanUpToStart()
        
        # ---
        # --- rebuilder code --- beginning
        if not cmds.file(query=True, reference=True):
            if self.pipeliner.checkAssetContext():
                self.ioPath = self.getIOPath(self.ioDir)
                if self.ioPath:
                    if self.firstMode: #export
                        itemList = None
                        if objList:
                            itemList = objList
                        else:
                            itemList = self.dpUIinst.skin.getDeformedItemList(deformerTypeList=["skinCluster"], ignoreAttr=self.dpUIinst.skin.ignoreSkinningAttr)
                        if itemList:
                            self.exportDicToJsonFile(self.dpUIinst.skin.getSkinWeightData(itemList))
                        else:
                            self.maybeDoneIO("Render_Grp")
                    else: #import
                        skinWeightDic = self.importLatestJsonFile(self.getExportedList())
                        if skinWeightDic:
                            self.importSkinning(skinWeightDic)
                        else:
                            self.maybeDoneIO(self.dpUIinst.lang['r007_notExportedData'])
                else:
                    self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['r027_noAssetContext'])
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r072_noReferenceAllowed'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        self.refreshView()
        return self.dataLogDic


    def referOldWipFile(self, *args):
        """ Reference the latest wip rig file before the current, and return it's tranform elements, if there.
        """
        refNodeList = []
        wipFilesList = next(os.walk(self.pipeliner.pipeData['assetPath']))[2]
        if len(wipFilesList) > 1:
            wipFilesList.sort()
            if len(self.exportedList) > 1:
                self.refPathName = self.exportedList[-2][len(self.startName)+1:-5]
                if os.path.isfile(self.pipeliner.pipeData['assetPath']+"/"+self.refPathName+".ma"):
                    self.refPathName = self.refPathName+".ma"
                else:
                    self.refPathName = self.refPathName+".mb"
                self.refPathName = self.pipeliner.pipeData['assetPath']+"/"+wipFilesList[-2]
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
                        if refNodeName[refNodeName.rfind(":")+1:] == self.dpUIinst.skin.getIOFileName(item):
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
                self.dpUIinst.skin.importSkinWeightsFromFile(toImportList, self.ioPath, self.latestDataFile, False)
                self.wellDoneIO(self.latestDataFile)
            except Exception as e:
                self.notWorkedWellIO(self.latestDataFile+": "+str(e))
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+" "+str(', '.join(skinWeightDic.keys())))
        if not wellImported:
            if changedShapeMeshList:
                self.notWorkedWellIO(self.dpUIinst.lang['r018_changedMesh']+" shape "+str(', '.join(changedShapeMeshList)))
            elif changedTopoMeshList:
                self.notWorkedWellIO(self.dpUIinst.lang['r018_changedMesh']+" topology "+str(', '.join(changedTopoMeshList)))
            elif notFoundMeshList:
                self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+" "+str(', '.join(notFoundMeshList)))
