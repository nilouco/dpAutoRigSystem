###
#
#   THANKS to:
#       Renaud Lessard
#
#   Based on:
#       https://github.com/renaudll/omtk/blob/9b756fb9e822bf03b4c643328a283d29187298fd/omtk/animation/ikfkTools.py
#   
###


# importing libraries:
from maya import cmds
from maya.api import OpenMaya
import math



class IkFkSnap(object):
    def __init__(self, ar, net_name, world_ref, fk_ctrls, ik_ctrls, ik_joints, rev_foot_attrs, uniform_scale_attr, dp_dev=False, creation=True, *args):
        # defining variables:
        self.ar = ar
        self.net_name = net_name
        self.world_ref = world_ref
        self.ikfk_blend_attr = cmds.getAttr(self.world_ref+".ikFkBlendAttrName")
        self.ik_before_ctrl = fk_ctrls[0]
        self.ik_pole_vector_ctrl = ik_ctrls[0]
        self.ik_extreme_ctrl = ik_ctrls[1]
        self.ik_extreme_sub_ctrl = ik_ctrls[2]
        self.fk_ctrls = fk_ctrls
        self.ik_joints = ik_joints
        self.rev_foot_attrs = rev_foot_attrs
        self.uniform_scale_attr = uniform_scale_attr
        if creation:
            self.fk_ctrls = fk_ctrls[1:]
            self.ik_joints = ik_joints[1:-1]
            # calculate the initial ikFk extrem offset
            self.extreme_offset_matrix = self.get_offset_matrix(self.ik_extreme_ctrl, self.fk_ctrls[-1])
            # store data
            self.ikfk_state = round(cmds.getAttr(self.world_ref+"."+self.ikfk_blend_attr), 0)
            self.ikfk_snap_net = cmds.createNode("network", name=self.net_name+"_IkFkSnap_Net")
            self.ar.custom_attr.add_attr(0, [self.ikfk_snap_net]) #dpID
            self.id = cmds.getAttr(self.ikfk_snap_net+"."+self.ar.data.dp_id)
            self.store_ikfk_snap_data()
            if dp_dev:
                cmds.scriptJob(attributeChange=(self.world_ref+"."+self.ikfk_blend_attr, self.job_changed_ikfk), killWithScene=False, compressUndo=True)
            self.generate_script_node()
        else:
            self.ik_before_ctrl = cmds.listConnections(net_name+".ikBeforeCtrl")[0]
            self.extreme_offset_matrix = cmds.getAttr(net_name+".extremOffset")
    

    ###
    # ---------------------------------
    # Code to development or creating a new module instance
    ###

    def get_offset_matrix(self, wm, wim):
        """ Return the offset matrix (multiplied matrices) from given world and inverse matrices.
        """
        a_matrix = OpenMaya.MMatrix(cmds.getAttr(wm+".worldMatrix[0]"))
        b_matrix = OpenMaya.MMatrix(cmds.getAttr(wim+".worldInverseMatrix[0]"))
        return (a_matrix * b_matrix)


    def store_ikfk_snap_data(self):
        """ Store all the needed attributes data to snap ik and fk into the network node.
        """
        # add
        cmds.addAttr(self.ikfk_snap_net, longName="dpNetwork", attributeType="bool")
        cmds.addAttr(self.ikfk_snap_net, longName="dpIkFkSnapNet", attributeType="bool")
        cmds.addAttr(self.ikfk_snap_net, longName="dpIkFkSnapNetName", dataType="string")
        cmds.addAttr(self.ikfk_snap_net, longName="ikFkState", attributeType="short")
        cmds.addAttr(self.ikfk_snap_net, longName="worldRef", attributeType="message")
        cmds.addAttr(self.ikfk_snap_net, longName="ikBeforeCtrl", attributeType="message")
        cmds.addAttr(self.ikfk_snap_net, longName="ikPoleVectorCtrl", attributeType="message")
        cmds.addAttr(self.ikfk_snap_net, longName="ikExtremCtrl", attributeType="message")
        cmds.addAttr(self.ikfk_snap_net, longName="ikExtremSubCtrl", attributeType="message")
        cmds.addAttr(self.ikfk_snap_net, longName="fk_ctrls", multi=True)
        cmds.addAttr(self.ikfk_snap_net, longName="ik_joints", multi=True)
        cmds.addAttr(self.ikfk_snap_net, longName="rev_foot_attrs", dataType="string")
        cmds.addAttr(self.ikfk_snap_net, longName="uniform_scale_attr", dataType="string")
        cmds.addAttr(self.ikfk_snap_net, longName="ikFkBlendAttr", dataType="string")
        cmds.addAttr(self.ikfk_snap_net, longName="extremOffset", attributeType="matrix")
        cmds.addAttr(self.world_ref, longName="ikFkSnapNet", attributeType="message")
        # set
        cmds.setAttr(self.ikfk_snap_net+".dpNetwork", 1)
        cmds.setAttr(self.ikfk_snap_net+".dpIkFkSnapNet", 1)
        cmds.setAttr(self.ikfk_snap_net+".dpIkFkSnapNetName", self.net_name, type="string")
        cmds.setAttr(self.ikfk_snap_net+".ikFkState", self.ikfk_state)
        cmds.setAttr(self.ikfk_snap_net+".ikFkBlendAttr", self.ikfk_blend_attr, type="string")
        cmds.setAttr(self.ikfk_snap_net+".extremOffset", self.extreme_offset_matrix, type="matrix")
        cmds.setAttr(self.ikfk_snap_net+".rev_foot_attrs", ';'.join(self.rev_foot_attrs), type="string")
        cmds.setAttr(self.ikfk_snap_net+".uniform_scale_attr", self.uniform_scale_attr, type="string")
        # connect
        cmds.connectAttr(self.ikfk_snap_net+".message", self.world_ref+".ikFkSnapNet", force=True)
        cmds.connectAttr(self.world_ref+".message", self.ikfk_snap_net+".worldRef", force=True)
        cmds.connectAttr(self.ik_before_ctrl+".message", self.ikfk_snap_net+".ikBeforeCtrl", force=True)
        cmds.connectAttr(self.ik_pole_vector_ctrl+".message", self.ikfk_snap_net+".ikPoleVectorCtrl", force=True)
        cmds.connectAttr(self.ik_extreme_ctrl+".message", self.ikfk_snap_net+".ikExtremCtrl", force=True)
        cmds.connectAttr(self.ik_extreme_sub_ctrl+".message", self.ikfk_snap_net+".ikExtremSubCtrl", force=True)
        for f, fk_ctrl in enumerate(self.fk_ctrls):
            cmds.connectAttr(fk_ctrl+".message", self.ikfk_snap_net+".fk_ctrls["+str(f)+"]", force=True)
        for i, ik_joint in enumerate(self.ik_joints):
            cmds.connectAttr(ik_joint+".message", self.ikfk_snap_net+".ik_joints["+str(i)+"]", force=True)


    ###
    # ---------------------------------
    # Code to use by the scriptJob included in the scriptNode
    ###

    def job_changed_ikfk(self, *args):
        """ Just call snap function to set as well or update the ikFkState.
        """
        self.world_ref = cmds.listConnections(self.ikfk_snap_net+".worldRef")[0]
        current_value = cmds.getAttr(self.world_ref+"."+self.ikfk_blend_attr)
        if cmds.getAttr(self.world_ref+".ikFkSnap"):
            self.ikfk_state = cmds.getAttr(self.ikfk_snap_net+".ikFkState")
            if self.ikfk_state == 0: #ik
                if current_value >= 0.001:
                    self.change_ikfk_attr(0, False)
                    self.snap_ik_to_fk()
                    self.change_ikfk_attr(1, True)
            else: #fk
                if current_value < 0.999:
                    self.change_ikfk_attr(1, False)
                    self.snap_fk_to_ik()
                    self.change_ikfk_attr(0, True)
            self.reset_shear(list(set([self.ik_extreme_ctrl] + self.fk_ctrls)))
        else:
            if current_value <= 0.5: #ik
                cmds.setAttr(self.ikfk_snap_net+".ikFkState", 0)
            else: #fk
                cmds.setAttr(self.ikfk_snap_net+".ikFkState", 1)


    def change_ikfk_attr(self, ikfk_value, set_state):
        """ 0 = ik
            1 = fk
        """
        plugged = cmds.listConnections(self.world_ref+"."+self.ikfk_blend_attr, source=True, destination=False, plugs=True)
        if plugged:
            cmds.setAttr(plugged[0], ikfk_value)
        else:
            cmds.setAttr(self.world_ref+"."+self.ikfk_blend_attr, ikfk_value)
        if set_state:
            self.ikfk_state = ikfk_value
            cmds.setAttr(self.ikfk_snap_net+".ikFkState", ikfk_value)


    def snap_ik_to_fk(self):
        """ Switch from ik to fk keeping the same position.
            That means move the fk to the ik position.
        """
        self.bake_follow_rotation(self.ik_before_ctrl)
        self.bake_follow_rotation(self.fk_ctrls[0])
        self.transfer_attr_from_to(self.ik_extreme_ctrl, self.fk_ctrls[2], [self.uniform_scale_attr])
        # snap fk ctrl to ik jnt
        for ctrl, jnt in zip(self.fk_ctrls, self.ik_joints):
            cmds.xform(ctrl, matrix=(cmds.xform(jnt, matrix=True, query=True, worldSpace=True)), worldSpace=True)


    def snap_fk_to_ik(self):
        """ Switch from fk to ik keeping the same position.
            That means move the ik to the fk position.
        """
        self.bake_follow_rotation(self.ik_before_ctrl)
        self.zero_key_attr_value(self.ik_extreme_ctrl, ["twist"])
        self.zero_key_attr_value(self.ik_extreme_sub_ctrl, ["tx", "ty", "tz", "rx", "ry", "rz"])
        self.transfer_attr_from_to(self.fk_ctrls[2], self.ik_extreme_ctrl, [self.uniform_scale_attr])
        
        # extrem ctrl
        fk_matrix = OpenMaya.MMatrix(cmds.getAttr(self.fk_ctrls[-1]+".worldMatrix[0]"))
        to_ik_matrix = OpenMaya.MMatrix(self.extreme_offset_matrix) * fk_matrix #need redefine to load matrix in scriptNode
        cmds.xform(self.ik_extreme_ctrl, matrix=list(to_ik_matrix), worldSpace=True)
        # poleVector ctrl
        start_pos, corner_pos, end_pos, chain_len, pv_ratio = self.get_chain_position()
        # calculate the position of the base middle locator
        pv_base_pos_x = (end_pos[0] - start_pos[0]) * pv_ratio+start_pos[0]
        pv_base_pos_y = (end_pos[1] - start_pos[1]) * pv_ratio+start_pos[1]
        pv_base_pos_z = (end_pos[2] - start_pos[2]) * pv_ratio+start_pos[2]
        # working with vectors
        corner_base_pos_x = corner_pos[0] - pv_base_pos_x
        corner_base_pos_y = corner_pos[1] - pv_base_pos_y
        corner_base_pos_z = corner_pos[2] - pv_base_pos_z
        # magnitude of the vector
        mag_dir = math.sqrt(corner_base_pos_x**2+corner_base_pos_y**2+corner_base_pos_z**2)
        # normalize the vector
        normal_dir_x = corner_base_pos_x / mag_dir
        normal_dir_y = corner_base_pos_y / mag_dir
        normal_dir_z = corner_base_pos_z / mag_dir
        # calculate the poleVector position by multiplying the unitary vector by the chain length
        pv_dist_x = normal_dir_x * chain_len
        pv_dist_y = normal_dir_y * chain_len
        pv_dist_z = normal_dir_z * chain_len
        # get the poleVector position
        pv_pos_x = pv_base_pos_x+pv_dist_x
        pv_pos_y = pv_base_pos_y+pv_dist_y
        pv_pos_z = pv_base_pos_z+pv_dist_z
        # place poleVector controller in the correct position
        cmds.move(pv_pos_x, pv_pos_y, pv_pos_z, self.ik_pole_vector_ctrl, objectSpace=False, worldSpaceDistance=True)
        # reset footRoll attributes
        user_def_attrs = cmds.listAttr(self.ik_extreme_ctrl, userDefined=True, keyable=True)
        if user_def_attrs:
            for attr in user_def_attrs:
                for rev_foot_attr in self.rev_foot_attrs:
                    if rev_foot_attr in attr:
                        cmds.setAttr(self.ik_extreme_ctrl+"."+attr, 0)


    def get_offset_xform(self, wm, wim):
        """ Return the offset xform matrix (multiplied matrices) from given xform matrices.
        """
        a_matrix = OpenMaya.MMatrix(cmds.getAttr(wm+".xformMatrix"))
        b_matrix = OpenMaya.MMatrix(cmds.getAttr(wim+".xformMatrix"))
        return (a_matrix * b_matrix)


    def bake_follow_rotation(self, ctrl):
        """ Set clavicle rotation from offset xform calculus.
            Also set rotation keyframe.
        """
        if cmds.objExists(ctrl+".followAttrName"): #stored attribute name to avoid run procedure without dpAR language dictionary
            follow_attr = cmds.getAttr(ctrl+".followAttrName")
            if cmds.getAttr(ctrl+"."+follow_attr):
                father = cmds.listRelatives(ctrl, parent=True, type="transform")[0]
                negative_scale = cmds.getAttr(father+".scaleX")
                if negative_scale == -1:
                    cmds.setAttr(father+".scaleX", 1)
                    cmds.setAttr(father+".scaleY", 1)
                    cmds.setAttr(father+".scaleZ", 1)
                ctrl_offset = self.get_offset_xform(ctrl, father)
                cmds.xform(ctrl, matrix=list(ctrl_offset), worldSpace=False)
                cmds.xform(ctrl, translation=[0, 0, 0], worldSpace=False)
                # disable autoClavicle and keyframe it
                cmds.setAttr(ctrl+"."+follow_attr, 0)
                cmds.setKeyframe(ctrl, attribute=("rotateX", "rotateY", "rotateZ", follow_attr))
                if negative_scale == -1:
                    cmds.setAttr(father+".scaleX", -1)
                    cmds.setAttr(father+".scaleY", -1)
                    cmds.setAttr(father+".scaleZ", -1)


    def zero_key_attr_value(self, ctrl, attributes):
        """ Set zero value and keyframe the given attributes in the controller.
        """
        for attr in attributes:
            if cmds.objExists(ctrl+"."+attr):
                if cmds.getAttr(ctrl+"."+attr):
                    cmds.setAttr(ctrl+"."+attr, 0)
                    cmds.setKeyframe(ctrl, attribute=attr)


    def transfer_attr_from_to(self, from_ctrl, to_ctrl, attributes):
        """ It compares the attributes to transfer values from/to given controllers and keyframe them.
        """
        for attr in attributes:
            if cmds.objExists(from_ctrl+"."+attr) and cmds.objExists(to_ctrl+"."+attr):
                from_value = cmds.getAttr(from_ctrl+"."+attr)
                to_value = cmds.getAttr(to_ctrl+"."+attr)
                if not from_value == to_value:
                    cmds.setAttr(to_ctrl+"."+attr, from_value)
                    cmds.setKeyframe(to_ctrl, attribute=attr)


    def reset_shear(self, controllers):
        """ Set zero to all shear attributes in main controllers affected by possible stretch.
        """
        start_length = cmds.getAttr(self.ik_extreme_ctrl+".startChainLength")
        current_length = self.get_chain_position()[3] #chain_len
        if current_length == start_length:
            for ctrl in controllers:
                cmds.setAttr(ctrl+".shearXY", 0)
                cmds.setAttr(ctrl+".shearXZ", 0)
                cmds.setAttr(ctrl+".shearYZ", 0)
    

    def get_chain_position(self):
        """ Return the start, coner and end position, the chain lenght and poleVector Ratio values as a list,
            based on the fk_ctrls.
        """
        # get joint chain positions
        start_pos  = cmds.xform(self.fk_ctrls[0], query=True, worldSpace=True, rotatePivot=True) #shoulder, leg
        corner_pos = cmds.xform(self.fk_ctrls[1], query=True, worldSpace=True, rotatePivot=True) #elbow, knee
        end_pos    = cmds.xform(self.fk_ctrls[2], query=True, worldSpace=True, rotatePivot=True) #wrist, ankle
        # calculate distances (joint lenghts)
        upper_limb_len = self.utils_distance_vectors(start_pos, corner_pos)
        lower_limb_len = self.utils_distance_vectors(corner_pos, end_pos)
        chain_len = upper_limb_len+lower_limb_len
        # ratio of placement of the middle joint
        pv_ratio = upper_limb_len / chain_len
        return [start_pos, corner_pos, end_pos, chain_len, pv_ratio]


    ###
    # ---------------------------------
    # Code from utils
    ###

    def utils_distance_vectors(self, u, v):
        """ Returns the distance between 2 given points.
        """
        return math.sqrt((v[0]-u[0])**2+(v[1]-u[1])**2+(v[2]-u[2])**2)


    ###
    # ---------------------------------
    # Code to scriptNode
    ###

    def generate_script_node(self):
        """ Create a scriptNode to store the ikFkSnap code into it.
        """
        ikfk_snap_code = '''
from maya import cmds
from maya.api import OpenMaya
import math

class IkFkSnap(object):
    def __init__(self, ikFkSnapNet):
        self.ikfk_snap_net = ikFkSnapNet
        self.reloadNetData()
        cmds.scriptJob(attributeChange=(self.world_ref+"."+self.ikfk_blend_attr, self.job_changed_ikfk), killWithScene=False, compressUndo=True)

    def reloadNetData(self):
        self.world_ref = cmds.listConnections(self.ikfk_snap_net+".worldRef")[0]
        self.ikfk_state = cmds.getAttr(self.ikfk_snap_net+".ikFkState")
        self.ikfk_blend_attr = cmds.getAttr(self.world_ref+".ikFkBlendAttrName")
        self.uniform_scale_attr = cmds.getAttr(self.ikfk_snap_net+".uniform_scale_attr")
        self.ik_before_ctrl = cmds.listConnections(self.ikfk_snap_net+".ikBeforeCtrl")[0]
        self.ik_pole_vector_ctrl = cmds.listConnections(self.ikfk_snap_net+".ikPoleVectorCtrl")[0]
        self.ik_extreme_ctrl = cmds.listConnections(self.ikfk_snap_net+".ikExtremCtrl")[0]
        self.ik_extreme_sub_ctrl = cmds.listConnections(self.ikfk_snap_net+".ikExtremSubCtrl")[0]
        self.fk_ctrls = cmds.listConnections(self.ikfk_snap_net+".fk_ctrls")
        self.ik_joints = cmds.listConnections(self.ikfk_snap_net+".ik_joints")
        self.rev_foot_attrs = list(cmds.getAttr(self.ikfk_snap_net+".rev_foot_attrs").split(";"))
        self.extreme_offset_matrix = cmds.getAttr(self.ikfk_snap_net+".extremOffset")

    def job_changed_ikfk(self, *args):
        """ Just call snap function to set as well or update the ikFkState.
        """
        self.world_ref = cmds.listConnections(self.ikfk_snap_net+".worldRef")[0]
        current_value = cmds.getAttr(self.world_ref+"."+self.ikfk_blend_attr)
        if cmds.getAttr(self.world_ref+".ikFkSnap"):
            self.ikfk_state = cmds.getAttr(self.ikfk_snap_net+".ikFkState")
            if self.ikfk_state == 0: #ik
                if current_value >= 0.001:
                    self.change_ikfk_attr(0, False)
                    self.snap_ik_to_fk()
                    self.change_ikfk_attr(1, True)
            else: #fk
                if current_value < 0.999:
                    self.change_ikfk_attr(1, False)
                    self.snap_fk_to_ik()
                    self.change_ikfk_attr(0, True)
            self.reset_shear(list(set([self.ik_extreme_ctrl] + self.fk_ctrls)))
        else:
            if current_value <= 0.5: #ik
                cmds.setAttr(self.ikfk_snap_net+".ikFkState", 0)
            else: #fk
                cmds.setAttr(self.ikfk_snap_net+".ikFkState", 1)

    def change_ikfk_attr(self, ikfk_value, set_state, *args):
        """ 0 = ik
            1 = fk
        """
        plugged = cmds.listConnections(self.world_ref+"."+self.ikfk_blend_attr, source=True, destination=False, plugs=True)
        if plugged:
            cmds.setAttr(plugged[0], ikfk_value)
        else:
            cmds.setAttr(self.world_ref+"."+self.ikfk_blend_attr, ikfk_value)
        if set_state:
            self.ikfk_state = ikfk_value
            cmds.setAttr(self.ikfk_snap_net+".ikFkState", ikfk_value)

    def snap_ik_to_fk(self):
        """ Switch from ik to fk keeping the same position.
        """
        self.bake_follow_rotation(self.ik_before_ctrl)
        self.bake_follow_rotation(self.fk_ctrls[0])
        self.transfer_attr_from_to(self.ik_extreme_ctrl, self.fk_ctrls[2], [self.uniform_scale_attr])
        # snap fk ctrl to ik jnt
        for ctrl, jnt in zip(self.fk_ctrls, self.ik_joints):
            cmds.xform(ctrl, matrix=(cmds.xform(jnt, matrix=True, query=True, worldSpace=True)), worldSpace=True)
    
    def snap_fk_to_ik(self):
        """ Switch from fk to ik keeping the same position.
        """
        self.bake_follow_rotation(self.ik_before_ctrl)
        self.zero_key_attr_value(self.ik_extreme_ctrl, ["twist"])
        self.zero_key_attr_value(self.ik_extreme_sub_ctrl, ["tx", "ty", "tz", "rx", "ry", "rz"])
        self.transfer_attr_from_to(self.fk_ctrls[2], self.ik_extreme_ctrl, [self.uniform_scale_attr])
        # extrem ctrl
        fk_matrix = OpenMaya.MMatrix(cmds.getAttr(self.fk_ctrls[-1]+".worldMatrix[0]"))
        to_ik_matrix = OpenMaya.MMatrix(self.extreme_offset_matrix) * fk_matrix
        cmds.xform(self.ik_extreme_ctrl, matrix=list(to_ik_matrix), worldSpace=True)
        # poleVector ctrl
        start_pos, corner_pos, end_pos, chain_len, pv_ratio = self.get_chain_position()
        # calculate the position of the base middle locator
        pv_base_pos_x = (end_pos[0] - start_pos[0]) * pv_ratio+start_pos[0]
        pv_base_pos_y = (end_pos[1] - start_pos[1]) * pv_ratio+start_pos[1]
        pv_base_pos_z = (end_pos[2] - start_pos[2]) * pv_ratio+start_pos[2]
        # working with vectors
        corner_base_pos_x = corner_pos[0] - pv_base_pos_x
        corner_base_pos_y = corner_pos[1] - pv_base_pos_y
        corner_base_pos_z = corner_pos[2] - pv_base_pos_z
        # magnitude of the vector
        mag_dir = math.sqrt(corner_base_pos_x**2+corner_base_pos_y**2+corner_base_pos_z**2)
        # normalize the vector
        normal_dir_x = corner_base_pos_x / mag_dir
        normal_dir_y = corner_base_pos_y / mag_dir
        normal_dir_z = corner_base_pos_z / mag_dir
        # calculate the poleVector position by multiplying the unitary vector by the chain length
        pv_dist_x = normal_dir_x * chain_len
        pv_dist_y = normal_dir_y * chain_len
        pv_dist_z = normal_dir_z * chain_len
        # get the poleVector position
        pv_pos_x = pv_base_pos_x+pv_dist_x
        pv_pos_y = pv_base_pos_y+pv_dist_y
        pv_pos_z = pv_base_pos_z+pv_dist_z
        # place poleVector controller in the correct position
        cmds.move(pv_pos_x, pv_pos_y, pv_pos_z, self.ik_pole_vector_ctrl, objectSpace=False, worldSpaceDistance=True)
        # reset footRoll attributes
        user_def_attrs = cmds.listAttr(self.ik_extreme_ctrl, userDefined=True, keyable=True)
        if user_def_attrs:
            for attr in user_def_attrs:
                for rev_foot_attr in self.rev_foot_attrs:
                    if rev_foot_attr in attr:
                        cmds.setAttr(self.ik_extreme_ctrl+"."+attr, 0)

    def get_offset_xform(self, wm, wim):
        """ Return the offset xform matrix (multiplied matrices) from given xform matrices.
        """
        a_matrix = OpenMaya.MMatrix(cmds.getAttr(wm+".xformMatrix"))
        b_matrix = OpenMaya.MMatrix(cmds.getAttr(wim+".xformMatrix"))
        return (a_matrix * b_matrix)

    def bake_follow_rotation(self, ctrl):
        """ Set clavicle rotation from offset xform calculus.
            Also set rotation keyframe.
        """
        if cmds.objExists(ctrl+".followAttrName"): #stored attribute name to avoid run procedure without dpAR language dictionary
            follow_attr = cmds.getAttr(ctrl+".followAttrName")
            if cmds.getAttr(ctrl+"."+follow_attr):
                father = cmds.listRelatives(ctrl, parent=True, type="transform")[0]
                negative_scale = cmds.getAttr(father+".scaleX")
                if negative_scale == -1:
                    cmds.setAttr(father+".scaleX", 1)
                    cmds.setAttr(father+".scaleY", 1)
                    cmds.setAttr(father+".scaleZ", 1)
                ctrl_offset = self.get_offset_xform(ctrl, father)
                cmds.xform(ctrl, matrix=list(ctrl_offset), worldSpace=False)
                cmds.xform(ctrl, translation=[0, 0, 0], worldSpace=False)
                # disable autoClavicle and keyframe it
                cmds.setAttr(ctrl+"."+follow_attr, 0)
                cmds.setKeyframe(ctrl, attribute=("rotateX", "rotateY", "rotateZ", follow_attr))
                if negative_scale == -1:
                    cmds.setAttr(father+".scaleX", -1)
                    cmds.setAttr(father+".scaleY", -1)
                    cmds.setAttr(father+".scaleZ", -1)

    def zero_key_attr_value(self, ctrl, attributes):
        """ Set zero value and keyframe the given attributes in the controller.
        """
        for attr in attributes:
            if cmds.objExists(ctrl+"."+attr):
                if cmds.getAttr(ctrl+"."+attr):
                    cmds.setAttr(ctrl+"."+attr, 0)
                    cmds.setKeyframe(ctrl, attribute=attr)

    def transfer_attr_from_to(self, from_ctrl, to_ctrl, attributes):
        """ It compares the attributes to transfer values from/to given controllers and keyframe them.
        """
        for attr in attributes:
            if cmds.objExists(from_ctrl+"."+attr) and cmds.objExists(to_ctrl+"."+attr):
                from_value = cmds.getAttr(from_ctrl+"."+attr)
                to_value = cmds.getAttr(to_ctrl+"."+attr)
                if not from_value == to_value:
                    cmds.setAttr(to_ctrl+"."+attr, from_value)
                    cmds.setKeyframe(to_ctrl, attribute=attr)

    def reset_shear(self, controllers):
        """ Set zero to all shear attributes in main controllers affected by possible stretch.
        """
        start_length = cmds.getAttr(self.ik_extreme_ctrl+".startChainLength")
        current_length = self.get_chain_position()[3] #chain_len
        if current_length == start_length:
            for ctrl in controllers:
                cmds.setAttr(ctrl+".shearXY", 0)
                cmds.setAttr(ctrl+".shearXZ", 0)
                cmds.setAttr(ctrl+".shearYZ", 0)

    def get_chain_position(self):
        """ Return the start, coner and end position, the chain lenght and poleVector Ratio values as a list,
            based on the fk_ctrls.
        """
        # get joint chain positions
        start_pos  = cmds.xform(self.fk_ctrls[0], query=True, worldSpace=True, rotatePivot=True) #shoulder, leg
        corner_pos = cmds.xform(self.fk_ctrls[1], query=True, worldSpace=True, rotatePivot=True) #elbow, knee
        end_pos    = cmds.xform(self.fk_ctrls[2], query=True, worldSpace=True, rotatePivot=True) #wrist, ankle
        # calculate distances (joint lenghts)
        upper_limb_len = self.utils_distance_vectors(start_pos, corner_pos)
        lower_limb_len = self.utils_distance_vectors(corner_pos, end_pos)
        chain_len = upper_limb_len+lower_limb_len
        # ratio of placement of the middle joint
        pv_ratio = upper_limb_len / chain_len
        return [start_pos, corner_pos, end_pos, chain_len, pv_ratio]

    def utils_distance_vectors(self, u, v):
        """ Returns the distance between 2 given points.
        """
        return math.sqrt((v[0]-u[0])**2+(v[1]-u[1])**2+(v[2]-u[2])**2)

# fire scriptNode
for net in cmds.ls(type="network"):
    if cmds.objExists(net+".dpNetwork") and cmds.getAttr(net+".dpNetwork") == 1:
        if cmds.objExists(net+".dpIkFkSnapNet") and cmds.getAttr(net+".dpIkFkSnapNet") == 1:
            if cmds.objExists(net+".dpID") and cmds.getAttr(net+".dpID") == "'''+self.id+'''":
                IkFkSnap(net)
'''
        sn = cmds.scriptNode(name=self.net_name+'_IkFkSnap_SN', sourceType='python', scriptType=2, beforeScript=ikfk_snap_code)
        self.ar.custom_attr.add_attr(0, [sn]) #dpID
        cmds.addAttr(self.ikfk_snap_net, longName="ikFkSnapScriptNode", attributeType="message")
        cmds.addAttr(sn, longName="ikFkSnapNet", attributeType="message")
        cmds.connectAttr(sn+".message", self.ikfk_snap_net+".ikFkSnapScriptNode", force=True)
        cmds.connectAttr(self.ikfk_snap_net+".message", sn+".ikFkSnapNet", force=True)
        cmds.scriptNode(sn, executeBefore=True)
