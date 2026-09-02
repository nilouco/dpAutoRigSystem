###
#
#   THANKS to:
#       Nick Miller Genuine
#       https://vimeo.com/nickmillergenuine
#
#   Based on:
#       https://www.highend3d.com/maya/script/soft-ik-tool-for-maya
#   
#   This module will create a Soft Ik setup to be implemented by dpLimb.py
#
#
# Formula:
#
# y = {                                              
#                     -(x-da)/
#        dsoft(1 - e^  dsoft  ) + da   (da <= x)
#                                                   }
#
# da = dchain - dsoft
# dchain = sum of bone lengths
# dsoft = user set soft distance (how far the effector should fall behind)
# x = distance between root and ik (shoulder and wrist)
#
###


# importing libraries:
from maya import cmds



class SoftIk(object):
    def __init__(self, ar):
        self.ar = ar


    def create_soft_ik(self, user_name, ctrl_name, ikh_name, ik_joints, skin_joints, dist_between, world_ref, stretch=True, axis="Z"):
        """ Create the softIk setup for given parameters.
            Just a general function edited from Nick Miller code.
            Returns the softIk calibrate multiplyDivide node to receive the Option_Ctrl.rigScale output.
        """
        self.to_ids = []
        soft_ik_calib_value = 0.02*cmds.getAttr(dist_between+".distance")
        # add the dSoft and softIk attributes on the controller:
        cmds.addAttr(ctrl_name, longName="softIk", attributeType="double", min=0, defaultValue=0, max=1, keyable=True)
        cmds.addAttr(ctrl_name, longName="softIk_"+self.ar.data.lang['c111_calibrate'], attributeType="double", min=0.001, defaultValue=soft_ik_calib_value, keyable=False)
        cmds.addAttr(ctrl_name, longName="softDistance", attributeType="double", min=0.001, defaultValue=0.001, keyable=True)
        
        # set up node network for softIk:
        calibrate_md = cmds.createNode("multiplyDivide", name=user_name+"_SoftCalibrate_MD")
        soft_rmv = cmds.createNode("remapValue", name=user_name+"_SoftDistance_RmV")
        da_md = cmds.createNode("plusMinusAverage", name=user_name+"_DA_PMA")
        x_minus_da_pma = cmds.createNode("plusMinusAverage", name=user_name+"_X_Minus_DA_PMA")
        negative_x_minus_md = cmds.createNode("multiplyDivide", name=user_name+"_Negate_X_Minus_MD")
        div_by_d_soft_md = cmds.createNode("multiplyDivide", name=user_name+"_DivBy_DSoft_MD")
        pow_e_md = cmds.createNode("multiplyDivide", name=user_name+"_Pow_E_MD")
        one_minus_pow_e_pma = cmds.createNode("plusMinusAverage", name=user_name+"_One_Minus_Pow_E_PMA")
        times_d_soft_md = cmds.createNode("multiplyDivide", name=user_name+"_Times_DSoft_MD")
        plus_da_pma = cmds.createNode("plusMinusAverage", name=user_name+"_Plus_DA_PMA")
        da_cnd = cmds.createNode("condition", name=user_name+"_DA_Cnd")
        dist_diff_pma = cmds.createNode("plusMinusAverage", name=user_name+"_Dist_Diff_PMA")
        length_start_md = cmds.createNode("multiplyDivide", name=user_name+"_Length_Start_MD")
        lenght_output_md = cmds.createNode("multiplyDivide", name=user_name+"_Length_Output_MD")
        soft_ik_rig_scale_md = cmds.createNode("multiplyDivide", name=user_name+"_SoftIk_RigScale_MD")
        soft_ik_rig_scale_clp = cmds.createNode("clamp", name=user_name+"_SoftIk_RigScale_Clp")
        self.to_ids.extend([calibrate_md, soft_rmv, da_md, x_minus_da_pma, negative_x_minus_md, div_by_d_soft_md, pow_e_md, one_minus_pow_e_pma, times_d_soft_md, plus_da_pma, da_cnd, dist_diff_pma, length_start_md, lenght_output_md, soft_ik_rig_scale_md, soft_ik_rig_scale_clp])
        
        # set default values and operations:
        cmds.setAttr(pow_e_md+".input1X", 2.718281828)
        cmds.setAttr(soft_rmv+".outputMin", 0.001)
        cmds.setAttr(negative_x_minus_md+".input2X", -1)
        cmds.setAttr(one_minus_pow_e_pma+".input1D[0]", 1)
        cmds.setAttr(da_md+".operation", 2) #divide
        cmds.setAttr(x_minus_da_pma+".operation", 2) #substract
        cmds.setAttr(negative_x_minus_md+".operation", 1) #multiply
        cmds.setAttr(div_by_d_soft_md+".operation", 2) #divide
        cmds.setAttr(pow_e_md+".operation", 3) #power
        cmds.setAttr(one_minus_pow_e_pma+".operation", 2) #substract
        cmds.setAttr(times_d_soft_md+".operation", 1) # multiply
        cmds.setAttr(plus_da_pma+".operation", 1) #sum
        cmds.setAttr(da_cnd+".operation", 5) #less or equal
        cmds.setAttr(dist_diff_pma+".operation", 2) #substract
        cmds.setAttr(soft_ik_rig_scale_clp+".maxR", 1000000)

        # make connections:
        cmds.connectAttr(ctrl_name+".softIk_"+self.ar.data.lang['c111_calibrate'], calibrate_md+".input1X", force=True)
        cmds.connectAttr(calibrate_md+".outputX", soft_rmv+".outputMax", force=True)
        cmds.connectAttr(ctrl_name+".softIk", soft_rmv+".inputValue", force=True)
        cmds.connectAttr(soft_rmv+".outValue", ctrl_name+".softDistance", force=True)
        cmds.connectAttr(ctrl_name+".startChainLength", length_start_md+".input1X", force=True)
        cmds.connectAttr(length_start_md+".outputX", da_md+".input1D[0]", force=True)
        cmds.connectAttr(ctrl_name+"."+self.ar.data.lang["c113_length"], length_start_md+".input2X", force=True)
        cmds.connectAttr(ctrl_name+".softDistance", da_md+".input1D[1]", force=True)
        cmds.connectAttr(dist_between+".distance", x_minus_da_pma+".input1D[0]", force=True)
        cmds.connectAttr(da_md+".output1D", x_minus_da_pma+".input1D[1]", force=True)
        cmds.connectAttr(x_minus_da_pma+".output1D", negative_x_minus_md+".input1X", force=True)
        cmds.connectAttr(negative_x_minus_md+".outputX", div_by_d_soft_md+".input1X", force=True)
        cmds.connectAttr(ctrl_name+".softDistance", div_by_d_soft_md+".input2X", force=True)
        cmds.connectAttr(div_by_d_soft_md+".outputX", pow_e_md+".input2X", force=True)
        cmds.connectAttr(pow_e_md+".outputX", one_minus_pow_e_pma+".input1D[1]", force=True)
        cmds.connectAttr(one_minus_pow_e_pma+".output1D", times_d_soft_md+".input1X", force=True)
        cmds.connectAttr(ctrl_name+".softDistance", times_d_soft_md+".input2X", force=True)
        cmds.connectAttr(times_d_soft_md+".outputX", plus_da_pma+".input1D[0]", force=True)
        cmds.connectAttr(da_md+".output1D", plus_da_pma+".input1D[1]", force=True)
        cmds.connectAttr(da_md+".output1D", da_cnd+".firstTerm", force=True)
        cmds.connectAttr(dist_between+".distance", da_cnd+".secondTerm", force=True)
        cmds.connectAttr(dist_between+".distance", da_cnd+".colorIfFalseR", force=True)
        cmds.connectAttr(plus_da_pma+".output1D", da_cnd+".colorIfTrueR", force=True)
        cmds.connectAttr(da_cnd+".outColorR", dist_diff_pma+".input1D[0]", force=True)
        cmds.connectAttr(dist_between+".distance", dist_diff_pma+".input1D[1]", force=True)        
        cmds.connectAttr(dist_diff_pma+".output1D", soft_ik_rig_scale_clp+".inputR", force=True)
        cmds.connectAttr(soft_ik_rig_scale_clp+".outputR", soft_ik_rig_scale_md+".input1X", force=True)
        cmds.connectAttr(world_ref+".scaleX", soft_ik_rig_scale_md+".input2X", force=True)
        cmds.connectAttr(soft_ik_rig_scale_md+".outputX", ikh_name+".translate"+axis, force=True)

        self.ar.ctrls.set_lock_hide([ctrl_name], ["softDistance"])

        # if stretch exists, we need to do this...
        if stretch:
            soft_ratio_md = cmds.createNode("multiplyDivide", name=user_name+"_Soft_Ratio_MD")
            disable_fk_stretch_md = cmds.createNode("multiplyDivide", name=user_name+"_DisableFkStretch_MD")
            stretch_bc = cmds.createNode("blendColors", name=user_name+"_Stretch_BC")
            self.to_ids.extend([soft_ratio_md, disable_fk_stretch_md, stretch_bc])
            cmds.setAttr(soft_ratio_md+".operation", 2) #divide
            cmds.setAttr(stretch_bc+".color2R", 1)
            cmds.connectAttr(ctrl_name+".stretchable", disable_fk_stretch_md+".input1X", force=True)
            cmds.connectAttr(ctrl_name+".disableIkFkRevOutputX", disable_fk_stretch_md+".input2X", force=True)
            cmds.connectAttr(disable_fk_stretch_md+".outputX", stretch_bc+".blender", force=True)
            cmds.connectAttr(dist_between+".distance", soft_ratio_md+".input1X", force=True)
            cmds.connectAttr(da_cnd+".outColorR", soft_ratio_md+".input2X", force=True)
            cmds.connectAttr(dist_diff_pma+".output1D", stretch_bc+".color2G", force=True)
            cmds.connectAttr(soft_ratio_md+".outputX", stretch_bc+".color1R", force=True)
            cmds.connectAttr(stretch_bc+".outputR", lenght_output_md+".input1X", force=True)
            cmds.connectAttr(ctrl_name+"."+self.ar.data.lang["c113_length"], lenght_output_md+".input2X", force=True)
            cmds.connectAttr(stretch_bc+".outputG", soft_ik_rig_scale_clp+".inputR", force=True)
            i = 0
            while ( i < len(ik_joints)-1 ):
                for k in self.ar.data.axes:
                    cmds.connectAttr(lenght_output_md+".outputX", ik_joints[i]+".scale"+k, force=True)
                    cmds.connectAttr(lenght_output_md+".outputX", skin_joints[i]+".scale"+k, force=True)
                i += 1
        
        self.ar.custom_attr.add_attr(0, self.to_ids) #dpID
        return calibrate_md
