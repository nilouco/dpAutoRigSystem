###
#
#   THANKS to:
#       David Johnson, who created the great djRivet.mel that I used a lot!
#       david@djx.com.au
#       www.djx.com.au
#
#    CREDITS by David Johnson:
#        Michael Bazhutkin, I used your excellent rivet.mel for years - thanks for sharing!
#        Mike Rhone, who said "Better than rivet:Use a follicle."
#        Brecht Debaene, for showing me how to hook up a follicle
#        robthebloke.org, for sharing the knowlege.
#
#   Also thanks to Caio Hidaka for the FaceToRivet implementation.
#   and André Rüegger for the rivet removal.
#
###


# importing libraries:
import json
from maya import cmds
from maya import mel
from ..base import base
from importlib import reload

# global variables to this module:
CLASS_NAME = "Rivet"
TITLE = "m083_rivet"
DESCRIPTION = "m084_rivetDesc"
WIKI = "06-‐-Tools#-rivet"

RIVET_GRP = "Rivet_Grp"
MORPH = "Morph"
WRAP = "Wrap"



class Rivet(base.BaseLibrary):
    def __init__(self, ar):
        base.BaseLibrary.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(base)
        self.geo_to_attach = None
        self.item_type = None
        self.mesh_node = None
        self.selected_uv_set = None
        self.deformer_to_use = MORPH
        self.morph_deformer = MORPH
        self.wrap_deformer = WRAP
        self.rivet_grp_name = RIVET_GRP
        self.maya_minimal_version = 2022.3
        self.maya_required_version = self.check_maya_version()
        self.nets = []
        

    def build_tool(self, *args):
        if self.ar.data.ui_state:
            self.ar.rivet_ui.create_ui(self)
            self.ar.rivet_ui.fill_ui()


    def disable_pac(self, rivet_indexes, *args):
        """ Receive a index list to disable parent constraint before remove rivet.
        """
        for index in rivet_indexes:
            net = self.rivet_nets[index]
            try:
                pac = cmds.listConnections(f"{net}.pacNode", destination=False)[0]
                follicle = cmds.listConnections(f"{net}.follicle", destination=False)[0]
                pac_attrs = cmds.listAttr(pac, settable=True, visible=True, string=f"{follicle}*")
                if pac_attrs:
                    pac_attr = pac_attrs[0]
                    cmds.setAttr(f"{pac}.{pac_attr}", 0)
            except:
                pass


    def remove_rivet_grp(self, *args):
        """ Verify if rivet group is empty to remove it.
        """
        if cmds.objExists(self.rivet_grp_name):
            if not cmds.listRelatives(self.rivet_grp_name, children=True):
                cmds.delete(self.rivet_grp_name)
    

    def remove_rivet_from_net(self, rivetNetNode):
        """ Remove the rivet from its network node.
        """
        rivet_transform = cmds.listConnections(f"{rivetNetNode}.rivet", destination=False)
        if rivet_transform:
            rivet_transform = rivet_transform[0]
        rivet_ctrl = cmds.listConnections(f"{rivetNetNode}.item_node", destination=False)[0]
        follicle = cmds.listConnections(f"{rivetNetNode}.follicle", destination=False)[0]
        attached_geo = cmds.listConnections(f"{rivetNetNode}.geo_to_attach", destination=False)[0]
        try:
            original_parent = cmds.listRelatives(rivet_transform, parent=True)
            current_parent = cmds.listRelatives(rivet_ctrl, parent=True)
            if original_parent == None:
                if current_parent != original_parent:
                    cmds.parent(rivet_ctrl, world=True)
            else:
                original_parent = original_parent[0]
                if not original_parent in current_parent:
                    cmds.parent(rivet_ctrl, original_parent)
            if rivet_ctrl != rivet_transform:
                cmds.delete([rivet_transform, follicle])
            else:
                cmds.delete(follicle)
        except:
            cmds.delete(follicle)

        connection = cmds.listConnections(f"{rivetNetNode}.message", plugs=True, destination=True)
        if len(connection) > 1:
            for connection in connection:
                if "rivetNet" in connection:
                    cmds.deleteAttr(connection)
                    break
        else:
            cmds.deleteAttr(connection[0])

        # check if attached geometry should be discarded
        networks = cmds.listConnections(attached_geo, type="network")
        networks = list(set(networks))
        networks.remove(rivetNetNode)
        if len(networks) == 0:
            skinclusters = cmds.ls(cmds.listHistory(attached_geo, pruneDagObjects=True), type='skinCluster')
            blendshapes = cmds.ls(cmds.listHistory(attached_geo, pruneDagObjects=True), type='blendShape')
            if len(skinclusters) == 0 and len(blendshapes) == 0:
                remove_attached_geo = cmds.confirmDialog(title=self.ar.data.lang['i319_removeGeometry'], icon="question", message=f"{self.ar.data.lang['i320_rivetHeldGeo']} {attached_geo} {self.ar.data.lang['i321_noConnectionGeo']}", button=[self.ar.data.lang['i071_yes'], self.ar.data.lang['i072_no']], defaultButton=self.ar.data.lang['i071_yes'], cancelButton=self.ar.data.lang['i072_no'], dismissString=self.ar.data.lang['i072_no'])

                if remove_attached_geo == self.ar.data.lang['i071_yes']:
                    current_parent = cmds.listRelatives(attached_geo, parent=True)
                    if current_parent:
                        cmds.lockNode(current_parent[0])
                        cmds.delete(attached_geo)
                        cmds.lockNode(current_parent[0], lock=False)
                    else:
                        cmds.delete(attached_geo)
        cmds.delete(rivetNetNode)
        mel.eval('print \"dpAR: '+self.ar.data.lang['m144_removedRivet']+" "+rivet_ctrl+'\\n\";')
    

    def get_ctrl_items(self):
        """ From all rivet network nodes, rise a controllers list to fill ui.
        """
        rivet_networks = self.ar.utils.getNetworkNodeByAttr("dpRivetNet")
        if rivet_networks:
            ctrls = []
            self.rivet_nets = []
            for rivet_node in rivet_networks:
                rivet_controllers = cmds.listConnections(f"{rivet_node}.item_node", destination=False)
                if rivet_controllers:
                    ctrls.append(rivet_controllers[0])
                    self.rivet_nets.append(rivet_node)
            return ctrls
        else:
            return None


    def filter_name(self, name, items, separator):
        """ Filter list with the name or a list of name as a string separated by the separator (usually a space).
            Returns the filtered list.
            Update the index list to match the returned list.
        """
        filtered_items = []
        multi_filters = [name]
        new_indexes = []
        if separator in name:
            multi_filters = list(name.split(separator))
        for filter_name in multi_filters:
            if filter_name:
                for i, item in enumerate(items):
                    if str(filter_name) in item:
                        filtered_items.append(item)
                        new_indexes.append(i)
        if len(new_indexes) > 0:
            new_nodes = []
            for index in new_indexes:
                new_nodes.append(self.rivet_nets[index])
            self.rivet_nets = new_nodes
        return filtered_items


    

    def get_to_remove_indexes(self, needToRemoveSet, has_rivets_items):
        """ From a set of items to be removed rise all rivets and matching indexes needed to removal.
        """
        need_to_remove_items = []
        true_indexes = []
        for item in needToRemoveSet:
            index = [i for i, x in enumerate(has_rivets_items) if x == item]
            for j in index:
                need_to_remove_items.append(item)
                true_indexes.append(j)
        return need_to_remove_items, true_indexes


    def invert_attr_transformation(self, node_name, inv_t=True, inv_r=False, *args):
        """ Creates a setup to invert attribute transformations in order to avoid doubleTransformation.
            Return inverted groups.
        """
        inv_t_grp = None
        inv_r_grp = None
        if cmds.objExists(node_name):
            node_pivot = cmds.xform(node_name, query=True, worldSpace=True, rotatePivot=True)
            if inv_t:
                inv_t_grp = cmds.group(node_name, name=node_name+"_InvT_Grp")
                cmds.xform(inv_t_grp, worldSpace=True, rotatePivot=(node_pivot[0], node_pivot[1], node_pivot[2]))
                t_md = cmds.createNode('multiplyDivide', name=node_name+"_InvT_MD", skipSelect=True)
                self.to_ids.append(t_md)
                cmds.setAttr(t_md+'.input2X', -1)
                cmds.setAttr(t_md+'.input2Y', -1)
                cmds.setAttr(t_md+'.input2Z', -1)
                for axis in self.ar.data.axes:
                    cmds.connectAttr(node_name+'.translate'+axis, t_md+'.input1'+axis, force=True)
                    cmds.connectAttr(t_md+'.output'+axis, inv_t_grp+'.translate'+axis, force=True)
            if inv_r:
                inv_r_grp = cmds.group(node_name, name=node_name+"_InvR_Grp")
                cmds.xform(inv_r_grp, worldSpace=True, rotatePivot=(node_pivot[0], node_pivot[1], node_pivot[2]), rotateOrder="zyx")
                r_md = cmds.createNode('multiplyDivide', name=node_name+"_InvR_MD", skipSelect=True)
                self.to_ids.append(r_md)
                cmds.setAttr(r_md+'.input2X', -1)
                cmds.setAttr(r_md+'.input2Y', -1)
                cmds.setAttr(r_md+'.input2Z', -1)
                for axis in self.ar.data.axes:
                    cmds.connectAttr(node_name+'.rotate'+axis, r_md+'.input1'+axis, force=True)
                    cmds.connectAttr(r_md+'.output'+axis, inv_r_grp+'.rotate'+axis, force=True)
        return inv_t_grp, inv_r_grp
    
    
    def create_rivet(self, geo_to_attach, uv_set_name, items, attatch_translate, attach_rotate, add_father_grp, add_invert, inv_t, inv_r, face_to_rivet, rivet_grp_name=RIVET_GRP, ask_component=False, use_offset=True, reuse_face_to_rivet=False, *args):
        """ Create the Rivet setup.
            Returns the created network node list. 
        """
        # declaring variables
        self.to_ids = []
        self.origined_geo = geo_to_attach
        self.shapes_to_attach = None
        self.shape_to_attach = None
        self.cp_node = None
        rivets, togethers = [], []
        is_component = None
        self.old_unit_conversions = cmds.ls(selection=False, type="unitConversion")

        # integrate to dpAutoRigSystem:
        master_ctrl = self.ar.utils.getNodeByMessage("masterCtrl")
        scalable_grp = self.ar.utils.getNodeByMessage("scalableGrp")
        
        # create Rivet_Grp in order to organize hierarchy:
        created_rivet_grp = False
        self.rivet_grp = rivet_grp_name
        if not cmds.objExists(rivet_grp_name):
            created_rivet_grp = True
            self.rivet_grp = cmds.group(name=rivet_grp_name, empty=True)
            self.to_ids.append(self.rivet_grp)
            for attr in self.ar.data.transform_attrs[:-1]:
                cmds.setAttr(self.rivet_grp+"."+attr, lock=True, keyable=False, channelBox=False)
            cmds.addAttr(self.rivet_grp, longName="dpRivetGrp", attributeType='bool')
            cmds.setAttr(self.rivet_grp+".dpRivetGrp", 1)
            if scalable_grp:
                cmds.parent(self.rivet_grp, scalable_grp)
            
        # if Create FaceToRivet is activated, it will create a new geometry with cut faces, wrap in the original and parent in the Support_Grp
        if face_to_rivet:
            if reuse_face_to_rivet and cmds.objExists(reuse_face_to_rivet):
                geo_to_attach = reuse_face_to_rivet
            else:
                geo_to_attach = self.create_face_to_rivet(items, self.extract_geo_to_rivet(geo_to_attach), 4)
            self.deform_face_to_rivet(geo_to_attach, self.origined_geo)
            support_grp = self.ar.utils.getNodeByMessage("supportGrp")
            if support_grp:
                self.ar.ctrls.colorShape([support_grp], [0.51, 1, 0.667], outliner=True) #green

        # get shape to attach:
        if cmds.objExists(geo_to_attach):
            self.shapes_to_attach = cmds.ls(geo_to_attach, dag=True, shapes=True)
        if self.shapes_to_attach:
            self.shape_to_attach = self.shapes_to_attach[0]
            # get shape type:
            self.shape_type = cmds.objectType(self.shape_to_attach)
            # verify if there are vertices, cv's or lattice points in our items:
            if items:
                asked = False
                for i, item in enumerate(items):
                    if ".vtx" in item or ".cv" in item or ".pt" in item:
                        if ask_component:
                            if not asked:
                                is_component = cmds.confirmDialog(title="dpRivet on Components", message="How do you want attach vertices, cv's or lattice points?", button=("Individually", "Together", "Ignore"), defaultButton="Individually", dismissString="Ignore", cancelButton="Ignore")
                                asked = True
                                if is_component == "Individually":
                                    cls = cmds.cluster(item, name=item[:item.rfind(".")]+"_"+str(i)+"_Cls")[0]+"Handle"
                                    cls_to_rivet = cmds.parent(cls, self.rivet_grp)[0]
                                    rivets.append(cls_to_rivet)
                                elif is_component == "Together":
                                    togethers.append(item)
                                elif is_component == "Ignore":
                                    items.remove(item)
                            elif is_component == "Ignore":
                                items.remove(item)
                            elif is_component == "Together":
                                togethers.append(item)
                            else: #Individually
                                cls = cmds.cluster(item, name=item[:item.rfind(".")]+"_"+str(i)+"_Cls")[0]+"Handle"
                                cls_to_rivet = cmds.parent(cls, self.rivet_grp)[0]
                                rivets.append(cls_to_rivet)
                        else: #Individually
                            cls = cmds.cluster(item, name=item[:item.rfind(".")]+"_"+str(i)+"_Cls")[0]+"Handle"
                            cls_to_rivet = cmds.parent(cls, self.rivet_grp)[0]
                            rivets.append(cls_to_rivet)
                    elif cmds.objExists(item):
                        rivets.append(item)
            else:
                mel.eval("error \"Select and add at least one item to be attached as a Rivet, please.\";")
            if is_component == "Together":
                cls = cmds.cluster(togethers, name="dpRivet_Cls")[0]+"Handle"
                cls_to_rivet = cmds.parent(cls, self.rivet_grp)[0]
                rivets.append(cls_to_rivet)
            
            # check about locked or animated attributes on items:
            if not add_father_grp:
                cancel_process = False
                for rivet in rivets:
                    # locked:
                    if cmds.listAttr(rivet, locked=True):
                        cancel_process = True
                        break
                    # animated:
                    for attr in self.ar.data.transform_attrs[:-1]:
                        if cmds.listConnections(rivet+"."+attr, source=True, destination=False):
                            cancel_process = True
                            break
                if cancel_process:
                    if created_rivet_grp:
                        cmds.delete(self.rivet_grp)
                    else:
                        for rivet in rivets:
                            if not rivet in items:
                                # clear created clusters:
                                cmds.delete(rivet)
                    mel.eval("error \"Canceled process: items to be Rivet can't be animated or have locked attributes, sorry.\";")
                    return
            
            # workaround to avoid closestPoint node ignores transformations.
            # then we need to duplicate, unlock attributes and freezeTransformation:
            dup_geo = cmds.duplicate(geo_to_attach, name=geo_to_attach+"_dpRivet_TEMP_Geo")[0]
            # unlock attr:
            self.ar.utils.unlockAttr([dup_geo])
            # parent to world:
            if cmds.listRelatives(dup_geo, allParents=True):
                cmds.parent(dup_geo, world=True)
            # freezeTransformation:
            cmds.makeIdentity(dup_geo, apply=True)
            dup_shape = cmds.ls(dup_geo, dag=True, shapes=True)[0]
            
            # temporary transform node to store object's location:
            self.temp_node = cmds.createNode("transform", name=geo_to_attach+"_dpRivet_TEMP_Transf", skipSelect=True)
                
            # working with mesh:
            if self.shape_type == "mesh":
                # working with uvSet:
                uv_sets = cmds.polyUVSet(dup_shape, query=True, allUVSets=True)
                if len(uv_sets) > 1:
                    if not uv_sets[0] == uv_set_name:
                        try:
                            # change uvSet order because closestPointOnMesh uses the default uv set
                            cmds.polyUVSet(dup_shape, copy=True, uvSet=uv_set_name, newUVSet=uv_sets[0])
                        except:
                            uv_set_name = uv_sets[0]
                # closest point on mesh node:
                self.cp_node = cmds.createNode("closestPointOnMesh", name=geo_to_attach+"_dpRivet_TEMP_CP", skipSelect=True)
                cmds.connectAttr(dup_shape+".outMesh", self.cp_node+".inMesh", force=True)
                # move temp_node to cp_node position:
                cmds.connectAttr(self.temp_node+".translate", self.cp_node+".inPosition", force=True)
            else: #nurbsSurface
                u_range = cmds.getAttr(dup_shape+".minMaxRangeU")[0]
                v_range = cmds.getAttr(dup_shape+".minMaxRangeV")[0]
                # closest point on mesh node:
                self.cp_node = cmds.createNode("closestPointOnSurface", name=geo_to_attach+"_dpRivet_TEMP_CP", skipSelect=True)
                cmds.connectAttr(dup_shape+".local", self.cp_node+".inputSurface", force=True)
            self.to_ids.append(self.cp_node)
                
            # working with follicles and attaches
            for r, rivet in enumerate(rivets):
                self.ar.utils.setProgress(self.ar.data.lang['i317_creatingRivet'])
                rivet_pos = cmds.xform(rivet, query=True, worldSpace=True, rotatePivot=True)
                if add_father_grp:
                    rivet = cmds.group(rivet, name=rivet+"_"+self.rivet_grp_name)
                    self.to_ids.append(rivet)
                    cmds.xform(rivet, worldSpace=True, rotatePivot=(rivet_pos[0], rivet_pos[1], rivet_pos[2]))
                
                # move temp tranform to rivet location:
                cmds.xform(self.temp_node, worldSpace=True, translation=(rivet_pos[0], rivet_pos[1], rivet_pos[2]))
                
                # get uv coords from closestPoint node
                fu = cmds.getAttr(self.cp_node+".u")
                fv = cmds.getAttr(self.cp_node+".v")
                
                if self.shape_type == "nurbsSurface":
                    # normalize UVs:
                    fu = abs((fu - u_range[0])/(u_range[1] - u_range[0]))
                    fv = abs((fv - v_range[0])/(v_range[1] - v_range[0]))
                    
                # create follicle:
                fol_transform = cmds.createNode("transform", name=rivet+"_Fol", parent=self.rivet_grp, skipSelect=True)
                fol_shape = cmds.createNode("follicle", name=rivet+"_FolShape", parent=fol_transform, skipSelect=True)
                
                # connect geometry shape and follicle:
                if self.shape_type == "mesh":
                    cmds.connectAttr(self.shape_to_attach+".worldMesh[0]", fol_shape+".inputMesh", force=True)
                    cmds.setAttr(fol_shape+".mapSetName", uv_set_name, type="string")
                else: #nurbsSurface:
                    cmds.connectAttr(self.shape_to_attach+".local", fol_shape+".inputSurface", force=True)
                cmds.connectAttr(self.shape_to_attach+".worldMatrix[0]", fol_shape+".inputWorldMatrix", force=True)
                cmds.connectAttr(fol_shape+".outRotate", fol_transform+".rotate", force=True)
                cmds.connectAttr(fol_shape+".outTranslate", fol_transform+".translate", force=True)
                # put follicle in the correct place:
                cmds.setAttr(fol_shape+".parameterU", fu)
                cmds.setAttr(fol_shape+".parameterV", fv)
                
                # attach follicle and rivet using constraint:
                if attatch_translate and attach_rotate:
                    rivetPac = cmds.parentConstraint(fol_transform, rivet, maintainOffset=use_offset, name=rivet+"_PaC")[0]
                elif attatch_translate:
                    rivetPac = cmds.parentConstraint(fol_transform, rivet, maintainOffset=use_offset, name=rivet+"_PaC" , skipRotate=("x", "y", "z"))[0]
                elif attach_rotate:
                    rivetPac = cmds.parentConstraint(fol_transform, rivet, maintainOffset=use_offset, name=rivet+"_PaC" , skipTranslate=("x", "y", "z"))[0]
                
                # try to integrate to dpAutoRigSystem in order to keep the Rig as scalable:
                if master_ctrl:
                    cmds.scaleConstraint(master_ctrl, fol_transform, maintainOffset=True, name=fol_transform+"_ScC")
            
                # serialize network node
                self.net = cmds.createNode("network", name=rivet+"_Net")
                self.to_ids.append(self.net)
                self.nets.append(self.net)
                # add
                cmds.addAttr(self.net, longName="dpNetwork", attributeType="bool", defaultValue=1)
                cmds.addAttr(self.net, longName="dpRivetNet", attributeType="bool", defaultValue=1)
                cmds.addAttr(self.net, longName="item_node", attributeType="message")
                cmds.addAttr(self.net, longName="rivet", attributeType="message")
                cmds.addAttr(self.net, longName="follicle", attributeType="message")
                cmds.addAttr(self.net, longName="geo_to_attach", attributeType="message")
                cmds.addAttr(self.net, longName="inv_t_grp", attributeType="message")
                cmds.addAttr(self.net, longName="inv_r_grp", attributeType="message")
                cmds.addAttr(self.net, longName="deformerGeo", attributeType="message")
                cmds.addAttr(self.net, longName="deformer_node", attributeType="message")
                cmds.addAttr(self.net, longName="pacNode", attributeType="message")
                cmds.addAttr(self.net, longName="rivetData", dataType="string")
                # set
                cmds.setAttr(self.net+".rivetData", json.dumps(self.get_rivet_data(items[r], geo_to_attach, uv_set_name, items, attatch_translate, attach_rotate, add_father_grp, add_invert, inv_t, inv_r, face_to_rivet, rivet_grp_name, ask_component, use_offset)), type="string")
                # connect
                cmds.connectAttr(rivet+".message", self.net+".rivet", force=True)
                cmds.connectAttr(fol_transform+".message", self.net+".follicle", force=True)
                cmds.connectAttr(geo_to_attach+".message", self.net+".geo_to_attach", force=True)
                cmds.connectAttr(f"{rivetPac}.message", f"{self.net}.pacNode", force=True)
                
                if face_to_rivet:
                    cmds.connectAttr(self.deformerNodeList[0]+".message", self.net+".deformerGeo", force=True)
                    cmds.connectAttr(self.deformerNodeList[1]+".message", self.net+".deformer_node", force=True)
                if len(items) == len(rivets):
                    if cmds.objExists(items[r]):
                        cmds.connectAttr(items[r]+".message", self.net+".item_node", force=True)
                        if not cmds.objExists(f"{items[r]}.rivetNet"):
                            cmds.addAttr(items[r], longName="rivetNet", attributeType="message")
                            cmds.connectAttr(self.net+".message", items[r]+".rivetNet", force=True)
                        else:
                            rivet_networks = cmds.listAttr(items[r], string="rivetNet*")
                            rivet_networks.sort(reverse=True)
                            last_index = rivet_networks[0].removeprefix("rivetNet")
                            if last_index == "":
                                last_index = 0
                            else:
                                last_index = int(last_index)
                            new_index = last_index + 1
                            current_long_name = f"rivetNet{new_index}"
                            cmds.addAttr(items[r], longName=current_long_name, attributeType="message")
                            cmds.connectAttr(self.net+".message", f"{items[r]}.{current_long_name}", force=True)
            
            # check invert group (back) in order to avoid double transformations:
            if add_invert:
                for rivet, net in zip(rivets, self.nets):
                    inv_t_grp, inv_r_grp = self.invert_attr_transformation(rivet, inv_t, inv_r)
                    if inv_t_grp:
                        cmds.connectAttr(inv_t_grp+".message", net+".inv_t_grp", force=True)
                    if inv_r_grp:
                        cmds.connectAttr(inv_r_grp+".message", net+".inv_r_grp", force=True)
            # clean-up temporary nodes:
            cmds.delete(dup_geo, self.cp_node, self.temp_node)
        else:
            mel.eval("error \"Load one geometry to attach Rivets on it, please.\";")
        
        self.ar.utils.nodeRenamingTreatment(list(set(cmds.ls(selection=False, type="unitConversion"))-set(self.old_unit_conversions)))
        self.ar.custom_attr.add_attr(0, self.to_ids, descendents=True) #dpID
        cmds.select(clear=True)
        return self.nets
    

    def get_rivet_data(self, item_node, geo_to_attach, uv_set_name, items, attatch_translate, attach_rotate, add_father_grp, add_invert, inv_t, inv_r, face_to_rivet, rivet_grp_name, ask_component, use_offset, *args):
        """ Collect all rivet data and return it as a dictionary.
        """
        data = {
                "rivetNetName" : self.net,
                "item_node" : item_node,
                "geo_to_attach" : self.origined_geo,
                "uv_set_name" : uv_set_name,
                "items" : items,
                "attatch_translate" : attatch_translate,
                "attach_rotate" : attach_rotate,
                "add_father_grp" : add_father_grp,
                "add_invert" : add_invert,
                "inv_t" : inv_t,
                "inv_r" : inv_r,
                "face_to_rivet" : face_to_rivet,
                "rivet_grp_name" : rivet_grp_name,
                "ask_component" : ask_component,
                "use_offset" : use_offset,
                "deformer_to_use" : self.deformer_to_use,
                "reuse_face_to_rivet": geo_to_attach
        }
        return data


    def extract_geo_to_rivet(self, geo, *args):
        """ Turn off skinCluster and blendShape envelope if exists, duplicate the selected geometry
            apply initial shading and remove it from any display layer,
            if the face_to_rivet geometry doesn't exist yet.
        """ 
        face_to_rivet_geo_name = self.get_face_to_rivet_geo_name(geo)
        if not cmds.objExists(face_to_rivet_geo_name):
            # Get the history to turn off envelopes if exists
            hist_items = cmds.listHistory(geo)
            shapes = cmds.listRelatives(geo, shapes=True)
            if shapes:
                # check if there's a skinCluster node connected to the first selected item
                check_skin = self.check_node_exists(shapes, "skinCluster")
                check_bs = self.check_node_exists(shapes, "blendShape")
                if check_skin == 1:
                    skincluster_node = cmds.ls(hist_items, type="skinCluster")[0]
                    cmds.setAttr(skincluster_node+".envelope", 0)
                if check_bs == 2:
                    bs_node = cmds.ls(hist_items, type="blendShape")[0]
                    cmds.setAttr(bs_node+".envelope", 0)
                # Duplicate geometry after turn off skinCluster and blendShape. 
                to_rivet_geo = cmds.duplicate(geo)[0]
                self.ar.utils.removeUserDefinedAttr(to_rivet_geo)
                # Unparenting
                if cmds.listRelatives(to_rivet_geo, allParents=True):
                    cmds.parent(to_rivet_geo, world=True)
                # Unlock attributes and apply initialShading
                self.ar.ctrls.setLockHide([to_rivet_geo], self.ar.data.transform_attrs, False, True, True)
                cmds.sets(to_rivet_geo, edit=True, forceElement="initialShadingGroup")
                cmds.editDisplayLayerMembers("defaultLayer", to_rivet_geo, noRecurse=False)
                self.ar.ctrls.setLockHide([to_rivet_geo], self.ar.data.transform_attrs[:-1], True, False, True)
                # Renaming
                cmds.rename(to_rivet_geo, face_to_rivet_geo_name)
                # Turning on nodes
                if check_skin == 1:
                    cmds.setAttr(skincluster_node+".envelope", 1)
                if check_bs == 2:
                    cmds.setAttr(bs_node+".envelope", 1)
        return face_to_rivet_geo_name
    

    def get_face_to_rivet_geo_name(self, geo, *args):
        """ Get the unused FaceToRivet geo to avoid multiples connections to the same original geometry.
            Returns the suggested name.
        """
        to_rivet_name = self.ar.utils.extractSuffix(geo)
        if "|" in to_rivet_name:
            to_rivet_name = to_rivet_name[to_rivet_name.rfind("|")+1:]
        i = 0
        done = False
        while done == False:
            if not cmds.objExists(to_rivet_name+"_FaceToRivet_"+str(i).zfill(2)+"_Geo"):
                done = True
            else:
                i += 1
        return to_rivet_name+"_FaceToRivet_"+str(i).zfill(2)+"_Geo"

    
    def create_face_to_rivet(self, controllers, geometry, grow_multiplier, *args):
        """ Get the pivot coordinates from each control to get the nearest face from control to the geometry.
            After the initial selection it will grow 4 times by default.
            It uses delta to delete the extra faces, than glue it to the original model with Morph or Wrap deformer.
        """
        # Get the pivot's coordinates from each control.
        pivots_data = {}
        for control in controllers:
            pivot = cmds.xform(control, query=True, translation=True, worldSpace=True)
            pivots_data[control] = pivot
        # Get the coordinates from geometry faces.
        faces = cmds.ls(geometry+".f[:]", flatten=True)
        face_coordinates = []
        for face in faces:
            vertex_coordinates = cmds.xform(face, query=True, translation=True, worldSpace=True)
            average_coordinates = [
                sum(vertex_coordinates[i::3]) / len(vertex_coordinates[i::3])
                for i in range(3)
            ]
            face_coordinates.append(average_coordinates)
        # Select the nearest face from each pivot.
        for control, pivot in pivots_data.items():
            nearest_face = None
            minimal_distance = None
            for i, coord in enumerate(face_coordinates):
                distance = sum((coord[j] - pivot[j])**2 for j in range(3)) ** 0.5
                if minimal_distance is None or distance < minimal_distance:
                    minimal_distance = distance
                    nearest_face = faces[i]
            if nearest_face:
                cmds.select(nearest_face, add=True)
        # Select the faces and growUp selection.
        cmds.scriptEditorInfo(edit=True, suppressWarnings=True, suppressInfo=True, suppressErrors=True, suppressResults=True)
        cmds.selectMode(component=True)
        cmds.selectType(facet=True)
        grow_multiplier = grow_multiplier - 1
        if grow_multiplier > 0:
            for i in range(0, grow_multiplier):
                cmds.GrowPolygonSelectionRegion()
        # Delta to delete unnecessary faces.
        selected_faces = cmds.ls(selection=True, flatten=True)
        all_faces = cmds.ls(geometry+".f[*]", flatten=True)
        non_selected_faces = list(set(all_faces) - set(selected_faces))
        if non_selected_faces:
            cmds.delete(non_selected_faces)
        # AutoProjection for new UV and order selection to use rivet.
        cmds.polyAutoProjection(geometry, constructionHistory=False)
        cmds.selectMode(object=True)
        cmds.scriptEditorInfo(edit=True, suppressWarnings=False, suppressInfo=True, suppressErrors=False, suppressResults=False)
        return geometry
    

    def deform_face_to_rivet(self, geometry, origGeo, *args):
        """ Do deformation from original mesh to face_to_rivet geo.
        """
        if self.ar.data.ui_state:
            # Create deformer by user selection
            selected_deformer_rb = cmds.radioCollection('rivet_deformer_rc', query=True, select=True)
            self.deformer_to_use = cmds.radioButton(selected_deformer_rb, query=True, annotation=True)
        else:
            self.deformer_to_use = self.morph_deformer
        if self.deformer_to_use:
            if self.deformer_to_use == self.morph_deformer:
                self.deformerNodeList = self.apply_morph_deformer(geometry, origGeo)
            elif self.deformer_to_use == self.wrap_deformer:
                self.deformerNodeList = self.apply_wrap_deformer(geometry, origGeo)


    def check_node_exists(self, shapes, type, *args):
        """ Verify if there's a skinCluster or blendShape node in the list of history of the shape.
            Return 1 if there's skinCluster.
            Return 2 if there's blendShape node
            Return -1 if there's another node with the same name.
        """
        for shape in shapes:
            if not shape.endswith("Orig"):
                try:
                    hist_items = cmds.listHistory(shape)
                    if hist_items:
                        for histItem in hist_items:
                            if type == "skinCluster":
                                if cmds.objectType(histItem) == "skinCluster":
                                    return 1
                            if type == "blendShape":
                                if cmds.objectType(histItem) == "blendShape":
                                    return 2
                except:
                    return -1
        return False
    
                    
    def apply_morph_deformer(self, morph_geo, target_geo, *args):
        """ Apply morphDeform from morph_geo(FaceToRivet) to target_geo(Source)
            Rename and Parent to Support_Grp
            Return morph geometry and deformer node
        """
        targets = cmds.ls(target_geo, dag=True, shapes=True)
        target_shape = targets[0]
        target_orig = self.find_orig(targets)
        if not target_orig:
            cmds.delete(cmds.cluster(target_geo, name="ToOrig_ClsTemp"))
            targets = cmds.ls(target_geo, dag=True, shapes=True)
            target_orig = self.find_orig(targets)
        morph_deformer = cmds.deformer(morph_geo, type="morph")[0]
        cmds.setAttr(morph_deformer+".morphMode", 1)
        cmds.setAttr(morph_deformer+".useComponentLookup", 1)
        cmds.setAttr(morph_deformer+".morphSpace", 0)
        cmds.connectAttr(target_shape+".worldMesh[0]", morph_deformer+".morphTarget[0]")
        component_match_node = cmds.createNode("componentMatch")
        cmds.connectAttr(component_match_node+".componentLookup", morph_deformer+".componentLookupList[0].componentLookup")
        morphOrigOutMesh = cmds.listConnections(morph_deformer+".originalGeometry[0]", source=True, destination=False, plugs=True)[0]
        cmds.connectAttr(morphOrigOutMesh, component_match_node+".inputGeometry")
        cmds.connectAttr(target_orig+".outMesh", component_match_node+".targetGeometry")
        #Renaming
        hist = cmds.listHistory(morph_geo)
        morphs = cmds.ls(hist, type="morph")[0]
        to_rivet_name = self.ar.utils.extractSuffix(morph_geo)
        if "|" in to_rivet_name:
            to_rivet_name = to_rivet_name[to_rivet_name.rfind("|")+1:]
        morph_node = cmds.rename(morphs, to_rivet_name+"_Mrp")
        component_match_node = cmds.listConnections(morph_node+".componentLookupList[0].componentLookup")[0]
        component_match_node = cmds.rename(component_match_node, to_rivet_name+"_CpM")
        self.to_ids.extend([morph_geo, morph_node, component_match_node])
        # Parent in supportGrp
        self.parent_to_transform([morph_geo], self.ar.utils.getNodeByMessage("supportGrp"))
        return morph_geo, morph_node


    def apply_wrap_deformer(self, wrap_geo, target_geo, *args):
        """ Apply wrap_deformer from wrap_geo(FaceToRivet) to target_geo(Source)
            Rename and Parent to Support_Grp
            Return wrap geometry and wrap deformer
        """
        cmds.select([wrap_geo, target_geo])
        mel.eval("CreateWrap;")
        hist = cmds.listHistory(wrap_geo)
        wrap_items = cmds.ls(hist, type="wrap")[0]
        # Renaming
        to_rivet_name = self.ar.utils.extractSuffix(wrap_geo)
        if "|" in to_rivet_name:
            to_rivet_name = to_rivet_name[to_rivet_name.rfind("|")+1:]
        wrap_node = cmds.rename(wrap_items, to_rivet_name+"_Wrp")
        base_shape = cmds.listConnections(wrap_node+".basePoints")[0]
        base_shape = cmds.rename(base_shape, to_rivet_name+"_Base")
        self.ar.ctrls.setLockHide([base_shape], self.ar.data.transform_attrs[:-1], True, False, True)
        # Remove from displayLayers
        cmds.editDisplayLayerMembers("defaultLayer", base_shape, noRecurse=False)
        self.to_ids.extend([wrap_geo, wrap_node, base_shape])
        # Parent in supportGrp
        self.parent_to_transform([wrap_geo, base_shape], self.ar.utils.getNodeByMessage("supportGrp"))
        return wrap_geo, wrap_node


    def parent_to_transform(self, items, dest_parent, *args):
        """ Just check if the item is child of the destination parent node then parent it if needed.
        """
        if items and dest_parent:
            if cmds.objExists(dest_parent):
                for item in items:
                    children = cmds.listRelatives(dest_parent, allDescendents=True, children=True)
                    if not children:
                        cmds.parent(item, dest_parent)
                    elif not item in children:
                        cmds.parent(item, dest_parent)


    def find_orig(self, geos, *args):
        """ Return the orig of the shapes
        """
        #TODO maybe use this command instead?
        #cmds.deformableShape(item, originalGeometry=True)
        if geos:
            for item in geos:
                if item.endswith("Orig"):
                    return item
                

    def check_maya_version(self, *args):
        """ Get Maya's version installed to compare with the minimalVersionRequired (2022.3)
            If the installed version is above the minimal it returns True, otherwise False
        """ 
        maya_version = cmds.about(installedVersion=True)
        maya_version = maya_version.split(" ")[-1]
        if maya_version.count(".") > 1:
            maya_version = maya_version[:maya_version.rfind(".")]
        current_version = float(maya_version)
        return current_version > self.maya_minimal_version
