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


    def getDeformerWeights(self, deformerNode, idx, infList=False, *args):
        """ Read the deformer information to return a dictionary with influence index or connected matrix nodes as keys and the weight as values.
        """
        weightPlug = deformerNode+".weightList["+str(idx)+"].weights"
        weightKeyList = cmds.getAttr(weightPlug, multiIndices=True)
        if infList:
            matrixList = []
            for item in weightKeyList:
                matrixList.append(cmds.listConnections(deformerNode+".matrix["+str(item)+"]", source=True, destination=False)[0])
            weightKeyList = matrixList
        for weightIndex in weightKeyList:
            valueList = cmds.getAttr(weightPlug)[0]
            return dict(zip(weightKeyList, valueList))


    def normalizeMeshWeights(self, mesh, *args):
        """ Just normalize the skinCluster weigths for the given mesh.
        """
        for skinClusterNode in self.checkExistingSkinClusterNode(mesh)[2]:
            self.unlockJoints(skinClusterNode)
            cmds.skinPercent(skinClusterNode, mesh, normalize=True)


    def getConnectedMatrixDic(self, deformerName, *args):
        """ Returns a dictionary with the connected matrix nodes as keys and them index as values.
            Useful to set skinCluster weights values correctly.
        """
        matrixDic = {}
        matrixList = cmds.getAttr(deformerName+".matrix", multiIndices=True)
        for m in matrixList:
            matrixItem = cmds.listConnections(deformerName+".matrix["+str(m)+"]", source=True, destination=False)[0]
            matrixDic[matrixItem] = m
        return matrixDic

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


    


    def unlockJoints(self, skinCluster, *args):
        """ Just unlock joints from a given skinCluster node.
        """
        jointsList = cmds.skinCluster(skinCluster, inf=True, q=True)
        for joint in jointsList:
            cmds.setAttr(joint+'.liw', 0)

    def exportWeightsToFile(self, *args):
        """ Export the weights......
        """
        print("todo")
        


    def importWeightsFromFile(self, *args):
        """ Import the weights......
        """
        print("todo")
        


