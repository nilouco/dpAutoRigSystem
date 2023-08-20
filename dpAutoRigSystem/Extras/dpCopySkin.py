# importing libraries:
from maya import cmds
from maya import mel
from ..Modules.Library import dpUtils

# global variables to this module:    
CLASS_NAME = "CopySkin"
TITLE = "m097_copySkin"
DESCRIPTION = "m098_copySkinDesc"
ICON = "/Icons/dp_copySkin.png"

DP_COPYSKIN_VERSION = 1.5


class CopySkin(object):
    def __init__(self, dpUIinst, ui=True, *args):
        # redeclaring variables
        self.dpUIinst = dpUIinst
        # call main function
        if ui:
            self.dpMain(self)
    
    
    def dpMain(self, *args):
        """ Main function to analise and call copy skin process. 
        """
        selList = cmds.ls(selection=True, long=True)
        if selList and len(selList) > 1:
            # get first selected item
            sourceItem = selList[0]
            # get other selected items
            destinationList = selList[1:]
            shapeList = cmds.listRelatives(sourceItem, shapes=True, fullPath=True)
            if shapeList:
                # check if there's a skinCluster node connected to the first selected item
                if self.checkExistingSkinClusterNode(shapeList):
                    # call copySkin function
                    self.dpSerializeCopySkin([sourceItem], destinationList)
                else:
                    mel.eval("warning \""+self.dpUIinst.lang['e007_notSkinFound']+"\";")
            else:
                mel.eval("warning \""+self.dpUIinst.lang['e006_firstSkinnedGeo']+"\";")
        else:
            mel.eval("warning \""+self.dpUIinst.lang['e005_selectOneObj']+"\";")


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


    def dpSerializeCopySkin(self, sourceList, destinationList, oneSource=True, *args):
        """ Serialize the copy skinning for one source or not.
        """
        ranList = []
        for sourceItem in sourceList:
            if oneSource:
                for item in destinationList:
                    self.dpCopySkin(sourceItem, item)
                return
            else:
                if not sourceItem in ranList:
                    for item in reversed(destinationList): #to avoid find the same item in the same given list
                        if sourceItem[sourceItem.rfind("|")+1:] == item[item.rfind("|")+1:]:
                            if self.checkExistingSkinClusterNode(sourceItem)[0]:
                                self.dpCopySkin(sourceItem, item)
                            elif self.checkExistingSkinClusterNode(item)[0]:
                                self.dpCopySkin(item, sourceItem)
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


    def dpCopySkin(self, sourceItem, destinationItem, *args):
        """ Copty the skin from sourceItem to destinationItem.
            It will get skinInfList and skinMethod by source.
        """
        i = 0
        defOrderIdx = None
        # get correct naming
        skinClusterName = dpUtils.extractSuffix(destinationItem)
        if "|" in skinClusterName:
            skinClusterName = skinClusterName[skinClusterName.rfind("|")+1:]
        # clean-up current destination skinCluster
        destDefList = self.checkExistingSkinClusterNode(destinationItem, True)
        sourceDefList = self.checkExistingSkinClusterNode(sourceItem)[2]
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
            cmds.copySkinWeights(sourceSkin=sourceDef, destinationSkin=newSkinClusterNode, noMirror=True, surfaceAssociation="closestPoint", influenceAssociation=["label", "oneToOne", "closestJoint"])
            # deformer order
            if defOrderIdx:
                cmds.reorderDeformers(destDefList[1][defOrderIdx-1], newSkinClusterNode, destinationItem)
            i += 1
        # log result
        mel.eval("print \""+self.dpUIinst.lang['i083_copiedSkin']+" "+sourceItem+" "+destinationItem+"\"; ")
