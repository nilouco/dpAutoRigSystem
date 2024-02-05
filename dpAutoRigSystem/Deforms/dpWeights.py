# importing libraries:
from maya import cmds


DP_WEIGTHS_VERSION = 1.0


class Weights(object):
    def __init__(self, dpUIinst, *args, **kwargs):
        """ Initialize the class.
        """
        # defining variables:
        self.dpUIinst = dpUIinst
        self.utils = dpUIinst.utils
    
    
    def getIOFileName(self, mesh, *args):
        """ Returns the cut fileName if found "|" in the given mesh name to avoid windows special character backup issue.
        """
        fileName = mesh
        if "|" in mesh:
            fileName = mesh[mesh.rfind("|")+1:]
        return fileName
    

    def getDeformerOrder(self, defList, *args):
        """ Find and return the latest old deformer order index for the given list.
            It's useful to reorder the deformers and place the new skinCluster to the correct position of deformation.
        """
        for d, destItem in enumerate(defList[1]):
            if not cmds.objExists(destItem):
                if destItem in defList[2]: #it's an old deformer node
                    if d > 0:
                        return d
        return 0


    def getDeformerWeights(self, deformerNode, idx, *args):
        """ 
        """
        weightPlug = deformerNode+".weightList["+str(idx)+"].weights"
        weightIndexList = cmds.getAttr(weightPlug, multiIndices=True)
        for weightIndex in weightIndexList:
            valueList = cmds.getAttr(weightPlug)[0]
            return dict(zip(weightIndexList, valueList))





##
#
# NOT USED -----
#
#
    def getShapeIndexDic(self, deformerNode, *args):
        """ Return a dictionary of the deformer index by shape.
        """
        shapeLongList = cmds.ls(cmds.deformer(deformerNode, query=True, geometry=True), long=True)
        indexList = cmds.deformer(deformerNode, query=True, geometryIndices=True)
        defShapeIndexDic = dict(zip(shapeLongList, indexList))
        return defShapeIndexDic




    def exportWeightsToFile(self, *args):
        """ Export the weights......
        """
        print("todo")
        


    def importWeightsFromFile(self, *args):
        """ Import the weights......
        """
        print("todo")
        


