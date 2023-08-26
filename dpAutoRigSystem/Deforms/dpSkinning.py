# importing libraries:
from maya import cmds
from maya import mel
from ..Modules.Library import dpUtils

DP_SKINNING_VERSION = 1.0


class Skinning(object):
    def __init__(self, dpUIinst, *args, **kwargs):
        """ Initialize the class.
        """
        # defining variables:
        self.dpUIinst = dpUIinst
        

    def validateGeoList(self, geoList, mode=None, *args):
        """ Check if the geometry list from UI is good to be skinned, because we can get issue if the display long name is not used.
        """
        if geoList:
            for i, item in enumerate(geoList):
                if item in geoList[:i]:
                    self.dpUIinst.info('i038_canceled', 'e003_moreThanOneGeo', item, 'center', 205, 270)
                    return False
                elif not cmds.objExists(item):
                    self.dpUIinst.info('i038_canceled', 'i061_notExists', item, 'center', 205, 270)
                    return False
                elif not mode:
                    try:
                        inputDeformerList = cmds.findDeformers(item)
                        if inputDeformerList:
                            for deformerNode in inputDeformerList:
                                if cmds.objectType(deformerNode) == "skinCluster":
                                    self.dpUIinst.info('i038_canceled', 'i285_alreadySkinned', item, 'center', 205, 270)
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
                        baseName = dpUtils.extractSuffix(geomSkin)
                        skinClusterName = baseName+"_SC"
                        if "|" in skinClusterName:
                            skinClusterName = skinClusterName[skinClusterName.rfind("|")+1:]
                        cmds.skinCluster(jointSkinList, geomSkin, toSelectedBones=True, dropoffRate=4.0, maximumInfluences=3, skinMethod=0, normalizeWeights=1, removeUnusedInfluence=False, name=skinClusterName)
                print(self.dpUIinst.lang['i077_skinned'] + ', '.join(geomSkinList))
                if logWin:
                    self.dpUIinst.info('i028_skinButton', 'i077_skinned', '\n'.join(geomSkinList), 'center', 205, 270)
                cmds.select(geomSkinList)
        else:
            print(self.dpUIinst.lang['i029_skinNothing'])
            if logWin:
                self.dpUIinst.info('i028_skinButton', 'i029_skinNothing', ' ', 'center', 205, 270)

    
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
        """ Serialize the copy skinning for one source or not.
        """
        ranList = []
        for sourceItem in sourceList:
            if oneSource:
                for item in destinationList:
                    self.runCopySkin(sourceItem, item, byUVs)
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
            skinClusterName = dpUtils.extractSuffix(destinationItem)
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
