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
# x = distance between root and ik
#
###


# importing libraries:
from maya import cmds
from . import dpUtils


class SoftIkClass(object):

    def __init__(self, dpUIinst, langDic, langName, presetDic, presetName, ctrlRadius, curveDegree, *args):
        # defining variables:
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        self.presetDic = presetDic
        self.presetName = presetName
        self.ctrlRadius = ctrlRadius
        self.curveDegree = curveDegree
        
        
    

    def createSoftIk(self, name, ctrlName, ikhName, jointList, stretch=True, upAxis="X", primaryAxis="Z", *args):
        """ TODO description here...
        """
        # TODO: validade input data before run the code
        

        
        
        #lists the joints
        joints = jointList
        #joints = cmds.ls( sl = True , type="joint")
        n = len(joints)
        print("joints =", joints)
        #gives position value for joints
        firstPos = cmds.xform( joints[0], q = True, piv = True, ws = True )
        lastPos = cmds.xform( joints[n - 1], q = True, piv = True, ws = True )
        fPoints  = firstPos[0:3]
        lPoints = lastPos[0:3]
        
        #up axis options
        if upAxis == 'X':
            gPoint = ( 0, lPoints[1], lPoints[2] )
        if upAxis == 'Y':
            gPoint = (lPoints[0], 0, lPoints[2])
        if upAxis == 'Z':
            gPoint = ( lPoints[0], lPoints[1], 0)

    #-----------------------------------------------------------------------------------------------------------------------------#
        #find the dchain = sum of bone lengths
        i = 0
        dChain = 0
        while ( i < n - 1 ):
            a = cmds.xform( joints[i], q = True, piv = True, ws = True )
            b = cmds.xform( joints[ i + 1 ], q = True, piv = True, ws = True )
            x = b[0] - a[0]
            y = b[1] - a[1]
            z = b[2] - a[2]
            v = [x,y,z]
            dChain += dpUtils.magnitude(v)
            i += 1
    #-----------------------------------------------------------------------------------------------------------------------------#
        #get the distance from 0 to the ikh
        x = lPoints[0] - gPoint[0]
        y = lPoints[1] - gPoint[1]
        z = lPoints[2] - gPoint[2]
        v = [x,y,z]
        defPos = dpUtils.magnitude(v)
        if( ( upAxis == 'X' ) and ( lastPos[0] < 0 ) ):
            defPos = defPos * -1
        if( ( upAxis == 'Y' ) and ( lastPos[1] < 0 ) ):
            defPos = defPos * -1
        if( ( upAxis == 'Z' ) and ( lastPos[2] < 0 ) ):
            defPos = defPos * -1
    #-----------------------------------------------------------------------------------------------------------------------------#
        #create the distance node, otherwise know as x(distance between root and ik)
        cmds.spaceLocator( n = '%s_start_dist_loc' % name )
        cmds.xform( '%s_start_dist_loc' % name, t = fPoints, ws = True )
        cmds.spaceLocator( n = '%s_end_dist_loc' % name )
        cmds.xform( '%s_end_dist_loc' % name, t = lPoints, ws = True )
        
        cmds.select( ctrlName, '%s_end_dist_loc' % name, r = True )
        cmds.parentConstraint( w = 1, mo = True)
        # cmds.select( joints[0], '%s_start_dist_loc' % name, r = True )
        # cmds.parentConstraint( w = 1, mo = True)
        
        cmds.createNode( 'distanceBetween', n = '%s_x_distance' % name )
        cmds.connectAttr( '%s_start_dist_loc.translate' % name, '%s_x_distance.point1' % name )
        cmds.connectAttr( '%s_end_dist_loc.translate' % name, '%s_x_distance.point2' % name )
    #-----------------------------------------------------------------------------------------------------------------------------#
        #create the dSoft and softIK attributes on the controller
        cmds.addAttr( ctrlName, ln = 'dSoft', at = "double", min = 0.001, max = 2, dv = 0.001, k = True )
        cmds.addAttr( ctrlName, ln = 'softIK', at = "double", min = 0, max = 20, dv = 0, k = True )
        #make softIK drive dSoft
        cmds.setDrivenKeyframe( '%s.dSoft' % ctrlName, currentDriver = '%s.softIK' % ctrlName )
        cmds.setAttr( '%s.softIK' % ctrlName, 20 )
        cmds.setAttr( '%s.dSoft' % ctrlName, 2 )
        cmds.setDrivenKeyframe( '%s.dSoft' % ctrlName, currentDriver = '%s.softIK' % ctrlName )
        cmds.setAttr( '%s.softIK' % ctrlName, 0 )
        #lock and hide dSoft
        cmds.setAttr( '%s.dSoft' % ctrlName, lock = True, keyable = False, cb = False )
    #-----------------------------------------------------------------------------------------------------------------------------#   	
        #set up node network for soft IK
        cmds.createNode ('plusMinusAverage', n = '%s_da_pma' % name )
        cmds.createNode ('plusMinusAverage', n = '%s_x_minus_da_pma' % name )
        cmds.createNode ('multiplyDivide', n = '%s_negate_x_minus_md' % name )
        cmds.createNode ('multiplyDivide', n = '%s_divBy_dSoft_md' % name )
        cmds.createNode ('multiplyDivide', n = '%s_pow_e_md' % name )
        cmds.createNode ('plusMinusAverage', n = '%s_one_minus_pow_e_pma' % name )
        cmds.createNode ('multiplyDivide', n = '%s_times_dSoft_md' % name )
        cmds.createNode ('plusMinusAverage', n = '%s_plus_da_pma' % name )
        cmds.createNode ('condition', n = '%s_da_cond' % name )
        cmds.createNode ('plusMinusAverage', n = '%s_dist_diff_pma' % name )
        cmds.createNode ('plusMinusAverage', n = '%s_defaultPos_pma' % name )
        
        #set operations
        cmds.setAttr ('%s_da_pma.operation' % name, 2 )
        cmds.setAttr ('%s_x_minus_da_pma.operation' % name, 2 )
        cmds.setAttr ('%s_negate_x_minus_md.operation' % name, 1 )
        cmds.setAttr ('%s_divBy_dSoft_md.operation' % name, 2 )
        cmds.setAttr ('%s_pow_e_md.operation' % name, 3 )
        cmds.setAttr ('%s_one_minus_pow_e_pma.operation' % name, 2 )
        cmds.setAttr ('%s_times_dSoft_md.operation' % name, 1 )
        cmds.setAttr ('%s_plus_da_pma.operation' % name, 1 )
        cmds.setAttr ('%s_da_cond.operation' % name, 5 )
        cmds.setAttr ('%s_dist_diff_pma.operation' % name, 2 )
        cmds.setAttr ('%s_defaultPos_pma.operation' % name, 2 )
        if( ( upAxis == 'X' ) and ( defPos > 0 ) ):
            cmds.setAttr ('%s_defaultPos_pma.operation' % name, 1 )
        if( upAxis == 'Y'):
            cmds.setAttr ('%s_defaultPos_pma.operation' % name, 2 )
        if( ( upAxis == 'Z' ) and ( defPos < 0 ) ):
            cmds.setAttr ('%s_defaultPos_pma.operation' % name, 1 )

    #-----------------------------------------------------------------------------------------------------------------------------#   	
        #make connections
        cmds.setAttr( '%s_da_pma.input1D[0]' % name, dChain )
        cmds.connectAttr( '%s.dSoft' % ctrlName, '%s_da_pma.input1D[1]' % name )
        
        cmds.connectAttr( '%s_x_distance.distance' % name, '%s_x_minus_da_pma.input1D[0]' % name )
        cmds.connectAttr( '%s_da_pma.output1D' % name, '%s_x_minus_da_pma.input1D[1]' % name )
        
        cmds.connectAttr( '%s_x_minus_da_pma.output1D' % name, '%s_negate_x_minus_md.input1X' % name )
        cmds.setAttr( '%s_negate_x_minus_md.input2X' % name, -1 )
        
        cmds.connectAttr( '%s_negate_x_minus_md.outputX' % name, '%s_divBy_dSoft_md.input1X' % name )
        cmds.connectAttr( '%s.dSoft' % ctrlName, '%s_divBy_dSoft_md.input2X' % name )
        
        cmds.setAttr( '%s_pow_e_md.input1X' % name, 2.718281828 )
        cmds.connectAttr( '%s_divBy_dSoft_md.outputX' % name, '%s_pow_e_md.input2X' % name )
        
        cmds.setAttr( '%s_one_minus_pow_e_pma.input1D[0]' % name, 1 )
        cmds.connectAttr( '%s_pow_e_md.outputX' % name, '%s_one_minus_pow_e_pma.input1D[1]' % name )
        
        cmds.connectAttr('%s_one_minus_pow_e_pma.output1D' % name, '%s_times_dSoft_md.input1X' % name )
        cmds.connectAttr( '%s.dSoft' % ctrlName, '%s_times_dSoft_md.input2X' % name )
        
        cmds.connectAttr( '%s_times_dSoft_md.outputX' % name, '%s_plus_da_pma.input1D[0]' % name )
        cmds.connectAttr( '%s_da_pma.output1D' % name, '%s_plus_da_pma.input1D[1]' % name )
        
        cmds.connectAttr( '%s_da_pma.output1D' % name, '%s_da_cond.firstTerm' % name )
        cmds.connectAttr( '%s_x_distance.distance' % name, '%s_da_cond.secondTerm' % name )
        cmds.connectAttr( '%s_x_distance.distance' % name, '%s_da_cond.colorIfFalseR' % name )
        cmds.connectAttr( '%s_plus_da_pma.output1D' % name, '%s_da_cond.colorIfTrueR' % name )
        
        cmds.connectAttr( '%s_da_cond.outColorR' % name, '%s_dist_diff_pma.input1D[0]' % name )
        cmds.connectAttr( '%s_x_distance.distance' % name, '%s_dist_diff_pma.input1D[1]' % name )
        
        cmds.setAttr( '%s_defaultPos_pma.input1D[0]' % name, defPos )
        cmds.connectAttr( '%s_dist_diff_pma.output1D' % name, '%s_defaultPos_pma.input1D[1]' % name )
        
