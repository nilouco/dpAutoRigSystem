# importing libraries:
from maya import cmds
from maya import mel
from . import dpWeights

DP_SKINNING_VERSION = 1.4


class Skinning(dpWeights.Weights):
    def __init__(self, *args, **kwargs):
        """ Initialize the class.
        """
        dpWeights.Weights.__init__(self, *args, **kwargs)
        # defining variables:
        self.skinInfoAttrList = ['skinningMethod', 'maintainMaxInfluences', 'maxInfluences']
        self.jointSuffixList = ['Jnt', 'Jar', 'Jad', 'Jcr', 'Jis']
        self.ignoreSkinningAttr = "dpDoNotSkinIt"
        self.ioStartName = "dpSkinning"
        

    def validateGeoList(self, geoList, mode=None, *args):
        """ Check if the geometry list from UI is good to be skinned, because we can get issue if the display long name is not used.
        """
        if geoList:
            for i, item in enumerate(geoList):
                if item in geoList[:i]:
                    self.dpUIinst.logger.infoWin('i038_canceled', 'e003_moreThanOneGeo', item, 'center', 205, 270)
                    return False
                elif not cmds.objExists(item):
                    self.dpUIinst.logger.infoWin('i038_canceled', 'i061_notExists', item, 'center', 205, 270)
                    return False
                elif not mode:
                    try:
                        inputDeformerList = cmds.findDeformers(item)
                        if inputDeformerList:
                            for deformerNode in inputDeformerList:
                                if cmds.objectType(deformerNode) == "skinCluster":
                                    self.dpUIinst.logger.infoWin('i038_canceled', 'i285_alreadySkinned', item, 'center', 205, 270)
                                    return False
                    except:
                        pass
        return True
    

    def skinFromUI(self, mode=None, *args):
        """ Skin the geometries using the joints, reading from UI the selected items of the textScrollLists or getting all items if nothing selected.
        """
        # log window
        logWin = cmds.checkBox(self.dpUIinst.allUIs["displaySkinLogWin"], query=True, value=True)

        # get joints to be skinned:
        uiJointSkinList = cmds.textScrollList(self.dpUIinst.allUIs["jntTextScrollLayout"], query=True, selectItem=True)
        if not uiJointSkinList:
            uiJointSkinList = cmds.textScrollList(self.dpUIinst.allUIs["jntTextScrollLayout"], query=True, allItems=True)
        
        # check if all items in jointSkinList exists, then if not, show dialog box to skinWithoutNotExisting or Cancel
        jointSkinList, jointNotExistingList = [], []
        if uiJointSkinList:
            for item in uiJointSkinList:
                if cmds.objExists(item):
                    jointSkinList.append(item)
                else:
                    jointNotExistingList.append(item)
        if jointNotExistingList:
            notExistingJointMessage = self.dpUIinst.lang['i069_notSkinJoint'] +"\n\n"+ ", ".join(str(jntNotExitst) for jntNotExitst in jointNotExistingList) +"\n\n"+ self.dpUIinst.lang['i070_continueSkin']
            btYes = self.dpUIinst.lang['i071_yes']
            btNo = self.dpUIinst.lang['i072_no']
            confirmSkinning = cmds.confirmDialog(title='Confirm Skinning', message=notExistingJointMessage, button=[btYes,btNo], defaultButton=btYes, cancelButton=btNo, dismissString=btNo)
            if confirmSkinning == btNo:
                jointSkinList = None
        
        # get geometries to be skinned:
        geomSkinList = cmds.textScrollList(self.dpUIinst.allUIs["modelsTextScrollLayout"], query=True, selectItem=True)
        if not geomSkinList:
            geomSkinList = cmds.textScrollList(self.dpUIinst.allUIs["modelsTextScrollLayout"], query=True, allItems=True)
        
        # check if we have repeated listed geometries in case of the user choose to not display long names:
        if self.validateGeoList(geomSkinList, mode):
            if jointSkinList and geomSkinList:
                for geomSkin in geomSkinList:
                    if (mode == "Add"):
                        cmds.skinCluster(geomSkin, edit=True, addInfluence=jointSkinList, toSelectedBones=True, lockWeights=True, weight=0.0)
                    elif (mode == "Remove"):
                        cmds.skinCluster(geomSkin, edit=True, removeInfluence=jointSkinList, toSelectedBones=True)
                    else: # None = create a new skinCluster node
                        baseName = self.utils.extractSuffix(geomSkin)
                        skinClusterName = baseName+"_SC"
                        if "|" in skinClusterName:
                            skinClusterName = skinClusterName[skinClusterName.rfind("|")+1:]
                        newSkinClusterNode = cmds.skinCluster(jointSkinList, geomSkin, toSelectedBones=True, dropoffRate=4.0, maximumInfluences=3, skinMethod=0, normalizeWeights=1, removeUnusedInfluence=False, name=skinClusterName)[0]
                        cmds.rename(cmds.listConnections(newSkinClusterNode+".bindPose", destination=False, source=True), newSkinClusterNode.replace("_SC", "_BP"))
                print(self.dpUIinst.lang['i077_skinned'] + ', '.join(geomSkinList))
                if logWin:
                    self.dpUIinst.logger.infoWin('i028_skinButton', 'i077_skinned', '\n'.join(geomSkinList), 'center', 205, 270)
                cmds.select(geomSkinList)
        else:
            print(self.dpUIinst.lang['i029_skinNothing'])
            if logWin:
                self.dpUIinst.logger.infoWin('i028_skinButton', 'i029_skinNothing', ' ', 'center', 205, 270)

    
    def serializeCopySkin(self, sourceList, destinationList, oneSource=True, byUVs=False, *args):
        """ Serialize the copy skinning for one source or many items with the same name.
        """
        ranList = []
        maxProcess = len(destinationList)
        progressAmount = 0
        cmds.progressWindow(title=self.dpUIinst.lang['i287_copy']+" Skinning", progress=progressAmount, status='Skinning: 0%', isInterruptable=False)
        for sourceItem in sourceList:
            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=('Skinning: '+repr(progressAmount)))
            if oneSource:
                for item in destinationList:
                    self.runCopySkin(sourceItem, item, byUVs)
                cmds.progressWindow(endProgress=True)
                return
            else:
                if not sourceItem in ranList:
                    for item in reversed(destinationList): #to avoid find the same item in the same given list
                        if not sourceItem == item:
                            if sourceItem[sourceItem.rfind("|")+1:] == item[item.rfind("|")+1:]:
                                if self.checkExistingDeformerNode(sourceItem)[0]:
                                    self.runCopySkin(sourceItem, item, byUVs)
                                elif self.checkExistingDeformerNode(item)[0]:
                                    self.runCopySkin(item, sourceItem, byUVs)
                                # To avoid repeat the same item in the same given list
                                ranList.append(item)
                                break
                    ranList.append(sourceItem)
        cmds.progressWindow(endProgress=True)


    def runCopySkin(self, sourceItem, destinationItem, byUVs=False, *args):
        """ Copy the skin from sourceItem to destinationItem.
            It will get skinInfList and skinMethod by source.
        """
        i = 0
        defOrderIdx = None
        sourceDefList = self.checkExistingDeformerNode(sourceItem)[2]
        if sourceDefList:
            # get correct naming
            skinClusterName = self.utils.extractSuffix(destinationItem)
            if "|" in skinClusterName:
                skinClusterName = skinClusterName[skinClusterName.rfind("|")+1:]
            # clean-up current destination skinCluster
            destDefList = self.checkExistingDeformerNode(destinationItem, deleteIt=True)
            if destDefList[0] and destDefList[2]:
                defOrderIdx = self.getDeformerOrder(destDefList)
            for sourceDef in reversed(sourceDefList): #create reversed to have the multiple skinClusters in the good deformer order
                skinInfList = cmds.skinCluster(sourceDef, query=True, influence=True)
                skinMethodToUse = cmds.skinCluster(sourceDef, query=True, skinMethod=True)
                # create skinCluster node
                if i == 0: #Maya 2022 and 2023 versions
                    newSkinClusterNode = cmds.skinCluster(skinInfList, destinationItem, name=skinClusterName+"_"+str(i)+"_SC", toSelectedBones=True, maximumInfluences=3, skinMethod=skinMethodToUse)[0]
                elif cmds.about(version=True) >= "2024": #accepting multiple skinClusters
                    newSkinClusterNode = cmds.skinCluster(skinInfList, destinationItem, multi=True, name=skinClusterName+"_"+str(i)+"_SC", toSelectedBones=True, maximumInfluences=3, skinMethod=skinMethodToUse)[0]
                cmds.rename(cmds.listConnections(newSkinClusterNode+".bindPose", destination=False, source=True), newSkinClusterNode.replace("_SC", "_BP"))
                # copy skin weights from source to destination
                if byUVs:
                    sourceUVMap = cmds.polyUVSet(sourceItem, query=True, allUVSets=True)[0]
                    destinationUVMap = cmds.polyUVSet(destinationItem, query=True, allUVSets=True)[0]
                    cmds.copySkinWeights(sourceSkin=sourceDef, destinationSkin=newSkinClusterNode, noMirror=True, surfaceAssociation="closestPoint", influenceAssociation=["label", "oneToOne", "closestJoint"], uvSpace=[sourceUVMap, destinationUVMap])
                else:
                    cmds.copySkinWeights(sourceSkin=sourceDef, destinationSkin=newSkinClusterNode, noMirror=True, surfaceAssociation="closestPoint", influenceAssociation=["label", "oneToOne", "closestJoint"])
                # deformer order
                if defOrderIdx:
                    cmds.reorderDeformers(destDefList[1][defOrderIdx-1], newSkinClusterNode, destinationItem)
                i += 1
        # log result
        mel.eval("print \""+self.dpUIinst.lang['i083_copiedSkin']+" "+sourceItem+" "+destinationItem+"\"; ")


    def copySkinFromOneSource(self, objList=None, ui=False, byUVs=False, *args):
        """ Main function to analise and call copy skin process. 
        """
        if not objList:
            objList = cmds.ls(selection=True, long=True, type="transform")
        if objList and len(objList) > 1:
            # get first selected item
            sourceItem = objList[0]
            # get other selected items
            destinationList = objList[1:]
            shapeList = cmds.listRelatives(sourceItem, shapes=True, fullPath=True)
            if shapeList:
                # check if there's a skinCluster node connected to the first selected item
                if self.checkExistingDeformerNode(shapeList):
                    if ui:
                        byUVs = self.getByUVsFromUI()
                    # call copySkin function
                    self.serializeCopySkin([sourceItem], destinationList, True, byUVs)
                else:
                    mel.eval("warning \""+self.dpUIinst.lang['e007_notSkinFound']+"\";")
            else:
                mel.eval("warning \""+self.dpUIinst.lang['e006_firstSkinnedGeo']+"\";")
        else:
            mel.eval("warning \""+self.dpUIinst.lang['e005_selectOneObj']+"\";")


    def copySkinSameName(self, objList=None, ui=False, byUVs=False, *args):
        """ Copy the skinning between meshes with the same name, selected or not or using the given list.
        """
        if not objList:
            objList = cmds.ls(selection=True, long=True, type="transform")
            if not objList:
                objList = cmds.ls(selection=False, long=True, type="transform")
        if objList:
            if ui:
                byUVs = self.getByUVsFromUI()
            self.serializeCopySkin(objList, objList, False, byUVs)


    def getByUVsFromUI(self, *args):
        """ Read the radioCollection, verify its annotation and return True if found selected uvSpace.
        """
        skinSurfAssociationCollection = cmds.radioCollection(self.dpUIinst.allUIs["skinSurfAssociationCollection"], query=True, select=True)
        annot = cmds.radioButton(skinSurfAssociationCollection, query=True, annotation=True)
        if annot == "uvSpace":
            return True

            
    def createMissingJoints(self, incomingJointList, *args):
        """ Create missing joints if we don't have them in the scene.
        """
        missingJntList = []
        for jnt in incomingJointList:
            if not cmds.objExists(jnt):
                cmds.select(clear=True)
                cmds.joint(name=jnt)
                cmds.select(clear=True)
                missingJntList.append(jnt)
        return missingJntList


    def updateOrCreateSkinCluster(self, mesh, skinClusterName, skinWeightDic, *args):
        """ Add influence to the existing skinCluster.
            Create a new skinCluster if it needs.
            Ensure we have a skinCluster node with all weights in just one joint to avoid import issue.
            Return a dictionary with the joint name and it's matrix index connection.
        """
        needToCreateSkinCluster = True
        incomingJointList = skinWeightDic[mesh][skinClusterName]['skinInfList']
        missingJntList = self.createMissingJoints(incomingJointList)
        skinClusterInfoList = self.checkExistingDeformerNode(mesh)
        if skinClusterInfoList[0]:
            for scNode in skinClusterInfoList[2]:
                if scNode == skinClusterName:
                    if missingJntList:
                        for jnt in missingJntList:
                            # add influence
                            cmds.skinCluster(mesh, edit=True, addInfluence=jnt, lockWeights=True, weight=0.0)
                            needToCreateSkinCluster = False
                    else:
                        cmds.delete(scNode)
        if needToCreateSkinCluster:
            if cmds.about(version=True) >= "2024": #accepting multiple skinClusters
                cmds.skinCluster(incomingJointList, mesh, multi=True, name=skinClusterName, toSelectedBones=True, skinMethod=skinWeightDic[mesh][skinClusterName]['skinMethodToUse'], obeyMaxInfluences=skinWeightDic[mesh][skinClusterName]['skinMaintainMaxInf'], maximumInfluences=skinWeightDic[mesh][skinClusterName]['skinMaxInf'])[0]
            else:
                cmds.skinCluster(incomingJointList, mesh, name=skinClusterName, toSelectedBones=True, skinMethod=skinWeightDic[mesh][skinClusterName]['skinMethodToUse'], obeyMaxInfluences=skinWeightDic[mesh][skinClusterName]['skinMaintainMaxInf'], maximumInfluences=skinWeightDic[mesh][skinClusterName]['skinMaxInf'])[0]


    def getSkinWeights(self, mesh, skinClusterNode, infList=False, *args):
        """ Returns a list with all skin weights for each mesh vertex as a influence dictionary.
        """
        skinWeightsList = []
        vertexList = cmds.ls(mesh+".vtx[*]", flatten=True)
        for vertex in range(0, len(vertexList)):
            skinWeightsList.append(self.getDeformerWeights(skinClusterNode, vertex, infList))
        return skinWeightsList


    def getSkinWeightData(self, meshList, *args):
        """ Return the the skinCluster weights data of the given mesh list.
        """
        progressAmount = 0
        maxProcess = len(meshList)
        cmds.progressWindow(title=self.ioStartName, progress=0, status=self.ioStartName+': 0%', isInterruptable=False)
        skinWeightsDic = {}
        for mesh in meshList:
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=('SkinningIO: '+repr(progressAmount)+' - '+mesh))
            skinWeightsDic[mesh] = {}
            # get skinCluster nodes for the given mesh
            skinClusterInfoList = self.checkExistingDeformerNode(mesh)
            if skinClusterInfoList[0]:
                for skinClusterNode in skinClusterInfoList[2]:
                    # get skinCluster data
                    skinWeightsDic[mesh][skinClusterNode] = {
                        "skinMethodToUse"    : cmds.skinCluster(skinClusterNode, query=True, skinMethod=True),
                        "skinMaintainMaxInf" : cmds.skinCluster(skinClusterNode, query=True, obeyMaxInfluences=True),
                        "skinMaxInf"         : cmds.skinCluster(skinClusterNode, query=True, maximumInfluences=True),
                        "skinInfList"        : cmds.skinCluster(skinClusterNode, query=True, influence=True),
                        "skinJointsWeights"  : self.getSkinWeights(mesh, skinClusterNode, True)
                    }
        return skinWeightsDic    


    def setImportedSkinWeights(self, mesh, skinClusterName, skinWeightDic, *args):
        """ Set the skinCluster weight values from the given dictionary.
        """
        # workaround to have all weights in a temporary joint
        cmds.select(clear=True)
        tmpJoint = cmds.joint(name="dpTemp_Jnt")
        cmds.skinCluster(skinClusterName, edit=True, addInfluence=tmpJoint, toSelectedBones=True, lockWeights=False, weight=1.0)
        try:
            cmds.skinPercent(skinClusterName, mesh, transformValue=[(tmpJoint, 1)])
        except Exception as e:
            print(e)
        # get indices
        matrixDic = self.getConnectedMatrixDic(skinClusterName)
        vertexList = cmds.ls(mesh+".vtx[*]", flatten=True)
        for v in range(0, len(vertexList)):
            for jntName in skinWeightDic[mesh][skinClusterName]['skinJointsWeights'][v].keys():
                # set weights
                cmds.setAttr(skinClusterName+".weightList["+str(v)+"].weights["+str(matrixDic[jntName])+"]", skinWeightDic[mesh][skinClusterName]['skinJointsWeights'][v][jntName])
        # remove temporary joint
        cmds.delete(tmpJoint)
        self.normalizeMeshWeights(mesh)


    def importSkinWeightsFromFile(self, meshList, path, filename, *args):
        """ Import the skinCluster weights of the given mesh in the given path using the choose file extension (xml by default).
        """
        progressAmount = 0
        maxProcess = len(meshList)
        # Starting progress window
        cmds.progressWindow(title=self.ioStartName, progress=0, status=self.ioStartName+': 0%', isInterruptable=False)
        skinWeightDic = self.dpUIinst.pipeliner.getJsonContent(path+"/"+filename)
        if skinWeightDic:
            for mesh in meshList:
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=('SkinningIO: '+repr(progressAmount)+' - '+mesh))
                if cmds.objExists(mesh):
                    for skinClusterName in skinWeightDic[mesh].keys():
                        self.updateOrCreateSkinCluster(mesh, skinClusterName, skinWeightDic)
                        self.setImportedSkinWeights(mesh, skinClusterName, skinWeightDic)


    def ioSkinWeightsByUI(self, io=True, *args):
        """ Call export or import the skinCluster weights by UI.
            Export: If IO parameter is True
            Import: If IO parameter is False
        """
        meshList = cmds.ls(selection=True, type="transform")
        if not meshList:
            cmds.confirmDialog(title="SkinCluster Weights IO", message=self.dpUIinst.lang['i042_notSelection']+"\n"+self.dpUIinst.lang['m225_selectAnything'], button=[self.dpUIinst.lang['i038_canceled']])
            return
        action = self.dpUIinst.lang['i196_import']
        if io:
            action = self.dpUIinst.lang['i164_export']
        path = cmds.fileDialog2(fileMode=3, caption=action+" "+self.dpUIinst.lang['i298_folder'], okCaption=action)
        if meshList and path:
            for mesh in meshList:
                filename = path[0]+"/"+self.ioStartName+"_"+self.getIOFileName(mesh)+".json"
                if cmds.listRelatives(mesh, children=True, allDescendents=True, type="mesh"):
                    if io:
                        skinClusterDic = self.getSkinWeightData([mesh])
                        self.dpUIinst.pipeliner.saveJsonFile(skinClusterDic, filename)
                    else:
                        self.importSkinWeightsFromFile([mesh], path[0], filename)
