# importing libraries:
from maya import cmds
from .. import dpBaseActionClass
import os

# global variables to this module:
CLASS_NAME = "SkinningIO"
TITLE = "r016_skinningIO"
DESCRIPTION = "r017_skinningIODesc"
ICON = "/Icons/dp_skinningIO.png"

DP_SKINNINGIO_VERSION = 1.0


class SkinningIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_SKINNINGIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
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
        # ensure file has a name to define dpData path
        if not cmds.file(query=True, sceneName=True):
            self.notWorkedWellIO(self.dpUIinst.lang['i201_saveScene'])
        else:
            self.ioPath = self.getIOPath(self.ioDir)
            if self.ioPath:

                if self.firstMode: #export
                    meshList = None
                    if objList:
                        meshList = objList
                    else:
                        meshList = self.dpUIinst.skin.getSkinnedModelList()
                    if meshList:
                        progressAmount = 0
                        maxProcess = len(meshList)
                        if self.verbose:
                            # Update progress window
                            progressAmount += 1
                            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                        try:
                            # export skinning data
                            self.pipeliner.makeDirIfNotExists(self.ioPath)
                            jsonName = self.ioPath+"/"+self.startName+"_"+self.pipeliner.getCurrentFileName()+".json"
                            skinWeightDic = self.dpUIinst.skin.getSkinWeightData(meshList)
                            self.pipeliner.saveJsonFile(skinWeightDic, jsonName)
                            self.wellDoneIO(jsonName)
                        except:
                            self.notWorkedWellIO(', '.join(meshList))
                    else:
                        self.notWorkedWellIO("Render_Grp")
                else: #import
                    self.exportedList = self.getExportedList()
                    if self.exportedList:
                        self.exportedList.sort()
                        skinWeightDic = self.pipeliner.getJsonContent(self.ioPath+"/"+self.exportedList[-1])
                        if skinWeightDic:
                            progressAmount = 0
                            maxProcess = len(skinWeightDic.keys())

                            wellImported = True
                            toImportList, notFoundMeshList, changedTopoMeshList = [], [], []
                            
                            mayaVersion = cmds.about(version=True)
                            

                            self.currentPath = self.pipeliner.getCurrentPath()
                            # reference old wip rig version to compare meshes changes
                            refNodeList = self.referOldWipFile()
                            print("refNodeList =", refNodeList)
                            for mesh in skinWeightDic.keys():
                                if self.verbose:
                                    # Update progress window
                                    progressAmount += 1
                                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))

                                if cmds.objExists(mesh):
                                    


                                    if refNodeList:
                                        for refNodeName in refNodeList:

                                            if refNodeName[refNodeName.rfind(":")+1:] == self.dpUIinst.skin.getIOFileName(mesh):
                                                if cmds.polyCompare(mesh, refNodeName, vertices=True) > 0 or cmds.polyCompare(mesh, refNodeName, edges=True) > 0: #check if topology changes
                                                    changedTopoMeshList.append(mesh)
                                                    
                                                    print ("changed topology =", mesh)
                                                    wellImported = False
                                                else:
                                                    toImportList.append(mesh)
                                    else:
                                        toImportList.append(mesh)

#                                    for skinClusterNode in skinWeightDic[mesh].keys():
#                                        print("mesh, skinClusterNode, dic =", mesh, skinClusterNode, skinWeightDic[mesh][skinClusterNode])

                                        #WIP
                                        # redo/update skinCluster here...
                                        # use dpWeights ??
                                        
                                        #skinWeightDic[mesh][skinClusterNode]

                                        
                                        
                                else:
                                    print("MESH doesn't exist.....", mesh)
                                    notFoundMeshList.append(mesh)
                                    
                            if refNodeList:
                                cmds.file(self.refPathName, removeReference=True)
                            print("toImportList 0000 =", toImportList)
                            if toImportList:
                                try:
                                    
                                    self.dpUIinst.skin.importSkinWeightsFromFile(toImportList, self.ioPath, self.exportedList[-1])
                                    self.wellDoneIO(', '.join(toImportList))
                                except Exception as e:
                                    self.notWorkedWellIO(self.exportedList[-1]+": "+str(e))

                    else:
                        self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        cmds.refresh()
        return self.dataLogDic


    def referOldWipFile(self, *args):
        """ Reference the latest wip rig file before the current, and return it's tranform elements, if there.
        """
        refNodeList = []
        wipFilesList = next(os.walk(self.currentPath))[2]
        if len(wipFilesList) > 1:
            wipFilesList.sort()
            if len(self.exportedList) > 1:
                self.refPathName = self.exportedList[-2][len(self.startName)+1:-5]
                if os.path.isfile(self.currentPath+"/"+self.refPathName+".ma"):
                    self.refPathName = self.refPathName+".ma"
                else:
                    self.refPathName = self.refPathName+".mb"
                self.refPathName = self.pipeliner.getCurrentPath()+"/"+wipFilesList[-2]
                cmds.file(self.refPathName, reference=True, namespace=self.importRefName)
                refNode = cmds.file(self.refPathName, referenceNode=True, query=True)
                refNodeList = cmds.referenceQuery(refNode, nodes=True)
                if refNodeList:
                    refNodeList = cmds.ls(refNodeList, type="transform")
        return refNodeList
