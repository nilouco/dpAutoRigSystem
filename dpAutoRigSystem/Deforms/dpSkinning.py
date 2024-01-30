# importing libraries:
from maya import cmds
from maya import mel
from xml.dom import minidom
import os

DP_SKINNING_VERSION = 1.3


class Skinning(object):
    def __init__(self, dpUIinst, *args, **kwargs):
        """ Initialize the class.
        """
        # defining variables:
        self.dpUIinst = dpUIinst
        self.utils = dpUIinst.utils
        

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

    
    def checkExistingSkinClusterNode(self, item, deleteIt=False, *args):
        """ Return a list with:
                True/False if there's/not a skinCluster.
                The current deformer list by default.
                A list with existing skinCluster nodes.
            Delete existing skinCluster node if there's one.
        """
        result = [False, None, None]
        inputDeformerList = cmds.listHistory(item, pruneDagObjects=True, interestLevel=True)
        if inputDeformerList:
            skinClusterList = cmds.ls(inputDeformerList, type="skinCluster")
            if skinClusterList:
                if deleteIt:
                    cmds.delete(skinClusterList)
                result = [True, inputDeformerList, skinClusterList]
        return result


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
                                if self.checkExistingSkinClusterNode(sourceItem)[0]:
                                    self.runCopySkin(sourceItem, item, byUVs)
                                elif self.checkExistingSkinClusterNode(item)[0]:
                                    self.runCopySkin(item, sourceItem, byUVs)
                                # To avoid repeat the same item in the same given list
                                ranList.append(item)
                                break
                    ranList.append(sourceItem)
        cmds.progressWindow(endProgress=True)


    def getDeformerOrder(self, defList, *args):
        """ Find and return the latest old skinCluster deformer order index for the given list.
            It's useful to reorder the deformers and place the new skinCluster to the correct position of deformation.
        """
        for d, destItem in enumerate(defList[1]):
            if not cmds.objExists(destItem):
                if destItem in defList[2]: #it's an old skinCluster node
                    if d > 0:
                        return d
        return 0


    def runCopySkin(self, sourceItem, destinationItem, byUVs=False, *args):
        """ Copy the skin from sourceItem to destinationItem.
            It will get skinInfList and skinMethod by source.
        """
        i = 0
        defOrderIdx = None
        sourceDefList = self.checkExistingSkinClusterNode(sourceItem)[2]
        if sourceDefList:
            # get correct naming
            skinClusterName = self.utils.extractSuffix(destinationItem)
            if "|" in skinClusterName:
                skinClusterName = skinClusterName[skinClusterName.rfind("|")+1:]
            # clean-up current destination skinCluster
            destDefList = self.checkExistingSkinClusterNode(destinationItem, True)
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
                if self.checkExistingSkinClusterNode(shapeList):
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


    def getJointsFromXMLFile(self, mesh, path, skinClusterName, *args):
        """ Returns the influence joint list to the given mesh from xml file in the given path.
        """
        allDefList = []
        jointSuffixList = ['Jnt', 'Jar', 'Jad', 'Jcr', 'Jis']
        if os.path.exists(path+'/'+mesh+'.xml'):
            dom = minidom.parse(path+'/'+mesh+'.xml')
            elementList = dom.getElementsByTagName('weights')
            for element in elementList:
                if element.attributes['deformer'].value == skinClusterName:
                    allDefList.append(element.attributes['source'].value)
            jointsList = list(filter(lambda name : name[-3:] in jointSuffixList, allDefList))
            return jointsList
    

    def getSkinInfoFromXMLFile(self, mesh, path, *args):
        """ Returns the influence joint list to the given mesh from xml file in the given path.
            If not found skinningMethod attribute in the XML file, it'll return 0 for classical linear.
        """
        if os.path.exists(path+'/'+mesh+'.xml'):
            skinClusterInfoDic = {}
            dom = minidom.parse(path+'/'+mesh+'.xml')
            deformerList = dom.getElementsByTagName('deformer')
            if deformerList:
                for deform in deformerList:
                    attr = deform.getElementsByTagName('attribute')[0]
                    skinClusterInfoDic[deform.attributes['name'].value] = {attr.attributes['name'].value : attr.attributes['value'].value}
                return skinClusterInfoDic
            
    
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


    def fillSkinClusterWithOneJnt(self, mesh, incomingJointList, skinClusterName, skinningMethod, *args):
        """ Add influence to the existing skinCluster.
            Create a new skinCluster if it needs.
            Ensure we have a skinCluster node with all weights in just one joint to avoid import issue.
        """
        needToCreateSkinCluster = True
        missingJntList = self.createMissingJoints(incomingJointList)
        skinClusterInfoList = self.checkExistingSkinClusterNode(mesh)
        if skinClusterInfoList[0]:
            if missingJntList:
                for scNode in skinClusterInfoList[2]:
                    if scNode == skinClusterName:
                        for jnt in missingJntList:
                            # add influence
                            cmds.skinCluster(mesh, edit=True, addInfluence=jnt, lockWeights=True, weight=0.0)
                            needToCreateSkinCluster = False
        if needToCreateSkinCluster:
            if cmds.about(version=True) >= "2024": #accepting multiple skinClusters
                cmds.skinCluster(incomingJointList, mesh, multi=True, name=skinClusterName, toSelectedBones=True, maximumInfluences=3, skinMethod=int(skinningMethod))[0]
            else:
                cmds.skinCluster(incomingJointList, mesh, name=skinClusterName, toSelectedBones=True, maximumInfluences=3, skinMethod=int(skinningMethod))[0]
        # Transfer all the weights to just one joint
        cmds.skinPercent(skinClusterName, mesh+'.vtx[:]', transformValue=[(incomingJointList[-1], 1)])


    def unlockJoints(self, skinCluster, *args):
        """ Just unlock joints from a given skinCluster node.
        """
        jointsList = cmds.skinCluster(skinCluster, inf=True, q=True)
        for joint in jointsList:
            cmds.setAttr(joint+'.liw', 0)


    def normalizeMeshWeights(self, mesh, *args):
        """ Just normalize the skinCluster weigths for the given mesh.
        """
        for skinClusterNode in self.checkExistingSkinClusterNode(mesh)[2]:
            self.unlockJoints(skinClusterNode)
            cmds.skinPercent(skinClusterNode, mesh, normalize=True)


    def getIOFileName(self, mesh, *args):
        """ Returns the cut fileName if found "|" in the given mesh name to avoid windows special character backup issue.
        """
        fileName = mesh
        if "|" in mesh:
            fileName = mesh[mesh.rfind("|")+1:]
        return fileName


    def exportSkinWeightsToFile(self, mesh, path, extension="xml", methodToUse="index", *args):
        """ Export the skinCluster weights of the given mesh in the given path using the choose file extension (xml by default).
        """
        fileName = self.getIOFileName(mesh)
        cmds.deformerWeights(fileName+"."+extension, method=methodToUse, export=True, path=path, shape=mesh, attribute="skinningMethod")


    def importSkinWeightsFromFile(self, mesh, path, extension="xml", methodToUse="index", *args):
        """ Import the skinCluster weights of the given mesh in the given path using the choose file extension (xml by default).
        """
        fileName = self.getIOFileName(mesh)
        skinInfoDic = self.getSkinInfoFromXMLFile(mesh, path)
        if skinInfoDic:
            for skinClusterName in reversed(list(skinInfoDic)): #reversed to try create skinClusters in a good deformer order
                incomingJointList = self.getJointsFromXMLFile(mesh, path, skinClusterName)
                self.fillSkinClusterWithOneJnt(mesh, incomingJointList, skinClusterName, skinInfoDic[skinClusterName]['skinningMethod'])
                cmds.deformerWeights(fileName+"."+extension, method=methodToUse, im=True, path=path, shape=mesh)
                # after import weights it is necessary to normalize them
                self.normalizeMeshWeights(mesh)


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
                if cmds.listRelatives(mesh, children=True, allDescendents=True, type="mesh"):
                    if io:
                        self.exportSkinWeightsToFile(mesh, path[0])
                    else:
                        self.importSkinWeightsFromFile(mesh, path[0])
