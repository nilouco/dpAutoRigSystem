# importing libraries:
from maya import cmds
from maya import mel
from ....library.base import action

# global variables to this module:
CLASS_NAME = "DeformationIO"
TITLE = "r033_deformationIO"
DESCRIPTION = "r034_deformationIODesc"
WIKI = "10-‐-Rebuilder#-deformation"



class DeformationIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_deformationIO"
        self.start_name = "dpDeformation"
    

    def run_action(self, first_mode=True, inputs=None, *args):
        """ Main method to process this validator instructions.
            It's in export mode by default.
            If first_mode parameter is False, it'll run in import mode.
            Returns dataLog with the validation result as:
                - checked_items = node list of checked items
                - found_issues = True if an issue was found, False if there isn't an issue for the checked node
                - good_results = True if well done, False if we got an error
                - messages = reported text
        """
        # starting
        self.first_mode = first_mode
        self.cleanup_to_start(True)
        
        # ---
        # --- rebuilder code --- beginning
        if not cmds.file(query=True, reference=True):
            if self.ar.pipeliner.check_asset_context():
                self.io_path = self.get_io_path(self.io_folder)
                if self.io_path:
                    if self.first_mode: #export
                        items = None
                        if inputs:
                            items = inputs
                        else:
                            items = cmds.listRelatives(cmds.ls(selection=False, type="mesh"), parent=True) or []
                            items.extend(cmds.listRelatives(cmds.ls(selection=False, type="nurbsCurve"), parent=True) or [])
                        if items:
                            # finding deformers
                            has_def = False
                            input_deformers = cmds.listHistory(items, pruneDagObjects=False, interestLevel=True)
                            for deformer_type in self.ar.skin.typeAttrDic.keys():
                                if cmds.ls(input_deformers, type=deformer_type):
                                    has_def = True
                                    break
                            if has_def:
                                self.export_json_file(self.get_deformer_data(input_deformers))
                            else:
                                self.maybe_done_io(self.ar.data.lang['v014_notFoundNodes']+" deformers")
                        else:
                            self.maybe_done_io(self.ar.data.lang['v014_notFoundNodes']+" mesh")
                    else: #import
                        deformer_data = self.import_latest_json_file(self.get_exported_items())
                        if deformer_data:
                            self.import_deformation_data(deformer_data)
                        else:
                            self.maybe_done_io(self.ar.data.lang['r007_notExportedData'])
                else:
                    self.fail_io(self.ar.data.lang['r010_notFoundPath'])
            else:
                self.fail_io(self.ar.data.lang['r027_noAssetContext'])
        else:
            self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- rebuilder code --- end
        # ---

        # finishing
        cmds.select(clear=True)
        self.update_action_buttons()
        self.report_log()
        self.end_progress()
        self.refresh_view()
        return self.log_data


    def get_deformer_data(self, input_deformers):
        """ Return the deformer data dictionary to export.
        """
        self.ar.utils.setProgress(max=len(self.ar.skin.typeAttrDic.keys()), add_one=False, add_number=False)
        # Declaring the data dictionary to export it
        deformer_data = {}
        # run for all deformer types to get info
        for deformer_type in self.ar.skin.typeAttrDic.keys():
            self.ar.utils.setProgress(self.ar.data.lang[self.title])
            deformers = cmds.ls(selection=False, type=deformer_type)
            if deformers:
                for deformer_node in deformers:
                    if deformer_node in input_deformers:
                        # get the attributes and values for this deformer node
                        deformer_data[deformer_node] = self.ar.skin.getDeformerInfo(deformer_node)
                        # Get shape indexes for the deformer so we can query the deformer weights
                        shapes, indexes, shape_to_index_data = self.ar.skin.getShapeToIndexData(deformer_node)
                        # update dictionary
                        deformer_data[deformer_node]["shapes"] = shapes
                        deformer_data[deformer_node]["indexes"] = indexes
                        deformer_data[deformer_node]["shape_to_index_data"] = shape_to_index_data
                        deformer_data[deformer_node]["weights"] = {}
                        for shape in shapes:
                            # Get weights
                            index = shape_to_index_data[shape]
                            weights = self.ar.skin.getDeformerWeights(deformer_node, index)
                            if deformer_data[deformer_node]["relatedNode"]: 
                                if not deformer_type == "ffd":
                                    # nonLinear because other don't have weights (wrap, shrinkWrap and wire)
                                    weights = self.ar.skin.getDeformerWeights(deformer_data[deformer_node]["relatedNode"], index)
                            deformer_data[deformer_node]["weights"][index] = weights
                        # componentTag
                        deformer_data[deformer_node]["componentTag"] = self.ar.skin.checkUseComponentTag(deformer_node)
                        # parenting
                        deformer_data[deformer_node]["father"] = None
                        if deformer_data[deformer_node]["relatedNode"]:
                            if cmds.listRelatives(deformer_data[deformer_node]["relatedNode"], allParents=True):
                                deformer_data[deformer_node]["father"] = cmds.listRelatives(deformer_data[deformer_node]["relatedNode"], allParents=True, fullPath=True)[0]
        return deformer_data


    def import_deformation(self, deformer_node, deformer_data, well_imported):
        """ Import deformer data creating a new deformer node, set values and weights.
        """
        self.existShapeList = [s for s in deformer_data[deformer_node]["shapes"] if cmds.objExists(s)]
        new_def_node = None
        # verify if the deformer node exists to don't recreate it and import data
        if cmds.objExists(deformer_node):
            new_def_node = deformer_node
            self.ar.skin.assignDeformer(deformer_node, self.existShapeList)
        else:
            # create a new deformer if it doesn't exists
            if deformer_data[deformer_node]["type"] == "cluster":
                new_def_node = cmds.cluster(self.existShapeList, name=deformer_data[deformer_node]["name"], useComponentTags=deformer_data[deformer_node]["componentTag"])[0] #[cluster, handle]
            elif deformer_data[deformer_node]["type"] == "deltaMush":
                new_def_node = cmds.deltaMush(self.existShapeList, name=deformer_data[deformer_node]["name"], useComponentTags=deformer_data[deformer_node]["componentTag"])[0] #[deltaMush]
            elif deformer_data[deformer_node]["type"] == "tension":
                new_def_node = cmds.tension(self.existShapeList, name=deformer_data[deformer_node]["name"], useComponentTags=deformer_data[deformer_node]["componentTag"])[0] #[tension]
            elif deformer_data[deformer_node]["type"] == "ffd":
                lattice_items = cmds.lattice(self.existShapeList, name=deformer_data[deformer_node]["name"], divisions=deformer_data[deformer_node]["divisions"], useComponentTags=deformer_data[deformer_node]["componentTag"]) #[set, ffd, base] 
                new_def_node = lattice_items[0]
                self.ar.skin.setLatticePoints(lattice_items[1], deformer_data[deformer_node]["relatedData"]["pointList"])
                cmds.rename(lattice_items[1], deformer_data[deformer_node]["relatedNode"])
                cmds.rename(lattice_items[2], deformer_data[deformer_node]["relatedData"]["baseLatticeMatrix"])
            elif deformer_data[deformer_node]["type"] == "sculpt":
                sculpt_items = cmds.sculpt(self.existShapeList, name=deformer_data[deformer_node]["name"], useComponentTags=deformer_data[deformer_node]["componentTag"]) #[sculpt, sculptor, orig]
                new_def_node = sculpt_items[0]
                cmds.rename(sculpt_items[1], deformer_data[deformer_node]["relatedData"]["sculptor"])
                cmds.rename(sculpt_items[2], deformer_data[deformer_node]["relatedData"]["originLocator"])
            elif deformer_data[deformer_node]["type"] == "wrap":
                if cmds.objExists(deformer_data[deformer_node]["relatedNode"]):
                    wrap_base_shape = False
                    if "inflType" in cmds.listAttr(deformer_data[deformer_node]["relatedNode"]):
                        plugged_items = cmds.listConnections(deformer_data[deformer_node]["relatedNode"]+".inflType", destination=True, source=False)
                        if plugged_items:
                            for plugged in plugged_items:
                                if cmds.objectType(plugged) == "wrap":
                                    wrap_base_shapes = cmds.listConnections(plugged+".basePoints[0]", destination=False, source=True)
                                    if wrap_base_shapes:
                                        wrap_base_shape = wrap_base_shapes[0]
                                        break
                    cmds.select(self.existShapeList, deformer_data[deformer_node]["relatedNode"])
                    mel.eval("CreateWrap;")
                    hist = cmds.listHistory(self.existShapeList)
                    wrap_items = cmds.ls(hist, type="wrap")[0]
                    new_def_node = cmds.rename(wrap_items, deformer_data[deformer_node]["name"])
                    new_wrap_base_node = cmds.listConnections(new_def_node+".basePoints[0]", destination=False, source=True)[0]
                    if wrap_base_shape:
                        cmds.connectAttr(wrap_base_shape+".worldMesh[0]", new_def_node+".basePoints[0]", force=True)
                        cmds.delete(new_wrap_base_node)
                    support_grp = self.ar.utils.getNodeByMessage("supportGrp")
                    if support_grp:
                        parent_nodes = []
                        if wrap_base_shape:
                            parent_nodes = cmds.listRelatives(wrap_base_shape, parent=True)
                        else:
                            parent_nodes = cmds.listRelatives(new_wrap_base_node, parent=True)
                        if parent_nodes:
                            if not parent_nodes[0] == support_grp:
                                cmds.parent(new_wrap_base_node, support_grp)
            elif deformer_data[deformer_node]["type"] == "shrinkWrap":
                new_def_node = cmds.deformer(self.existShapeList, type=deformer_data[deformer_node]["type"], name=deformer_data[deformer_node]["name"], useComponentTags=deformer_data[deformer_node]["componentTag"])[0] #shrinkWrap
                for c_attr in ["continuity", "smoothUVs", "keepBorder", "boundaryRule", "keepHardEdge", "propagateEdgeHardness", "keepMapBorders"]:
                    cmds.connectAttr(deformer_data[deformer_node]["relatedNode"]+"."+c_attr, new_def_node+"."+c_attr, force=True)
                cmds.connectAttr(deformer_data[deformer_node]["relatedNode"]+".worldMesh", new_def_node+".targetGeom", force=True)
            elif deformer_data[deformer_node]["type"] == "wire":
                if not cmds.objExists(deformer_data[deformer_node]["relatedNode"]):
                    is_periodic = False
                    if deformer_data[deformer_node]["relatedData"]["form"] == 2:
                        is_periodic = True
                    cmds.curve(name=deformer_data[deformer_node]["relatedNode"], periodic=is_periodic, point=deformer_data[deformer_node]["relatedData"]["point"], degree=deformer_data[deformer_node]["relatedData"]["degree"], knot=deformer_data[deformer_node]["relatedData"]["knot"])
                new_def_node = cmds.wire(self.existShapeList, wire=deformer_data[deformer_node]["relatedNode"], name=deformer_data[deformer_node]["name"], useComponentTags=deformer_data[deformer_node]["componentTag"])[0] #wire
            elif deformer_data[deformer_node]["nonLinear"]:
                non_linears = cmds.nonLinear(self.existShapeList, type=deformer_data[deformer_node]["nonLinear"], name=deformer_data[deformer_node]["name"], useComponentTags=deformer_data[deformer_node]["componentTag"]) #[def, handle] bend, flare, sine, squash, twist, wave
                new_def_node = non_linears[0]
                cmds.rename(non_linears[1], deformer_data[deformer_node]["relatedData"])
            else: #solidify, proximityWrap, morph, textureDeformer, jiggle
                new_def_node = cmds.deformer(self.existShapeList, type=deformer_data[deformer_node]["type"], name=deformer_data[deformer_node]["name"], useComponentTags=deformer_data[deformer_node]["componentTag"])[0]
            if deformer_data[deformer_node]["type"] == "morph":
                if cmds.objExists(deformer_data[deformer_node]["relatedNode"]):
                    cmds.connectAttr(deformer_data[deformer_node]["relatedNode"]+".worldMesh[0]", new_def_node+".morphTarget[0]", force=True)
                else:
                    well_imported = False
                    self.fail_io(self.latest_data_file+": "+deformer_node+" - "+deformer_data[deformer_node]["relatedNode"])
        # parenting
        need_parent_it = False
        if deformer_data[deformer_node]["father"]:
            if cmds.objExists(deformer_data[deformer_node]["father"]):
                if cmds.listRelatives(deformer_data[deformer_node]["relatedNode"], allParents=True, fullPath=True):
                    if not deformer_data[deformer_node]["father"] in cmds.listRelatives(deformer_data[deformer_node]["relatedNode"], allParents=True, fullPath=True):
                        need_parent_it = True
                else:
                    need_parent_it = True
        if need_parent_it:
            if deformer_data[deformer_node]["type"] == "ffd":
                cmds.parent([deformer_data[deformer_node]["relatedNode"], deformer_data[deformer_node]["relatedData"]["baseLatticeMatrix"]], deformer_data[deformer_node]["father"])
            else:
                cmds.parent(deformer_data[deformer_node]["relatedNode"], deformer_data[deformer_node]["father"])
        # import attribute values
        if new_def_node:
            for attr in deformer_data[deformer_node]["attributes"].keys():
                try:
                    cmds.setAttr(new_def_node+"."+attr, deformer_data[deformer_node]["attributes"][attr])
                except:
                    pass #just to avoid try set connected attributes like envelope or curvature.
        # import deformer weights, except for skinCluster, blendShape, sculpt, wrap
        weights_data = deformer_data[deformer_node]["weights"]
        if weights_data:
            for index in deformer_data[deformer_node]["indexes"]:
                currentIndex = self.ar.skin.getCurrentDeformedIndex(deformer_node, deformer_data[deformer_node]["shape_to_index_data"], index)
                if weights_data[str(index)]:
                    # cluster, deltaMush, tension, ffd, shrinkWrap, wire, nonLinear, solidify, proximityWrap, textureDeformer, jiggle
                    self.ar.skin.setDeformerWeights(deformer_data[deformer_node]["name"], weights_data[str(index)], currentIndex)
        return well_imported


    def import_deformation_data(self, deformer_data):
        """ Import the deformation from exported file using the given dictionary.
        """
        well_imported = True
        to_import_items, not_found_meshs, changed_shape_meshes = [], [], []
        for deformer_node in deformer_data.keys():
            # check mesh existing
            for shape in deformer_data[deformer_node]["shapes"]:
                if cmds.objExists(shape):
                    if not deformer_node in to_import_items:
                        to_import_items.append(deformer_node)
                else:
                    not_found_meshs.append(deformer_node)
        if to_import_items:
            self.ar.utils.setProgress(max=len(to_import_items), add_one=False, add_number=False)
            for deformer_node in to_import_items:
                self.ar.utils.setProgress(self.ar.data.lang[self.title])
                try:
                    well_imported = self.import_deformation(deformer_node, deformer_data, well_imported)
                except Exception as e:
                    self.fail_io(self.latest_data_file+": "+deformer_node+" - "+str(e))
            if not_found_meshs: #call again the same instruction to try create a deformer in a deformer, like a cluster in a lattice.
                for deformer_node in not_found_meshs:
                    for shape in deformer_data[deformer_node]["shapes"]:
                        if cmds.objExists(shape):
                            try:
                                well_imported = self.import_deformation(deformer_node, deformer_data, well_imported)
                            except Exception as e:
                                self.fail_io(self.latest_data_file+": "+deformer_node+" - "+str(e))
            if well_imported:
                self.well_done_io(self.latest_data_file)
        else:
            self.fail_io(self.ar.data.lang['v014_notFoundNodes']+" "+str(', '.join(deformer_data.keys())))
        if not well_imported:
            if changed_shape_meshes:
                self.fail_io(self.ar.data.lang['r018_changedMesh']+" shape "+str(', '.join(changed_shape_meshes)))
            elif not_found_meshs:
                self.fail_io(self.ar.data.lang['v014_notFoundNodes']+" "+str(', '.join(not_found_meshs)))
