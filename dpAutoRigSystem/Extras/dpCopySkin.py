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
    def __init__(self, dpUIinst, *args):
        # redeclaring variables
        self.dpUIinst = dpUIinst
        # call main function
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
                checkSkin = self.checkExistingSkinClusterNode(shapeList)
                if checkSkin == True:
                    # get joints influence from skinCluster
                    skinInfList = cmds.skinCluster(sourceItem, query=True, influence=True)
                    if skinInfList:
                        skinMethodToUse = cmds.skinCluster(sourceItem, query=True, skinMethod=True)
                        # call copySkin function
                        self.dpCopySkin(sourceItem, destinationList, skinInfList, skinMethodToUse)
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
        return result


    def dpCopySkin(self, sourceItem, destinationList, skinInfList, skinMethodToUse=0, *args):
        """ Do the copy skin from sourceItem to destinationList using the skinInfList.
        """
        for item in destinationList:
            # get correct naming
            skinClusterName = dpUtils.extractSuffix(item)
            if "|" in skinClusterName:
                skinClusterName = skinClusterName[skinClusterName.rfind("|")+1:]
            self.checkExistingSkinClusterNode(item, True)
            # create skinCluster node
            cmds.skinCluster(skinInfList, item, name=skinClusterName+"_SC", toSelectedBones=True, maximumInfluences=3, skinMethod=skinMethodToUse)
            cmds.select(sourceItem)
            cmds.select(item, toggle=True)
            # copy skin weights from sourceItem to item node
            cmds.copySkinWeights(noMirror=True, surfaceAssociation="closestPoint", influenceAssociation=["label", "oneToOne", "closestJoint"])
            # log result
            mel.eval("print \""+self.dpUIinst.lang['i083_copiedSkin']+" "+sourceItem+" "+item+"\";")
