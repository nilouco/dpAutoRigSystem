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
        """ Delete existing skinCluster node if there's one
        """
        result = False
        inputDeformerList = cmds.findDeformers(item)
        if inputDeformerList:
            for deformerNode in inputDeformerList:
                if cmds.objectType(deformerNode) == "skinCluster":
                    if deleteIt:
                        cmds.delete(deformerNode)
                    result = True
                    break
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
                            if self.checkExistingSkinClusterNode(sourceItem):
                                self.dpCopySkin(sourceItem, item)
                            elif self.checkExistingSkinClusterNode(item):
                                self.dpCopySkin(item, sourceItem)
                            # To avoid repeat the same item in the same given list
                            ranList.append(item)
                            break
                    ranList.append(sourceItem)


    def dpCopySkin(self, sourceItem, destinationItem, *args):
        """ Copty the skin from sourceItem to destinationItem.
            It will get skinInfList and skinMethod by source.
        """
        # get correct naming
        skinClusterName = dpUtils.extractSuffix(destinationItem)
        if "|" in skinClusterName:
            skinClusterName = skinClusterName[skinClusterName.rfind("|")+1:]
        # clean-up current destination skinCluster
        self.checkExistingSkinClusterNode(destinationItem, True)
        skinInfList = cmds.skinCluster(sourceItem, query=True, influence=True)
        skinMethodToUse = cmds.skinCluster(sourceItem, query=True, skinMethod=True)
        # create skinCluster node
        cmds.skinCluster(skinInfList, destinationItem, name=skinClusterName+"_SC", toSelectedBones=True, maximumInfluences=3, skinMethod=skinMethodToUse)
        cmds.select(sourceItem)
        cmds.select(destinationItem, toggle=True)
        # copy skin weights from sourceItem to item node
        cmds.copySkinWeights(noMirror=True, surfaceAssociation="closestPoint", influenceAssociation=["label", "oneToOne", "closestJoint"])
        # log result
        mel.eval("print \""+self.dpUIinst.lang['i083_copiedSkin']+" "+sourceItem+" "+destinationItem+"\"; ")


# TODO
# deformerOrder