#        cmds.connectAttr('%s_defaultPos_pma.output1D' % name, '%s.translate%s' % (ikhName, upAxis) )
        cmds.connectAttr('%s_defaultPos_pma.output1D' % name, '%s.translate%s' % (ikhName, upAxis) )
    #-----------------------------------------------------------------------------------------------------------------------------#
        #if stretch exists, we need to do this...
        
        if( stretch == True ):
            #add attribute to switch between stretchy and non-stretchy
            cmds.addAttr( ctrlName, ln = 'stretchSwitch', at = "double", min = 0, max = 10, dv = 10, k = True )
            
            cmds.createNode ('multiplyDivide', n = '%s_soft_ratio_md' % name )
            cmds.createNode ('blendColors', n = '%s_stretch_blend' % name )
            cmds.createNode ('multDoubleLinear', n = '%s_stretch_switch_mdl' % name )
            
            cmds.setAttr ('%s_soft_ratio_md.operation' % name, 2 )
            cmds.setAttr ('%s_stretch_blend.color2R' % name, 1 )
            cmds.setAttr ('%s_stretch_blend.color1G' % name, defPos )
            cmds.setAttr ('%s_stretch_switch_mdl.input2' % name, 0.1 )
            
            cmds.connectAttr ( '%s.stretchSwitch' % ctrlName, '%s_stretch_switch_mdl.input1' % name )
            cmds.connectAttr ( '%s_stretch_switch_mdl.output' % name, '%s_stretch_blend.blender' % name )
            cmds.connectAttr( '%s_x_distance.distance' % name, '%s_soft_ratio_md.input1X' % name )
            cmds.connectAttr( '%s_da_cond.outColorR' % name, '%s_soft_ratio_md.input2X' % name )
            cmds.connectAttr( '%s_defaultPos_pma.output1D' % name, '%s_stretch_blend.color2G' % name )
            cmds.connectAttr( '%s_soft_ratio_md.outputX' % name, '%s_stretch_blend.color1R' % name )
            
            cmds.connectAttr('%s_stretch_blend.outputG' % name, '%s.translate%s' % (ikhName, upAxis), force = True )
            i = 0
            while ( i < n - 1 ):
                cmds.connectAttr( '%s_stretch_blend.outputR' % name, '%s.scale%s' % (joints[i], primaryAxis), force = True )
                i += 1
