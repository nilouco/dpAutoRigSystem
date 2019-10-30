# importing libraries:
import maya.cmds as cmds
import maya.mel as mel
import dpAutoRigSystem.Modules.Library.dpUtils as utils
reload(utils)

# global variables to this module:    
CLASS_NAME = "CopySkin"
TITLE = "m097_copySkin"
DESCRIPTION = "m098_copySkinDesc"
ICON = "/Icons/dp_copySkin.png"

dpCopySkinVersion = 1.1

class CopySkin():
    def __init__(self, dpUIinst, langDic, langName):
        # redeclaring variables
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
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
            shapeList = cmds.listRelatives(sourceItem, shapes=True)
            if shapeList:
                # check if there's a skinCluster node connected to the first selected item
                checkSkin = self.dpCheckSkinCluster(shapeList)
                if checkSkin:
                    # get joints influence from skinCluster
                    skinInfList = cmds.skinCluster(sourceItem, query=True, influence=True)
                    if skinInfList:
                        # call copySkin function
                        self.dpCopySkin(sourceItem, destinationList, skinInfList)
                else:
                    print self.langDic[self.langName]['e007_notSkinFound']
            else:
                print self.langDic[self.langName]['e006_firstSkinnedGeo']
        else:
            print self.langDic[self.langName]['e005_selectOneObj']


    def dpCheckSkinCluster(self, shapeList, *args):
        """ Verify if there's a skinCluster node in the list of history of the shape.
            Return True if yes.
            Return False if no.
        """
        for shapeNode in shapeList:
            if not shapeNode.endswith("Orig"):
                histList = cmds.listHistory(shapeNode)
                if histList:
                    for histItem in histList:
                        if cmds.objectType(histItem) == "skinCluster":
                            return True
        return False
    
    
    def dpCopySkin(self, sourceItem, destinationList, skinInfList, *args):
        """ Do the copy skin from sourceItem to destinationList using the skinInfList.
        """
        for item in destinationList:
            # get correct naming
            skinClusterName = utils.extractSuffix(item)
            # create skinCluster node
            cmds.skinCluster(skinInfList, item, name=skinClusterName+"_SC", toSelectedBones=True, maximumInfluences=3, skinMethod=0)
            cmds.select(sourceItem)
            cmds.select(item, toggle=True)
            # copy skin weights from sourceItem to item node
            cmds.copySkinWeights(noMirror=True, surfaceAssociation="closestPoint", influenceAssociation=["label", "oneToOne", "closestJoint"])
        print self.langDic[self.langName]['i083_copiedSkin'], sourceItem, destinationList
