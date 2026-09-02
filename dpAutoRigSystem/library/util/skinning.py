# importing libraries:
from maya import cmds
from maya import mel
from . import weights
from importlib import reload



class Skinning(weights.Weights):
    def __init__(self, ar):
        if ar.dev:
            reload(weights)
        weights.Weights.__init__(self, ar)
        # defining variables:
        self.ignore_skinning_attr = "dpDoNotSkinIt"
        self.io_start_name = "skinning"
        

    def validate_geos(self, geos, mode=None):
        """ Check if the geometry list from UI is good to be skinned, because we can get issue if the display long name is not used.
        """
        if geos:
            for i, item in enumerate(geos):
                if item in geos[:i]:
                    self.ar.logger.infoWin('i038_canceled', 'e003_moreThanOneGeo', item, 'center', 205, 270)
                    return False
                elif not cmds.objExists(item):
                    self.ar.logger.infoWin('i038_canceled', 'i061_notExists', item, 'center', 205, 270)
                    return False
                elif not mode:
                    try:
                        input_deformers = cmds.findDeformers(item)
                        if input_deformers:
                            for deformer_node in input_deformers:
                                if cmds.objectType(deformer_node) == "skinCluster":
                                    self.ar.logger.infoWin('i038_canceled', 'i285_alreadySkinned', item, 'center', 205, 270)
                                    return False
                    except:
                        pass
        return True
    

    def set_skin_relative_mode(self, sc_node, sc_mode=1):
        """ Configure the skinCluster relative mode.
            Default is 1 = local to avoid only 1 joint deformation issue.
        """
        if cmds.about(version=True) >= "2023":
            if "relativeSpaceMode" in cmds.listAttr(sc_node):
                cmds.setAttr(sc_node+".relativeSpaceMode", sc_mode)
    

    def run_skinning(self, geos, joints, mode, log_win=False):
        # check if we have repeated listed geometries in case of the user choose to not display long names:
        if self.validate_geos(geos, mode):
            if joints and geos:
                not_skinned_items = []
                for geo in geos:
                    if (mode == "Add"):
                        for joint in joints:
                            try:
                                cmds.skinCluster(geo, edit=True, addInfluence=joint, toSelectedBones=True, lockWeights=True, weight=0.0)
                            except:
                                not_skinned_items.append(joint)
                    elif (mode == "Remove"):
                        for joint in joints:
                            try:
                                cmds.skinCluster(geo, edit=True, removeInfluence=joint, toSelectedBones=True)
                            except:
                                not_skinned_items.append(joint)
                    else: # None = create a new skinCluster node
                        base_name = self.ar.utils.extract_suffix(geo)
                        skincluster_name = base_name+"_SC"
                        if "|" in skincluster_name:
                            skincluster_name = skincluster_name[skincluster_name.rfind("|")+1:]
                        new_skin_cluster_node = cmds.skinCluster(joints, geo, toSelectedBones=True, dropoffRate=4.0, maximumInfluences=3, skinMethod=0, normalizeWeights=1, removeUnusedInfluence=False, name=skincluster_name)[0]
                        cmds.rename(cmds.listConnections(new_skin_cluster_node+".bindPose", destination=False, source=True), new_skin_cluster_node.replace("_SC", "_BP"))
                        self.set_skin_relative_mode(new_skin_cluster_node)
                print(self.ar.data.lang['i077_skinned']+', '.join(geos))
                if log_win:
                    if not_skinned_items:
                        self.ar.logger.infoWin('i028_skinButton', 'i077_skinned', '\n'.join(geos)+'\n\n'+self.ar.data.lang['i322_didntChangeInf']+'\n'.join(not_skinned_items), 'center', 205, 270)
                    else:
                        self.ar.logger.infoWin('i028_skinButton', 'i077_skinned', '\n'.join(geos), 'center', 205, 270)
                cmds.select(geos)
        else:
            print(self.ar.data.lang['i029_skinNothing'])
            if log_win:
                self.ar.logger.infoWin('i028_skinButton', 'i029_skinNothing', ' ', 'center', 205, 270)

    
    def serialize_copy_skin(self, source_items, destinations, one_source=True, by_uvs=False, *args):
        """ Serialize the copy skinning for one source or many items with the same name.
        """
        done_items = []
        self.ar.utils.set_progress('Skinning: ', self.ar.data.lang['i287_copy']+" Skinning", len(destinations), add_one=False, add_number=False)
        for source_item in source_items:
            self.ar.utils.set_progress("Skinning: ")
            if one_source:
                for item in destinations:
                    self.run_copy_skin(source_item, item, by_uvs)
                self.ar.utils.set_progress(end_it=True)
                return
            else:
                if not source_item in done_items:
                    for item in reversed(destinations): #to avoid find the same item in the same given list
                        if not source_item == item:
                            if source_item[source_item.rfind("|")+1:] == item[item.rfind("|")+1:]:
                                if self.check_existing_deformer_node(source_item)[0]:
                                    self.run_copy_skin(source_item, item, by_uvs)
                                elif self.check_existing_deformer_node(item)[0]:
                                    self.run_copy_skin(item, source_item, by_uvs)
                                # To avoid repeat the same item in the same given list
                                done_items.append(item)
                                break
                    done_items.append(source_item)
        self.ar.utils.set_progress(end_it=True)


    def run_copy_skin(self, source_item, destination_item, by_uvs=False, *args):
        """ Copy the skin from source_item to destination_item.
            It will get skin_influences and skinMethod by source.
        """
        i = 0
        def_order_index = None
        source_def_items = self.check_existing_deformer_node(source_item)[2]
        if source_def_items:
            # get correct naming
            skincluster_name = self.ar.utils.extract_suffix(destination_item)
            if "|" in skincluster_name:
                skincluster_name = skincluster_name[skincluster_name.rfind("|")+1:]
            # clean-up current destination skinCluster
            dest_def_items = self.check_existing_deformer_node(destination_item, deleteIt=True)
            if dest_def_items[0] and dest_def_items[2]:
                def_order_index = self.get_deformer_order(dest_def_items)
            for source_def in reversed(source_def_items): #create reversed to have the multiple skinClusters in the good deformer order
                skin_influences = cmds.skinCluster(source_def, query=True, influence=True)
                skin_method_to_use = cmds.skinCluster(source_def, query=True, skinMethod=True)
                # create skinCluster node
                if i == 0: #Maya 2022 and 2023 versions
                    new_skin_cluster_node = cmds.skinCluster(skin_influences, destination_item, name=skincluster_name+"_"+str(i)+"_SC", toSelectedBones=True, maximumInfluences=3, skinMethod=skin_method_to_use)[0]
                elif cmds.about(version=True) >= "2024": #accepting multiple skinClusters
                    new_skin_cluster_node = cmds.skinCluster(skin_influences, destination_item, multi=True, name=skincluster_name+"_"+str(i)+"_SC", toSelectedBones=True, maximumInfluences=3, skinMethod=skin_method_to_use)[0]
                cmds.rename(cmds.listConnections(new_skin_cluster_node+".bindPose", destination=False, source=True), new_skin_cluster_node.replace("_SC", "_BP"))
                self.set_skin_relative_mode(new_skin_cluster_node)
                if not skin_method_to_use == 0:
                    if cmds.getAttr(source_def+".dqsSupportNonRigid"):
                        cmds.setAttr(new_skin_cluster_node+".dqsSupportNonRigid", 1)
                        plug = cmds.listConnections(source_def+".dqsScaleX", destination=False, source=True, plugs=True)
                        if plug:
                            cmds.connectAttr(plug[0], new_skin_cluster_node+".dqsScaleX", force=True)
                            cmds.connectAttr(plug[0], new_skin_cluster_node+".dqsScaleY", force=True)
                            cmds.connectAttr(plug[0], new_skin_cluster_node+".dqsScaleZ", force=True)
                # copy skin weights from source to destination
                if by_uvs:
                    source_uv_map = cmds.polyUVSet(source_item, query=True, allUVSets=True)[0]
                    destination_uv_map = cmds.polyUVSet(destination_item, query=True, allUVSets=True)[0]
                    cmds.copySkinWeights(sourceSkin=source_def, destinationSkin=new_skin_cluster_node, noMirror=True, surfaceAssociation="closestPoint", influenceAssociation=["label", "oneToOne", "closestJoint"], uvSpace=[source_uv_map, destination_uv_map])
                else:
                    cmds.copySkinWeights(sourceSkin=source_def, destinationSkin=new_skin_cluster_node, noMirror=True, surfaceAssociation="closestPoint", influenceAssociation=["label", "oneToOne", "closestJoint"])
                # deformer order
                if def_order_index:
                    cmds.reorderDeformers(dest_def_items[1][def_order_index-1], new_skin_cluster_node, destination_item)
                i += 1
        # log result
        mel.eval("print \""+self.ar.data.lang['i083_copiedSkin']+" "+source_item+" "+destination_item+"\"; ")


    def copy_skin_from_one_source(self, items=None, ui=False, by_uvs=False, *args):
        """ Main function to analise and call copy skin process. 
        """
        if not items:
            items = cmds.ls(selection=True, long=True, type="transform")
        if items and len(items) > 1:
            # get first selected item
            source_item = items[0]
            # get other selected items
            destinations = items[1:]
            shapes = cmds.listRelatives(source_item, shapes=True, fullPath=True)
            if shapes:
                # check if there's a skinCluster node connected to the first selected item
                if self.check_existing_deformer_node(shapes):
                    if ui and self.ar.data.ui_state:
                        by_uvs = self.ar.auto_rig_ui.get_by_uvs_from_ui()
                    # call copySkin function
                    self.serialize_copy_skin([source_item], destinations, True, by_uvs)
                else:
                    mel.eval("warning \""+self.ar.data.lang['e007_notSkinFound']+"\";")
            else:
                mel.eval("warning \""+self.ar.data.lang['e006_firstSkinnedGeo']+"\";")
        else:
            mel.eval("warning \""+self.ar.data.lang['e005_selectOneObj']+"\";")


    def copy_skin_same_name(self, items=None, ui=False, by_uvs=False, *args):
        """ Copy the skinning between meshes with the same name, selected or not or using the given list.
        """
        if not items:
            items = cmds.ls(selection=True, long=True, type="transform")
            if not items:
                items = cmds.ls(selection=False, long=True, type="transform")
        if items:
            if ui and self.ar.data.ui_state:
                by_uvs = self.ar.auto_rig_ui.get_by_uvs_from_ui()
            self.serialize_copy_skin(items, items, False, by_uvs)

            
    def create_missing_joints(self, incoming_joints):
        """ Create missing joints if we don't have them in the scene.
        """
        missing_joints = []
        for jnt in incoming_joints:
            if not cmds.objExists(jnt):
                cmds.select(clear=True)
                cmds.joint(name=jnt)
                cmds.select(clear=True)
                missing_joints.append(jnt)
        return missing_joints


    def update_or_create_skincluster(self, item, skincluster_name, skin_weight_data):
        """ Add influence to the existing skinCluster.
            Create a new skinCluster if it needs.
        """
        need_to_create_skincluster = True
        incoming_joints = skin_weight_data[item][skincluster_name]['skinInfList']
        missing_joints = self.create_missing_joints(incoming_joints)
        if cmds.objExists(skincluster_name):
            if cmds.listConnections(skincluster_name+".outputGeometry", destination=True, source=False):
                need_to_create_skincluster = False
                skincluster_info_items = self.check_existing_deformer_node(item)
                if skincluster_info_items[0]:
                    for sc_node in skincluster_info_items[2]:
                        if sc_node == skincluster_name:
                            if missing_joints:
                                for jnt in missing_joints:
                                    # add influence
                                    cmds.skinCluster(item, edit=True, addInfluence=jnt, lockWeights=True, weight=0.0)
            else:
                cmds.lockNode(skincluster_name, lock=False)
                cmds.delete(skincluster_name)
        if need_to_create_skincluster:
            if cmds.about(version=True) >= "2024": #accepting multiple skinClusters
                sc_node = cmds.skinCluster(incoming_joints, item, multi=True, name=skincluster_name, toSelectedBones=True, skinMethod=skin_weight_data[item][skincluster_name]['skinMethodToUse'], obeyMaxInfluences=skin_weight_data[item][skincluster_name]['skinMaintainMaxInf'], maximumInfluences=skin_weight_data[item][skincluster_name]['skinMaxInf'])[0]
            else:
                sc_node = cmds.skinCluster(incoming_joints, item, name=skincluster_name, toSelectedBones=True, skinMethod=skin_weight_data[item][skincluster_name]['skinMethodToUse'], obeyMaxInfluences=skin_weight_data[item][skincluster_name]['skinMaintainMaxInf'], maximumInfluences=skin_weight_data[item][skincluster_name]['skinMaxInf'])[0]
            self.set_skin_relative_mode(sc_node)


    def get_skin_weights(self, item, skincluster_node, influences=False):
        """ Returns a list with all skin weights for each item component (vertex or cv) as a influence dictionary.
        """
        skin_weights = []
        components = cmds.ls(item+".vtx[*]", flatten=True) or [] #mesh
        components.extend(cmds.ls(item+".cv[*]", flatten=True) or []) #nurbsCurve
        for component in range(0, len(components)):
            skin_weights.append(self.get_deformer_weights(skincluster_node, component, influences))
        return skin_weights
    

    def get_skin_blend_weights_data(self, item, skincluster_node, attr_name="blendWeights"):
        """ Returns a dictionary with the skin blend weights by each item component (vertex or cv) that has non zero blend weight value.
        """
        skin_data = {}
        components = cmds.ls(item+".vtx[*]", flatten=True) or [] #mesh
        components.extend(cmds.ls(item+".cv[*]", flatten=True) or []) #nurbsCurve
        for component in range(0, len(components)):
            value = cmds.getAttr(skincluster_node+"."+attr_name+"["+str(component)+"]")
            if not value == 0:
                skin_data[component] = value
        return skin_data


    def get_skin_weights_data(self, items):
        """ Return the the skinCluster weights data of the given item list.
        """
        self.ar.utils.set_progress(self.io_start_name+': '+self.ar.data.lang['c110_start'], self.io_start_name, len(items), add_one=False, add_number=False)
        skin_weights_data = {}
        for item in items:
            self.ar.utils.set_progress('SkinningIO: '+item)
            skin_weights_data[item] = {}
            # get skinCluster nodes for the given item
            skincluster_info_items = self.check_existing_deformer_node(item)
            if skincluster_info_items[0]:
                for skincluster_node in skincluster_info_items[2]:
                    # get skinCluster data
                    skin_weights_data[item][skincluster_node] = {
                        "skinMethodToUse"           : cmds.skinCluster(skincluster_node, query=True, skinMethod=True),
                        "skinMaintainMaxInf"        : cmds.skinCluster(skincluster_node, query=True, obeyMaxInfluences=True),
                        "skinMaxInf"                : cmds.skinCluster(skincluster_node, query=True, maximumInfluences=True),
                        "skinInfList"               : cmds.skinCluster(skincluster_node, query=True, influence=True),
                        "skinSupportNonRigid"       : cmds.getAttr(skincluster_node+".dqsSupportNonRigid"),
                        "skinUseComponents"         : cmds.getAttr(skincluster_node+".useComponents"),
                        "skinDeformUserNormals"     : cmds.getAttr(skincluster_node+".deformUserNormals"),
                        "skinNormalizeWeights"      : cmds.getAttr(skincluster_node+".normalizeWeights"),
                        "skinWeightDistribution"    : cmds.getAttr(skincluster_node+".weightDistribution"),
                        "skinMaxInfluences"         : cmds.getAttr(skincluster_node+".maxInfluences"),
                        "skinMaintainMaxInfluences" : cmds.getAttr(skincluster_node+".maintainMaxInfluences"),
                        "skinJointsWeights"         : self.get_skin_weights(item, skincluster_node, True),
                        "skinBlendWeights"          : self.get_skin_blend_weights_data(item, skincluster_node, "blendWeights"),
                        "skinDropoffWeights"        : self.get_skin_blend_weights_data(item, skincluster_node, "dropoff")
                    }
                    if cmds.objExists(skincluster_node+".relativeSpaceMode"):
                        skin_weights_data[item][skincluster_node]["skinRelativeSpaceMode"] = cmds.getAttr(skincluster_node+".relativeSpaceMode")
        return skin_weights_data


    def set_imported_skin_weights(self, item, skincluster_name, skin_weight_data):
        """ Set the skinCluster weight values from the given dictionary.
            Ensure we have a skinCluster node with all weights in just one joint to avoid import issue.
        """
        # workaround to have all weights in a temporary joint
        cmds.select(clear=True)
        self.tmp_joint = cmds.joint(name="dpTemp_Jnt")
        cmds.skinCluster(skincluster_name, edit=True, addInfluence=self.tmp_joint, toSelectedBones=True, lockWeights=False, weight=1.0)
        try:
            cmds.skinPercent(skincluster_name, item, transformValue=[(self.tmp_joint, 1)])
        except Exception as e:
            print(e)
        # get indices
        matrix_data = self.get_connected_matrix_data(skincluster_name)
        components = cmds.ls(item+".vtx[*]", flatten=True) or [] #mesh
        components.extend(cmds.ls(item+".cv[*]", flatten=True) or []) #nurbsCurve
        for c in range(0, len(components)):
            for joint_name in skin_weight_data[item][skincluster_name]['skinJointsWeights'][c].keys():
                # set weights
                cmds.setAttr(skincluster_name+".weightList["+str(c)+"].weights["+str(matrix_data[joint_name])+"]", skin_weight_data[item][skincluster_name]['skinJointsWeights'][c][joint_name])
        # remove temporary joint
        cmds.skinCluster(skincluster_name, edit=True, removeInfluence=self.tmp_joint, toSelectedBones=True)
        cmds.delete(self.tmp_joint)
        self.normalize_item_weights(item)


    def set_imported_skin_items_weights(self, skincluster_name, skin_weight_data, attr_name="blendWeights"):
        """ Set the skinCluster blend or dropoff weight values from the given dictionary.
        """
        if skin_weight_data:
            for vertex in skin_weight_data.keys():
                cmds.setAttr(skincluster_name+"."+attr_name+"["+str(vertex)+"]", skin_weight_data[vertex])


    def import_skin_weights_from_file(self, items, path, filename, verbose=True):
        """ Import the skinCluster weights of the given item in the given path and filename.
        """
        self.ar.utils.set_progress(self.io_start_name+": "+self.ar.data.lang['c110_start'], self.io_start_name, len(items), add_one=False, add_number=False)
        skin_weight_data = self.ar.pipeliner.get_json_content(path+"/"+filename)
        if skin_weight_data:
            for item in items:
                self.ar.utils.set_progress("SkinningIO: "+item)
                if cmds.objExists(item):
                    for skincluster_name in skin_weight_data[item].keys():
                        self.update_or_create_skincluster(item, skincluster_name, skin_weight_data)
                        self.set_imported_skin_weights(item, skincluster_name, skin_weight_data)
                        self.set_imported_skin_items_weights(skincluster_name, skin_weight_data[item][skincluster_name]['skinBlendWeights'], "blendWeights")
                        self.set_imported_skin_items_weights(skincluster_name, skin_weight_data[item][skincluster_name]['skinDropoffWeights'], "dropoff")
                        cmds.setAttr(skincluster_name+".dqsSupportNonRigid", skin_weight_data[item][skincluster_name]["skinSupportNonRigid"])
                        cmds.setAttr(skincluster_name+".useComponents", skin_weight_data[item][skincluster_name]["skinUseComponents"])
                        cmds.setAttr(skincluster_name+".deformUserNormals", skin_weight_data[item][skincluster_name]["skinDeformUserNormals"])
                        cmds.setAttr(skincluster_name+".normalizeWeights", skin_weight_data[item][skincluster_name]["skinNormalizeWeights"])
                        cmds.setAttr(skincluster_name+".weightDistribution", skin_weight_data[item][skincluster_name]["skinWeightDistribution"])
                        cmds.setAttr(skincluster_name+".maxInfluences", skin_weight_data[item][skincluster_name]["skinMaxInfluences"])
                        cmds.setAttr(skincluster_name+".maintainMaxInfluences", skin_weight_data[item][skincluster_name]["skinMaintainMaxInfluences"])
                        if cmds.objExists(skincluster_name+".relativeSpaceMode"):
                            if "skinRelativeSpaceMode" in skin_weight_data[item][skincluster_name].keys():
                                cmds.setAttr(skincluster_name+".relativeSpaceMode", skin_weight_data[item][skincluster_name]["skinRelativeSpaceMode"])
        if verbose:
            self.ar.utils.set_progress(end_it=True)


    def io_skin_weights_by_dialog(self, export=True, *args):
        """ Call export or import the skinCluster weights by UI.
            Export: if export parameter is True
            Import: if export parameter is False
        """
        items = cmds.ls(selection=True, type="transform")
        if not items:
            cmds.confirmDialog(title="SkinCluster Weights IO", message=self.ar.data.lang['i042_notSelection']+"\n"+self.ar.data.lang['m225_selectAnything'], button=[self.ar.data.lang['i038_canceled']])
            return
        action = self.ar.data.lang['i196_import']
        if export:
            action = self.ar.data.lang['i164_export']
        path = cmds.fileDialog2(fileMode=3, caption=action+" "+self.ar.data.lang['i298_folder'], okCaption=action)
        if items and path:
            for item in items:
                filename = path[0]+"/"+self.io_start_name+"_"+self.get_io_filename(item)+".json"
                if cmds.listRelatives(item, children=True, allDescendents=True, shapes=True):
                    if export:
                        skinClusterDic = self.get_skin_weights_data([item])
                        self.ar.pipeliner.save_json_file(skinClusterDic, filename)
                    else:
                        self.import_skin_weights_from_file([item], path[0], self.io_start_name+"_"+self.get_io_filename(item)+".json")
        self.ar.utils.set_progress(end_it=True)

    
    def get_skinned_joints(self, skinclusters=None):
        """ Returns a list of influence of the given skinCluster list or all.
        """
        skinned_items = []
        if not skinclusters:
            skinclusters = cmds.ls(selection=False, type="skinCluster")
        if skinclusters:
            for item in skinclusters:
                skinned_items.extend(cmds.skinCluster(item, query=True, influence=True))
        return skinned_items
