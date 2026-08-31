###########################################################
#
#   jcRibbon.py
#
#   author: James do Carmo Correa
#   contact: james.2js@gmail.com
#   portfolio: james2js.blogspot.com
#   
#   This module will create a good ribbon system to be implemented by dpLimb.py
#
#   Thanks James :)
#
###########################################################


# importing libraries:
from maya import cmds



class Ribbon(object):
    def __init__(self, ar):
        # defining variables:
        self.ar = ar
        
        
    def add_ribbon_to_limb(self, limb_instance, prefix='', name=None, ori_loc=None, ini_jnt=None, skip_axis='y', num=5, ini_jxt=None, side=0, arm=True, world_ref="worldRef", joint_label_add=0, add_artic=True, additional=False, add_correct=True, jcr_number=0, jcr_pos=None, jcr_rot=None, ori_b_loc=None):
        """ Create the Ribbon system to be added in the Limb module.
            Returns a dictionary with all nodes needed to be integrated.
        """
        self.limb_instance = limb_instance
        self.radius = limb_instance.radius
        self.curve_degree = limb_instance.curve_degree
        self.limb_manual_vv_attr = self.ar.data.lang['m019_limb'].lower()+"Manual_"+self.ar.data.lang['c031_volumeVariation']
        self.limb_vv_attr = self.ar.data.lang['m019_limb'].lower()+"_"+self.ar.data.lang['c031_volumeVariation']
        self.limb_min_vv_attr = self.ar.data.lang['m019_limb'].lower()+"Min_"+self.ar.data.lang['c031_volumeVariation']
        self.limb_length_attr = self.ar.data.lang['c113_length']
        self.to_ids = []

        corner_name = self.ar.data.lang['c007_leg_corner']
        if arm:
            corner_name = self.ar.data.lang['c002_arm_corner']
        artic_number = 1
        if add_artic:
            artic_number = 2
        
        if not ori_loc:
            ori_loc = cmds.ls(sl=True, l=True)[0]
        if not ini_jnt:
            ini_jnt = cmds.ls(sl=True)[1]
        
        if not prefix == '':
            if not prefix.endswith('_'):
                prefix+='_'
        skipa = ['x', 'y', 'z']
        skipa.remove(skip_axis)
        lista = []
        lista.append(ini_jnt)
        lista.append(cmds.listRelatives(lista[0], c=True)[0])
        lista.append(cmds.listRelatives(lista[1], c=True)[0])
        aux_loc = cmds.duplicate(ori_loc, rr=True)
        mid_loc = cmds.duplicate(ori_loc, rr=True)

        cmds.matchTransform(aux_loc, lista[1], position=True, rotation=True)
        cmds.delete(cmds.aimConstraint(lista[2], aux_loc, mo=False, weight=2, aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpType="vector", worldUpVector=(0, 1, 0)))
        cmds.delete(cmds.orientConstraint(ori_loc, aux_loc, mo=False, skip=skipa, weight=1))

        cmds.matchTransform(mid_loc, lista[1], position=True, rotation=True)

        cmds.delete(cmds.orientConstraint(ori_loc, mid_loc, mo=False, skip=skipa, weight=1))
        
        up_ctrls = self.create_bend_ctrl(prefix+name+'_Up_Offset_Ctrl', r=self.radius)
        up_zero = up_ctrls[0]
        up_ctrl = up_ctrls[1]
        down_ctrls = self.create_bend_ctrl(prefix+name+'_Down_Offset_Ctrl', r=self.radius)
        down_zero = down_ctrls[0]
        down_ctrl = down_ctrls[1]
        elbow_ctrls = self.create_elbow_ctrl(prefix+name+'_'+corner_name+'_Offset_Ctrl', arm_style=arm)
        elbow_grp = elbow_ctrls[0]
        self.elbow_ctrl = elbow_ctrls[1]
        self.elbow_zero_0 = elbow_ctrls[2]
        self.elbow_zero_1 = elbow_ctrls[3]
        
        attr_value = 0.25
        if arm:
            attr_value = 0.75
        cmds.addAttr(up_ctrl, longName="autoTwistBone", attributeType='float', min=0, defaultValue=attr_value, max=1, keyable=True)
        cmds.addAttr(up_ctrl, longName="baseTwist", attributeType='float', keyable=True)
        cmds.addAttr(up_ctrl, longName="autoRotate", attributeType='float', min=0, defaultValue=0.5, max=1, keyable=True)
        cmds.addAttr(up_ctrl, longName="invert", attributeType='bool', defaultValue=0, keyable=False)
        cmds.addAttr(down_ctrl, longName="autoRotate", attributeType='float', min=0, defaultValue=0.5, max=1, keyable=True)
        cmds.addAttr(down_ctrl, longName="invert", attributeType='bool', defaultValue=0, keyable=False)
        
        if ori_b_loc:
            lista.append(cmds.listRelatives(lista[2], c=True)[0])
            aux_b_loc = cmds.duplicate(ori_b_loc, rr=True)
            mid_b_loc = cmds.duplicate(ori_b_loc, rr=True)
            cmds.matchTransform(aux_b_loc, lista[2], position=True, rotation=True)
            cmds.delete(cmds.aimConstraint(lista[3], aux_b_loc, mo=False, weight=2, aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpType="vector", worldUpVector=(0, 1, 0)))
            cmds.delete(cmds.orientConstraint(ori_b_loc, aux_b_loc, mo=False, skip=skipa, weight=1))
            cmds.matchTransform(mid_b_loc, lista[2], position=True, rotation=True)
            cmds.delete(cmds.orientConstraint(ori_b_loc, mid_b_loc, mo=False, skip=skipa, weight=1))
            down_b_ctrls = self.create_bend_ctrl(prefix+name+'_DownB_Offset_Ctrl', r=self.radius)
            down_b_zero = down_b_ctrls[0]
            down_b_ctrl = down_b_ctrls[1]
            elbow_b_ctrls = self.create_elbow_ctrl(prefix+name+'_'+corner_name+'B_Offset_Ctrl', arm_style=arm)
            elbow_b_grp = elbow_b_ctrls[0]
            self.elbow_b_ctrl = elbow_b_ctrls[1]
            self.elbow_b_zero_0 = elbow_b_ctrls[2]
            self.elbow_b_zero_1 = elbow_b_ctrls[3]
            cmds.addAttr(down_b_ctrl, longName="autoRotate", attributeType='float', min=0, defaultValue=0.5, max=1, keyable=True)
            cmds.addAttr(down_b_ctrl, longName="invert", attributeType='bool', defaultValue=0, keyable=False)

        if add_artic:
            # corner joint
            self.corner_jxt, self.corner_jnt = self.create_corner_joint(prefix, name, "Corner", self.elbow_ctrl)
            if ori_b_loc:
                self.corner_b_jxt, self.corner_b_jnt = self.create_corner_joint(prefix, name, "CornerB", self.elbow_b_ctrl)
            if not arm:
                cmds.setAttr(self.corner_jnt+".rotateX", 180)
                cmds.setAttr(self.corner_jnt+".rotateZ", 90)
                if ori_b_loc:
                    cmds.setAttr(self.corner_b_jnt+".rotateX", 180)
                    cmds.setAttr(self.corner_b_jnt+".rotateZ", 90)
            if side == 1:
                if arm:
                    cmds.setAttr(self.corner_jnt+".rotateX", 180)
                    cmds.setAttr(self.corner_jnt+".scaleX", -1)
                else:
                    cmds.setAttr(self.corner_jnt+".rotateX", 0)
                    cmds.setAttr(self.corner_jnt+".rotateZ", -90)
                    if ori_b_loc:
                        cmds.setAttr(self.corner_b_jnt+".rotateX", 0)
                        cmds.setAttr(self.corner_b_jnt+".rotateZ", -90)
            if add_correct:
                self.add_corrective_joint(jcr_number, self.corner_jnt, jcr_pos, jcr_rot)
                if ori_b_loc:
                    self.add_corrective_joint(jcr_number, self.corner_b_jnt, jcr_pos, jcr_rot)
        
        if arm:
            up_limb = self.create_ribbon(name=prefix+name+'_Up', axis=(0, 0, -1), horizontal=True, num_joints=num, v=False, guides=[lista[0], lista[1]], s=side, up_ctrl=up_ctrl, world_ref=world_ref, joint_label_add=joint_label_add, joint_label_name='Up_'+name, center_up_down=1, add_artic=add_artic, additional_joint=additional, limbArm=arm)
            down_limb = self.create_ribbon(name=prefix+name+'_Down', axis=(0, 0, -1), horizontal=True, num_joints=num, ini_jxt=ini_jxt, v=False, guides=[lista[1], lista[2]], s=side, world_ref=world_ref, joint_label_add=joint_label_add, joint_label_name='Down_'+name, center_up_down=2, add_artic=add_artic, additional_joint=additional, limbArm=arm)
            cmds.connectAttr(up_ctrl+".scaleX", up_limb['extraCtrlGrp']+".scaleX", force=True)
            cmds.connectAttr(up_ctrl+".scaleY", up_limb['extraCtrlGrp']+".scaleY", force=True)
            cmds.connectAttr(down_ctrl+".scaleX", down_limb['extraCtrlGrp']+".scaleX", force=True)
            cmds.connectAttr(down_ctrl+".scaleY", down_limb['extraCtrlGrp']+".scaleY", force=True)
        else:
            up_limb = self.create_ribbon(name=prefix+name+'_Up', axis=(0, 0, 1), horizontal=True, num_joints=num, v=False, guides=[lista[0], lista[1]], s=side, up_ctrl=up_ctrl, world_ref=world_ref, joint_label_add=joint_label_add, joint_label_name='Up_'+name, center_up_down=1, add_artic=add_artic, additional_joint=additional, limbArm=arm)
            down_limb = self.create_ribbon(name=prefix+name+'_Down', axis=(0, 0, 1), horizontal=True, num_joints=num, v=False, guides=[lista[1], lista[2]], s=side, world_ref=world_ref, joint_label_add=joint_label_add, joint_label_name='Down_'+name, center_up_down=2, add_artic=add_artic, additional_joint=additional, limbArm=arm)
            cmds.connectAttr(up_ctrl+".scaleX", up_limb['extraCtrlGrp']+".scaleY", force=True)
            cmds.connectAttr(up_ctrl+".scaleY", up_limb['extraCtrlGrp']+".scaleX", force=True)
            cmds.connectAttr(down_ctrl+".scaleX", down_limb['extraCtrlGrp']+".scaleY", force=True)
            cmds.connectAttr(down_ctrl+".scaleY", down_limb['extraCtrlGrp']+".scaleX", force=True)
            if ori_b_loc:
                down_b_limb = self.create_ribbon(name=prefix+name+'_DownB', axis=(0, 0, 1), horizontal=True, num_joints=num, v=False, guides=[lista[2], lista[3]], s=side, world_ref=world_ref, joint_label_add=joint_label_add, joint_label_name='DownB_'+name, center_up_down=2, add_artic=add_artic, additional_joint=additional, limbArm=arm, ori_b_loc=ori_b_loc)
                cmds.connectAttr(down_b_ctrl+".scaleZ", down_b_limb['extraCtrlGrp']+".scaleZ", force=True)
        cmds.connectAttr(up_ctrl+".scaleZ", up_limb['extraCtrlGrp']+".scaleZ", force=True)
        cmds.connectAttr(down_ctrl+".scaleZ", down_limb['extraCtrlGrp']+".scaleZ", force=True)
        
        # parentTag
        cmds.connectAttr(up_ctrl+".message", up_limb['extraCtrlList'][0]+".parentTag", force=True)
        cmds.connectAttr(down_ctrl+".message", down_limb['extraCtrlList'][0]+".parentTag", force=True)

        cmds.matchTransform(up_zero, ori_loc, position=True, rotation=True)
        cmds.delete(cmds.pointConstraint(up_limb['middleCtrl'], up_zero, mo=False, w=1))
        
        cmds.matchTransform(down_zero, aux_loc, position=True, rotation=True)
        cmds.delete(cmds.pointConstraint(down_limb['middleCtrl'], down_zero, mo=False, w=1))
        if ori_b_loc:
            cmds.matchTransform(down_b_zero, aux_b_loc, position=True, rotation=True)
            cmds.delete(cmds.pointConstraint(down_b_limb['middleCtrl'], down_b_zero, mo=False, w=1))

        cmds.matchTransform(elbow_grp, mid_loc, position=True, rotation=True)
        orc = cmds.orientConstraint(lista[0], lista[1], elbow_grp, mo=False, w=1, name=elbow_grp+"_OrC")[0]
        cmds.setAttr(orc+".interpType", 2)
        if ori_b_loc:
            cmds.matchTransform(elbow_b_grp, mid_b_loc, position=True, rotation=True)
            orc_b = cmds.orientConstraint(lista[1], lista[2], elbow_b_grp, mo=False, w=1, name=elbow_b_grp+"_OrC")[0]
            cmds.setAttr(orc_b+".interpType", 2)

        cmds.delete(up_limb['constraints'][1])
        cmds.parentConstraint(self.elbow_ctrl, up_limb['locsList'][0], mo=True, w=1, name=up_limb['locsList'][0]+"_PaC")
        cmds.delete(up_limb['constraints'][3])
        cmds.pointConstraint(self.elbow_ctrl, up_limb['locsList'][3], mo=True, w=1, name=up_limb['locsList'][3]+"_PoC")
        
        cmds.delete(down_limb['constraints'][0])
        cmds.parentConstraint(self.elbow_ctrl, down_limb['locsList'][2], mo=True, w=1, name=down_limb['locsList'][2]+"_PaC")
        cmds.delete(down_limb['constraints'][2])
        cmds.pointConstraint(self.elbow_ctrl, down_limb['locsList'][4], mo=True, w=1, name=down_limb['locsList'][4]+"_PoC")
        if ori_b_loc:
            cmds.delete(down_limb['constraints'][1])
            cmds.parentConstraint(self.elbow_b_ctrl, down_limb['locsList'][0], mo=True, w=1, name=down_limb['locsList'][2]+"_2_PaC")
            cmds.delete(down_limb['constraints'][3])
            cmds.pointConstraint(self.elbow_b_ctrl, down_limb['locsList'][3], mo=True, w=1, name=down_limb['locsList'][4]+"_2_PoC")
            
            cmds.delete(down_b_limb['constraints'][0])
            cmds.parentConstraint(self.elbow_b_ctrl, down_b_limb['locsList'][2], mo=True, w=1, name=down_b_limb['locsList'][2]+"_PaC")
            cmds.delete(down_b_limb['constraints'][2])
            cmds.pointConstraint(self.elbow_b_ctrl, down_b_limb['locsList'][4], mo=True, w=1, name=down_b_limb['locsList'][4]+"_PoC")

            down_b_pac = cmds.parentConstraint(cmds.listRelatives(down_b_limb['middleCtrl'], p=True)[0], self.elbow_b_ctrl, down_b_zero, mo=True, w=1, skipRotate=['x', 'y', 'z'], name=down_b_zero+"_PaC")[0]
            cmds.orientConstraint(cmds.listRelatives(down_b_limb['middleCtrl'], p=True)[0], down_b_zero, mo=True, w=1, name=down_b_zero+"_OrC")
            cmds.setAttr(down_b_pac+'.interpType', 2)
            cmds.connectAttr(self.elbow_b_ctrl+'.autoBend', down_b_pac+'.'+self.elbow_b_ctrl+'W1', force=True)
            cmds.parentConstraint(cmds.listRelatives(down_b_zero, c=True)[0], down_b_limb['middleCtrl'], mo=True, w=1, name=down_b_limb['middleCtrl']+"_PaC")
            cmds.pointConstraint(lista[2], elbow_b_grp, mo=True, w=1, name=elbow_b_grp+"_PoC")
        
        up_pac = cmds.parentConstraint(cmds.listRelatives(up_limb['middleCtrl'], p=True)[0], self.elbow_ctrl, up_zero, mo=True, w=1, skipRotate=['x', 'y', 'z'], name=up_zero+"_PaC")[0]
        cmds.orientConstraint(cmds.listRelatives(up_limb['middleCtrl'], p=True)[0], up_zero, mo=True, w=1, name=up_zero+"_OrC")
        cmds.setAttr(up_pac+'.interpType', 2)
        cmds.connectAttr(self.elbow_ctrl+'.autoBend', up_pac+'.'+self.elbow_ctrl+'W1', force=True)
        cmds.parentConstraint(cmds.listRelatives(up_zero, c=True)[0], up_limb['middleCtrl'], mo=True, w=1, name=up_limb['middleCtrl']+"_PaC")
        
        down_pac = cmds.parentConstraint(cmds.listRelatives(down_limb['middleCtrl'], p=True)[0], self.elbow_ctrl, down_zero, mo=True, w=1, skipRotate=['x', 'y', 'z'], name=down_zero+"_PaC")[0]
        cmds.orientConstraint(cmds.listRelatives(down_limb['middleCtrl'], p=True)[0], down_zero, mo=True, w=1, name=down_zero+"_OrC")
        cmds.setAttr(down_pac+'.interpType', 2)
        cmds.connectAttr(self.elbow_ctrl+'.autoBend', down_pac+'.'+self.elbow_ctrl+'W1', force=True)
        cmds.parentConstraint(cmds.listRelatives(down_zero, c=True)[0], down_limb['middleCtrl'], mo=True, w=1, name=down_limb['middleCtrl']+"_PaC")
        
        cmds.pointConstraint(lista[1], elbow_grp, mo=True, w=1, name=elbow_grp+"_PoC")
        
        up_jnt_grp = cmds.listRelatives(up_limb['skinJointsList'][0], p=True, f=True)
        down_jnt_grp = cmds.listRelatives(down_limb['skinJointsList'][0], p=True, f=True)
        if ori_b_loc:
            down_b_jnt_grp = cmds.listRelatives(down_b_limb['skinJointsList'][0], p=True, f=True)
        
        limb_joints = list(up_limb['skinJointsList'])
        if add_artic:
            limb_joints.extend([self.corner_jxt])
        limb_joints.extend(down_limb['skinJointsList'])
        if ori_b_loc:
            if add_artic:
                limb_joints.extend([self.corner_b_jxt])
            limb_joints.extend(down_b_limb['skinJointsList'])
        
        jnt_grp = cmds.group(limb_joints, n=prefix+name+'_Jnts_Grp')
        #Deactivate the segment scale compensate on the bone to prevent scaling problem.
        #It will prevent a double scale problem that will come from the upper parent in the rig
        for n_bone in limb_joints:
            cmds.setAttr(n_bone+".segmentScaleCompensate", 0)
        
        # fix renaming:
        if add_artic:
            limb_joints.pop(len(up_limb['skinJointsList']))
            limb_joints.insert(len(up_limb['skinJointsList']), self.corner_jnt)
            if ori_b_loc:
                limb_joints.pop(len(up_limb['skinJointsList'])+len(down_limb['skinJointsList'])+1)
                limb_joints.insert(len(up_limb['skinJointsList'])+len(down_limb['skinJointsList'])+1, self.corner_b_jnt)
        for i in range(len(limb_joints)):
            old_name = limb_joints[i][:-4]
            limb_joints[i] = cmds.rename(limb_joints[i], prefix+name+'_%02d_Jnt'%(i+artic_number)) #because 00 is the clavicle and 01 is the shoulder if we have articulation joint
            if not self.ar.data.lang['c043_corner'] in old_name:
                for child in cmds.listRelatives(limb_joints[i], allDescendents=True) or []:
                    if old_name in child:
                        cmds.rename(child, child.replace(old_name, prefix+name+'_%02d'%(i+artic_number)))
        
        scale_grp = cmds.group(up_limb['scaleGrp'], down_limb['scaleGrp'], jnt_grp, n=prefix+name+'_Ribbon_Scale_Grp')
        cmds.setAttr(up_limb['scaleGrp']+'.v', cmds.getAttr(up_limb['finalGrp']+'.v'))
        cmds.setAttr(down_limb['scaleGrp']+'.v', cmds.getAttr(down_limb['finalGrp']+'.v'))
        
        cmds.delete(up_jnt_grp, down_jnt_grp)
        
        static_grp = cmds.group(up_limb['finalGrp'], down_limb['finalGrp'], n=prefix+name+'_Ribbon_Static_Grp')
        
        ctrls_grp = cmds.group(up_zero, down_zero, elbow_grp, up_limb['extraCtrlGrp'], down_limb['extraCtrlGrp'], n=prefix+name+'_Ctrls_Grp')
        
        cmds.delete(mid_loc, aux_loc)
        if ori_b_loc:
            cmds.parent(down_b_limb['scaleGrp'], scale_grp)
            cmds.setAttr(down_b_limb['scaleGrp']+'.v', cmds.getAttr(down_b_limb['finalGrp']+'.v'))
            cmds.delete(down_b_jnt_grp)
            cmds.parent(down_b_limb['finalGrp'], static_grp)
            cmds.parent(down_b_zero, elbow_b_grp, down_b_limb['extraCtrlGrp'], ctrls_grp)
            cmds.delete(mid_b_loc, aux_b_loc)
        
        # organizing joint nomenclature ('_Jnt', '_Jxt') and skin attributes (".dpAR_joint")
        # in order to quickly skin using dpAR_UI
        for item in lista[:-1]:
            #fix joint name suffix
            if '_Jnt' in item:
                # remove dpAR skin attribute
                try:
                    self.ar.utils.clearDpArAttr([item])
                except:
                    pass
                # rename joint
                cmds.rename(item, item.replace('_Jnt', '_Jxt'))
        
        if ini_jxt: #arm elbow
            if cmds.objExists(ini_jxt):
                pac = cmds.parentConstraint(ini_jxt, down_limb['bendGrpList'][0], mo=True, name=down_limb['bendGrpList'][0]+"_PaC")[0]
                cmds.setAttr(pac+".interpType", 2) #shortest
                cmds.setAttr(pac+"."+ini_jxt+"W1", 0.3)

        # corner autoRotate setup
        loaded_quaternion_plugin = self.ar.utils.checkLoadedPlugin("quatNodes", self.ar.data.lang['e014_cantLoadQuatNode'])
        loaded_matrix_plugin = self.ar.utils.checkLoadedPlugin("matrixNodes", self.ar.data.lang['e002_matrixPluginNotFound'])
        if loaded_quaternion_plugin and loaded_matrix_plugin:
            corner_auto_rotate_md = cmds.createNode("multiplyDivide", name=prefix+name+"_"+corner_name+"_AutoRotate_MD")
            corner_auto_rotate_mm = cmds.createNode("multMatrix", name=prefix+name+"_"+corner_name+"_AutoRotate_MM")
            corner_auto_rotate_dm = cmds.createNode("decomposeMatrix", name=prefix+name+"_"+corner_name+"_AutoRotate_DM")
            corner_auto_rotate_qte = cmds.createNode("quatToEuler", name=prefix+name+"_"+corner_name+"_AutoRotate_QtE")
            corner_auto_rotate_rev = cmds.createNode("reverse", name=prefix+name+"_"+corner_name+"_AutoRotate_Rev")
            corner_auto_rotate_inv_pin_md = cmds.createNode("multiplyDivide", name=corner_auto_rotate_md.replace("MD", "Pin_Inv_MD"))
            corner_auto_rotate_inv_mid_md = cmds.createNode("multiplyDivide", name=corner_auto_rotate_md.replace("MD", "Mid_Inv_MD"))
            self.to_ids.extend([corner_auto_rotate_md, corner_auto_rotate_mm, corner_auto_rotate_dm, corner_auto_rotate_qte, corner_auto_rotate_rev, corner_auto_rotate_inv_pin_md, corner_auto_rotate_inv_mid_md])
            idx = 2
            if ori_b_loc:
                idx = 3
            extreme_loc = cmds.spaceLocator(name=lista[idx].replace("Jnt", "AutoRotate_Loc"))[0]
            cmds.matchTransform(extreme_loc, lista[idx], position=True, rotation=True)
            corner_auto_rot_grp = cmds.group(extreme_loc, name=extreme_loc+"_Grp")
            extreme_orig_loc = cmds.duplicate(extreme_loc, name=lista[2].replace("Jnt", "AutoRotate_Orig_Loc"))[0]
            for axis in self.ar.data.axes:
                cmds.connectAttr(lista[idx]+".rotate"+axis, extreme_loc+".rotate"+axis, force=True)
                cmds.setAttr(extreme_orig_loc+".rotate"+axis, cmds.getAttr(extreme_loc+".rotate"+axis))
            cmds.setAttr(corner_auto_rot_grp+".inheritsTransform", 0)
            cmds.setAttr(corner_auto_rot_grp+".visibility", 0)
            cmds.parent(corner_auto_rot_grp, static_grp)
            cmds.connectAttr(self.elbow_ctrl+".autoRotate", corner_auto_rotate_md+".input1Z", force=True)
            cmds.connectAttr(self.elbow_ctrl+".autoRotate", corner_auto_rotate_rev+".inputZ", force=True)
            cmds.connectAttr(extreme_orig_loc+".worldInverseMatrix[0]", corner_auto_rotate_mm+".matrixIn[0]", force=True)
            cmds.connectAttr(extreme_loc+".worldMatrix[0]", corner_auto_rotate_mm+".matrixIn[1]", force=True)
            cmds.connectAttr(corner_auto_rotate_mm+".matrixSum", corner_auto_rotate_dm+".inputMatrix", force=True)
            cmds.connectAttr(corner_auto_rotate_dm+".outputQuatX", corner_auto_rotate_qte+".inputQuatX", force=True)
            cmds.connectAttr(corner_auto_rotate_dm+".outputQuatY", corner_auto_rotate_qte+".inputQuatY", force=True)
            cmds.connectAttr(corner_auto_rotate_dm+".outputQuatZ", corner_auto_rotate_qte+".inputQuatZ", force=True)
            cmds.connectAttr(corner_auto_rotate_dm+".outputQuatW", corner_auto_rotate_qte+".inputQuatW", force=True)
            cmds.connectAttr(corner_auto_rotate_md+".outputZ", corner_auto_rotate_inv_pin_md+".input1Z", force=True)
            cmds.connectAttr(corner_auto_rotate_rev+".outputZ", corner_auto_rotate_inv_mid_md+".input1Z", force=True)
            cmds.connectAttr(corner_auto_rotate_qte+".outputRotateZ", corner_auto_rotate_md+".input2Z", force=True)
            if arm:
                cmds.connectAttr(corner_auto_rotate_inv_pin_md+".outputZ", self.elbow_zero_0+".rotateX", force=True)
            else: #leg
                cmds.connectAttr(corner_auto_rotate_inv_pin_md+".outputZ", self.elbow_zero_0+".rotateY", force=True)

        # implementing pin setup to ribbon corner offset control:
        if elbow_ctrls[2]:
            self.pin_corner_setup(world_ref, elbow_grp, self.elbow_ctrl, self.elbow_zero_1, corner_auto_rotate_inv_pin_md)
        if ori_b_loc:
            if elbow_b_ctrls[2]:
                self.pin_corner_setup(world_ref, elbow_b_grp, self.elbow_b_ctrl, self.elbow_b_zero_1, corner_auto_rotate_inv_pin_md)
        
        # autoRotate by twistBone control setup:
        if up_limb['up_twist_bone_md']:
            cmds.connectAttr(up_ctrl+".autoRotate", up_limb['up_twist_bone_md']+".input1Z", force=True)
            cmds.connectAttr(up_ctrl+".invert", up_limb['twist_bone_cnd']+".firstTerm", force=True)
        if up_limb['bottom_twist_bone_md']:
            cmds.connectAttr(up_ctrl+".autoRotate", up_limb['bottom_twist_bone_md']+".input1Z", force=True)
        if down_limb['up_twist_bone_md']:
            cmds.connectAttr(down_ctrl+".autoRotate", down_limb['up_twist_bone_md']+".input1Z", force=True)
            cmds.connectAttr(down_ctrl+".invert", down_limb['twist_bone_cnd']+".firstTerm", force=True)
        if down_limb['bottom_twist_bone_md']:
            cmds.connectAttr(down_ctrl+".autoRotate", down_limb['bottom_twist_bone_md']+".input1Z", force=True)
            cmds.connectAttr(corner_auto_rotate_inv_mid_md+".outputZ", down_limb['twist_auto_rot_md']+".input2X", force=True)
        if ori_b_loc:
            if down_b_limb['up_twist_bone_md']:
                cmds.connectAttr(down_b_ctrl+".autoRotate", down_b_limb['up_twist_bone_md']+".input1Z", force=True)
                cmds.connectAttr(down_b_ctrl+".invert", down_b_limb['twist_bone_cnd']+".firstTerm", force=True)
            if down_b_limb['bottom_twist_bone_md']:
                cmds.connectAttr(down_b_ctrl+".autoRotate", down_b_limb['bottom_twist_bone_md']+".input1Z", force=True)
                cmds.connectAttr(corner_auto_rotate_inv_mid_md+".outputZ", down_b_limb['twist_auto_rot_md']+".input2X", force=True)

        self.ar.utils.addCustomAttr([scale_grp, ], self.ar.utils.ignoreTransformIOAttr)
        self.ar.custom_attr.add_attr(0, self.to_ids) #dpID

        # result lists to return them:
        extra_ctrls = up_limb['extraCtrlList']
        extra_ctrls.extend(down_limb['extraCtrlList'])
        result_bend_grps = [up_zero, down_zero]
        result_ctrls = [up_ctrl, down_ctrl, self.elbow_ctrl]
        result_extra_bend_grps = [up_limb['extraCtrlGrp'], down_limb['extraCtrlGrp']]
        result_rot_extreme = down_limb['locsList'][3]
        if ori_b_loc:
            extra_ctrls.extend(down_b_limb['extraCtrlList'])
            result_bend_grps.append(down_b_zero)
            result_ctrls.extend([down_b_ctrl, self.elbow_b_ctrl])
            result_extra_bend_grps.append(down_b_limb['extraCtrlGrp'])
            result_rot_extreme = down_b_limb['locsList'][3]
        
        return {'scaleGrp'      : scale_grp,
                'staticGrp'     : static_grp,
                'ctrlsGrp'      : ctrls_grp,
                'bendGrpList'   : result_bend_grps,
                'controllers'   : result_ctrls,
                'extraBendGrp'  : result_extra_bend_grps,
                'extraCtrlList' : extra_ctrls,
                'twistBoneMD'   : up_limb['twistBoneMD'],
                'jntGrp'        : jnt_grp,
                'rotFirst'      : up_limb['locsList'][4],
                'rotExtrem'     : result_rot_extreme,
                'bottomPosPaC'  : [up_limb['locsList'][2], up_limb['constraints'][0]]
                }
    
    
    def create_bend_ctrl(self, name='Bend_Ctrl', r=1, zero=True):
        """ Create the Ribbon Bend control.
            Returns the group zeroOut and the control curve.
        """
        grp = None
        curve = self.ar.ctrls.create_controller("id_038_RibbonBend", name, r=self.radius, d=self.curve_degree, rot=(0, 90, 0), guide_source=self.limb_instance.guide_base)
        self.ar.ctrls.set_lock_hide([curve], ['v'])
        if zero:
            grp = cmds.group(curve, n=name+'_Grp')
            self.ar.utils.addCustomAttr([grp], self.ar.utils.ignoreTransformIOAttr)
        return [grp, curve]
    
    
    def create_elbow_ctrl(self, name='Limb_Ctrl', zero=True, arm_style=True):
        """ Create the Ribbon Corner (Elbow) control.
            Returns the group, the control curve and its zeroOut group.
        """
        if arm_style:
            curve = self.ar.ctrls.create_controller("id_039_RibbonCorner", name, r=self.radius, d=self.curve_degree, rot=(0, 90, 0), guide_source=self.limb_instance.name_guide+"_Corner")
        else:
            curve = self.ar.ctrls.create_controller("id_039_RibbonCorner", name, r=self.radius, d=self.curve_degree, rot=(90, 0, 0), guide_source=self.limb_instance.name_guide+"_Corner")
        grp = None
        if zero:
            zero0 = cmds.group(curve, name=name+'_Zero_0_Grp')
            zero1 = cmds.group(zero0, name=name+'_Zero_1_Grp')
            grp = cmds.group(zero1, name=name+'_Grp')
            if arm_style:
                cmds.rotate(0, -90, -90, zero1)
            else:
                cmds.rotate(-90, 0, -90, zero1)
            self.ar.utils.addCustomAttr([zero1, grp], self.ar.utils.ignoreTransformIOAttr)
        cmds.addAttr(curve, longName='autoBend', attributeType='float', minValue=0, maxValue=1, defaultValue=0, keyable=True)
        if arm_style:
            cmds.addAttr(curve, longName='autoRotate', attributeType='float', minValue=0, maxValue=1, defaultValue=0.2, keyable=True)
        else:
            cmds.addAttr(curve, longName='autoRotate', attributeType='float', minValue=0, maxValue=1, defaultValue=0, keyable=True)
        cmds.addAttr(curve, longName='pin', attributeType='float', minValue=0, maxValue=1, defaultValue=0, keyable=True)
        self.ar.ctrls.set_lock_hide([curve], ['v'])
        return [grp, curve, zero0, zero1]
    
    
    def create_ribbon(self, axis=(0, 0, 1), name='RibbonSetup', horizontal=False, num_joints=3, guides=None, ini_jxt=None, v=True, s=0, up_ctrl=None, world_ref="worldRef", joint_label_add=0, joint_label_name="RibbonName", center_up_down=0, add_artic=True, additional_joint=False, limbArm=True, ori_b_loc=None):
        """ Main method to create the Ribbon system.
            center_up_down = [0, 1, 2] # center, up, down ribbon part to change proportions used in volumeVariation.
            Returns results in a dictionary.
        """
        result_data = {}
        
        #define variables
        top_Loc = []
        mid_Loc = []
        bttm_Loc = []
        rb_Jnt = []
        drv_Jnt =[]
        fols = []
        aux_Jnt = []
        ribbon = ''
        extra_ctrls = []
        
        #create a nurbsPlane based in the choose orientation option
        if horizontal:
            ribbon = cmds.nurbsPlane(ax=axis, w=num_joints, lr=(1/float(num_joints)), d=3, u=num_joints, v=1, ch=0, name=name+'_Plane')[0]
            cmds.rebuildSurface(ribbon, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kc=0, sv=1, du=3, dv=1, tol=0.01, fr=0, dir=1) 
        else:
            ribbon = cmds.nurbsPlane(ax=axis, w=1, lr=num_joints, d=3, u=1, v=num_joints, ch=0, name=name+'_Plane')[0]
            cmds.rebuildSurface(ribbon, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kc=0, su=1, du=1, dv=3, tol=0.01, fr=0, dir=0) 
        # make this ribbonNurbsPlane as not skinable from dpAR_UI:
        self.ar.utils.addCustomAttr([ribbon], self.ar.skin.ignoreSkinningAttr)
        #call the function to create follicles and joint in the nurbsPlane
        results = self.create_follicles(rib=ribbon, num=num_joints, name=name, horizontal=horizontal, side=s, joint_label_add=joint_label_add, joint_label_name=joint_label_name)
        rb_Jnt = results[0]
        fols = results[1]
        #create locator controls for the middle of the ribbon
        mid_Loc.append(cmds.spaceLocator(name=name+'_Mid_Pos_Loc')[0])
        mid_Loc.append(cmds.spaceLocator(name=name+'_Mid_Aim_Loc')[0])
        mid_Loc.append(cmds.spaceLocator(name=name+'_Mid_Off_Loc')[0])
        mid_Loc.append(cmds.spaceLocator(name=name+'_Mid_Up_Loc')[0])
        #parent correctly the middle locators
        cmds.parent(mid_Loc[2], mid_Loc[1], relative=True)
        cmds.parent(mid_Loc[1], mid_Loc[0], relative=True)
        cmds.parent(mid_Loc[3], mid_Loc[0], relative=True)
        #create the locators controls for the top of the ribbon
        top_Loc.append(cmds.spaceLocator(name=name+'_Top_Pos_Loc')[0])
        top_Loc.append(cmds.spaceLocator(name=name+'_Top_Aim_Loc')[0])
        top_Loc.append(cmds.spaceLocator(name=name+'_Top_Up_Loc')[0])
        top_Loc.append(cmds.spaceLocator(name=name+'_Top_Rot0_Loc')[0])
        #parent correctly the top locators
        cmds.parent(top_Loc[1], top_Loc[0], relative=True)
        cmds.parent(top_Loc[2], top_Loc[0], relative=True)
        cmds.parent(top_Loc[3], top_Loc[0], relative=True)
        #create the locators for the end of the ribbon
        bttm_Loc.append(cmds.spaceLocator(name=name+'_Bottom_Pos_Loc')[0])
        bttm_Loc.append(cmds.spaceLocator(name=name+'_Bottom_Aim_Loc')[0])
        bttm_Loc.append(cmds.spaceLocator(name=name+'_Bottom_Up_Loc')[0])
        bttm_Loc.append(cmds.spaceLocator(name=name+'_Bottom_Rot0_Loc')[0])
        #parent correctly the bottom locators
        cmds.parent(bttm_Loc[1], bttm_Loc[0], relative=True)
        cmds.parent(bttm_Loc[2], bttm_Loc[0], relative=True)
        cmds.parent(bttm_Loc[3], bttm_Loc[0], relative=True)
        
        #put the top locators in the same place of the top joint
        cmds.parent(top_Loc[0], fols[len(fols)-1], relative=True)
        cmds.parent(top_Loc[0], world=True)
        
        #put the bottom locators in the same place of the bottom joint
        cmds.parent(bttm_Loc[0], fols[0], relative=True)
        cmds.parent(bttm_Loc[0], world=True)
        cmds.select(clear=True)
        
        #create the joints that will be used to control the ribbon
        drv_Jnt = cmds.duplicate([rb_Jnt[0], rb_Jnt[int((len(rb_Jnt)-1)//2)], rb_Jnt[int(len(rb_Jnt)-1)]])
        dup = cmds.duplicate([drv_Jnt[0], drv_Jnt[2]])
        drv_Jnt.append(dup[0])
        drv_Jnt.append(dup[1])
        #cmds.parent(drv_Jnt, w=True)
        for jnt in drv_Jnt:
            cmds.joint(jnt, e=True, oj='none', ch=True, zso=True);
            cmds.setAttr(jnt+'.radius', cmds.getAttr(jnt+'.radius')+0.5)
        #rename created joints
        drv_Jnt[0] = cmds.rename(drv_Jnt[0], name+'_Drv_Bottom_Jxt')
        drv_Jnt[1] = cmds.rename(drv_Jnt[1], name+'_Drv_Mid_Jxt')
        drv_Jnt[2] = cmds.rename(drv_Jnt[2], name+'_Drv_Top_Jxt')
        drv_Jnt[3] = cmds.rename(drv_Jnt[3], name+'_Drv_Bottom_'+self.ar.data.joint_end_attr)
        drv_Jnt[4] = cmds.rename(drv_Jnt[4], name+'_Drv_Top_'+self.ar.data.joint_end_attr)
        
        #place joints correctly accordaly with the user options choose
        if (horizontal and axis==(1, 0, 0)) or (horizontal and axis==(0, 0, 1)):
            cmds.setAttr(bttm_Loc[2]+'.translateY', 2)
            cmds.setAttr(top_Loc[2]+'.translateY', 2)
            cmds.setAttr(mid_Loc[3]+'.translateY', 2)
        elif (horizontal and axis==(0, 1, 0)) or (not horizontal and axis==(1, 0, 0)):
            cmds.setAttr(bttm_Loc[2]+'.translateZ', 2)
            cmds.setAttr(top_Loc[2]+'.translateZ', 2)
            cmds.setAttr(mid_Loc[3]+'.translateZ', 2)
        elif not horizontal and axis==(0, 1, 0) or (not horizontal and axis==(0, 0, 1)):
            cmds.setAttr(bttm_Loc[2]+'.translateX', 2)
            cmds.setAttr(top_Loc[2]+'.translateX', 2)
            cmds.setAttr(mid_Loc[3]+'.translateX', 2)
        elif horizontal and axis==(0, 0, -1):
            cmds.setAttr(bttm_Loc[2]+'.translateX', 2)
            cmds.setAttr(top_Loc[2]+'.translateX', 2)
            cmds.setAttr(mid_Loc[3]+'.translateX', 2)
        
        #create auxiliary joints that will be used to control the ribbon
        aux_Jnt.append(cmds.duplicate(drv_Jnt[1], name=name+'_Rot_Jxt')[0])
        cmds.setAttr(aux_Jnt[0]+'.jointOrient', 0, 0, 0)
        cmds.setAttr(aux_Jnt[0]+'.rotateOrder', 5)
        aux_Jnt.append(cmds.duplicate(aux_Jnt[0], name=name+'_Rot_Extra_Jxt')[0])
        self.ar.utils.addJointEndAttr([drv_Jnt[3], drv_Jnt[4]])
        
        cmds.parent(aux_Jnt[1], mid_Loc[3])
        cmds.setAttr(aux_Jnt[1]+'.translate', 0, 0, 0)
        cmds.parent(aux_Jnt[1], aux_Jnt[0])
        cmds.parent(mid_Loc[3], aux_Jnt[1])
        #calculate the adjust for the new chain position
        dist = float(num_joints)/2.0
        end_dist = (1/float(num_joints))
        cmds.parent(drv_Jnt[3], drv_Jnt[0])
        cmds.parent(drv_Jnt[4], drv_Jnt[2])
        
        #adjust the joints orientation and position based in the options choose from user
        if horizontal and axis==(1, 0, 0):
            cmds.setAttr(drv_Jnt[0]+'.jointOrient', 0, 90, 0)
            cmds.setAttr(drv_Jnt[2]+'.jointOrient', 0, 90, 0)
            
            cmds.setAttr(drv_Jnt[0]+'.tz', -dist)
            cmds.setAttr(drv_Jnt[3]+'.tz', end_dist*dist)
            cmds.setAttr(drv_Jnt[2]+'.tz', dist)
            cmds.setAttr(drv_Jnt[4]+'.tz', -end_dist*dist)
        
        elif horizontal and axis==(0, 1, 0):
            cmds.setAttr(drv_Jnt[0]+'.jointOrient', 0, 0, 0)
            cmds.setAttr(drv_Jnt[2]+'.jointOrient', 0, 0, 0)
            
            cmds.setAttr(drv_Jnt[0]+'.tx', -dist)
            cmds.setAttr(drv_Jnt[3]+'.tx', end_dist*dist)
            cmds.setAttr(drv_Jnt[2]+'.tx', dist)
            cmds.setAttr(drv_Jnt[4]+'.tx', -end_dist*dist)
        
        elif horizontal and axis==(0, 0, 1): #leg
            cmds.setAttr(drv_Jnt[0]+'.jointOrient', 0, 0, 0)
            cmds.setAttr(drv_Jnt[2]+'.jointOrient', 0, 0, 0)
            
            cmds.setAttr(drv_Jnt[0]+'.tx', -dist)
            cmds.setAttr(drv_Jnt[3]+'.tx', end_dist*dist)
            cmds.setAttr(drv_Jnt[2]+'.tx', dist)
            cmds.setAttr(drv_Jnt[4]+'.tx', -end_dist*dist)
        
        elif horizontal and axis==(0, 0, -1): #arm
            cmds.setAttr(drv_Jnt[0]+'.jointOrient', 0, 0, 0)
            cmds.setAttr(drv_Jnt[2]+'.jointOrient', 0, 0, 0)
            
            cmds.setAttr(drv_Jnt[0]+'.tx', -dist)
            cmds.setAttr(drv_Jnt[3]+'.tx', end_dist*dist)
            cmds.setAttr(drv_Jnt[2]+'.tx', dist)
            cmds.setAttr(drv_Jnt[4]+'.tx', -end_dist*dist)
            
        elif not horizontal and axis==(1, 0, 0):
            cmds.setAttr(drv_Jnt[0]+'.jointOrient', 0, 0, -90)
            cmds.setAttr(drv_Jnt[2]+'.jointOrient', 0, 0, -90)
        
            cmds.setAttr(drv_Jnt[0]+'.ty', -dist)
            cmds.setAttr(drv_Jnt[3]+'.ty', end_dist*dist)
            cmds.setAttr(drv_Jnt[2]+'.ty', dist)
            cmds.setAttr(drv_Jnt[4]+'.ty', -end_dist*dist)
            
        elif not horizontal and axis==(0, 1, 0):
            cmds.setAttr(drv_Jnt[0]+'.jointOrient', 0, 90, 0)
            cmds.setAttr(drv_Jnt[2]+'.jointOrient', 0, 90, 0)
        
            cmds.setAttr(drv_Jnt[0]+'.tz', -dist)
            cmds.setAttr(drv_Jnt[3]+'.tz', end_dist*dist)
            cmds.setAttr(drv_Jnt[2]+'.tz', dist)
            cmds.setAttr(drv_Jnt[4]+'.tz', -end_dist*dist)
            
        elif not horizontal and axis==(0, 0, 1):
            cmds.setAttr(drv_Jnt[0]+'.jointOrient', 0, 0, -90)
            cmds.setAttr(drv_Jnt[2]+'.jointOrient', 0, 0, -90)
        
            cmds.setAttr(drv_Jnt[0]+'.ty', -dist)
            cmds.setAttr(drv_Jnt[3]+'.ty', end_dist*dist)
            cmds.setAttr(drv_Jnt[2]+'.ty', dist)
            cmds.setAttr(drv_Jnt[4]+'.ty', -end_dist*dist)
        
        #fix the control locators position and orientation
        cmds.parent(top_Loc[0], drv_Jnt[2])
        cmds.setAttr(top_Loc[0]+'.translate', 0, 0, 0)
        cmds.parent(top_Loc[0], world=True)
        cmds.setAttr(top_Loc[0]+'.rotate', 0, 0, 0)
        
        cmds.parent(bttm_Loc[0], drv_Jnt[0])
        cmds.setAttr(bttm_Loc[0]+'.translate', 0, 0, 0)
        cmds.parent(bttm_Loc[0], world=True)
        cmds.setAttr(bttm_Loc[0]+'.rotate', 0, 0, 0)    
        
        cmds.parent(drv_Jnt[2], top_Loc[1])
        cmds.parent(drv_Jnt[1], mid_Loc[2])
        cmds.parent(drv_Jnt[0], bttm_Loc[1])
        
        cmds.parent(aux_Jnt[0], mid_Loc[0])
        #create a nurbs control in order to be used in the ribbon offset
        mid_ctrl = self.ar.ctrls.create_controller("Circle", name+'_MidCtrl', r=self.radius, d=self.curve_degree, rot=(0, 90, 0), guide_source=self.limb_instance.name_guide+"_Corner")
        self.ar.utils.removeUserDefinedAttr(mid_ctrl, True)
        middle_ctrl = mid_ctrl #TODO: it's very confused yet, sorry... seems mid_ctrl is a father curve of the middle_ctrl
        mid_ctrl = cmds.group(n=mid_ctrl+'_Grp', em=True)
        cmds.matchTransform(mid_ctrl, middle_ctrl, position=True, rotation=True)
        cmds.parent(middle_ctrl, mid_ctrl)
        
        #adjust the relationship between the locators
        cmds.parent(mid_ctrl, mid_Loc[2], r=True)
        cmds.parent(drv_Jnt[1], middle_ctrl)
        cmds.parent([top_Loc[2], mid_Loc[3], bttm_Loc[2]], w=True)
        cmds.makeIdentity(top_Loc[0], apply=True)
        cmds.makeIdentity(mid_Loc[0], apply=True)
        cmds.makeIdentity(bttm_Loc[0], apply=True)
        cmds.parent(top_Loc[2], top_Loc[0])
        cmds.parent(bttm_Loc[2], bttm_Loc[0])
        cmds.parent(mid_Loc[3], aux_Jnt[1]) 
        #create needed constraints in the locators in order to set the top always follow, to the base always aim the middle, to the middle always aim the top
        cmds.aimConstraint(drv_Jnt[1], bttm_Loc[1], offset=(0, 0, 0), weight=1, aimVector=(1, 0, 0), upVector=(0, 0, 1), worldUpType='object', worldUpObject=bttm_Loc[2], name=bttm_Loc[1]+"_AiC")
        cmds.aimConstraint(top_Loc[0], mid_Loc[1], offset=(0, 0, 0), weight=1, aimVector=(1, 0, 0), upVector=(0, 0, 1), worldUpType='object', worldUpObject=mid_Loc[3], name=mid_Loc[1]+"_AiC")
        cmds.aimConstraint(drv_Jnt[1], top_Loc[1], offset=(0, 0, 0), weight=1, aimVector=(-1, 0, 0), upVector=(0, 0, 1), worldUpType='object', worldUpObject=top_Loc[2], name=top_Loc[1]+"_AiC")
        
        #create a point and orient constraint for the middle control
        cmds.pointConstraint(top_Loc[0], bttm_Loc[0], mid_Loc[0], offset=(0, 0, 0), weight=1, name=mid_Loc[0]+"_PoC")
        cmds.delete(cmds.orientConstraint(bttm_Loc[0], aux_Jnt[0], weight=1, mo=False))
        mid_pac = cmds.parentConstraint(top_Loc[0], bttm_Loc[0], aux_Jnt[0], maintainOffset=True, skipTranslate=['x', 'y', 'z'], weight=0.5, name=aux_Jnt[0]+"_PaC")[0]
        cmds.setAttr(mid_pac+".interpType", 2) #Shortest
        
        #ribbon scale (volume variation)
        if num_joints == 3:
            if center_up_down == 0: #center
                proportions = [0.5, 1, 0.5]
            elif center_up_down == 1: #up
                proportions = [0.25, 0.5, 0.75]
            elif center_up_down == 2: #down
                proportions = [0.75, 0.5, 0.25]
        elif num_joints == 5:
            if center_up_down == 0: #center
                proportions = [0.4, 0.8, 1, 0.8, 0.4]
            if center_up_down == 1: #up
                proportions = [0.16, 0.33, 0.5, 0.66, 0.83]
            if center_up_down == 2: #down
                proportions = [0.83, 0.66, 0.5, 0.33, 0.16]
        elif num_joints == 7:
            if center_up_down == 0: #center
                proportions = [0.25, 0.5, 0.75, 1, 0.75, 0.5, 0.25]
            if center_up_down == 1: #up
                proportions = [0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875]
            if center_up_down == 2: #down
                proportions = [0.875, 0.75, 0.625, 0.5, 0.375, 0.25, 0.125]

        curve_info_node = cmds.arclen(ribbon+".v[0.5]", constructionHistory=True)
        curve_info_node = cmds.rename(curve_info_node, ribbon+"_CurveInfo")
        curve_from_surface_iso = cmds.listConnections(curve_info_node+".inputCurve", source=True, destination=False)
        cmds.rename(curve_from_surface_iso, ribbon+"_CurveFromSurface_Iso")
        rb_scale_md = cmds.createNode("multiplyDivide", name=ribbon+"_ScaleCompensate_MD")
        rb_normalize_md = cmds.createNode("multiplyDivide", name=ribbon+"_Normalize_MD")
        self.to_ids.extend([curve_info_node, rb_scale_md, rb_normalize_md, ribbon+"_CurveFromSurface_Iso"])
        cmds.setAttr(rb_normalize_md+".operation", 2)
        cmds.connectAttr(curve_info_node+".arcLength", rb_normalize_md+".input2X", force=True)
        cmds.connectAttr(rb_scale_md+".outputX", rb_normalize_md+".input1X", force=True)

        if cmds.objExists(world_ref):
            if not cmds.objExists(world_ref+"."+self.limb_manual_vv_attr):
                cmds.addAttr(world_ref, longName=self.limb_vv_attr, attributeType="float", minValue=0, maxValue=1, defaultValue=1, keyable=True)
                cmds.addAttr(world_ref, longName=self.limb_manual_vv_attr, attributeType="float", defaultValue=1, keyable=True)
                cmds.addAttr(world_ref, longName=self.limb_min_vv_attr, attributeType="float", defaultValue=0.01, keyable=True)
            cmds.connectAttr(world_ref+".scaleX", rb_scale_md+".input1X", force=True)
        
        #fix group hierarchy
        extra_ctrl_grp = cmds.group(empty=True, name=name+"_ExtraBendyCtrl_Grp")
        i = 0
        for jnt in rb_Jnt:
            cmds.makeIdentity(jnt, apply=True)
            
            # create extra control
            extra_name = jnt[:-4] #removed _Jnt suffix
            extra_ctrl = self.ar.ctrls.create_controller("id_040_RibbonExtra", ctrl_name=extra_name+"_Ctrl", r=self.radius, d=self.curve_degree, guide_source=self.limb_instance.guide_base, parent_tag=self.limb_instance.get_parent_to_tag(extra_ctrls))
            extra_ctrls.append(extra_ctrl)
            cmds.rotate(0, 90, 0, extra_ctrl)
            cmds.makeIdentity(extra_ctrl, a=True)
            extra_zero = self.ar.utils.zeroOut([extra_ctrl])[0]
            cmds.parent(extra_zero, extra_ctrl_grp)
            cmds.parentConstraint(fols[i], extra_zero, w=1, name=extra_zero+"_PaC")
            cmds.parentConstraint(extra_ctrl, jnt, w=1, name=jnt+"_PaC")
            cmds.scaleConstraint(extra_ctrl, jnt, w=1, name=jnt+"_ScC")
            
            # work with volume variation
            rb_proportion_md = cmds.createNode("multiplyDivide", name=extra_name+"_Proportion_MD")
            rb_intensity_md = cmds.createNode("multiplyDivide", name=extra_name+"_Intensity_MD")
            rb_length_md = cmds.createNode("multiplyDivide", name=extra_name+"_Length_MD")
            rb_add_scale_pma = cmds.createNode("plusMinusAverage", name=extra_name+"_AddScale_PMA")
            rb_scale_clp = cmds.createNode("clamp", name=extra_name+"_Scale_Clp")
            rb_blend_bc = cmds.createNode("blendColors", name=extra_name+"_BC")
            self.to_ids.extend([rb_proportion_md, rb_intensity_md, rb_length_md, rb_add_scale_pma, rb_scale_clp, rb_blend_bc])
            cmds.connectAttr(world_ref+"."+self.limb_vv_attr, rb_blend_bc+".blender", force=True)
            cmds.setAttr(rb_blend_bc+".color2", 1, 1, 1, type="double3")
            cmds.connectAttr(rb_normalize_md+".outputX", rb_proportion_md+".input1X", force=True)
            cmds.setAttr(rb_proportion_md+".input2X", proportions[i])
            cmds.connectAttr(rb_proportion_md+".outputX", rb_intensity_md+".input1X", force=True)
            cmds.connectAttr(world_ref+"."+self.limb_manual_vv_attr, rb_intensity_md+".input2X", force=True)
            cmds.connectAttr(world_ref+"."+self.limb_length_attr, rb_length_md+".input2X", force=True)
            cmds.connectAttr(rb_intensity_md+".outputX", rb_length_md+".input1X", force=True)
            cmds.connectAttr(rb_length_md+".outputX", rb_add_scale_pma+".input1D[1]", force=True)
            cmds.connectAttr(rb_add_scale_pma+".output1D", rb_scale_clp+".inputR", force=True)
            cmds.connectAttr(world_ref+"."+self.limb_min_vv_attr, rb_scale_clp+".minR")
            cmds.setAttr(rb_scale_clp+".maxR", 1000000)
            cmds.connectAttr(rb_scale_clp+".outputR", rb_blend_bc+".color1.color1R", force=True)
            cmds.connectAttr(rb_blend_bc+".output.outputR", extra_zero+".scaleY", force=True)
            cmds.connectAttr(rb_blend_bc+".output.outputR", extra_zero+".scaleZ", force=True)
            
            # additional joint
            if additional_joint:
                additional_axes = ["Y", "Z"]
                additional_dirs = [-1, 1]
                d = 1
                for add_dir in additional_dirs:
                    for add_axis in additional_axes:
                        cmds.select(jnt)
                        jad = cmds.joint(name=jnt.replace("_Jnt", "_"+str(d).zfill(2)+"_Jad"), scaleCompensate=False)
                        # joint position:
                        if s == 1: #right
                            if axis == (0, 0, -1): #arm
                                if add_axis == "Z":
                                    # flip direction to conform with left side
                                    add_dir = -1 * add_dir
                            else: #leg
                                # flip direction to conform with left side
                                add_dir = -1 * add_dir
                        cmds.setAttr(jad+".translate"+add_axis, add_dir*self.radius*0.5)
                        self.ar.utils.setJointLabel(jad, s+joint_label_add, 18, joint_label_name+'_%02d_%02d'%(i,d))
                        cmds.addAttr(jad, longName="dpAR_joint", attributeType='float', keyable=False)
                        # control:
                        add_ctrl = self.ar.ctrls.create_controller("id_088_LimbAdditional", ctrl_name=extra_name+"_Add_%02d_Ctrl"%d, r=self.radius*0.1, d=self.curve_degree, guide_source=self.limb_instance.guide_base)
                        extra_ctrls.append(add_ctrl)
                        add_ctrl_grp = self.ar.utils.zeroOut([add_ctrl])[0]
                        cmds.matchTransform(add_ctrl_grp, jad, position=True, rotation=True)
                        cmds.parentConstraint(add_ctrl, jad, maintainOffset=True, name=jad+"_PaC")
                        cmds.scaleConstraint(add_ctrl, jad, maintainOffset=True, name=jad+"_ScC")
                        cmds.parent(add_ctrl_grp, extra_ctrl, absolute=True)
                        cmds.setAttr(add_ctrl_grp+".scaleY", 1)
                        cmds.setAttr(add_ctrl_grp+".scaleZ", 1)
                        d = d + 1

            # update i
            i = i + 1
        
        if add_artic:
            if center_up_down == 1: #up
                # corner scale volumeVariation setup:
                rb_proportion_md = cmds.createNode("multiplyDivide", name=self.elbow_ctrl.replace("_Ctrl", "_Proportion_MD"))
                rb_intensity_md = cmds.createNode("multiplyDivide", name=self.elbow_ctrl.replace("_Ctrl", "_Intensity_MD"))
                rb_add_scale_pma = cmds.createNode("plusMinusAverage", name=self.elbow_ctrl.replace("_Ctrl", "_AddScale_PMA"))
                rb_length_md = cmds.createNode("multiplyDivide", name=self.elbow_ctrl.replace("_Ctrl", "_Length_MD"))
                rb_scale_clp = cmds.createNode("clamp", name=self.elbow_ctrl.replace("_Ctrl", "_Scale_Clp"))
                rb_blend_bc = cmds.createNode("blendColors", name=self.elbow_ctrl.replace("_Ctrl", "_BC"))
                self.to_ids.extend([rb_proportion_md, rb_intensity_md, rb_add_scale_pma, rb_length_md, rb_scale_clp, rb_blend_bc])
                cmds.connectAttr(world_ref+"."+self.limb_vv_attr, rb_blend_bc+".blender", force=True)
                cmds.setAttr(rb_blend_bc+".color2", 1, 1, 1, type="double3")
                cmds.connectAttr(rb_normalize_md+".outputX", rb_proportion_md+".input1X", force=True)
                cmds.setAttr(rb_proportion_md+".input2X", 1)
                cmds.connectAttr(rb_proportion_md+".outputX", rb_intensity_md+".input1X", force=True)
                cmds.connectAttr(world_ref+"."+self.limb_manual_vv_attr, rb_intensity_md+".input2X", force=True)
                cmds.connectAttr(world_ref+"."+self.limb_length_attr, rb_length_md+".input2X", force=True)
                cmds.connectAttr(rb_intensity_md+".outputX", rb_length_md+".input1X", force=True)
                cmds.connectAttr(rb_length_md+".outputX", rb_add_scale_pma+".input1D[1]", force=True)
                cmds.connectAttr(rb_add_scale_pma+".output1D", rb_scale_clp+".inputR", force=True)
                cmds.connectAttr(world_ref+"."+self.limb_min_vv_attr, rb_scale_clp+".minR")
                cmds.setAttr(rb_scale_clp+".maxR", 1000000)
                cmds.connectAttr(rb_scale_clp+".outputR", rb_blend_bc+".color1.color1R", force=True)
                cmds.connectAttr(rb_blend_bc+".output.outputR", self.corner_jnt+".scaleY", force=True)
                cmds.connectAttr(rb_blend_bc+".output.outputR", self.corner_jnt+".scaleZ", force=True)
                if ori_b_loc:
                    cmds.connectAttr(rb_blend_bc+".output.outputR", self.corner_b_jnt+".scaleY", force=True)
                    cmds.connectAttr(rb_blend_bc+".output.outputR", self.corner_b_jnt+".scaleZ", force=True)
        
        locators_grps = cmds.group(bttm_Loc[0], top_Loc[0], mid_Loc[0], bttm_Loc[3], top_Loc[3], n=name+'_Loc_Grp')
        skin_jnt_grp = cmds.group(rb_Jnt, n=name+'_Jnt_Grp')
        final_system_grp = cmds.group(ribbon, locators_grps, skin_jnt_grp, n=name+'_RibbonSystem_Grp')
        #do the controller joints skin and the ribbon
        ribbon_shape = cmds.listRelatives(ribbon, shapes=True)
        skincluster_node = cmds.skinCluster(drv_Jnt[0:3], ribbon_shape, tsb=True, mi=2, dr=1, n=name+"_SC")[0]
        bindpose = cmds.listConnections(skincluster_node+".bindPose", destination=False, source=True)
        cmds.rename(bindpose, name+"_BP")
        self.to_ids.extend([skincluster_node, name+"_BP"])
        
        #skin presets for the ribbon (that's amazing!)
        if not horizontal:
            if num_joints == 3:
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0:1][5]', transformValue=[(drv_Jnt[2], 0.99), (drv_Jnt[1], 0.01)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0:1][4]', transformValue=[(drv_Jnt[2], 0.6), (drv_Jnt[1], 0.4)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0:1][3]', transformValue=[(drv_Jnt[2], 0.2), (drv_Jnt[1], 0.8)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0:1][2]', transformValue=[(drv_Jnt[0], 0.2), (drv_Jnt[1], 0.8)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0:1][1]', transformValue=[(drv_Jnt[0], 0.6), (drv_Jnt[1], 0.4)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0:1][0]', transformValue=[(drv_Jnt[0], 0.99), (drv_Jnt[1], 0.01)])

            elif num_joints == 5:
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0:1][7]', transformValue=[(drv_Jnt[2], 0.99), (drv_Jnt[1], 0.01)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0:1][6]', transformValue=[(drv_Jnt[2], 0.8), (drv_Jnt[1], 0.2)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0:1][5]', transformValue=[(drv_Jnt[2], 0.5), (drv_Jnt[1], 0.5)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0:1][4]', transformValue=[(drv_Jnt[2], 0.25), (drv_Jnt[1], 0.75)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0:1][3]', transformValue=[(drv_Jnt[0], 0.25), (drv_Jnt[1], 0.75)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0:1][2]', transformValue=[(drv_Jnt[0], 0.5), (drv_Jnt[1], 0.5)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0:1][1]', transformValue=[(drv_Jnt[0], 0.8), (drv_Jnt[1], 0.2)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0:1][0]', transformValue=[(drv_Jnt[0], 0.99), (drv_Jnt[1], 0.01)])
            elif num_joints == 7:
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0:1][9]', transformValue=[(drv_Jnt[2], 0.99), (drv_Jnt[1], 0.01)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0:1][8]', transformValue=[(drv_Jnt[2], 0.85), (drv_Jnt[1], 0.15)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0:1][7]', transformValue=[(drv_Jnt[2], 0.6), (drv_Jnt[1], 0.4)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0:1][6]', transformValue=[(drv_Jnt[2], 0.35), (drv_Jnt[1], 0.65)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0:1][5]', transformValue=[(drv_Jnt[2], 0.25), (drv_Jnt[1], 0.75)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0:1][4]', transformValue=[(drv_Jnt[0], 0.25), (drv_Jnt[1], 0.75)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0:1][3]', transformValue=[(drv_Jnt[0], 0.35), (drv_Jnt[1], 0.65)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0:1][2]', transformValue=[(drv_Jnt[0], 0.6), (drv_Jnt[1], 0.4)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0:1][1]', transformValue=[(drv_Jnt[0], 0.85), (drv_Jnt[1], 0.15)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0:1][0]', transformValue=[(drv_Jnt[0], 0.99), (drv_Jnt[1], 0.01)])
        else:
            if num_joints == 3:
                cmds.skinPercent(skincluster_node, ribbon+'.cv[5][0:1]', transformValue=[(drv_Jnt[2], 0.99), (drv_Jnt[1], 0.01)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[4][0:1]', transformValue=[(drv_Jnt[2], 0.6), (drv_Jnt[1], 0.4)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[3][0:1]', transformValue=[(drv_Jnt[2], 0.2), (drv_Jnt[1], 0.8)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[2][0:1]', transformValue=[(drv_Jnt[0], 0.2), (drv_Jnt[1], 0.8)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[1][0:1]', transformValue=[(drv_Jnt[0], 0.6), (drv_Jnt[1], 0.4)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0][0:1]', transformValue=[(drv_Jnt[0], 0.99), (drv_Jnt[1], 0.01)])
            elif num_joints == 5:
                cmds.skinPercent(skincluster_node, ribbon+'.cv[7][0:1]', transformValue=[(drv_Jnt[2], 0.99), (drv_Jnt[1], 0.01)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[6][0:1]', transformValue=[(drv_Jnt[2], 0.8), (drv_Jnt[1], 0.2)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[5][0:1]', transformValue=[(drv_Jnt[2], 0.5), (drv_Jnt[1], 0.5)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[4][0:1]', transformValue=[(drv_Jnt[2], 0.25), (drv_Jnt[1], 0.75)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[3][0:1]', transformValue=[(drv_Jnt[0], 0.25), (drv_Jnt[1], 0.75)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[2][0:1]', transformValue=[(drv_Jnt[0], 0.5), (drv_Jnt[1], 0.5)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[1][0:1]', transformValue=[(drv_Jnt[0], 0.8), (drv_Jnt[1], 0.2)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0][0:1]', transformValue=[(drv_Jnt[0], 0.99), (drv_Jnt[1], 0.01)])
            elif num_joints == 7:
                cmds.skinPercent(skincluster_node, ribbon+'.cv[9][0:1]', transformValue=[(drv_Jnt[2], 0.99), (drv_Jnt[1], 0.01)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[8][0:1]', transformValue=[(drv_Jnt[2], 0.85), (drv_Jnt[1], 0.15)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[7][0:1]', transformValue=[(drv_Jnt[2], 0.6), (drv_Jnt[1], 0.4)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[6][0:1]', transformValue=[(drv_Jnt[2], 0.35), (drv_Jnt[1], 0.65)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[5][0:1]', transformValue=[(drv_Jnt[2], 0.25), (drv_Jnt[1], 0.75)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[4][0:1]', transformValue=[(drv_Jnt[0], 0.25), (drv_Jnt[1], 0.75)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[3][0:1]', transformValue=[(drv_Jnt[0], 0.35), (drv_Jnt[1], 0.65)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[2][0:1]', transformValue=[(drv_Jnt[0], 0.6), (drv_Jnt[1], 0.4)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[1][0:1]', transformValue=[(drv_Jnt[0], 0.85), (drv_Jnt[1], 0.15)])
                cmds.skinPercent(skincluster_node, ribbon+'.cv[0][0:1]', transformValue=[(drv_Jnt[0], 0.99), (drv_Jnt[1], 0.01)])
        constr = []
        if guides:
            top = guides[0]
            bottom = guides[1]
            constr.append(cmds.parentConstraint(top, bttm_Loc[0], mo=False, name=bttm_Loc[0]+"_PaC"))
            constr.append(cmds.parentConstraint(bottom, top_Loc[0], mo=False, name=top_Loc[0]+"_PaC")) #to integrate jxt after
            cmds.matchTransform(bttm_Loc[3], top, position=True, rotation=True)
            cmds.matchTransform(top_Loc[3], bottom, position=True, rotation=True)
            constr.append(cmds.pointConstraint(top, bttm_Loc[3], mo=False, name=bttm_Loc[3]+"_PoC"))
            constr.append(cmds.pointConstraint(bottom, top_Loc[3], mo=False, name=top_Loc[3]+"_PoC"))
            # this is an important constraint to avoid Ribbon flipping and follow correctely the hierarchy:
            cmds.parentConstraint(top, locators_grps, maintainOffset=True, name=locators_grps+"_PaC")
        #fix loc_Grp scale
        if guides:
            from math import sqrt, pow
            aux_loc_1 = cmds.spaceLocator(name='aux_loc_1')[0]
            aux_loc_2 = cmds.spaceLocator(name='aux_loc_2')[0]
            cmds.matchTransform(aux_loc_1, top, position=True, rotation=True)
            cmds.matchTransform(aux_loc_2, bottom, position=True, rotation=True)
            a = cmds.xform(aux_loc_1, ws=True, translation=True, q=True)
            b = cmds.xform(aux_loc_2, ws=True, translation=True, q=True)
            
            dist = sqrt(pow(a[0]-b[0], 2.0)+pow(a[1]-b[1], 2.0)+pow(a[2]-b[2], 2.0))
            scale = dist/float(num_joints)
            
            cmds.setAttr(locators_grps+'.s', scale, scale, scale)
        
            cmds.delete(aux_loc_1, aux_loc_2)

        # baseTwist:
        if not up_ctrl == None:
            bttm_LocGrp = cmds.group(bttm_Loc[2], name=bttm_Loc[2]+"_Grp")
            bttm_LocTwistBoneGrp = cmds.group(bttm_LocGrp, name=bttm_Loc[2]+"_TwistBone_Grp")
            self.ar.utils.addCustomAttr([bttm_LocGrp, bttm_LocTwistBoneGrp], self.ar.utils.ignoreTransformIOAttr)
            bttm_LocPos = cmds.xform(bttm_Loc[0], query=True, worldSpace=True, translation=True)
            cmds.move(bttm_LocPos[0], bttm_LocPos[1], bttm_LocPos[2], bttm_LocGrp+".scalePivot", bttm_LocGrp+".rotatePivot", absolute=True)
            cmds.move(bttm_LocPos[0], bttm_LocPos[1], bttm_LocPos[2], bttm_LocTwistBoneGrp+".scalePivot", bttm_LocTwistBoneGrp+".rotatePivot", absolute=True)
            twist_bone_md = cmds.createNode("multiplyDivide", name=up_ctrl+"_TwistBone_MD")
            invert_twist_bone_md = cmds.createNode("multiplyDivide", name=up_ctrl+"_InvertTwistBone_MD")
            self.to_ids.extend([twist_bone_md, invert_twist_bone_md])
            cmds.setAttr(invert_twist_bone_md+".input2Z", -1)
            cmds.connectAttr(up_ctrl+".autoTwistBone", twist_bone_md+".input1Z", force=True)
            cmds.connectAttr(twist_bone_md+".outputZ", invert_twist_bone_md+".input1Z", force=True)
            cmds.connectAttr(invert_twist_bone_md+".outputZ", bttm_LocTwistBoneGrp+".rotateZ", force=True)
            cmds.connectAttr(up_ctrl+".baseTwist", bttm_LocGrp+".rotateZ", force=True)
            result_data['twistBoneMD'] = twist_bone_md
        
        # autoRotate:
        loaded_quaternion_plugin = self.ar.utils.checkLoadedPlugin("quatNodes", self.ar.data.lang['e014_cantLoadQuatNode'])
        loaded_matrix_plugin = self.ar.utils.checkLoadedPlugin("matrixNodes", self.ar.data.lang['e002_matrixPluginNotFound'])
        if loaded_quaternion_plugin and loaded_matrix_plugin:
            up_twist_bone_md = self.ar.utils.twistBoneMatrix(top_Loc[0], top_Loc[3], name+"_Top_TwistBone")
            bottom_twist_bone_md = self.ar.utils.twistBoneMatrix(bttm_Loc[0], bttm_Loc[3], name+"_Bottom_TwistBone")
            twist_bone_pma = cmds.createNode("plusMinusAverage", name=name+"_TwistBone_PMA")
            twist_bone_inv_md = cmds.createNode("multiplyDivide", name=name+"_TwistBone_Inv_MD")
            twist_bone_cnd = cmds.createNode("condition", name=name+"_TwistBone_Cnd")
            twist_auto_rot_md = cmds.createNode("multiplyDivide", name=name+"_TwistBone_AutoRotate_MD")
            self.to_ids.extend([twist_bone_pma, twist_bone_inv_md, twist_bone_inv_md, twist_bone_cnd, twist_auto_rot_md])
            cmds.setAttr(twist_bone_cnd+".colorIfTrueR", -1)
            cmds.setAttr(twist_bone_cnd+".secondTerm", 1)
            cmds.connectAttr(twist_bone_pma+".output1D", twist_bone_inv_md+".input1X", force=True)
            cmds.connectAttr(twist_bone_cnd+".outColor.outColorR", twist_bone_inv_md+".input2X", force=True)
            cmds.connectAttr(up_twist_bone_md+".outputZ", twist_bone_pma+".input1D[0]", force=True)
            cmds.connectAttr(bottom_twist_bone_md+".outputZ", twist_bone_pma+".input1D[1]", force=True)
            cmds.connectAttr(twist_bone_inv_md+".outputX", twist_auto_rot_md+".input1X", force=True)
            cmds.connectAttr(twist_auto_rot_md+".outputX", mid_Loc[2]+".rotateX", force=True)
            result_data['up_twist_bone_md'] = up_twist_bone_md
            result_data['bottom_twist_bone_md'] = bottom_twist_bone_md
            result_data['twist_bone_cnd'] = twist_bone_cnd
            result_data['twist_auto_rot_md'] = twist_auto_rot_md
            
        #updating values
        cmds.setAttr(rb_scale_md+".input2X", cmds.getAttr(curve_info_node+".arcLength"))
        for jnt in rb_Jnt:
            rb_add_scale_pma = jnt.replace("_Jnt", "_AddScale_PMA")
            cmds.setAttr(rb_add_scale_pma+".input1D[0]", 1-cmds.getAttr(rb_add_scale_pma+".input1D[1]"))

        self.ar.utils.addCustomAttr([mid_ctrl, extra_ctrl_grp, locators_grps, skin_jnt_grp, final_system_grp], self.ar.utils.ignoreTransformIOAttr)

        #change renderStats
        ribbon_shape = cmds.listRelatives(ribbon, s=True, f=True)[0]
        
        cmds.setAttr(ribbon_shape+'.castsShadows', 0)
        cmds.setAttr(ribbon_shape+'.receiveShadows', 0)
        cmds.setAttr(ribbon_shape+'.motionBlur', 0)
        cmds.setAttr(ribbon_shape+'.primaryVisibility', 0)
        cmds.setAttr(ribbon_shape+'.smoothShading', 0)
        cmds.setAttr(ribbon_shape+'.visibleInReflections', 0)
        cmds.setAttr(ribbon_shape+'.visibleInRefractions', 0)
        cmds.setAttr(ribbon_shape+'.doubleSided', 1)
        
        result_data['name'] = name
        result_data['locsList'] = [top_Loc[0], mid_Loc[0], bttm_Loc[0], top_Loc[3], bttm_Loc[3]]
        result_data['skinJointsList'] = rb_Jnt
        result_data['scaleGrp'] = locators_grps
        result_data['finalGrp'] = final_system_grp
        result_data['middleCtrl'] = mid_ctrl
        result_data['constraints'] = constr
        result_data['bendGrpList'] = [top_Loc[0], bttm_Loc[0]]
        result_data['extraCtrlGrp'] = extra_ctrl_grp
        result_data['extraCtrlList'] = extra_ctrls
        cmds.setAttr(final_system_grp+'.v', v)
        return result_data
    
    
    def create_follicles(self, rib, num, pad=0.5, name='xxxx', horizontal=False, side=0, joint_label_add=0, joint_label_name="RibbonName"): 
        """ Create follicles to be used by the Ribbon system.
            Returns a list with joints and follicles created.
        """
        #define variables
        jnts = []
        fols = []
        #create joints and follicles based in the choose options from user
        if horizontal:
            #calculate the position of the first follicle
            passo = (1/float(num))/2.0;
            for i in range(num):
                #create the follicle and do correct connections to link it to the 
                fol_shape = cmds.createNode('follicle', name=name+'_%02d_FolShape'%i)
                fol_transform = cmds.rename(cmds.listRelatives(fol_shape, p=1)[0], name+'_%02d_Fol'%i)         
                fols.append(fol_transform)
                cmds.connectAttr(rib+'.worldMatrix[0]', fol_shape+'.inputWorldMatrix')
                cmds.connectAttr(rib+'.local', fol_shape+'.inputSurface')
                cmds.connectAttr(fol_shape+'.outTranslate', fol_transform+'.translate')
                cmds.connectAttr(fol_shape+'.outRotate', fol_transform+'.rotate')
                cmds.setAttr(fol_shape+'.parameterU', passo)
                cmds.setAttr(fol_shape+'.parameterV', 0.5) 
                #create the joint in the follicle
                cmds.select(cl=True)
                jnts.append(cmds.joint(n=name+'_%02d_Jnt'%i))
                cmds.setAttr(jnts[i]+'.jointOrient', 0, 0, 0)
                self.ar.utils.setJointLabel(name+'_%02d_Jnt'%i, side+joint_label_add, 18, joint_label_name+'_%02d'%i)
                cmds.addAttr(jnts[i], longName="dpAR_joint", attributeType='float', keyable=False)
                cmds.select(cl=True)
                #calculate the position of the first follicle
                passo+=(1/float(num))
            results = [jnts, fols]
            #return the joints and follicles created
        else:
            #calculate the position of the first follicle
            passo = (1/float(num))/2.0;
            for i in range(num):
                #create the follicle and do correct connections in order to link it to the ribbon
                fol_shape = cmds.createNode('follicle', name=name+'_%02d_FolShape'%i)
                fol_transform = cmds.rename(cmds.listRelatives(fol_shape, p=1)[0], name+'_%02d_Fol'%i)
                fols.append(fol_transform)
                cmds.connectAttr(rib+'.worldMatrix[0]', fol_shape+'.inputWorldMatrix')
                cmds.connectAttr(rib+'.local', fol_shape+'.inputSurface')
                cmds.connectAttr(fol_shape+'.outTranslate', fol_transform+'.translate')
                cmds.connectAttr(fol_shape+'.outRotate', fol_transform+'.rotate')
                cmds.setAttr(fol_shape+'.parameterU', 0.5)   
                cmds.setAttr(fol_shape+'.parameterV', passo) 
                #create the joint in the follicle
                cmds.select(cl=True)
                jnts.append(cmds.joint(n=name+'_%02d_Jnt'%i))
                cmds.setAttr(jnts[i]+'.jointOrient', 0, 0, 0)
                self.ar.utils.setJointLabel(name+'_%02d_Jnt'%i, side+joint_label_add, 18, joint_label_name+'_%02d'%i)
                cmds.addAttr(jnts[i], longName="dpAR_joint", attributeType='float', keyable=False)
                cmds.select(cl=True)
                #calculate the first follicle position
                passo+=(1/float(num))
            results = [jnts, fols]
        #return the created joints and follicles
        cmds.parent(fols, rib)
        return results
    

    def create_corner_joint(self, prefix, name, corner_name, ctrl):
        """ Create and return the corner joint and jxt.
        """
        cmds.select(clear=True)
        corner_jxt = cmds.joint(name=prefix+name+'_'+corner_name+'_Jxt', scaleCompensate=False)
        corner_jnt = cmds.joint(name=prefix+name+'_'+corner_name+'_Jnt', scaleCompensate=False, radius=1.5)
        cmds.setAttr(corner_jxt+".segmentScaleCompensate", 1)
        cmds.setAttr(corner_jnt+".segmentScaleCompensate", 0) #jar
        cmds.addAttr(corner_jnt, longName="dpAR_joint", attributeType='float', keyable=False)
        cmds.parentConstraint(ctrl, corner_jxt, maintainOffset=False, name=corner_jxt+"_PaC")
        cmds.scaleConstraint(ctrl, corner_jxt, maintainOffset=False, name=corner_jxt+"_ScC")
        return [corner_jxt, corner_jnt]


    def add_corrective_joint(self, jcr_number, corner_jnt, jcr_pos, jcr_rot):
        """ Add corrective joint to the ribbon corner.
        """
        for i in range(0, jcr_number):
            cmds.select(corner_jnt)
            jcr = cmds.joint(name=corner_jnt[:corner_jnt.rfind("_")+1]+str(i)+"_Jcr")
            cmds.setAttr(jcr+".segmentScaleCompensate", 0)
            cmds.addAttr(jcr, longName='dpAR_joint', attributeType='float', keyable=False)
            if jcr_pos:
                cmds.setAttr(jcr+".translateX", jcr_pos[i][0])
                cmds.setAttr(jcr+".translateY", jcr_pos[i][1])
                cmds.setAttr(jcr+".translateZ", jcr_pos[i][2])
            if jcr_rot:
                cmds.setAttr(jcr+".rotateX", jcr_rot[i][0])
                cmds.setAttr(jcr+".rotateY", jcr_rot[i][1])
                cmds.setAttr(jcr+".rotateZ", jcr_rot[i][2])


    def pin_corner_setup(self, world_ref, elbow_grp, elbow_ctrl, elbow_zero_1, corner_auto_rotate_inv_pin_md):
        """ Create the pin setup for the given corner controller.
        """
        world_ref_pac = cmds.parentConstraint(world_ref, elbow_grp, elbow_zero_1, mo=True, name=elbow_zero_1+"_PaC")[0]
        pin_rev = cmds.createNode('reverse', name=elbow_ctrl+"_Pin_Rev")
        self.to_ids.append(pin_rev)
        cmds.connectAttr(elbow_ctrl+".pin", world_ref_pac+"."+world_ref+"W0", force=True)
        cmds.connectAttr(elbow_ctrl+".pin", pin_rev+".inputX", force=True)
        cmds.connectAttr(pin_rev+".outputX", world_ref_pac+"."+elbow_grp+"W1", force=True)
        cmds.connectAttr(pin_rev+".outputX", corner_auto_rotate_inv_pin_md+".input2Z", force=True)
        cmds.setAttr(world_ref_pac+".interpType", 2) #shortest
