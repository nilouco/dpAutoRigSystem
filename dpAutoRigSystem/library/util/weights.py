# importing libraries:
from maya import cmds
from maya import mel



class Weights(object):
    def __init__(self, ar, *args, **kwargs):
        """ Initialize the class.
        """
        # defining variables:
        self.ar = ar
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
        """ Returns the cut file_name if found "|" in the given mesh name to avoid windows special character backup issue.
        """
        file_name = mesh
        if "|" in mesh:
            file_name = mesh[mesh.rfind("|")+1:]
        return file_name
    

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


    def getDeformerWeights(self, deformer_node, idx, infList=False, *args):
        """ Read the deformer information to return a dictionary with influence index or connected matrix nodes as keys and the weight as values.
        """
        weightPlug = deformer_node+".weightList["+str(idx)+"].weights"
        if cmds.objExists(weightPlug):
            weightKeyList = cmds.getAttr(weightPlug, multiIndices=True)
            if infList:
                matrixList = []
                for item in weightKeyList:
                    sourceList = cmds.listConnections(deformer_node+".matrix["+str(item)+"]", source=True, destination=False)
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


    def normalizeItemWeights(self, item, *args):
        """ Just normalize the skinCluster weigths for the given item.
        """
        for skinClusterNode in self.checkExistingDeformerNode(item)[2]:
            self.unlockJoints(skinClusterNode)
            cmds.skinPercent(skinClusterNode, item, normalize=True)


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


    def getDeformedItemList(self, deformerTypeList=["skinCluster"], ignoreAttr="None", *args):
        """ Returns a list of deformed item transforms of meshes and nurbsCurves.
            Use given lists and attribute to filter the results.
        """
        deformedItemList, ranList = [], []
        items = cmds.ls(selection=False, noIntermediate=True, long=True, type="mesh") or []
        items.extend(cmds.ls(selection=False, noIntermediate=True, long=True, type="nurbsCurve") or [])
        if items:
            for item in items:
                transformNode = item[:item[1:].find("|")+1]
                if not transformNode in ranList:
                    ranList.append(transformNode)
                    transforms = cmds.listRelatives(transformNode, allDescendents=True, children=True, fullPath=True, type="transform")
                    if transforms:
                        transforms.append(transformNode)
                    else:
                        transforms = [transformNode]
                    for childNode in transforms:
                        if not cmds.objExists(childNode+"."+ignoreAttr):
                            if len(cmds.ls(childNode[childNode.rfind("|")+1:])) == 1:
                                childNode = childNode[childNode.rfind("|")+1:] #unique name
                            else:
                                print(self.ar.data.lang['i299_notUniqueName'], childNode)
                            for desiredType in deformerTypeList:
                                if self.checkExistingDeformerNode(childNode, deformer_type=desiredType)[0]:
                                    if not childNode in deformedItemList:
                                        deformedItemList.append(childNode)
        return deformedItemList


    def checkExistingDeformerNode(self, item, deleteIt=False, deformer_type="skinCluster", *args):
        """ Return a list with:
                True/False if there's/not a deformer.
                The current deformer list by default.
                A list with existing deformer nodes by givenType.
            Delete existing deformer node if there's one using the deleteIt parametter as True.
        """
        result = [False, None, None]
        input_deformers = cmds.listHistory(item, pruneDagObjects=True, interestLevel=True)
        if input_deformers:
            defList = cmds.ls(input_deformers, type=deformer_type)
            if defList:
                if deleteIt:
                    cmds.delete(defList)
                result = [True, input_deformers, defList]
        return result


    def getDeformerInfo(self, deformer_node, *args):
        """ Return the dictionary with attributes and values.
        """
        defDic = {"attributes" : {}}
        if deformer_node:
            defType = cmds.objectType(deformer_node)
            defDic["type"] = defType
            for n, attr in enumerate(list(self.typeAttrDic[defType])):
                if n == 0:
                    defDic["nonLinear"] = None
                    defDic["relatedNode"] = None
                    defDic["relatedData"] = None
                    defDic["divisions"] = None
                    if attr:
                        connectedNodeList = None
                        connectedNodeList = cmds.listConnections(deformer_node+"."+attr, destination=False, source=True)
                        if attr == "deformerData": #nonLinear
                            connectedNodeList = cmds.listConnections(deformer_node+"."+attr, destination=True, source=False)
                            if connectedNodeList:
                                defDic["relatedData"] = cmds.listRelatives(deformer_node, parent=True, type="transform")[0]
                                deformer_node = connectedNodeList[0]
                                defDic["nonLinear"] = defType.replace("deform", "").lower()
                        if defType == "ffd": #lattice
                            defDic["relatedData"] = self.getLatticeInfo(connectedNodeList[0], deformer_node)
                            defDic["divisions"] = cmds.lattice(deformer_node, query=True, divisions=True)
                        elif defType == "wire":
                            defDic["relatedData"] = self.getCurveInfo(connectedNodeList[0])
                        if connectedNodeList:
                            defDic["relatedNode"] = connectedNodeList[0]
                    if defType == "sculpt":
                        defDic["relatedData"] = self.getSculptInfo(deformer_node)
                    elif defType == "morph":
                        defDic["relatedNode"] = cmds.listConnections(deformer_node+".morphTarget[0]", destination=False, source=True)[0]
                else:
                    defDic["attributes"][attr] = cmds.getAttr(deformer_node+"."+attr)
            defDic["name"] = deformer_node
        return defDic


    def getComponentTagInfo(self, nodes=None, *args):
        """ Return the dictionary with the componentTag tagged info.
        """
        if not nodes:
            nodes = cmds.listRelatives(cmds.ls(selection=False, type=["mesh", "lattice"]), parent=True)
        tagInfoDic = {}
        if nodes:
            for node in nodes:
                outAttr = cmds.deformableShape(node, localShapeOutAttr=True)[0]
                tagHistList = cmds.geometryAttrInfo(node+"."+outAttr, componentTagHistory=True)
                if tagHistList:
                    tagInfoDic[node] = {}
                    for tagDic in tagHistList:
                        tagInfoDic[node][tagDic["key"]] = tagDic
                        tagInfoDic[node][tagDic["key"]].update({"components": cmds.geometryAttrInfo(node+"."+outAttr, components=True, componentTagExpression=tagDic["key"])})
        return tagInfoDic


    def getComponentTagInfluencer(self, deformers=None, *args):
        """ Return the dictionary with the componentTag influencer info.
        """
        if not deformers:
            deformers = []
            for deformer_type in self.typeAttrDic.keys():
                defList = cmds.ls(selection=False, type=deformer_type)
                if defList:
                    deformers.extend(defList)
        tagInfluenceDic = {}
        if deformers:
            for deformer_node in deformers:
                if cmds.objExists(deformer_node+".originalGeometry"):
                    origGeomList = cmds.getAttr(deformer_node+".originalGeometry", multiIndices=True)
                    if origGeomList:
                        hasTag = False
                        for index in origGeomList:
                            if not cmds.getAttr(deformer_node+".input["+str(index)+"].componentTagExpression") == "*":
                                hasTag = True
                                break
                        if hasTag:
                            tagInfluenceDic[deformer_node] = {"expression" : {}}
                            for index in origGeomList:
                                tagInfluenceDic[deformer_node]["expression"][index] = cmds.getAttr(deformer_node+".input["+str(index)+"].componentTagExpression")
        return tagInfluenceDic
    

    def getComponentTagFalloff(self, nodes=None, *args):
        """ Mount and return a dictionary with all componentTag falloff nodes to export them.
        """
        falloffDic = {}
        falloffTypeAttrDic = {
                            "primitiveFalloff" : ["primitive", "useOriginalGeometry", "vertexSpace", "positiveSizeX", "positiveSizeY", "positiveSizeZ", "negativeSizeX", "negativeSizeY", "negativeSizeZ"],
                            "blendFalloff"     : ["baseWeight"],
                            "uniformFalloff"   : ["uniformWeight"],
                            "proximityFalloff" : ["useOriginalGeometry", "vertexSpace", "volume", "proximitySubset", "useBindTags", "bindTagsFilter"],
                            "subsetFalloff"    : ["useFalloffTags", "falloffTags",  "withinBoundary",  "useOriginalGeometry",  "mode",  "scale"],
                            "componentFalloff" : None,
                            "transferFalloff"  : ["useBindTags", "bindTagsFilter"]
                        }
        commonAttrList = ["start", "end"]
        multiAttrDic = { "ramp"             : ["ramp_Position", "ramp_FloatValue", "ramp_Interp"],
                         "target"           : ["weight", "mode"],
                         "weightInfoLayers" : ["defaultWeight"]
                        }
        if not nodes:
            nodes = cmds.ls(selection=False, type=list(falloffTypeAttrDic.keys()))
        if nodes:
            for node in nodes:
                node_type = cmds.objectType(node)
                falloffDic[node] = { "name" : node,
                                     "type" : node_type,
                                     "outputWeightFunction" : cmds.listConnections(node+".outputWeightFunction", source=False, destination=True, plugs=True),
                                     "attributes" : {}
                                    }
                # node attributes and common
                if falloffTypeAttrDic[node_type]:
                    for attr in (falloffTypeAttrDic[node_type] + commonAttrList):
                        if cmds.objExists(node+"."+attr):
                            falloffDic[node]["attributes"][attr] = cmds.getAttr(node+"."+attr)
                # specific multiIndices attributes
                for multi_attr in multiAttrDic.keys():
                    if cmds.objExists(node+"."+multi_attr):
                        if cmds.getAttr(node+"."+multi_attr, multiIndices=True):
                            for i, index in enumerate(cmds.getAttr(node+"."+multi_attr, multiIndices=True)):
                                for name in multiAttrDic[multi_attr]:
                                    attr_name = multi_attr+"["+str(index)+"]."+name
                                    falloffDic[node]["attributes"][attr_name] = cmds.getAttr(node+"."+attr_name)
        return falloffDic
    

    def importComponentTag(self, taggedNode, tagName, injestNode, componentList, *args):
        """
            Import componentList to the tagged node using the injestNode as injestLocation parameter.
            Need to eval a MEL command because seems the Python command isn't implemented properly in Maya2022.
        """
        well_imported = True
        index = 0
        indexes = cmds.getAttr(taggedNode+".componentTags", multiIndices=True)
        if indexes:
            index = len(indexes)+1
        contents = " ".join(componentList)
        try:
            cmds.setAttr(injestNode+".componentTags["+str(index)+"].componentTagName", tagName, type="string")
            #cmds.setAttr(tagList[0]+".componentTags["+str(index)+"].componentTagContents", len(componentList), contents, type="componentList")
            mel.eval('setAttr '+injestNode+'.componentTags['+str(index)+'].componentTagContents -type componentList '+str(len(componentList))+' '+contents+';')
        except:
            well_imported = False
        return well_imported


    def importComponentTagInfo(self, taggedDic, nodes, *args):
        """ Import component tag tagged "nodes" as "tag" info.
        """
        well_imported = True
        to_import_items, self.notWorkWellInfoList = [], []
        currentTaggedDic = self.getComponentTagInfo(nodes)
        for taggedNode in taggedDic.keys():
            # check mesh existing
            if cmds.objExists(taggedNode):
                for tag in taggedDic[taggedNode].keys():
                    if not currentTaggedDic:
                        to_import_items.append([taggedNode, tag, taggedDic[taggedNode][tag]["node"]])
                    elif taggedNode in currentTaggedDic.keys():
                        if not tag in currentTaggedDic[taggedNode]:
                            if not [taggedNode, tag, taggedDic[taggedNode][tag]["node"]] in to_import_items:
                                to_import_items.append([taggedNode, tag, taggedDic[taggedNode][tag]["node"]])
                    else:
                        if not [taggedNode, tag, taggedDic[taggedNode][tag]["node"]] in to_import_items:
                            to_import_items.append([taggedNode, tag, taggedDic[taggedNode][tag]["node"]])
            else:
                self.notWorkWellInfoList.append(taggedNode)
                well_imported = False
        if to_import_items:
            for tagList in to_import_items:
                try:
                    well_imported = self.importComponentTag(tagList[0], tagList[1], tagList[2], taggedDic[tagList[0]][tagList[1]]["components"], well_imported)
                except Exception as e:
                    self.notWorkWellInfoList.append(", ".join(tagList)+" - "+str(e))
                    well_imported = False
        return well_imported


    def importComponentTagInfluencer(self, infDic, *args):
        """ Import component tag influencer info from deformer nodes.
        """
        well_imported = True
        self.notWorkWellInfoList = []
        for infNode in infDic.keys():
            # check deformer node existing
            if cmds.objExists(infNode):
                for infIndex in infDic[infNode]["expression"].keys():
                    if not infDic[infNode]["expression"][infIndex] == "":
                        try:
                            cmds.setAttr(infNode+".input["+str(infIndex)+"].componentTagExpression", infDic[infNode]["expression"][infIndex], type="string")
                        except Exception as e:
                            self.notWorkWellInfoList.append(infNode+" - "+str(e))
                            well_imported = False
        return well_imported


    def importComponentTagFalloff(self, falloffDic, *args):
        """ Import the component tag falloff info.
            Create them if they don't exists.
            Connect node attributes.
            Set all specific node attributes for each falloff type.
        """
        well_imported = True
        self.notWorkWellInfoList = []
        for falloffNode in falloffDic.keys():
            # check falloff node existing
            if not cmds.objExists(falloffNode):
                falloffNode = cmds.createNode(falloffDic[falloffNode]["type"], name=falloffDic[falloffNode]["name"])
            if not falloffNode:
                self.notWorkWellInfoList.append(falloffNode)
                well_imported = False
            else:
                # connect falloff
                if falloffDic[falloffNode]["outputWeightFunction"]:
                    for plug in falloffDic[falloffNode]["outputWeightFunction"]:
                        if not cmds.listConnections(falloffNode+".outputWeightFunction", plugs=True, source=False, destination=True) or not plug in cmds.listConnections(falloffNode+".outputWeightFunction", plugs=True, source=False, destination=True):
                            try:
                                cmds.connectAttr(falloffNode+".outputWeightFunction", plug, force=True)
                            except:
                                self.notWorkWellInfoList.append(falloffNode+".outputWeightFunction -> "+plug)
                                well_imported = False
                # set falloff attributes
                for attr in falloffDic[falloffNode]["attributes"].keys():
                    try:
                        cmds.setAttr(falloffNode+"."+attr, falloffDic[falloffNode]["attributes"][attr])
                    except:
                        try:
                            cmds.setAttr(falloffNode+"."+attr, falloffDic[falloffNode]["attributes"][attr], type="string")
                        except:
                            self.notWorkWellInfoList.append(falloffNode+"."+attr)
                            well_imported = False
        return well_imported


    def setDeformerWeights(self, deformer_node, weights_data, idx=0, *args):
        """ Set the deformer weights to the given node for the indexed shape.
        """
        for vtx in weights_data.keys():
            cmds.setAttr(deformer_node+".weightList["+str(idx)+"].weights["+str(vtx)+"]", weights_data[vtx])


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


    def getLatticeInfo(self, connectedNode, deformer_node, *args):
        """
        """
        return {
                "pointList" : self.getLatticePoints(connectedNode),
                "baseLatticeMatrix" : cmds.listConnections(deformer_node+".baseLatticeMatrix", destination=False, source=True)[0]
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


    def getSculptInfo(self, deformer_node, *args):
        """ Return a dictionary of the connected nodes on sculptObjectGeometry and startPosition of the given sculpt deformer node.
        """
        return {
                "sculptor"      : cmds.listConnections(deformer_node+".sculptObjectGeometry", destination=False, source=True)[0],
                "originLocator" : cmds.listConnections(deformer_node+".startPosition", destination=False, source=True)[0]
                }


    def getAllDeformerTypeList(self, *args):
        """ Return a list of all current supported deformer types.
        """
        deformers = list(self.typeAttrDic.keys())
        deformers.extend(["skinCluster", "blendShape", "nonLinear"])
        return deformers


    def getOrderList(self, node, *args):
        """ Return a list of deformer order of the given node.
        """
        results = []
        deformers = self.getAllDeformerTypeList()
        input_deformers = cmds.listHistory(node, pruneDagObjects=True, interestLevel=True)
        if input_deformers:
            for item in input_deformers:
                if cmds.objectType(item) in deformers:
                    if not item in results:
                      results.append(item)
        return results


    def setOrderList(self, node, desiredList, *args):
        """ Set the deformer order in the given node using the deformers argument.
        """
        currentOrderList = self.getOrderList(node)
        if not currentOrderList == desiredList:
            # pair up the deformer list properly
            orderedDeformerPairs = self.getPairsFromList(desiredList)
            for pair in orderedDeformerPairs:
                try:
                    cmds.reorderDeformers(pair[0], pair[1], node)
                except:
                    pass


    def getPairsFromList(self, lst, *args):
        """ Returns pairs like 1-2, 2-3, 3-4, 4-5, etc...
        """
        results = []
        for i, item in enumerate(lst):
            if i < len(lst)-1:
                results.append([item, lst[i+1]])
        return results


    def assignDeformer(self, deformer_node, items, *args):
        """ Assign the deformer node to the given item list if it isn't assigned yet.
        """
        if deformer_node and items:
            for item in items:
                needToAddDef = True
                input_deformers = cmds.listHistory(item, pruneDagObjects=True, interestLevel=True)
                if input_deformers:
                    if deformer_node in input_deformers:
                        needToAddDef = False
                    else:
                        for inputDef in input_deformers:
                            if deformer_node == inputDef+"HandleShape": #hack to check if it's a nonLinear handle shape
                                needToAddDef = False
                if needToAddDef:
                    cmds.deformer(deformer_node, edit=True, geometry=item)


    def getShapeToIndexData(self, deformer_node, *args):
        """ Return a shapes, a indexes and a dictionary with the shape name as keys and deformer index as values.
        """
        shapes = cmds.ls(cmds.deformer(deformer_node, query=True, geometry=True), long=True)
        indexes = cmds.deformer(deformer_node, query=True, geometryIndices=True)
        return shapes, indexes, dict(zip(shapes, indexes))
    

    def getCurrentDeformedIndex(self, deformer_node, shape_to_index_data, index, *args):
        """ Returns the current deformer index based on the shape and current deformer index list.
        """
        currentIndex = index
        if deformer_node and shape_to_index_data:
            shapeName = None
            for node in shape_to_index_data.keys():
                if shape_to_index_data[node] == index:
                    shapeName = node
                    break
            if shapeName:
                currentShapeToIndexDic = self.getShapeToIndexData(deformer_node)[2]
                if currentShapeToIndexDic:
                    for item in currentShapeToIndexDic.keys():
                        if item == shapeName:
                            currentIndex = currentShapeToIndexDic[item]
        return currentIndex


    def checkUseComponentTag(self, deformer_node, *args):
        """ Returns False if found an object set node in the deformer node given message output connections.
        """
        hasTag = True
        if deformer_node:
            messageOutputList = cmds.listConnections(deformer_node+".message", destination=True, source=False)
            if messageOutputList:
                for item in messageOutputList:
                    if cmds.objectType(item) == "objectSet":
                        hasTag = False
                        break
        return hasTag
