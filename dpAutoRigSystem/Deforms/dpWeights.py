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
        self.typeAttrDic = {
                            "cluster"         : [None, "envelope", "relative", "angleInterpolation"],
                            "deltaMush"       : [None, "envelope", "smoothingIterations", "smoothingStep", "inwardConstraint", "outwardConstraint", "distanceWeight", "displacement", "scaleX", "scaleY", "scaleZ", "pinBorderVertices"],
                            "tension"         : [None, "envelope", "smoothingIterations", "smoothingStep", "inwardConstraint", "outwardConstraint", "squashConstraint", "stretchConstraint", "relative", "pinBorderVertices", "shearStrength", "bendStrength"],
                            "solidify"        : [None, "envelope", "normalScale", "tangentPlaneScale", "scaleEnvelope", "attachmentMode", "useBorderFalloff", "stabilizationLevel", "borderFalloffBlur"],
                            "ffd"             : ["deformedLatticeMatrix", "envelope", "localInfluenceS", "localInfluenceT", "localInfluenceU", "local", "outsideLattice", "outsideFalloffDist", "usePartialResolution", "partialResolution", "bindToOriginalGeometry", "freezeGeometry"],
                            "proximityWrap"   : [None, "envelope", "maxDrivers", "falloffScale", "dropoffRateScale", "scaleCompensation", "wrapMode", "coordinateFrames", "smoothNormals", "spanSamples", "smoothInfluences", "softNormalization", "useBindTags"],
                            "wrap"            : ["driverPoints", "envelope", "weightThreshold", "maxDistance", "autoWeightThreshold", "exclusiveBind", "falloffMode", "envelope"],
                            "shrinkWrap"      : ["targetGeom", "envelope", "targetSmoothLevel", "projection", "closestIfNoIntersection", "reverse", "bidirectional", "boundingBoxCenter", "axisReference", "alongX", "alongY", "alongZ", "offset", "targetInflation", "falloff", "falloffIterations", "shapePreservationEnable", "shapePreservationSteps", "shapePreservationReprojection"],
                            "morph"           : [None, "envelope", "morphMode", "morphSpace", "useComponentLookup", "scaleEnvelope", "uniformScaleWeight", "normalScale", "tangentPlaneScale", "tangentialDamping", "inwardConstraint", "outwardConstraint"],
                            "wire"            : ["deformedWire", "envelope", "crossingEffect", "tension", "localInfluence", "rotation"],
                            "sculpt"          : [None, "envelope", "mode", "dropoffType", "maximumDisplacement", "dropoffDistance", "insideMode"],
                            "textureDeformer" : [None, "envelope", "strength", "offset", "vectorStrengthX", "vectorStrengthY", "vectorStrengthZ", "vectorOffsetX", "vectorOffsetY", "vectorOffsetZ", "handleVisibility", "pointSpace"],
                            "jiggle"          : [None, "envelope", "currentTime", "enable", "ignoreTransform", "forceAlongNormal", "forceOnTangent", "motionMultiplier", "stiffness", "damping", "jiggleWeight", "directionBias"],
                            "deformBend"      : ["deformerData", "envelope", "curvature", "lowBound", "highBound"],
                            "deformFlare"     : ["deformerData", "envelope", "startFlareX", "startFlareZ", "endFlareX", "endFlareZ", "curve", "lowBound", "highBound"],
                            "deformSine"      : ["deformerData", "envelope", "amplitude", "wavelength", "offset", "dropoff", "lowBound", "highBound"],
                            "deformSquash"    : ["deformerData", "envelope", "factor", "expand", "maxExpandPos", "startSmoothness", "endSmoothness", "lowBound", "highBound"],
                            "deformTwist"     : ["deformerData", "envelope", "startAngle", "endAngle", "lowBound", "highBound"],
                            "deformWave"      : ["deformerData", "envelope", "amplitude", "wavelength", "offset", "dropoff", "dropoffPosition", "minRadius", "maxRadius"],
                            } #first element used to find the attribute node listing connection
    
    
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
        if cmds.objExists(weightPlug):
            weightKeyList = cmds.getAttr(weightPlug, multiIndices=True)
            if infList:
                matrixList = []
                for item in weightKeyList:
                    sourceList = cmds.listConnections(deformerNode+".matrix["+str(item)+"]", source=True, destination=False)
                    if sourceList:
                        matrixList.append(sourceList[0])
                weightKeyList = matrixList
            if weightKeyList:
                for weightIndex in weightKeyList:
                    valueList = cmds.getAttr(weightPlug)[0]
                    #if any(x != 1.0 for x in valueList):
                    return dict(zip(weightKeyList, valueList))
    

    def unlockJoints(self, skinCluster, *args):
        """ Just unlock joints from a given skinCluster node.
        """
        jointsList = cmds.skinCluster(skinCluster, inf=True, q=True)
        for joint in jointsList:
            cmds.setAttr(joint+".liw", 0)


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


    def getDeformedModelList(self, deformerTypeList=["skinCluster"], ignoreAttr="None", *args):
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
                            for desiredType in deformerTypeList:
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


    def getDeformerInfo(self, deformerNode, *args):
        """ Return the dictionary with attributes and values.
        """
        defDic = {"attributes" : {}}
        if deformerNode:
            defType = cmds.objectType(deformerNode)
            defDic["type"] = defType
            for n, attr in enumerate(list(self.typeAttrDic[defType])):
                if n == 0:
                    defDic["nonLinear"] = None
                    defDic["relatedNode"] = None
                    defDic["relatedData"] = None
                    if attr:
                        connectedNodeList = None
                        connectedNodeList = cmds.listConnections(deformerNode+"."+attr, destination=False, source=True)
                        if attr == "deformerData": #nonLinear
                            connectedNodeList = cmds.listConnections(deformerNode+"."+attr, destination=True, source=False)
                            if connectedNodeList:
                                defDic["relatedData"] = cmds.listRelatives(deformerNode, parent=True, type="transform")[0]
                                deformerNode = connectedNodeList[0]
                                defDic["nonLinear"] = defType.replace("deform", "").lower()
                        if defType == "ffd": #lattice
                            defDic["relatedData"] = self.getLatticeInfo(connectedNodeList[0], deformerNode)
                        elif defType == "wire":
                            defDic["relatedData"] = self.getCurveInfo(connectedNodeList[0])
                        if connectedNodeList:
                            defDic["relatedNode"] = connectedNodeList[0]
                    if defType == "sculpt":
                        defDic["relatedData"] = self.getSculptInfo(deformerNode)
                    elif defType == "morph":
                        defDic["relatedNode"] = cmds.listConnections(deformerNode+".morphTarget[0]", destination=False, source=True)[0]
                else:
                    defDic["attributes"][attr] = cmds.getAttr(deformerNode+"."+attr)
            defDic["name"] = deformerNode
        return defDic


    def getComponentTagInfo(self, nodeList=None, *args):
        """ Return the dictionary with the componentTag tagged info.
        """
        if not nodeList:
            nodeList = cmds.listRelatives(cmds.ls(selection=False, type=["mesh", "lattice"]), parent=True)
        tagInfoDic = {}
        if nodeList:
            for node in nodeList:
                outAttr = cmds.deformableShape(node, localShapeOutAttr=True)[0]
                tagHistList = cmds.geometryAttrInfo(node+"."+outAttr, componentTagHistory=True)
                if tagHistList:
                    tagInfoDic[node] = {}
                    for tagDic in tagHistList:
                        tagInfoDic[node][tagDic["key"]] = tagDic
                        tagInfoDic[node][tagDic["key"]].update({"components": cmds.geometryAttrInfo(node+"."+outAttr, components=True, componentTagExpression=tagDic["key"])})
        return tagInfoDic


    def getComponentTagInfluencer(self, deformerList=None, *args):
        """ Return the dictionary with the componentTag influencer info.
        """
        if not deformerList:
            deformerList = []
            for deformerType in self.typeAttrDic.keys():
                defList = cmds.ls(selection=False, type=deformerType)
                if defList:
                    deformerList.extend(defList)
        tagInfluenceDic = {}
        if deformerList:
            for deformerNode in deformerList:
                if cmds.objExists(deformerNode+".originalGeometry"):
                    origGeomList = cmds.getAttr(deformerNode+".originalGeometry", multiIndices=True)
                    if origGeomList:
                        hasTag = False
                        for index in origGeomList:
                            if not cmds.getAttr(deformerNode+".input["+str(index)+"].componentTagExpression") == "*":
                                hasTag = True
                                break
                        if hasTag:
                            tagInfluenceDic[deformerNode] = {"expression" : {}}
                            for index in origGeomList:
                                tagInfluenceDic[deformerNode]["expression"][index] = cmds.getAttr(deformerNode+".input["+str(index)+"].componentTagExpression")
        return tagInfluenceDic
    

    def setDeformerWeights(self, deformerNode, weightsDic, idx=0, *args):
        """ Set the deformer weights to the given node for the indexed shape.
        """
        for vtx in weightsDic.keys():
            cmds.setAttr(deformerNode+".weightList["+str(idx)+"].weights["+str(vtx)+"]", weightsDic[vtx])


    def getLatticePoints(self, latticeNode, *args):
        """ Return the points position of the given lattice node.
        """
        pointList = []
        # loop for all 3D points
        for s in range(0, cmds.getAttr(latticeNode+".sDivisions")):
            for t in range(0, cmds.getAttr(latticeNode+".tDivisions")):
                for u in range(0, cmds.getAttr(latticeNode+".uDivisions")):
                    pointList.append(cmds.getAttr(latticeNode+".pt["+str(s)+"]["+str(t)+"]["+str(u)+"]")[0])
        return pointList


    def setLatticePoints(self, latticeHandle, pointList, *args):
        """ Loop for all lattice 3D points and set them position.
        """
        i = 0
        for s in range(0, cmds.getAttr(latticeHandle+".sDivisions")):
            for t in range(0, cmds.getAttr(latticeHandle+".tDivisions")):
                for u in range(0, cmds.getAttr(latticeHandle+".uDivisions")):
                    cmds.xform(latticeHandle+".pt["+str(s)+"]["+str(t)+"]["+str(u)+"]", translation=pointList[i])
                    i += 1


    def getLatticeInfo(self, connectedNode, deformerNode, *args):
        """
        """
        return {
                "pointList" : self.getLatticePoints(connectedNode),
                "baseLatticeMatrix" : cmds.listConnections(deformerNode+".baseLatticeMatrix", destination=False, source=True)[0]
               }


    def getCurveInfo(self, curve, *args):
        """ Return a dictionary with the information about the curve like points, degree, spans, form and knots.
        """
        crvInfo = cmds.createNode("curveInfo")
        cmds.connectAttr(cmds.listRelatives(curve, children=True, type="shape")[0]+".worldSpace", crvInfo+".inputCurve", force=True)
        resultDic = {
                        "point"  : cmds.getAttr(curve+".cv[*]"),
                        "degree" : cmds.getAttr(curve+".degree"),
                        "spans"  : cmds.getAttr(curve+".spans"),
                        "form"   : cmds.getAttr(curve+".form"),
                        "knot"   : cmds.getAttr(crvInfo+".knots[*]")
                    }
        cmds.delete(crvInfo)
        return resultDic


    def getSculptInfo(self, deformerNode, *args):
        """ Return a dictionary of the connected nodes on sculptObjectGeometry and startPosition of the given sculpt deformer node.
        """
        return {
                "sculptor"      : cmds.listConnections(deformerNode+".sculptObjectGeometry", destination=False, source=True)[0],
                "originLocator" : cmds.listConnections(deformerNode+".startPosition", destination=False, source=True)[0]
                }


    def getAllDeformerTypeList(self, *args):
        """ Return a list of all current supported deformer types.
        """
        deformerList = list(self.typeAttrDic.keys())
        deformerList.extend(["skinCluster", "blendShape", "nonLinear"])
        return deformerList


    def getOrderList(self, node, *args):
        """ Return a list of deformer order of the given node.
        """
        resultList = []
        deformerList = self.getAllDeformerTypeList()
        inputDeformerList = cmds.listHistory(node, pruneDagObjects=True, interestLevel=True)
        if inputDeformerList:
            for item in inputDeformerList:
                if cmds.objectType(item) in deformerList:
                    if not item in resultList:
                      resultList.append(item)
        return resultList


    def setOrderList(self, node, desiredList, *args):
        """ Set the deformer order in the given node using the deformerList argument.
        """
        currentOrderList = self.getOrderList(node)
        if not currentOrderList == desiredList:
            # pair up the deformer list properly
            orderedDeformerPairs = self.getPairsFromList(desiredList)
            for pair in orderedDeformerPairs:
                cmds.reorderDeformers(pair[0], pair[1], node)


    def getPairsFromList(self, lst, *args):
        """ Returns pairs like 1-2, 2-3, 3-4, 4-5, etc...
        """
        resultList = []
        for i, item in enumerate(lst):
            if i < len(lst)-1:
                resultList.append([item, lst[i+1]])
        return resultList


    def assignDeformer(self, deformerNode, itemList, *args):
        """ Assign the deformer node to the given item list if it isn't assigned yet.
        """
        if deformerNode and itemList:
            for item in itemList:
                needToAddDef = True
                inputDeformerList = cmds.listHistory(item, pruneDagObjects=True, interestLevel=True)
                if inputDeformerList:
                    if deformerNode in inputDeformerList:
                        needToAddDef = False
                if needToAddDef:
                    cmds.deformer(deformerNode, edit=True, geometry=item)
