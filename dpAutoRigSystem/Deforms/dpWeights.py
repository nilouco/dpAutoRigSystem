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
                sourceList = cmds.listConnections(deformerNode+".matrix["+str(item)+"]", source=True, destination=False)
                if sourceList:
                    matrixList.append(sourceList[0])
            weightKeyList = matrixList
        for weightIndex in weightKeyList:
            valueList = cmds.getAttr(weightPlug)[0]
            return dict(zip(weightKeyList, valueList))


    def unlockJoints(self, skinCluster, *args):
        """ Just unlock joints from a given skinCluster node.
        """
        jointsList = cmds.skinCluster(skinCluster, inf=True, q=True)
        for joint in jointsList:
            cmds.setAttr(joint+'.liw', 0)


    def normalizeMeshWeights(self, mesh, *args):
        """ Just normalize the skinCluster weigths for the given mesh.
        """
        for skinClusterNode in self.checkExistingDeformerNode(mesh)[2]:
            self.unlockJoints(skinClusterNode)
            cmds.skinPercent(skinClusterNode, mesh, normalize=True)


    def getConnectedMatrixDic(self, deformerName, *args):
        """ Returns a dictionary with the connected matrix nodes as keys and their index as values.
            Useful to set skinCluster weights values correctly.
        """
        matrixDic = {}
        matrixList = cmds.getAttr(deformerName+".matrix", multiIndices=True)
        for m in matrixList:
            matrixItemList = cmds.listConnections(deformerName+".matrix["+str(m)+"]", source=True, destination=False)
            if matrixItemList:
                matrixDic[matrixItemList[0]] = m
        return matrixDic


    def getDeformedModelList(self, desiredTypeList=["skinCluster"], ignoreAttr="None", *args):
        """ Returns a list of deformed mesh transforms.
            Use given lists and attribute to filter the results.
        """
        deformedModelList, ranList = [], []
        allMeshList = cmds.ls(selection=False, noIntermediate=True, long=True, type="mesh")
        if allMeshList:
            for item in allMeshList:
                transformNode = item[:item[1:].find("|")+1]
                if not transformNode in ranList:
                    ranList.append(transformNode)
                    transformList = cmds.listRelatives(transformNode, allDescendents=True, children=True, fullPath=True, type="transform")
                    if transformList:
                        transformList.append(transformNode)
                    else:
                        transformList = [transformNode]
                    for childNode in transformList:
                        if not cmds.objExists(childNode+"."+ignoreAttr):
                            if len(cmds.ls(childNode[childNode.rfind("|")+1:])) == 1:
                                childNode = childNode[childNode.rfind("|")+1:] #unique name
                            else:
                                print(self.dpUIinst.lang['i299_notUniqueName'], childNode)
                            for desiredType in desiredTypeList:
                                if self.checkExistingDeformerNode(childNode, deformerType=desiredType)[0]:
                                    if not childNode in deformedModelList:
                                        deformedModelList.append(childNode)
        return deformedModelList


    def checkExistingDeformerNode(self, item, deleteIt=False, deformerType="skinCluster", *args):
        """ Return a list with:
                True/False if there's/not a deformer.
                The current deformer list by default.
                A list with existing deformer nodes by givenType.
            Delete existing deformer node if there's one using the deleteIt parametter as True.
        """
        result = [False, None, None]
        inputDeformerList = cmds.listHistory(item, pruneDagObjects=True, interestLevel=True)
        if inputDeformerList:
            defList = cmds.ls(inputDeformerList, type=deformerType)
            if defList:
                if deleteIt:
                    cmds.delete(defList)
                result = [True, inputDeformerList, defList]
        return result
