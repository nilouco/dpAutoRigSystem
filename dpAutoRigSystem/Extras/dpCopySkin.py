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
        selList = cmds.ls(selection=True)
        if selList and len(selList) > 1:
            # get first selected item
            sourceItem = selList[0]
            # get other selected items
            destinationList = selList[1:]
            # validade unique node name
            if len(cmds.ls(sourceItem)) == 1:
                shapeList = cmds.listRelatives(sourceItem, shapes=True)
                if shapeList:
                    # check if there's a skinCluster node connected to the first selected item
                    checkSkin = self.dpCheckSkinCluster(shapeList)
                    if checkSkin == True:
                        # get joints influence from skinCluster
                        skinInfList = cmds.skinCluster(sourceItem, query=True, influence=True)
                        if skinInfList:
                            # call copySkin function
                            self.dpCopySkin(sourceItem, destinationList, skinInfList)
                    elif checkSkin == -1:
                        mel.eval("warning \""+self.dpUIinst.lang["i163_sameName"]+" "+sourceItem+"\";")
                    else:
                        print(self.dpUIinst.lang['e007_notSkinFound'])
                else:
                    print(self.dpUIinst.lang['e006_firstSkinnedGeo'])
            else:
                mel.eval("warning \""+self.dpUIinst.lang["i163_sameName"]+" "+sourceItem+"\";")
        else:
            print(self.dpUIinst.lang['e005_selectOneObj'])


    def dpCheckSkinCluster(self, shapeList, *args):
        """ Verify if there's a skinCluster node in the list of history of the shape.
            Return True if yes.
            Return False if no.
            Return -1 if there's another node with the same name.
        """
        for shapeNode in shapeList:
            if not shapeNode.endswith("Orig"):
                try:
                    histList = cmds.listHistory(shapeNode)
                    if histList:
                        for histItem in histList:
                            if cmds.objectType(histItem) == "skinCluster":
                                return True
                except:
                    return -1
        return False
    
    
    def deleteExistingSkinClusterNode(self, item, *args):
        """ Delete existing skinCluster node if there's one
        """
        inputDeformerList = cmds.findDeformers(item)
        if inputDeformerList:
            for deformerNode in inputDeformerList:
                if cmds.objectType(deformerNode) == "skinCluster":
                    cmds.delete(deformerNode)


    def dpCopySkin(self, sourceItem, destinationList, skinInfList, *args):
        """ Do the copy skin from sourceItem to destinationList using the skinInfList.
        """
        for item in destinationList:
            # get correct naming
            skinClusterName = dpUtils.extractSuffix(item)
            if "|" in skinClusterName:
                skinClusterName = skinClusterName[skinClusterName.rfind("|")+1:]
            self.deleteExistingSkinClusterNode(item)
            # create skinCluster node
            cmds.skinCluster(skinInfList, item, name=skinClusterName+"_SC", toSelectedBones=True, maximumInfluences=3, skinMethod=0)
            cmds.select(sourceItem)
            cmds.select(item, toggle=True)
            # copy skin weights from sourceItem to item node
            cmds.copySkinWeights(noMirror=True, surfaceAssociation="closestPoint", influenceAssociation=["label", "oneToOne", "closestJoint"])
            # log result
            print(self.dpUIinst.lang['i083_copiedSkin'], sourceItem, item)
