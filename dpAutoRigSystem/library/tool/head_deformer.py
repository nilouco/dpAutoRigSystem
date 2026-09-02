# importing libraries:
from maya import cmds
from maya import mel
from ..base import base
from importlib import reload

# global variables to this module:    
CLASS_NAME = "HeadDeformer"
TITLE = "m051_headDef"
DESCRIPTION = "m052_headDefDesc"
WIKI = "06-‐-Tools#-head-deformer"

DPHEADDEFINFLUENCE = "dpHeadDeformerInfluence"
DPJAWDEFINFLUENCE = "dpJawDeformerInfluence"



class HeadDeformer(base.BaseLibrary):
    def __init__(self, ar):
        base.BaseLibrary.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(base)
        self.head_def_name = CLASS_NAME
        

    def build_tool(self, *args):
        # call main function
        if self.ar.data.ui_state:
            self.create_head_def(self)
    
    
    def head_def_dialog(self, *args):
        """ dpDeformer prompt dialog to get the name of the deformer
        """
        bt_continue = self.ar.data.lang['i174_continue']
        bt_cancel = self.ar.data.lang['i132_cancel']
        result = cmds.promptDialog(title="dpHeadDeformer", 
                                   message=self.ar.data.lang["m006_name"], 
                                   text=self.ar.data.lang["c024_head"], 
                                   button=[bt_continue, bt_cancel], 
                                   defaultButton=bt_continue, 
                                   cancelButton=bt_cancel, 
                                   dismissString=bt_cancel)
        if result == bt_continue:
            dialog_name = cmds.promptDialog(query=True, text=True)
            dialog_name = dialog_name[0].upper() + dialog_name[1:]
            return dialog_name
        elif result is None:
            return None


    def add_def_in_name(self, deformer_name, deformer_in, *args):
        """ When the flag deformer_in is True, it will add the word Deformer as suffix. If it's false, it will maintain the name or take off Deformer in the name.
        """
        if deformer_name:
            if deformer_in == True:
                if not "Deformer" in deformer_name:
                    deformer_name = deformer_name+"Deformer"
                return deformer_name
            if deformer_in == False:
                if "Deformer" in deformer_name:
                    deformer_name = deformer_name.replace("Deformer", "")
                return deformer_name+"_"
            

    def create_head_def(self, dialog_name=None, hd_items=None, ctrl=None, deformed_by_items=None, guide_net=None, ui=True, *args):
        """ Create the arrow curve and deformers (squash and bends).
        """
        head_ctrl = None
        self.well_done = True
        if ui:
            dialog_name = self.head_def_dialog()
        if dialog_name == None:
            return
        # defining variables
        self.to_ids = []
        self.old_unit_conversions = cmds.ls(selection=False, type="unitConversion")
        head_ctrl = ctrl
        deformer_name = self.add_def_in_name(dialog_name, True)
        cluster_name = self.add_def_in_name(dialog_name, False)
        main_ctrl_name = deformer_name+"_"+self.ar.data.lang["c058_main"]
        center_symmetry_name = cluster_name+self.ar.data.lang["c098_center"]+self.ar.data.lang["c101_symmetry"]
        top_symmetry_name = cluster_name+self.ar.data.lang["c099_top"]+self.ar.data.lang["c101_symmetry"]
        intensity_name = cluster_name+self.ar.data.lang["c049_intensity"]
        expand_name = cluster_name+self.ar.data.lang["c104_expand"]
        bottom_ctrl_name = cluster_name+self.ar.data.lang["c100_bottom"]
        middle_ctrl_name = cluster_name+self.ar.data.lang["m033_middle"]
        top_ctrl_name = cluster_name+self.ar.data.lang["c099_top"]
        calibrate_name = self.ar.data.lang["c111_calibrate"].lower()
        position = [self.ar.data.lang["c100_bottom"], self.ar.data.lang["m033_middle"], self.ar.data.lang["c099_top"]]
        
        # validating namming in order to be possible create more than one setup
        valid_name = self.ar.utils.validate_name(deformer_name+"_FFD", "FFD")
        numbering = valid_name.replace(deformer_name, "")[:-4]
        if numbering:
            deformer_name = deformer_name+numbering
            main_ctrl_name = main_ctrl_name+numbering
            center_symmetry_name = center_symmetry_name+numbering
            top_symmetry_name = top_symmetry_name+numbering
            bottom_ctrl_name = bottom_ctrl_name+numbering
            middle_ctrl_name = middle_ctrl_name+numbering
            top_ctrl_name = top_ctrl_name+numbering
        net_name = "dp"+deformer_name+"_Net"

        if not hd_items:
            # get a list of selected items
            hd_items = cmds.ls(selection=True)
        if hd_items:
            for hd_node in hd_items:
                if not cmds.objExists(hd_node):
                    cmds.polyCube(name=hd_node, constructionHistory=False)
                    print(self.ar.data.lang["i304_new"], "=", hd_node)
            cmds.select(hd_items)
            # lattice deformer
            lattice_def_items = cmds.lattice(name=deformer_name+"_FFD", divisions=(6, 6, 6), ldivisions=(6, 6, 6), outsideLattice=2, outsideFalloffDistance=1, objectCentered=True) #[Deformer/Set, Lattice, Base], mode=falloff
            lattice_points = lattice_def_items[1]+".pt[0:5][2:5][0:5]"
            # get lattice points to add sub controls
            lattice_bottom_points = lattice_def_items[1]+".pt[0:5][0:1][0:5]"
            lattice_middle_points = lattice_def_items[1]+".pt[0:5][2:3][0:5]"
            lattice_top_points = lattice_def_items[1]+".pt[0:5][4:5][0:5]"
            lattice_sub_points = [lattice_bottom_points, lattice_middle_points, lattice_top_points]
            
            # store initial scaleY in order to avoid lattice rotation bug on non frozen transformations
            bbox_max_y = cmds.getAttr(lattice_def_items[2]+".boundingBox.boundingBoxMax.boundingBoxMaxY")
            bbox_min_y = cmds.getAttr(lattice_def_items[2]+".boundingBox.boundingBoxMin.boundingBoxMinY")
            initial_size_y = bbox_max_y-bbox_min_y
            
            # force rotate zero to lattice in order to avoid selected non froozen transformations
            for axis in self.ar.data.axes:
                cmds.setAttr(lattice_def_items[1]+".rotate"+axis, 0)
                cmds.setAttr(lattice_def_items[2]+".rotate"+axis, 0)
            cmds.setAttr(lattice_def_items[1]+".scaleY", initial_size_y)
            cmds.setAttr(lattice_def_items[2]+".scaleY", initial_size_y)
            
            # getting size and distances from Lattice Bounding Box
            bbox_max_y = cmds.getAttr(lattice_def_items[2]+".boundingBox.boundingBoxMax.boundingBoxMaxY")
            bbox_min_y = cmds.getAttr(lattice_def_items[2]+".boundingBox.boundingBoxMin.boundingBoxMinY")
            bbox_size = bbox_max_y - bbox_min_y
            bbox_min_y = bbox_min_y + (bbox_size*0.5)
            
            # twist deformer
            twist_def_items = cmds.nonLinear(lattice_points, name=deformer_name+"_Twist", type="twist") #[Deformer, Handle]
            cmds.setAttr(twist_def_items[0]+".lowBound", 0)
            cmds.setAttr(twist_def_items[0]+".highBound", bbox_size)
            cmds.setAttr(twist_def_items[1]+".ty", bbox_min_y)
            
            # squash deformer
            squash_def_items = cmds.nonLinear(lattice_points, name=deformer_name+"_Squash", type="squash") #[Deformer, Handle]
            cmds.setAttr(squash_def_items[0]+".highBound", 0.5*bbox_size)
            cmds.setAttr(squash_def_items[0]+".startSmoothness", 1)
            cmds.setAttr(squash_def_items[1]+".ty", bbox_min_y)
            
            # side bend deformer
            side_bend_def_items = cmds.nonLinear(lattice_points, name=deformer_name+"_Side_Bend", type="bend") #[Deformer, Handle]
            cmds.setAttr(side_bend_def_items[0]+".lowBound", 0)
            cmds.setAttr(side_bend_def_items[0]+".highBound", bbox_size)
            cmds.setAttr(side_bend_def_items[1]+".ty", bbox_min_y)
            
            # front bend deformer
            front_bend_def_items = cmds.nonLinear(lattice_points, name=deformer_name+"_Front_Bend", type="bend") #[Deformer, Handle]
            cmds.setAttr(front_bend_def_items[0]+".lowBound", 0)
            cmds.setAttr(front_bend_def_items[0]+".highBound", bbox_size)
            cmds.setAttr(front_bend_def_items[1]+".ry", -90)
            cmds.setAttr(front_bend_def_items[1]+".ty", bbox_min_y)
            
            # fix deform transforms scale to 1
            def_handle_items = [twist_def_items[1], squash_def_items[1], side_bend_def_items[1], front_bend_def_items[1]]
            for def_handle in def_handle_items:
                for axis in self.ar.data.axes:
                    cmds.setAttr(def_handle+".scale"+axis, 1)
            
            # arrow control curve
            arrow_ctrl = self.ar.ctrls.create_controller("id_053_HeadDeformer", deformer_name+"_Ctrl", 0.25*bbox_size, d=0)

            # main control curve and shape
            main_ctrl = self.ar.ctrls.create_controller("id_097_HeadDeformerMain", main_ctrl_name+"_Ctrl", 0.57*bbox_size, d=0, parent_tag=arrow_ctrl)
            main_ctrl_shape = cmds.listRelatives(main_ctrl, shapes=True)[0]
            
            # add control intensity and calibrate attributes
            for axis in self.ar.data.axes:
                cmds.addAttr(arrow_ctrl, longName=intensity_name+axis, attributeType='float', defaultValue=1)
                cmds.setAttr(arrow_ctrl+"."+intensity_name+axis, edit=True, keyable=False, channelBox=True)
            cmds.addAttr(arrow_ctrl, longName=expand_name, attributeType='float', min=0, defaultValue=1, max=10, keyable=True)
            cmds.addAttr(arrow_ctrl, longName=calibrate_name+"X", attributeType='float', defaultValue=100/(3*bbox_size), keyable=False)
            cmds.addAttr(arrow_ctrl, longName=calibrate_name+"Y", attributeType='float', defaultValue=300/bbox_size, keyable=False)
            cmds.addAttr(arrow_ctrl, longName=calibrate_name+"Z", attributeType='float', defaultValue=100/(3*bbox_size), keyable=False)
            cmds.addAttr(arrow_ctrl, longName=calibrate_name+"Reduce", attributeType='float', defaultValue=100, keyable=False)
            cmds.addAttr(arrow_ctrl, longName=self.ar.data.lang["c021_showControls"], attributeType='long', min=0, max=1, defaultValue=0)
            cmds.setAttr(arrow_ctrl+"."+self.ar.data.lang["c021_showControls"], edit=True, keyable=False, channelBox=True)
            
            # multiply divide in order to intensify influences
            calibrate_md = cmds.createNode("multiplyDivide", name=deformer_name+"_Calibrate_MD")
            calibrate_reduce_md = cmds.createNode("multiplyDivide", name=deformer_name+"_CalibrateReduce_MD")
            intensity_md = cmds.createNode("multiplyDivide", name=deformer_name+"_"+intensity_name.capitalize()+"_MD")
            twist_md = cmds.createNode("multiplyDivide", name=deformer_name+"_Twist_MD")
            cmds.setAttr(twist_md+".input2Y", -1)
            cmds.setAttr(calibrate_reduce_md+".operation", 2)

            # create a remapValue node instead of a setDrivenKey
            rmv_node = cmds.createNode("remapValue", name=deformer_name+"_Squash_RmV")
            cmds.setAttr(rmv_node+".inputMin", -0.25*bbox_size)
            cmds.setAttr(rmv_node+".inputMax", 0.5*bbox_size)
            cmds.setAttr(rmv_node+".outputMin", -1*bbox_size)
            cmds.setAttr(rmv_node+".outputMax", -0.25*bbox_size)            
            cmds.setAttr(rmv_node+".value[2].value_Position", 0.149408)
            cmds.setAttr(rmv_node+".value[2].value_FloatValue", 0.128889)
            cmds.setAttr(rmv_node+".value[3].value_Position", 0.397929)
            cmds.setAttr(rmv_node+".value[3].value_FloatValue", 0.742222)
            cmds.setAttr(rmv_node+".value[4].value_Position", 0.60355)
            cmds.setAttr(rmv_node+".value[4].value_FloatValue", 0.951111)
            for v in range(0, 5):
                cmds.setAttr(rmv_node+".value["+str(v)+"].value_Interp", 3) #spline
            
            # connections
            for axis in self.ar.data.axes:
                cmds.connectAttr(arrow_ctrl+"."+intensity_name+axis, calibrate_md+".input1"+axis, force=True)
                cmds.connectAttr(arrow_ctrl+"."+calibrate_name+axis, calibrate_reduce_md+".input1"+axis, force=True)
                cmds.connectAttr(arrow_ctrl+"."+calibrate_name+"Reduce", calibrate_reduce_md+".input2"+axis, force=True)
                cmds.connectAttr(calibrate_reduce_md+".output"+axis, calibrate_md+".input2"+axis, force=True)
                cmds.connectAttr(arrow_ctrl+".translate"+axis, intensity_md+".input1"+axis, force=True)
                cmds.connectAttr(calibrate_md+".output"+axis, intensity_md+".input2"+axis, force=True)
            cmds.connectAttr(intensity_md+".outputX", side_bend_def_items[1]+".curvature", force=True)
            cmds.connectAttr(intensity_md+".outputY", squash_def_items[1]+".factor", force=True)
            cmds.connectAttr(intensity_md+".outputZ", front_bend_def_items[1]+".curvature", force=True)
            cmds.connectAttr(arrow_ctrl+".ry", twist_md+".input1Y", force=True)
            cmds.connectAttr(twist_md+".outputY", twist_def_items[1]+".endAngle", force=True)
            # change squash to be more cartoon
            cmds.connectAttr(intensity_md+".outputY", rmv_node+".inputValue", force=True)
            cmds.connectAttr(rmv_node+".outValue", squash_def_items[0]+".lowBound", force=True)
            cmds.connectAttr(arrow_ctrl+"."+expand_name, squash_def_items[0]+".expand", force=True)
            # fix side values
            for axis in self.ar.data.axes:
                unit_conv_node = cmds.listConnections(intensity_md+".output"+axis, destination=True)[0]
                if unit_conv_node:
                    if cmds.objectType(unit_conv_node) == "unitConversion":
                        cmds.setAttr(unit_conv_node+".conversionFactor", 1)
            cmds.connectAttr(arrow_ctrl+"."+self.ar.data.lang["c021_showControls"], main_ctrl_shape+".visibility")
            self.ar.ctrls.set_lock_hide([arrow_ctrl], ['rx', 'rz', 'sx', 'sy', 'sz', 'v', 'ro'])
            
            # create symmetry setup
            center_cluster_items = cmds.cluster(lattice_def_items[1]+".pt[0:5][2:3][0:5]", relative=True, name=center_symmetry_name+"_Cls") #[Cluster, Handle]
            top_cluster_items = cmds.cluster(lattice_def_items[1]+".pt[0:5][2:5][0:5]", relative=True, name=top_symmetry_name+"_Cls")
            cluster_zeros = self.ar.utils.create_zero_out([center_cluster_items[1], top_cluster_items[1]])
            cmds.matchTransform(cluster_zeros[1], center_cluster_items[1])
            cluter_grp = cmds.group(cluster_zeros, name=deformer_name+"_Cluster_Grp")
            # arrange lattice deform points percent
            cmds.percent(top_cluster_items[0], [lattice_def_items[1]+".pt[0:5][2][0]", lattice_def_items[1]+".pt[0:5][2][1]", lattice_def_items[1]+".pt[0:5][2][2]", lattice_def_items[1]+".pt[0:5][2][3]", lattice_def_items[1]+".pt[0:5][2][4]", lattice_def_items[1]+".pt[0:5][2][5]"], value=0.5)
            # symmetry controls
            center_symmetry_ctrl = self.ar.ctrls.create_controller("id_068_Symmetry", center_symmetry_name+"_Ctrl", bbox_size, d=0, rot=(-90, 0, 90), parent_tag=arrow_ctrl)
            top_symmetry_ctrl = self.ar.ctrls.create_controller("id_068_Symmetry", top_symmetry_name+"_Ctrl", bbox_size, d=0, rot=(0, 90, 0), parent_tag=arrow_ctrl)
            symmetry_ctrl_zeros = self.ar.utils.create_zero_out([center_symmetry_ctrl, top_symmetry_ctrl])
            for axis in self.ar.data.axes:
                cmds.connectAttr(center_symmetry_ctrl+".translate"+axis, center_cluster_items[1]+".translate"+axis, force=True)
                cmds.connectAttr(center_symmetry_ctrl+".rotate"+axis, center_cluster_items[1]+".rotate"+axis, force=True)
                cmds.connectAttr(center_symmetry_ctrl+".scale"+axis, center_cluster_items[1]+".scale"+axis, force=True)
                cmds.connectAttr(top_symmetry_ctrl+".translate"+axis, top_cluster_items[1]+".translate"+axis, force=True)
                cmds.connectAttr(top_symmetry_ctrl+".rotate"+axis, top_cluster_items[1]+".rotate"+axis, force=True)
                cmds.connectAttr(top_symmetry_ctrl+".scale"+axis, top_cluster_items[1]+".scale"+axis, force=True)

            # create subControls setup
            sub_ctrls = []
            sub_ctrl_grps = []
            for pos, latticeSubPoints in zip(position, lattice_sub_points):
                # create and connect cluster
                namePos = bottom_ctrl_name.replace(self.ar.data.lang["c100_bottom"], pos)
                sub_cluster_items = cmds.cluster(latticeSubPoints, relative=True, name=namePos+"_Cls")
                self.to_ids.extend(sub_cluster_items)
                cmds.parent(self.ar.utils.create_zero_out([sub_cluster_items[1]])[0], cluter_grp)
                # create control and match zeroOutGrp
                sub_ctrl = self.ar.ctrls.create_controller("id_098_HeadDeformerSub", namePos+"_Ctrl", 0.55*bbox_size, d=0, rot=(90, 0, 0), parent_tag=arrow_ctrl)
                sub_ctrls.append(sub_ctrl)
                ctrl_sub_zeros = self.ar.utils.create_zero_out([sub_ctrl])[0]
                sub_ctrl_grps.append(ctrl_sub_zeros)
                cmds.matchTransform(ctrl_sub_zeros, sub_cluster_items[1], pos=True)
                # connect atributes
                cmds.connectAttr(arrow_ctrl+"."+self.ar.data.lang["c021_showControls"], ctrl_sub_zeros+".visibility")
                for axis in self.ar.data.axes:
                    cmds.connectAttr(sub_ctrl+".translate"+axis, sub_cluster_items[1]+".translate"+axis, force=True)
                    cmds.connectAttr(sub_ctrl+".rotate"+axis, sub_cluster_items[1]+".rotate"+axis, force=True)
                    cmds.connectAttr(sub_ctrl+".scale"+axis, sub_cluster_items[1]+".scale"+axis, force=True)

            # create groups
            arrow_ctrl_grp = cmds.group(arrow_ctrl, name=arrow_ctrl+"_Grp")
            self.ar.utils.create_zero_out([arrow_ctrl], False, False)
            offset_grp = cmds.group(name=deformer_name+"_Offset_Grp", empty=True)
            data_grp = cmds.group(name=deformer_name+"_Data_Grp", empty=True)
            cmds.matchTransform(arrow_ctrl_grp, lattice_def_items[2], position=True, rotation=True)
            arrow_ctrl_height = bbox_max_y + (bbox_size*0.5)
            cmds.setAttr(arrow_ctrl_grp+".ty", arrow_ctrl_height)
            cmds.matchTransform(offset_grp, lattice_def_items[2], position=True, rotation=True)
            cmds.matchTransform(symmetry_ctrl_zeros[0], lattice_def_items[2], position=True, rotation=True)
            cmds.matchTransform(symmetry_ctrl_zeros[1], lattice_def_items[2], position=True, rotation=True)
            top_symmetry_height = cmds.getAttr(symmetry_ctrl_zeros[1]+".ty") - (bbox_size*0.3)
            cmds.setAttr(symmetry_ctrl_zeros[1]+".ty", top_symmetry_height)
            cmds.parent(symmetry_ctrl_zeros, arrow_ctrl_grp)
            lattice_grp = cmds.group(name=lattice_def_items[1]+"_Grp", empty=True)
            cmds.parent(lattice_def_items[1], lattice_def_items[2], lattice_grp)
            main_ctrl_grp = cmds.group(main_ctrl, name=main_ctrl+"_Grp")
            cmds.matchTransform(main_ctrl_grp, main_ctrl, pivots=True)
            cmds.matchTransform(main_ctrl_grp, lattice_def_items[1], position=True, rotation=True)
            cmds.parent(arrow_ctrl_grp, main_ctrl)
            cmds.parentConstraint(main_ctrl, data_grp, maintainOffset=True, name=data_grp+"_PaC")
            cmds.scaleConstraint(main_ctrl, data_grp, maintainOffset=True, name=data_grp+"_ScC")
            cmds.parent(sub_ctrl_grps, arrow_ctrl_grp)
            # fix topSymmetryCluster pivot
            top_symmetry_ctrl_pos = cmds.xform(symmetry_ctrl_zeros[1], query=True, rotatePivot=True, worldSpace=True)
            cmds.xform(top_cluster_items[1], rotatePivot=(top_symmetry_ctrl_pos[0], top_symmetry_ctrl_pos[1], top_symmetry_ctrl_pos[2]), worldSpace=True)

            # workaround to add the deformer attribute on the remaining maincontrols from head and jaw control         
            ctrls_children = []
            head_sub_ctrl = self.ar.ctrls.get_controller_node_by_id("id_093_HeadSub")
            jaw_ctrl = self.ar.ctrls.get_controller_node_by_id("id_024_HeadJaw")
            jaw_conditions = [self.ar.data.lang["m075_upperTeeth"], self.ar.data.lang["m076_lowerTeeth"], self.ar.data.lang["m077_tongue"], self.ar.data.lang["c039_lip"]+"_"+self.ar.data.lang["c058_main"]]
            ctrl_id_not_include_items = ["id_029_SingleIndSkin", "id_052_FacialFace", "id_068_Symmetry", "id_053_HeadDeformer", "id_098_HeadDeformerSub", "id_097_HeadDeformerMain"]
            if head_sub_ctrl:
                head_sub_ctrl_children = cmds.listRelatives(head_sub_ctrl, allDescendents=True)
                if head_sub_ctrl_children:
                    for child in head_sub_ctrl_children:
                        ctrls_children.append(child)
            if jaw_ctrl:
                jaw_ctrl_children = cmds.listRelatives(jaw_ctrl, allDescendents=True)
                if jaw_ctrl_children:
                    for child in jaw_ctrl_children:
                        ctrls_children.append(child)
            if ctrls_children:
                for item in ctrls_children:
                    if cmds.objExists(item+".controlID"):
                        if not cmds.objExists(item+"."+DPHEADDEFINFLUENCE):
                            if cmds.getAttr(item+".controlID") not in ctrl_id_not_include_items:
                                self.ar.ctrls.add_def_influence_attrs(item, def_influence_type=1)
                                if not cmds.objExists(item+"."+DPJAWDEFINFLUENCE):
                                    for condition in jaw_conditions:
                                        if condition in item:
                                            self.ar.ctrls.add_def_influence_attrs(item, def_influence_type=2)

            # apply influence deformer only in child shape controls which have the attribute or given nodes
            if not deformed_by_items:
                deformed_by_items = cmds.ls(selection=False, type="transform")
            if deformed_by_items:
                for item in deformed_by_items:
                    if cmds.objExists(item+".controlID"):
                        if not self.ar.data.lang["c025_jaw"] in arrow_ctrl:
                            if cmds.objExists(item+"."+DPHEADDEFINFLUENCE) and cmds.getAttr(item+"."+DPHEADDEFINFLUENCE):
                                shape = cmds.listRelatives(item, shapes=True)
                                if shape:
                                    cmds.deformer(deformer_name+"_FFD", edit=True, geometry=shape)
                        else:
                            if cmds.objExists(item+"."+DPJAWDEFINFLUENCE) and cmds.getAttr(item+"."+DPJAWDEFINFLUENCE):
                                shape = cmds.listRelatives(item, shapes=True)
                                if shape:
                                    cmds.deformer(deformer_name+"_FFD", edit=True, geometry=shape)
                                
            # try to integrate to Head_Head_Sub_Ctrl
            if not head_ctrl:
                if head_sub_ctrl:
                    if len(head_sub_ctrl) > 1:
                        mel.eval("warning" + "\"" + self.ar.data.lang["i075_moreOne"] + " Head control.\"" + ";")
                    else:
                        head_ctrl = head_sub_ctrl[0]
            if head_ctrl:
                # correcting topSymetry pivot to match headCtrl pivot
                cmds.matchTransform(top_symmetry_ctrl, top_cluster_items[1], head_ctrl, pivots=True)
                # setup hierarchy
                head_ctrl_pos = cmds.xform(head_ctrl, query=True, rotatePivot=True, worldSpace=True)
                cmds.xform(data_grp, translation=(head_ctrl_pos[0], head_ctrl_pos[1], head_ctrl_pos[2]), worldSpace=True)
                cmds.parent(main_ctrl_grp, head_ctrl)
            else:
                mel.eval("warning" + "\"" + self.ar.data.lang["e020_notFoundHeadCtrl"] + "\"" + ";")
                self.well_done = False
            
            cmds.parent(squash_def_items[1], side_bend_def_items[1], front_bend_def_items[1], twist_def_items[1], offset_grp)
            cmds.parent(offset_grp, cluter_grp, lattice_grp, data_grp)
            
            # try to integrate to Scalable_Grp
            scalable_grp = self.ar.utils.get_node_by_message("scalableGrp")
            if scalable_grp:
                cmds.parent(data_grp, scalable_grp)
            
            # try to change deformers to get better result
            cmds.scale(1.25, 1.25, 1.25, offset_grp)
            
            # colorize
            self.ar.ctrls.color_shape([arrow_ctrl, main_ctrl, center_symmetry_ctrl, top_symmetry_ctrl, sub_ctrls[0], sub_ctrls[1], sub_ctrls[2]], "cyan")

            # if there's Jaw in the deformer_name it will configure rotate and delete symetries and subControls setup
            if self.ar.data.lang["c025_jaw"] in main_ctrl:
                cmds.setAttr(main_ctrl_grp+".rotateX", 145)
                cmds.delete(cluter_grp, sub_ctrl_grps, symmetry_ctrl_zeros)

            # serialize network node
            self.net = cmds.createNode("network", name=net_name)
            self.to_ids.append(self.net)
            # add
            cmds.addAttr(self.net, longName="dpNetwork", attributeType="bool", defaultValue=1)
            cmds.addAttr(self.net, longName="dpHeadDeformerNet", attributeType="bool", defaultValue=1)
            cmds.addAttr(self.net, longName="guideNet", attributeType="message")
            cmds.addAttr(self.net, longName="linkedNode", attributeType="message")
            cmds.addAttr(self.net, longName="netData", dataType="string")
            cmds.addAttr(arrow_ctrl, longName="hdNet", attributeType="message")
            # set
            cmds.setAttr(self.net+".netData", self.get_net_data(deformer_name, hd_items), type="string")
            # connect
            if guide_net:
                cmds.connectAttr(guide_net+".message", self.net+".guideNet", force=True)
            cmds.connectAttr(arrow_ctrl+".message", self.net+".linkedNode", force=True)
            cmds.connectAttr(self.net+".message", arrow_ctrl+".hdNet", force=True)

            # calibration attributes:
            hd_calibrations = [
                                    calibrate_name+"X",
                                    calibrate_name+"Y",
                                    calibrate_name+"Z",
                                    calibrate_name+"Reduce"
                                ]
            self.ar.ctrls.set_string_attr_from_items(arrow_ctrl, hd_calibrations)
            
            # rename unitConversion nodes
            self.ar.utils.node_renaming_treatment(list(set(cmds.ls(selection=False, type="unitConversion"))-set(self.old_unit_conversions)))
            # add ignoreTranformIO attribute
            self.ar.utils.add_attr_to_items([lattice_def_items[1], lattice_def_items[2], offset_grp, arrow_ctrl_grp], self.ar.utils.ignore_transform_io_attr)
            # add dpID attributes
            self.to_ids.extend([main_ctrl_grp, data_grp, calibrate_md, calibrate_reduce_md, intensity_md, twist_md, rmv_node])
            for deformers in [lattice_def_items, twist_def_items, squash_def_items, side_bend_def_items, front_bend_def_items, center_cluster_items, top_cluster_items]:
                self.to_ids.extend(deformers)
            self.ar.custom_attr.add_attr(0, self.to_ids, descendents=True) #dpID
            # finish selection the arrow control
            cmds.select(arrow_ctrl)
            if self.well_done:
                print(self.ar.data.lang["i179_addedHeadDef"])
            return self.net
        else:
            mel.eval("warning" + "\"" + self.ar.data.lang["i034_notSelHeadDef"] + "\"" + ";")


    def get_net_data(self, deformer_name, hd_items):
        """ Collect all headDeformer data and return it as a dictionary.
        """
        data = {}
        data["hdName"] = deformer_name
        data["hd_items"] = hd_items
        data["moduleType"] = CLASS_NAME
        return data
