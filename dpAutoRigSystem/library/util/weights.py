# importing libraries:
from maya import cmds
from maya import mel



class Weights(object):
    def __init__(self, ar):
        self.ar = ar
        self.def_attr_data = {
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
    
    
    def get_io_filename(self, mesh):
        """ Returns the cut file_name if found "|" in the given mesh name to avoid windows special character backup issue.
        """
        file_name = mesh
        if "|" in mesh:
            file_name = mesh[mesh.rfind("|")+1:]
        return file_name
    

    def get_deformer_order(self, def_items):
        """ Find and return the latest old deformer order index for the given list.
            It's useful to reorder the deformers and place the new skinCluster to the correct position of deformation.
        """
        for d, dest_item in enumerate(def_items[1]):
            if not cmds.objExists(dest_item):
                if dest_item in def_items[2]: #it's an old deformer node
                    if d > 0:
                        return d
        return 0


    def get_deformer_weights(self, deformer_node, idx, influences=False, *args):
        """ Read the deformer information to return a dictionary with influence index or connected matrix nodes as keys and the weight as values.
        """
        weight_plug = deformer_node+".weightList["+str(idx)+"].weights"
        if cmds.objExists(weight_plug):
            weight_keys = cmds.getAttr(weight_plug, multiIndices=True)
            if influences:
                matrix_items = []
                for item in weight_keys:
                    sources = cmds.listConnections(deformer_node+".matrix["+str(item)+"]", source=True, destination=False)
                    if sources:
                        matrix_items.append(sources[0])
                weight_keys = matrix_items
            if weight_keys:
                for weight_index in weight_keys:
                    values = cmds.getAttr(weight_plug)[0]
                    #if any(x != 1.0 for x in values):
                    return dict(zip(weight_keys, values))
    

    def unlock_joints(self, skincluster_node):
        """ Just unlock joints from a given skinCluster node.
        """
        for joint in cmds.skinCluster(skincluster_node, influences=True, query=True):
            cmds.setAttr(joint+".liw", 0)


    def normalize_item_weights(self, item):
        """ Just normalize the skinCluster weigths for the given item.
        """
        for skincluster_node in self.check_existing_deformer_node(item)[2]:
            self.unlock_joints(skincluster_node)
            cmds.skinPercent(skincluster_node, item, normalize=True)


    def get_connected_matrix_data(self, deformer_name):
        """ Returns a dictionary with the connected matrix nodes as keys and their index as values.
            Useful to set skinCluster weights values correctly.
        """
        matrix_data = {}
        matrix_items = cmds.getAttr(deformer_name+".matrix", multiIndices=True)
        for m in matrix_items:
            matrix_items = cmds.listConnections(deformer_name+".matrix["+str(m)+"]", source=True, destination=False)
            if matrix_items:
                matrix_data[matrix_items[0]] = m
        return matrix_data


    def get_deformed_items(self, deformer_types=["skinCluster"], ignore_attr="None"):
        """ Returns a list of deformed item transforms of meshes and nurbsCurves.
            Use given lists and attribute to filter the results.
        """
        deformerd_items, done_items = [], []
        items = cmds.ls(selection=False, noIntermediate=True, long=True, type="mesh") or []
        items.extend(cmds.ls(selection=False, noIntermediate=True, long=True, type="nurbsCurve") or [])
        if items:
            for item in items:
                transform_node = item[:item[1:].find("|")+1]
                if not transform_node in done_items:
                    done_items.append(transform_node)
                    transforms = cmds.listRelatives(transform_node, allDescendents=True, children=True, fullPath=True, type="transform")
                    if transforms:
                        transforms.append(transform_node)
                    else:
                        transforms = [transform_node]
                    for child in transforms:
                        if not cmds.objExists(child+"."+ignore_attr):
                            if len(cmds.ls(child[child.rfind("|")+1:])) == 1:
                                child = child[child.rfind("|")+1:] #unique name
                            else:
                                print(self.ar.data.lang['i299_notUniqueName'], child)
                            for desired_type in deformer_types:
                                if self.check_existing_deformer_node(child, deformer_type=desired_type)[0]:
                                    if not child in deformerd_items:
                                        deformerd_items.append(child)
        return deformerd_items


    def check_existing_deformer_node(self, item, deleteIt=False, deformer_type="skinCluster"):
        """ Return a list with:
                True/False if there's/not a deformer.
                The current deformer list by default.
                A list with existing deformer nodes by givenType.
            Delete existing deformer node if there's one using the deleteIt parametter as True.
        """
        result = [False, None, None]
        input_deformers = cmds.listHistory(item, pruneDagObjects=True, interestLevel=True)
        if input_deformers:
            def_items = cmds.ls(input_deformers, type=deformer_type)
            if def_items:
                if deleteIt:
                    cmds.delete(def_items)
                result = [True, input_deformers, def_items]
        return result


    def get_deformer_info(self, deformer_node):
        """ Return the dictionary with attributes and values.
        """
        def_data = {"attributes" : {}}
        if deformer_node:
            def_type = cmds.objectType(deformer_node)
            def_data["type"] = def_type
            for n, attr in enumerate(list(self.def_attr_data[def_type])):
                if n == 0:
                    def_data["nonLinear"] = None
                    def_data["relatedNode"] = None
                    def_data["relatedData"] = None
                    def_data["divisions"] = None
                    if attr:
                        connected_nodes = None
                        connected_nodes = cmds.listConnections(deformer_node+"."+attr, destination=False, source=True)
                        if attr == "deformerData": #nonLinear
                            connected_nodes = cmds.listConnections(deformer_node+"."+attr, destination=True, source=False)
                            if connected_nodes:
                                def_data["relatedData"] = cmds.listRelatives(deformer_node, parent=True, type="transform")[0]
                                deformer_node = connected_nodes[0]
                                def_data["nonLinear"] = def_type.replace("deform", "").lower()
                        if def_type == "ffd": #lattice
                            def_data["relatedData"] = self.get_lattice_info(connected_nodes[0], deformer_node)
                            def_data["divisions"] = cmds.lattice(deformer_node, query=True, divisions=True)
                        elif def_type == "wire":
                            def_data["relatedData"] = self.get_curve_info(connected_nodes[0])
                        if connected_nodes:
                            def_data["relatedNode"] = connected_nodes[0]
                    if def_type == "sculpt":
                        def_data["relatedData"] = self.get_sculpt_info(deformer_node)
                    elif def_type == "morph":
                        def_data["relatedNode"] = cmds.listConnections(deformer_node+".morphTarget[0]", destination=False, source=True)[0]
                else:
                    def_data["attributes"][attr] = cmds.getAttr(deformer_node+"."+attr)
            def_data["name"] = deformer_node
        return def_data


    def get_component_tag_info(self, nodes=None):
        """ Return the dictionary with the componentTag tagged info.
        """
        if not nodes:
            nodes = cmds.listRelatives(cmds.ls(selection=False, type=["mesh", "lattice"]), parent=True)
        tag_info_data = {}
        if nodes:
            for node in nodes:
                out_attr = cmds.deformableShape(node, localShapeOutAttr=True)[0]
                tag_hists = cmds.geometryAttrInfo(node+"."+out_attr, componentTagHistory=True)
                if tag_hists:
                    tag_info_data[node] = {}
                    for tag_dic in tag_hists:
                        tag_info_data[node][tag_dic["key"]] = tag_dic
                        tag_info_data[node][tag_dic["key"]].update({"components": cmds.geometryAttrInfo(node+"."+out_attr, components=True, componentTagExpression=tag_dic["key"])})
        return tag_info_data


    def get_component_tag_influencer(self, deformers=None):
        """ Return the dictionary with the componentTag influencer info.
        """
        if not deformers:
            deformers = []
            for deformer_type in self.def_attr_data.keys():
                def_items = cmds.ls(selection=False, type=deformer_type)
                if def_items:
                    deformers.extend(def_items)
        tag_influence_data = {}
        if deformers:
            for deformer_node in deformers:
                if cmds.objExists(deformer_node+".originalGeometry"):
                    orig_geos = cmds.getAttr(deformer_node+".originalGeometry", multiIndices=True)
                    if orig_geos:
                        has_tag = False
                        for index in orig_geos:
                            if not cmds.getAttr(deformer_node+".input["+str(index)+"].componentTagExpression") == "*":
                                has_tag = True
                                break
                        if has_tag:
                            tag_influence_data[deformer_node] = {"expression" : {}}
                            for index in orig_geos:
                                tag_influence_data[deformer_node]["expression"][index] = cmds.getAttr(deformer_node+".input["+str(index)+"].componentTagExpression")
        return tag_influence_data
    

    def get_component_tag_falloff(self, nodes=None):
        """ Mount and return a dictionary with all componentTag falloff nodes to export them.
        """
        falloff_data = {}
        fallof_type_attr_data = {
                                "primitiveFalloff" : ["primitive", "useOriginalGeometry", "vertexSpace", "positiveSizeX", "positiveSizeY", "positiveSizeZ", "negativeSizeX", "negativeSizeY", "negativeSizeZ"],
                                "blendFalloff"     : ["baseWeight"],
                                "uniformFalloff"   : ["uniformWeight"],
                                "proximityFalloff" : ["useOriginalGeometry", "vertexSpace", "volume", "proximitySubset", "useBindTags", "bindTagsFilter"],
                                "subsetFalloff"    : ["useFalloffTags", "falloffTags",  "withinBoundary",  "useOriginalGeometry",  "mode",  "scale"],
                                "componentFalloff" : None,
                                "transferFalloff"  : ["useBindTags", "bindTagsFilter"]
                                }
        common_attrs = ["start", "end"]
        multi_attr_data = { "ramp"             : ["ramp_Position", "ramp_FloatValue", "ramp_Interp"],
                            "target"           : ["weight", "mode"],
                            "weightInfoLayers" : ["defaultWeight"]
                            }
        if not nodes:
            nodes = cmds.ls(selection=False, type=list(fallof_type_attr_data.keys()))
        if nodes:
            for node in nodes:
                node_type = cmds.objectType(node)
                falloff_data[node] = { "name" : node,
                                     "type" : node_type,
                                     "outputWeightFunction" : cmds.listConnections(node+".outputWeightFunction", source=False, destination=True, plugs=True),
                                     "attributes" : {}
                                    }
                # node attributes and common
                if fallof_type_attr_data[node_type]:
                    for attr in (fallof_type_attr_data[node_type] + common_attrs):
                        if cmds.objExists(node+"."+attr):
                            falloff_data[node]["attributes"][attr] = cmds.getAttr(node+"."+attr)
                # specific multiIndices attributes
                for multi_attr in multi_attr_data.keys():
                    if cmds.objExists(node+"."+multi_attr):
                        if cmds.getAttr(node+"."+multi_attr, multiIndices=True):
                            for i, index in enumerate(cmds.getAttr(node+"."+multi_attr, multiIndices=True)):
                                for name in multi_attr_data[multi_attr]:
                                    attr_name = multi_attr+"["+str(index)+"]."+name
                                    falloff_data[node]["attributes"][attr_name] = cmds.getAttr(node+"."+attr_name)
        return falloff_data
    

    def import_component_tag(self, tagged_node, tag_name, injest_node, component_items):
        """
            Import component_items to the tagged node using the injest_node as injestLocation parameter.
            Need to eval a MEL command because seems the Python command isn't implemented properly in Maya2022.
        """
        well_imported = True
        index = 0
        indexes = cmds.getAttr(tagged_node+".componentTags", multiIndices=True)
        if indexes:
            index = len(indexes)+1
        contents = " ".join(component_items)
        try:
            cmds.setAttr(injest_node+".componentTags["+str(index)+"].componentTagName", tag_name, type="string")
            #cmds.setAttr(tags[0]+".componentTags["+str(index)+"].componentTagContents", len(component_items), contents, type="component_items")
            mel.eval('setAttr '+injest_node+'.componentTags['+str(index)+'].componentTagContents -type component_items '+str(len(component_items))+' '+contents+';')
        except:
            well_imported = False
        return well_imported


    def import_component_tag_info(self, tagged_data, nodes):
        """ Import component tag tagged "nodes" as "tag" info.
        """
        well_imported = True
        to_import_items, self.not_work_well_infos = [], []
        current_tagged_data = self.get_component_tag_info(nodes)
        for tagged_node in tagged_data.keys():
            # check mesh existing
            if cmds.objExists(tagged_node):
                for tag in tagged_data[tagged_node].keys():
                    if not current_tagged_data:
                        to_import_items.append([tagged_node, tag, tagged_data[tagged_node][tag]["node"]])
                    elif tagged_node in current_tagged_data.keys():
                        if not tag in current_tagged_data[tagged_node]:
                            if not [tagged_node, tag, tagged_data[tagged_node][tag]["node"]] in to_import_items:
                                to_import_items.append([tagged_node, tag, tagged_data[tagged_node][tag]["node"]])
                    else:
                        if not [tagged_node, tag, tagged_data[tagged_node][tag]["node"]] in to_import_items:
                            to_import_items.append([tagged_node, tag, tagged_data[tagged_node][tag]["node"]])
            else:
                self.not_work_well_infos.append(tagged_node)
                well_imported = False
        if to_import_items:
            for tags in to_import_items:
                try:
                    well_imported = self.import_component_tag(tags[0], tags[1], tags[2], tagged_data[tags[0]][tags[1]]["components"], well_imported)
                except Exception as e:
                    self.not_work_well_infos.append(", ".join(tags)+" - "+str(e))
                    well_imported = False
        return well_imported


    def import_component_tag_influencer(self, inf_data):
        """ Import component tag influencer info from deformer nodes.
        """
        well_imported = True
        self.not_work_well_infos = []
        for inf_node in inf_data.keys():
            # check deformer node existing
            if cmds.objExists(inf_node):
                for inf_index in inf_data[inf_node]["expression"].keys():
                    if not inf_data[inf_node]["expression"][inf_index] == "":
                        try:
                            cmds.setAttr(inf_node+".input["+str(inf_index)+"].componentTagExpression", inf_data[inf_node]["expression"][inf_index], type="string")
                        except Exception as e:
                            self.not_work_well_infos.append(inf_node+" - "+str(e))
                            well_imported = False
        return well_imported


    def import_component_tag__falloff(self, falloff_data):
        """ Import the component tag falloff info.
            Create them if they don't exists.
            Connect node attributes.
            Set all specific node attributes for each falloff type.
        """
        well_imported = True
        self.not_work_well_infos = []
        for falloff_node in falloff_data.keys():
            # check falloff node existing
            if not cmds.objExists(falloff_node):
                falloff_node = cmds.createNode(falloff_data[falloff_node]["type"], name=falloff_data[falloff_node]["name"])
            if not falloff_node:
                self.not_work_well_infos.append(falloff_node)
                well_imported = False
            else:
                # connect falloff
                if falloff_data[falloff_node]["outputWeightFunction"]:
                    for plug in falloff_data[falloff_node]["outputWeightFunction"]:
                        if not cmds.listConnections(falloff_node+".outputWeightFunction", plugs=True, source=False, destination=True) or not plug in cmds.listConnections(falloff_node+".outputWeightFunction", plugs=True, source=False, destination=True):
                            try:
                                cmds.connectAttr(falloff_node+".outputWeightFunction", plug, force=True)
                            except:
                                self.not_work_well_infos.append(falloff_node+".outputWeightFunction -> "+plug)
                                well_imported = False
                # set falloff attributes
                for attr in falloff_data[falloff_node]["attributes"].keys():
                    try:
                        cmds.setAttr(falloff_node+"."+attr, falloff_data[falloff_node]["attributes"][attr])
                    except:
                        try:
                            cmds.setAttr(falloff_node+"."+attr, falloff_data[falloff_node]["attributes"][attr], type="string")
                        except:
                            self.not_work_well_infos.append(falloff_node+"."+attr)
                            well_imported = False
        return well_imported


    def set_deformer_weights(self, deformer_node, weights_data, idx=0):
        """ Set the deformer weights to the given node for the indexed shape.
        """
        for vtx in weights_data.keys():
            cmds.setAttr(deformer_node+".weightList["+str(idx)+"].weights["+str(vtx)+"]", weights_data[vtx])


    def get_lattice_points(self, lattice_node):
        """ Return the points position of the given lattice node.
        """
        points = []
        # loop for all 3D points
        for s in range(0, cmds.getAttr(lattice_node+".sDivisions")):
            for t in range(0, cmds.getAttr(lattice_node+".tDivisions")):
                for u in range(0, cmds.getAttr(lattice_node+".uDivisions")):
                    points.append(cmds.getAttr(lattice_node+".pt["+str(s)+"]["+str(t)+"]["+str(u)+"]")[0])
        return points


    def set_lattice_points(self, lattice_handle, points):
        """ Loop for all lattice 3D points and set them position.
        """
        i = 0
        for s in range(0, cmds.getAttr(lattice_handle+".sDivisions")):
            for t in range(0, cmds.getAttr(lattice_handle+".tDivisions")):
                for u in range(0, cmds.getAttr(lattice_handle+".uDivisions")):
                    cmds.xform(lattice_handle+".pt["+str(s)+"]["+str(t)+"]["+str(u)+"]", translation=points[i])
                    i += 1


    def get_lattice_info(self, connected_node, deformer_node):
        """
        """
        return {
                "pointList" : self.get_lattice_points(connected_node),
                "baseLatticeMatrix" : cmds.listConnections(deformer_node+".baseLatticeMatrix", destination=False, source=True)[0]
               }


    def get_curve_info(self, curve):
        """ Return a dictionary with the information about the curve like points, degree, spans, form and knots.
        """
        crv_info = cmds.createNode("curveInfo")
        cmds.connectAttr(cmds.listRelatives(curve, children=True, type="shape")[0]+".worldSpace", crv_info+".inputCurve", force=True)
        result_data = {
                        "point"  : cmds.getAttr(curve+".cv[*]"),
                        "degree" : cmds.getAttr(curve+".degree"),
                        "spans"  : cmds.getAttr(curve+".spans"),
                        "form"   : cmds.getAttr(curve+".form"),
                        "knot"   : cmds.getAttr(crv_info+".knots[*]")
                    }
        cmds.delete(crv_info)
        return result_data


    def get_sculpt_info(self, deformer_node):
        """ Return a dictionary of the connected nodes on sculptObjectGeometry and startPosition of the given sculpt deformer node.
        """
        return {
                "sculptor"      : cmds.listConnections(deformer_node+".sculptObjectGeometry", destination=False, source=True)[0],
                "originLocator" : cmds.listConnections(deformer_node+".startPosition", destination=False, source=True)[0]
                }


    def get_all_deformer_types(self):
        """ Return a list of all current supported deformer types.
        """
        deformers = list(self.def_attr_data.keys())
        deformers.extend(["skinCluster", "blendShape", "nonLinear"])
        return deformers


    def get_order_items(self, node):
        """ Return a list of deformer order of the given node.
        """
        results = []
        deformers = self.get_all_deformer_types()
        input_deformers = cmds.listHistory(node, pruneDagObjects=True, interestLevel=True)
        if input_deformers:
            for item in input_deformers:
                if cmds.objectType(item) in deformers:
                    if not item in results:
                      results.append(item)
        return results


    def set_order_items(self, node, desired_items):
        """ Set the deformer order in the given node using the deformers argument.
        """
        current_order_items = self.get_order_items(node)
        if not current_order_items == desired_items:
            # pair up the deformer list properly
            ordered_deformer_pairs = self.get_pairs_from_list(desired_items)
            for pair in ordered_deformer_pairs:
                try:
                    cmds.reorderDeformers(pair[0], pair[1], node)
                except:
                    pass


    def get_pairs_from_list(self, lst):
        """ Returns pairs like 1-2, 2-3, 3-4, 4-5, etc...
        """
        results = []
        for i, item in enumerate(lst):
            if i < len(lst)-1:
                results.append([item, lst[i+1]])
        return results


    def assign_deformer(self, deformer_node, items):
        """ Assign the deformer node to the given item list if it isn't assigned yet.
        """
        if deformer_node and items:
            for item in items:
                need_to_add_def = True
                input_deformers = cmds.listHistory(item, pruneDagObjects=True, interestLevel=True)
                if input_deformers:
                    if deformer_node in input_deformers:
                        need_to_add_def = False
                    else:
                        for input_def in input_deformers:
                            if deformer_node == input_def+"HandleShape": #hack to check if it's a nonLinear handle shape
                                need_to_add_def = False
                if need_to_add_def:
                    cmds.deformer(deformer_node, edit=True, geometry=item)


    def get_shape_to_index_data(self, deformer_node):
        """ Return a shapes, a indexes and a dictionary with the shape name as keys and deformer index as values.
        """
        shapes = cmds.ls(cmds.deformer(deformer_node, query=True, geometry=True), long=True)
        indexes = cmds.deformer(deformer_node, query=True, geometryIndices=True)
        return shapes, indexes, dict(zip(shapes, indexes))
    

    def get_current_deformed_index(self, deformer_node, shape_to_index_data, index):
        """ Returns the current deformer index based on the shape and current deformer index list.
        """
        current_index = index
        if deformer_node and shape_to_index_data:
            shape_name = None
            for node in shape_to_index_data.keys():
                if shape_to_index_data[node] == index:
                    shape_name = node
                    break
            if shape_name:
                current_shape_to_index_data = self.get_shape_to_index_data(deformer_node)[2]
                if current_shape_to_index_data:
                    for item in current_shape_to_index_data.keys():
                        if item == shape_name:
                            current_index = current_shape_to_index_data[item]
        return current_index


    def check_use_component_tag(self, deformer_node):
        """ Returns False if found an object set node in the deformer node given message output connections.
        """
        has_tag = True
        if deformer_node:
            message_outputs = cmds.listConnections(deformer_node+".message", destination=True, source=False)
            if message_outputs:
                for item in message_outputs:
                    if cmds.objectType(item) == "objectSet":
                        has_tag = False
                        break
        return has_tag
