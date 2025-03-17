# importing libraries:
from maya import cmds
from maya import mel
from . import dpWeights

DP_SKINNING_VERSION = 1.5


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
                notSkinnedList = []
                for geomSkin in geomSkinList:
                    if (mode == "Add"):
                        for joint in jointSkinList:
                            try:
                                cmds.skinCluster(geomSkin, edit=True, addInfluence=joint, toSelectedBones=True, lockWeights=True, weight=0.0)
                            except:
                                notSkinnedList.append(joint)
                    elif (mode == "Remove"):
                        for joint in jointSkinList:
                            try:
                                cmds.skinCluster(geomSkin, edit=True, removeInfluence=joint, toSelectedBones=True)
                            except:
                                notSkinnedList.append(joint)
                    else: # None = create a new skinCluster node
                        baseName = self.utils.extractSuffix(geomSkin)
                        skinClusterName = baseName+"_SC"
                        if "|" in skinClusterName:
                            skinClusterName = skinClusterName[skinClusterName.rfind("|")+1:]
                        newSkinClusterNode = cmds.skinCluster(jointSkinList, geomSkin, toSelectedBones=True, dropoffRate=4.0, maximumInfluences=3, skinMethod=0, normalizeWeights=1, removeUnusedInfluence=False, name=skinClusterName)[0]
                        cmds.rename(cmds.listConnections(newSkinClusterNode+".bindPose", destination=False, source=True), newSkinClusterNode.replace("_SC", "_BP"))
                print(self.dpUIinst.lang['i077_skinned']+', '.join(geomSkinList))
                if logWin:
                    if notSkinnedList:
                        self.dpUIinst.logger.infoWin('i028_skinButton', 'i077_skinned', '\n'.join(geomSkinList)+'\n\n'+self.dpUIinst.lang['i322_didntChangeInf']+'\n'.join(notSkinnedList), 'center', 205, 270)
                    else:
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
        self.utils.setProgress('Skinning: ', self.dpUIinst.lang['i287_copy']+" Skinning", len(destinationList), addOne=False, addNumber=False)
        for sourceItem in sourceList:
            self.utils.setProgress("Skinning: ")
            if oneSource:
                for item in destinationList:
                    self.runCopySkin(sourceItem, item, byUVs)
                self.utils.setProgress(endIt=True)
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
        self.utils.setProgress(endIt=True)


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


    def updateOrCreateSkinCluster(self, item, skinClusterName, skinWeightDic, *args):
        """ Add influence to the existing skinCluster.
            Create a new skinCluster if it needs.
        """
        needToCreateSkinCluster = True
        incomingJointList = skinWeightDic[item][skinClusterName]['skinInfList']
        missingJntList = self.createMissingJoints(incomingJointList)
        skinClusterInfoList = self.checkExistingDeformerNode(item)
        if skinClusterInfoList[0]:
            for scNode in skinClusterInfoList[2]:
                if scNode == skinClusterName:
                    if missingJntList:
                        for jnt in missingJntList:
                            # add influence
                            cmds.skinCluster(item, edit=True, addInfluence=jnt, lockWeights=True, weight=0.0)
                            needToCreateSkinCluster = False
                    else:
                        cmds.lockNode(scNode, lock=False)
                        cmds.delete(scNode)
        if needToCreateSkinCluster:
            if cmds.about(version=True) >= "2024": #accepting multiple skinClusters
                cmds.skinCluster(incomingJointList, item, multi=True, name=skinClusterName, toSelectedBones=True, skinMethod=skinWeightDic[item][skinClusterName]['skinMethodToUse'], obeyMaxInfluences=skinWeightDic[item][skinClusterName]['skinMaintainMaxInf'], maximumInfluences=skinWeightDic[item][skinClusterName]['skinMaxInf'])[0]
            else:
                cmds.skinCluster(incomingJointList, item, name=skinClusterName, toSelectedBones=True, skinMethod=skinWeightDic[item][skinClusterName]['skinMethodToUse'], obeyMaxInfluences=skinWeightDic[item][skinClusterName]['skinMaintainMaxInf'], maximumInfluences=skinWeightDic[item][skinClusterName]['skinMaxInf'])[0]


    def getSkinWeights(self, item, skinClusterNode, infList=False, *args):
        """ Returns a list with all skin weights for each item component (vertex or cv) as a influence dictionary.
        """
        skinWeightsList = []
        componentList = cmds.ls(item+".vtx[*]", flatten=True) or [] #mesh
        componentList.extend(cmds.ls(item+".cv[*]", flatten=True) or []) #nurbsCurve
        for component in range(0, len(componentList)):
            skinWeightsList.append(self.getDeformerWeights(skinClusterNode, component, infList))
        return skinWeightsList
    

    def getSkinListWeights(self, item, skinClusterNode, attrName="blendWeights", *args):
        """ Returns a dictionary with the skin blend weights by each item component (vertex or cv) that has non zero blend weight value.
        """
        skinDataDic = {}
        componentList = cmds.ls(item+".vtx[*]", flatten=True) or [] #mesh
        componentList.extend(cmds.ls(item+".cv[*]", flatten=True) or []) #nurbsCurve
        for component in range(0, len(componentList)):
            value = cmds.getAttr(skinClusterNode+"."+attrName+"["+str(component)+"]")
            if not value == 0:
                skinDataDic[component] = value
        return skinDataDic


    def getSkinWeightData(self, itemList, *args):
        """ Return the the skinCluster weights data of the given item list.
        """
        self.utils.setProgress(self.ioStartName+': '+self.dpUIinst.lang['c110_start'], self.ioStartName, len(itemList), addOne=False, addNumber=False)
        skinWeightsDic = {}
        for item in itemList:
            self.utils.setProgress('SkinningIO: '+item)
            skinWeightsDic[item] = {}
            # get skinCluster nodes for the given item
            skinClusterInfoList = self.checkExistingDeformerNode(item)
            if skinClusterInfoList[0]:
                for skinClusterNode in skinClusterInfoList[2]:
                    # get skinCluster data
                    skinWeightsDic[item][skinClusterNode] = {
                        "skinMethodToUse"           : cmds.skinCluster(skinClusterNode, query=True, skinMethod=True),
                        "skinMaintainMaxInf"        : cmds.skinCluster(skinClusterNode, query=True, obeyMaxInfluences=True),
                        "skinMaxInf"                : cmds.skinCluster(skinClusterNode, query=True, maximumInfluences=True),
                        "skinInfList"               : cmds.skinCluster(skinClusterNode, query=True, influence=True),
                        "skinSupportNonRigid"       : cmds.getAttr(skinClusterNode+".dqsSupportNonRigid"),
                        "skinUseComponents"         : cmds.getAttr(skinClusterNode+".useComponents"),
                        "skinDeformUserNormals"     : cmds.getAttr(skinClusterNode+".deformUserNormals"),
                        "skinNormalizeWeights"      : cmds.getAttr(skinClusterNode+".normalizeWeights"),
                        "skinWeightDistribution"    : cmds.getAttr(skinClusterNode+".weightDistribution"),
                        "skinMaxInfluences"         : cmds.getAttr(skinClusterNode+".maxInfluences"),
                        "skinMaintainMaxInfluences" : cmds.getAttr(skinClusterNode+".maintainMaxInfluences"),
                        "skinJointsWeights"         : self.getSkinWeights(item, skinClusterNode, True),
                        "skinBlendWeights"          : self.getSkinListWeights(item, skinClusterNode, "blendWeights"),
                        "skinDropoffWeights"        : self.getSkinListWeights(item, skinClusterNode, "dropoff")
                    }
                    if cmds.objExists(skinClusterNode+".relativeSpaceMode"):
                        skinWeightsDic[item][skinClusterNode]["skinRelativeSpaceMode"] = cmds.getAttr(skinClusterNode+".relativeSpaceMode")
        return skinWeightsDic


    def setImportedSkinWeights(self, item, skinClusterName, skinWeightDic, *args):
        """ Set the skinCluster weight values from the given dictionary.
            Ensure we have a skinCluster node with all weights in just one joint to avoid import issue.
        """
        # workaround to have all weights in a temporary joint
        cmds.select(clear=True)
        self.tmpJoint = cmds.joint(name="dpTemp_Jnt")
        cmds.skinCluster(skinClusterName, edit=True, addInfluence=self.tmpJoint, toSelectedBones=True, lockWeights=False, weight=1.0)
        try:
            cmds.skinPercent(skinClusterName, item, transformValue=[(self.tmpJoint, 1)])
        except Exception as e:
            print(e)
        # get indices
        matrixDic = self.getConnectedMatrixDic(skinClusterName)
        componentList = cmds.ls(item+".vtx[*]", flatten=True) or [] #mesh
        componentList.extend(cmds.ls(item+".cv[*]", flatten=True) or []) #nurbsCurve
        for c in range(0, len(componentList)):
            for jntName in skinWeightDic[item][skinClusterName]['skinJointsWeights'][c].keys():
                # set weights
                cmds.setAttr(skinClusterName+".weightList["+str(c)+"].weights["+str(matrixDic[jntName])+"]", skinWeightDic[item][skinClusterName]['skinJointsWeights'][c][jntName])
        # remove temporary joint
        cmds.skinCluster(skinClusterName, edit=True, removeInfluence=self.tmpJoint, toSelectedBones=True)
        cmds.delete(self.tmpJoint)
        self.normalizeItemWeights(item)


    def setImportedSkinListWeights(self, skinClusterName, skinWeightDic, attrName="blendWeights", *args):
        """ Set the skinCluster blend or dropoff weight values from the given dictionary.
        """
        if skinWeightDic:
            for vertex in skinWeightDic.keys():
                cmds.setAttr(skinClusterName+"."+attrName+"["+str(vertex)+"]", skinWeightDic[vertex])


    def importSkinWeightsFromFile(self, itemList, path, filename, verbose=True, *args):
        """ Import the skinCluster weights of the given item in the given path and filename.
        """
        self.utils.setProgress(self.ioStartName+": "+self.dpUIinst.lang['c110_start'], self.ioStartName, len(itemList), addOne=False, addNumber=False)
        skinWeightDic = self.dpUIinst.pipeliner.getJsonContent(path+"/"+filename)
        if skinWeightDic:
            for item in itemList:
                self.utils.setProgress("SkinningIO: "+item)
                if cmds.objExists(item):
                    for skinClusterName in skinWeightDic[item].keys():
                        self.updateOrCreateSkinCluster(item, skinClusterName, skinWeightDic)
                        self.setImportedSkinWeights(item, skinClusterName, skinWeightDic)
                        self.setImportedSkinListWeights(skinClusterName, skinWeightDic[item][skinClusterName]['skinBlendWeights'], "blendWeights")
                        self.setImportedSkinListWeights(skinClusterName, skinWeightDic[item][skinClusterName]['skinDropoffWeights'], "dropoff")
                        cmds.setAttr(skinClusterName+".dqsSupportNonRigid", skinWeightDic[item][skinClusterName]["skinSupportNonRigid"])
                        cmds.setAttr(skinClusterName+".useComponents", skinWeightDic[item][skinClusterName]["skinUseComponents"])
                        cmds.setAttr(skinClusterName+".deformUserNormals", skinWeightDic[item][skinClusterName]["skinDeformUserNormals"])
                        cmds.setAttr(skinClusterName+".normalizeWeights", skinWeightDic[item][skinClusterName]["skinNormalizeWeights"])
                        cmds.setAttr(skinClusterName+".weightDistribution", skinWeightDic[item][skinClusterName]["skinWeightDistribution"])
                        cmds.setAttr(skinClusterName+".maxInfluences", skinWeightDic[item][skinClusterName]["skinMaxInfluences"])
                        cmds.setAttr(skinClusterName+".maintainMaxInfluences", skinWeightDic[item][skinClusterName]["skinMaintainMaxInfluences"])
                        if cmds.objExists(skinClusterName+".relativeSpaceMode"):
                            if "skinRelativeSpaceMode" in skinWeightDic[item][skinClusterName].keys():
                                cmds.setAttr(skinClusterName+".relativeSpaceMode", skinWeightDic[item][skinClusterName]["skinRelativeSpaceMode"])
        if verbose:
            self.utils.setProgress(endIt=True)


    def ioSkinWeightsByUI(self, export=True, *args):
        """ Call export or import the skinCluster weights by UI.
            Export: if export parameter is True
            Import: if export parameter is False
        """
        itemList = cmds.ls(selection=True, type="transform")
        if not itemList:
            cmds.confirmDialog(title="SkinCluster Weights IO", message=self.dpUIinst.lang['i042_notSelection']+"\n"+self.dpUIinst.lang['m225_selectAnything'], button=[self.dpUIinst.lang['i038_canceled']])
            return
        action = self.dpUIinst.lang['i196_import']
        if export:
            action = self.dpUIinst.lang['i164_export']
        path = cmds.fileDialog2(fileMode=3, caption=action+" "+self.dpUIinst.lang['i298_folder'], okCaption=action)
        if itemList and path:
            for item in itemList:
                filename = path[0]+"/"+self.ioStartName+"_"+self.getIOFileName(item)+".json"
                if cmds.listRelatives(item, children=True, allDescendents=True, type="item"):
                    if export:
                        skinClusterDic = self.getSkinWeightData([item])
                        self.dpUIinst.pipeliner.saveJsonFile(skinClusterDic, filename)
                    else:
                        self.importSkinWeightsFromFile([item], path[0], self.ioStartName+"_"+self.getIOFileName(item)+".json")
        self.utils.setProgress(endIt=True)
