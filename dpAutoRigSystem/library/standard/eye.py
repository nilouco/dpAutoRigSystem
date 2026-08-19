# importing libraries:
from maya import cmds
from ..base import standard

# global variables to this module:    
CLASS_NAME = "Eye"
TITLE = "m063_eye"
DESCRIPTION = "m064_eyeDesc"
WIKI = "03-‐-Guides#-eye"

EYELID = "eyelid"
IRIS = "iris"
PUPIL = "pupil"
SPEC = "specular"
PIVOT = "lidPivot"



class Eye(standard.BaseStandard):
    def __init__(self, ar):
        standard.BaseStandard.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.cValue = 70
        self.aimMenuItemList = ['+X', '-X', '+Y', '-Y', '+Z', '-Z']
    
    
#    def create_module_layout(self):
#        standard.BaseStandard.create_module_layout(self)
    
    
    def create_guide(self, *args):
        self.create_guide_base()
        # Custom GUIDE:
        cmds.addAttr(self.guide_base, longName="flip", attributeType='bool')
        # adding extra attributes
        cmds.addAttr(self.guide_base, longName="aimDirection", attributeType='enum', enumName="+X:-X:+Y:-Y:+Z:-Z")
        cmds.setAttr(self.guide_base+".aimDirection", 4)
        cmds.addAttr(self.guide_base, longName="aimDirectionName", dataType='string')
        cmds.setAttr(self.guide_base+".aimDirectionName", "Z", type="string")
        cmds.addAttr(self.guide_base, longName="aimDirectionPositive", attributeType='bool')
        cmds.setAttr(self.guide_base+".aimDirectionPositive", 1)
        cmds.addAttr(self.guide_base, longName=EYELID, attributeType='bool')
        cmds.setAttr(self.guide_base+"."+EYELID, 1)
        cmds.addAttr(self.guide_base, longName=IRIS, attributeType='bool')
        cmds.setAttr(self.guide_base+"."+IRIS, 1)
        cmds.addAttr(self.guide_base, longName=PUPIL, attributeType='bool')
        cmds.setAttr(self.guide_base+"."+PUPIL, 1)
        cmds.addAttr(self.guide_base, longName=SPEC, attributeType='bool')
        cmds.addAttr(self.guide_base, longName=PIVOT, attributeType='bool')
        cmds.addAttr(self.guide_base, longName="deformedBy", minValue=0, defaultValue=1, maxValue=3, attributeType='long')
        cmds.addAttr(self.guide_base, longName="corrective", attributeType='bool')
        # main joint (center of eye globe)
        self.cvJointLoc = self.ar.ctrls.cvJointLoc(ctrlName=self.name_guide+"_JointLoc1", r=0.3, d=1, guide=True)
        self.jGuide1 = cmds.joint(name=self.name_guide+"_JGuide1", radius=0.001)
        cmds.setAttr(self.jGuide1+".template", 1)
        cmds.parent(self.jGuide1, self.guide_base, relative=True)
        # eyelid
        self.jEyelid = cmds.joint(name=self.name_guide+"_JEyelid", radius=0.001)
        # end joints (to aim)
        self.cvEndJoint = self.ar.ctrls.cvControl("id_059_AimLoc", ctrlName=self.name_guide+"_JointEnd", r=0.5, d=1, rot=(-90, 0, -90))
        self.ar.ctrls.colorShape([self.cvEndJoint], "blue")
        self.ar.ctrls.shapeSizeSetup(self.cvEndJoint)
        self.cvUpLocGuide = cmds.spaceLocator(name=self.cvEndJoint+"_UpLoc")[0]
        self.cvEndJointZero = cmds.group(self.cvEndJoint, self.cvUpLocGuide, name=self.cvEndJoint+"_Grp")
        self.cvEndBackRotGrp = cmds.group(self.cvEndJointZero, name=self.cvEndJointZero+"_Back_Grp")
        cmds.parent(self.cvEndBackRotGrp, self.guide_base)
        cmds.setAttr(self.cvEndJoint+".tz", 13)
        cmds.setAttr(self.cvUpLocGuide+".ty", 13)
        cmds.setAttr(self.cvUpLocGuide+".visibility", 0)
        cmds.orientConstraint(self.ar.data.temp_grp, self.cvEndBackRotGrp, maintainOffset=False, name=self.cvEndBackRotGrp+"_OrC")
        self.jGuideEnd = cmds.joint(name=self.name_guide+"_JGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        self.ar.ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
        # eyelid center pivot
        self.cvLidPivotLoc = self.ar.ctrls.cvLocator(ctrlName=self.name_guide+"_LidPivotLoc", r=0.5, d=1, guide=True)
        cmds.setAttr(self.cvLidPivotLoc+"0Shape.visibility", 0)
        cmds.parent(self.cvLidPivotLoc, self.cvJointLoc)
        # upper eyelid guide
        self.cvUpperEyelidLoc = self.ar.ctrls.cvLocator(ctrlName=self.name_guide+"_UpperEyelidLoc", r=0.2, d=1, guide=True)
        cmds.parent(self.cvUpperEyelidLoc, self.cvLidPivotLoc)
        cmds.setAttr(self.cvUpperEyelidLoc+".ty", 0.5)
        cmds.setAttr(self.cvUpperEyelidLoc+".tz", 0.5)
        self.ar.ctrls.setLockHide([self.cvUpperEyelidLoc], ['tx', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
        self.jUpperEyelid = cmds.joint(name=self.name_guide+"_JUpperEyelid", radius=0.001)
        cmds.setAttr(self.jUpperEyelid+".template", 1)
        # lower eyelid guide
        self.cvLowerEyelidLoc = self.ar.ctrls.cvLocator(ctrlName=self.name_guide+"_LowerEyelidLoc", r=0.2, d=1, guide=True)
        cmds.parent(self.cvLowerEyelidLoc, self.cvLidPivotLoc)
        cmds.setAttr(self.cvLowerEyelidLoc+".ty", -0.5)
        cmds.setAttr(self.cvLowerEyelidLoc+".tz", 0.5)
        self.ar.ctrls.setLockHide([self.cvLowerEyelidLoc], ['tx', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
        self.jLowerEyelid = cmds.joint(name=self.name_guide+"_JLowerEyelid", radius=0.001)
        cmds.setAttr(self.jLowerEyelid+".template", 1)
        # iris guide
        self.cvIrisLoc = self.ar.ctrls.cvLocator(ctrlName=self.name_guide+"_IrisLoc", r=0.15, d=1, guide=True)
        cmds.parent(self.cvIrisLoc, self.cvJointLoc)
        cmds.setAttr(self.cvIrisLoc+".tz", 0.4)
        # pupil guide
        self.cvPupilLoc = self.ar.ctrls.cvLocator(ctrlName=self.name_guide+"_PupilLoc", r=0.12, d=1, guide=True)
        cmds.parent(self.cvPupilLoc, self.cvJointLoc)
        cmds.setAttr(self.cvPupilLoc+".tz", 0.3)
        # specular guide
        self.cvSpecularLoc = self.ar.ctrls.cvLocator(ctrlName=self.name_guide+"_SpecularLoc", r=0.12, d=1, guide=True)
        cmds.parent(self.cvSpecularLoc, self.cvJointLoc)
        cmds.setAttr(self.cvSpecularLoc+".tz", 1)
        cmds.setAttr(self.cvSpecularLoc+".visibility", 0)
        # hierarchy mounting
        cmds.parent(self.cvJointLoc, self.guide_base)
        cmds.parent(self.jUpperEyelid, self.jLowerEyelid, self.jEyelid)
        cmds.parent(self.jGuideEnd, self.jGuide1)
        cmds.parentConstraint(self.cvJointLoc, self.jGuide1, maintainOffset=True, name=self.jGuide1+"_PaC")
        cmds.parentConstraint(self.cvUpperEyelidLoc, self.jUpperEyelid, maintainOffset=True, name=self.jUpperEyelid+"_PaC")
        cmds.parentConstraint(self.cvLowerEyelidLoc, self.jLowerEyelid, maintainOffset=True, name=self.jLowerEyelid+"_PaC")
        cmds.parentConstraint(self.cvEndJoint, self.jGuideEnd, maintainOffset=False, name=self.jGuideEnd+"_PaC")
        cmds.parentConstraint(self.cvLidPivotLoc, self.jEyelid, maintainOffset=False, name=self.jEyelid+"_PaC")
        # include nodes into net
        self.add_node_to_guide_net([self.cvJointLoc, self.cvEndJoint, self.cvLidPivotLoc, self.cvUpperEyelidLoc, self.cvLowerEyelidLoc, self.cvIrisLoc, self.cvPupilLoc, self.cvSpecularLoc, ], ["JointLoc1", "JointEnd", "_LidPivotLoc", "_UpperEyelidLoc", "_LowerEyelidLoc", "_IrisLoc", "_PupilLoc", "_SpecularLoc"])
    
    
    def changeEyelid(self, *args):
        """ Set the attribute value for eyelid.
        """
        # re-declaring variables:
        self.cvUpperEyelidLoc = self.name_guide+"_UpperEyelidLoc"
        self.cvLowerEyelidLoc = self.name_guide+"_LowerEyelidLoc"
        self.jEyelid = self.name_guide+"_JEyelid"
        self.jUpperEyelid = self.name_guide+"_JUpperEyelid"
        self.jLowerEyelid = self.name_guide+"_JLowerEyelid"
        # getting value:
        currentEyelidValue = cmds.checkBox('edit_guide_eyelid_cb', query=True, value=True)
        # setting values:
        cmds.setAttr(self.guide_base+".eyelid", currentEyelidValue)
        cmds.setAttr(self.cvUpperEyelidLoc+".visibility", currentEyelidValue)
        cmds.setAttr(self.cvLowerEyelidLoc+".visibility", currentEyelidValue)
        cmds.setAttr(self.jEyelid+".visibility", currentEyelidValue)
        cmds.setAttr(self.jUpperEyelid+".visibility", currentEyelidValue)
        cmds.setAttr(self.jLowerEyelid+".visibility", currentEyelidValue)
        cmds.checkBox('edit_guide_eyelid_pivot_cb', edit=True, value=currentEyelidValue)
        self.changeLidPivot()
        
        
    def changeSpecular(self, *args):
        """ Set the attribute value for specular.
        """
        self.cvSpecularLoc = self.name_guide+"_SpecularLoc"
        cmds.setAttr(self.guide_base+".specular", cmds.checkBox('edit_guide_eyelid_specular_cb', query=True, value=True))
        cmds.setAttr(self.cvSpecularLoc+".visibility", cmds.checkBox('edit_guide_eyelid_specular_cb', query=True, value=False))


    def changeLidPivot(self, *args):
        """ Set the attribute value for eyelid center pivot.
        """
        self.cvLidPivotLoc = self.name_guide+"_LidPivotLoc"
        cmds.setAttr(self.guide_base+".lidPivot", cmds.checkBox('edit_guide_eyelid_pivot_cb', query=True, value=True))
        cmds.setAttr(self.cvLidPivotLoc+"0Shape.visibility", cmds.checkBox('edit_guide_eyelid_pivot_cb', query=True, value=False))


    def changeIris(self, *args):
        """ Set the attribute value for iris.
        """
        self.cvIrisLoc = self.name_guide+"_IrisLoc"
        cmds.setAttr(self.guide_base+".iris", cmds.checkBox('edit_guide_eyelid_iris_cb', query=True, value=True))
        cmds.setAttr(self.cvIrisLoc+".visibility", cmds.checkBox('edit_guide_eyelid_iris_cb', query=True, value=True))
        
    
    def changePupil(self, *args):
        """ Set the attribute value for pupil.
        """
        self.cvPupilLoc = self.name_guide+"_PupilLoc"
        cmds.setAttr(self.guide_base+".pupil", cmds.checkBox('edit_guide_eyelid_pupil_cb', query=True, value=True))
        cmds.setAttr(self.cvPupilLoc+".visibility", cmds.checkBox('edit_guide_eyelid_pupil_cb', query=True, value=True))
        
    
    def changeAimDirection(self, item, *args):
        """ Set the good direction for Eye look at Aim setup.
        """
        if self.check_guide_integrity():
            # re-declaring variables:
            self.jGuideEnd = self.name_guide+"_JGuideEnd"
            self.cvEndJointZero = self.name_guide+"_JointEnd_Grp"
            # setting attributes:
            cmds.setAttr(self.guide_base+".aimDirection", self.aimMenuItemList.index(item))
            cmds.setAttr(self.guide_base+".aimDirectionName", item[1], type='string')
            cmds.setAttr(self.guide_base+".aimDirectionPositive", 0)
            if item[0] == "+":
                cmds.setAttr(self.guide_base+".aimDirectionPositive", 1)
            # changing module aim guides:
            cmds.setAttr(self.cvEndJointZero+".rotateX", 0)
            cmds.setAttr(self.cvEndJointZero+".rotateY", 0)
            if item[1] == "X":
                if item[0] == "+":
                    cmds.setAttr(self.cvEndJointZero+".rotateY", 90)
                else:
                    cmds.setAttr(self.cvEndJointZero+".rotateY", -90)
            if item[1] == "Y":
                if item[0] == "+":
                    cmds.setAttr(self.cvEndJointZero+".rotateX", -90)
                else:
                    cmds.setAttr(self.cvEndJointZero+".rotateX", 90)
            if item[1] == "Z":
                if item[0] == "-":
                    cmds.setAttr(self.cvEndJointZero+".rotateY", 180)
    
    
    def createEyelidJoints(self, side, lid, middle, cvEyelidLoc, jointLabelNumber, *args):
        ''' Create the eyelid joints to be used in the needed setup.
            Returns EyelidBaseJxt and EyelidJnt created for rotate and skinning.
        '''
        # declating a concatenated name used for base to compose:
        baseName = side+self.number_name+"_"+self.ar.data.lang[lid]+"_"+self.ar.data.lang['c042_eyelid']+middle
        # creating joints:
        eyelidBaseZeroJxt = cmds.joint(name=baseName+"_Base_Zero_Jxt", rotationOrder="yzx", scaleCompensate=False)
        eyelidBaseJxt = cmds.joint(name=baseName+"_Base_Jxt", rotationOrder="yzx", scaleCompensate=False)
        eyelidZeroJxt = cmds.joint(name=baseName+"_Zero_Jxt", rotationOrder="yzx", scaleCompensate=False)
        eyelidJnt = cmds.joint(name=baseName+"_Jnt", rotationOrder="yzx", scaleCompensate=False)
        cmds.addAttr(eyelidJnt, longName='dpAR_joint', attributeType='float', keyable=False)
        self.ar.utils.setJointLabel(eyelidJnt, jointLabelNumber, 18, self.number_name+"_"+self.ar.data.lang[lid]+"_"+self.ar.data.lang['c042_eyelid']+middle)
        cmds.select(eyelidZeroJxt)
        eyelidSupportJxt = cmds.joint(name=baseName+"_Jxt", rotationOrder="yzx", scaleCompensate=False)
        cmds.setAttr(eyelidSupportJxt+".translateX", self.radius*0.1)
        # positioning and orienting correctely eyelid joints:
        cmds.delete(cmds.aimConstraint(cvEyelidLoc, eyelidBaseZeroJxt, aimVector=(0,0,1), worldUpType="objectrotation", worldUpObject=self.eyelidJxt))
        cmds.delete(cmds.parentConstraint(cvEyelidLoc, eyelidZeroJxt, mo=False))
        cmds.setAttr(eyelidZeroJxt+".rotateX", 0)
        cmds.setAttr(eyelidZeroJxt+".rotateY", 0)
        cmds.setAttr(eyelidZeroJxt+".rotateZ", 0)
        cmds.select(self.eyelidJxt)
        return eyelidBaseJxt, eyelidJnt


    def createEyelidSetup(self, side, lid, eyelidJnt, eyelidBaseJxt, eyelidMiddleBaseJxt, eyelidMiddleJnt, preset, rotCtrl, cvEyelidLoc, *args):
        ''' Work with the joints created in order to develop a solid and stable eyelid setup for blink and facial eye expressions using direct skinning process in the final render mesh.
            Returns the main controller and its zeroOut group.
        '''
        # declating a concatenated name used for base to compose:
        baseName = side+self.number_name+"_"+self.ar.data.lang[lid]+"_"+self.ar.data.lang['c042_eyelid']
        # creating eyelid control:
        eyelidCtrl = self.ar.ctrls.cvControl("id_008_Eyelid", baseName+"_Ctrl", self.radius*0.4, d=self.curve_degree, rot=rotCtrl, headDef=self.headDefValue, guideSource=self.name_guide+"__"+cvEyelidLoc.replace("_Guide", ":Guide"), parentTag=self.fkEyeSubCtrl)
        self.ar.utils.originedFrom(objName=eyelidCtrl, attrString=cvEyelidLoc)
        eyelidCtrlZero = self.ar.utils.zeroOut([eyelidCtrl])[0]
        self.ar.ctrls.setLockHide([eyelidCtrl], ['tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v', 'ro'])
        cmds.parent(eyelidCtrlZero, self.baseEyeCtrl)
        # positioning correctely eyelid control:
        cmds.delete(cmds.parentConstraint(self.eyelidJxt, eyelidCtrlZero, mo=False))
        cmds.delete(cmds.pointConstraint(eyelidJnt, eyelidCtrlZero, mo=False))
        cmds.xform(eyelidCtrlZero, translation=(0, 0, self.radius), relative=True)
        # adding useful control attributes to calibrate eyelid setup:
        cmds.addAttr(eyelidCtrl, longName=self.ar.data.lang['c049_intensity']+"X", attributeType="float", minValue=0, defaultValue=1)
        cmds.addAttr(eyelidCtrl, longName=self.ar.data.lang['c049_intensity']+"Y", attributeType="float", minValue=0, defaultValue=1)
        cmds.addAttr(eyelidCtrl, longName=self.ar.data.lang['c032_follow'], attributeType="float", minValue=0, defaultValue=0.6, maxValue=1)
        cmds.setAttr(eyelidCtrl+"."+self.ar.data.lang['c049_intensity']+"X", keyable=False, channelBox=True)
        cmds.setAttr(eyelidCtrl+"."+self.ar.data.lang['c049_intensity']+"Y", keyable=False, channelBox=True)
        cmds.setAttr(eyelidCtrl+"."+self.ar.data.lang['c032_follow'], channelBox=True)
        cmds.setAttr(eyelidCtrl+"."+self.ar.data.lang['c032_follow'], keyable=True)
        cmds.addAttr(eyelidCtrl, longName=self.ar.data.lang['c053_invert']+"X", attributeType="bool", defaultValue=0)
        cmds.addAttr(eyelidCtrl, longName=self.ar.data.lang['c053_invert']+"Y", attributeType="bool", defaultValue=0)
        cmds.addAttr(eyelidCtrl, longName=self.ar.data.lang['c053_invert']+self.ar.data.lang['c029_middle'], attributeType="bool", defaultValue=0)
        cmds.addAttr(eyelidCtrl, longName=self.ar.data.lang['c051_preset']+"X", attributeType="float", defaultValue=preset, keyable=False)
        cmds.addAttr(eyelidCtrl, longName=self.ar.data.lang['c051_preset']+"Y", attributeType="float", defaultValue=preset, keyable=False)
        cmds.addAttr(eyelidCtrl, longName=self.ar.data.lang['c050_proximity']+self.ar.data.lang['c029_middle'], attributeType="float", minValue=0, defaultValue=0.5, maxValue=1, keyable=False)
        cmds.addAttr(eyelidCtrl, longName=self.ar.data.lang['c052_fix']+"ScaleX", attributeType="float", defaultValue=0.01, minValue=0, keyable=False)
        cmds.addAttr(eyelidCtrl, longName=self.ar.data.lang['c052_fix']+"TranslateZ", attributeType="float", defaultValue=0.15, minValue=0, keyable=False)
        cmds.addAttr(eyelidCtrl, longName=self.ar.data.lang['c052_fix']+self.ar.data.lang['c029_middle']+"TranslateZ", attributeType="float", defaultValue=0.3, minValue=0, keyable=False)
        cmds.addAttr(eyelidCtrl, longName=self.ar.data.lang['c107_reduce']+self.ar.data.lang['c029_middle']+"Open", attributeType="float", defaultValue=0.2, minValue=0, maxValue=1, keyable=False)
        # creating utility nodes to eyelid setup:
        eyelidIntensityMD = cmds.createNode('multiplyDivide', name=baseName+"_Intensity_MD")
        eyelidInvertMD = cmds.createNode('multiplyDivide', name=baseName+"_Invert_MD")
        eyelidInvertXCnd = cmds.createNode('condition', name=baseName+"_InvertX_Cnd")
        eyelidInvertYCnd = cmds.createNode('condition', name=baseName+"_InvertY_Cnd")
        eyelidInvertYMiddleCnd = cmds.createNode('condition', name=baseName+"_InvertY_Middle_Cnd")
        eyelidInvertFixMiddleCnd = cmds.createNode('condition', name=baseName+"_InvertFix_Middle_Cnd")
        eyelidPresetMD = cmds.createNode('multiplyDivide', name=baseName+"_Preset_MD")
        eyelidMiddleMD = cmds.createNode('multiplyDivide', name=baseName+"_Middle_MD")
        eyelidMiddleCnd = cmds.createNode('condition', name=baseName+"_Middle_Cnd")
        eyelidFixMD = cmds.createNode('multiplyDivide', name=baseName+"_Fix_MD")
        eyelidFixPMA = cmds.createNode('plusMinusAverage', name=baseName+"_Fix_PMA")
        eyelidFixModulusXCnd = cmds.createNode('condition', name=baseName+"_Fix_ModulusX_Cnd")
        eyelidFixModulusYMiddleCnd = cmds.createNode('condition', name=baseName+"_Fix_ModulusYMiddle_Cnd")
        eyelidFixModulusYCnd = cmds.createNode('condition', name=baseName+"_Fix_ModulusY_Cnd")
        eyelidFixNegativeMD = cmds.createNode('multiplyDivide', name=baseName+"_Fix_Negative_MD")
        eyelidReduceOpenMiddleMD = cmds.createNode('multiplyDivide', name=baseName+"_Reduce_MiddleOpen_MD")
        eyelidInvertOpenMiddleMD = cmds.createNode('multiplyDivide', name=baseName+"_Invert_MiddleOpen_MD")
        eyelidFixInvertOpenMiddleMD = cmds.createNode('multiplyDivide', name=baseName+"_Fix_Invert_MiddleOpen_MD")
        eyelidFixMiddleMD = cmds.createNode('multiplyDivide', name=baseName+"_Fix_Middle_MD")
        eyelidFixMiddleTZMD = cmds.createNode('multiplyDivide', name=baseName+"_Fix_MiddleTZ_MD")
        eyelidFixMiddleScaleClp = cmds.createNode('clamp', name=baseName+"_Fix_Middle_Clp")
        eyelidFollowRev = cmds.createNode('reverse', name=baseName+"_Follow_Rev")
        self.to_ids.extend([eyelidIntensityMD, eyelidInvertMD, eyelidInvertXCnd, eyelidInvertYCnd, eyelidInvertYMiddleCnd, eyelidInvertFixMiddleCnd, eyelidPresetMD, eyelidMiddleMD, eyelidMiddleCnd, eyelidFixMD,
                              eyelidFixPMA, eyelidFixModulusXCnd, eyelidFixModulusYMiddleCnd, eyelidFixModulusYCnd, eyelidFixNegativeMD, eyelidReduceOpenMiddleMD, eyelidInvertOpenMiddleMD, eyelidFixInvertOpenMiddleMD,
                              eyelidFixMiddleMD, eyelidFixMiddleTZMD, eyelidFixMiddleScaleClp, eyelidFollowRev])
        # seting up the node attributes:
        cmds.setAttr(eyelidInvertXCnd+".colorIfTrueR", 1)
        cmds.setAttr(eyelidInvertXCnd+".colorIfFalseR", -1)
        cmds.setAttr(eyelidInvertYCnd+".colorIfTrueR", 1)
        cmds.setAttr(eyelidInvertYCnd+".colorIfFalseR", -1)
        cmds.setAttr(eyelidInvertYMiddleCnd+".colorIfTrueR", 4)
        cmds.setAttr(eyelidInvertYMiddleCnd+".colorIfFalseR", 2)
        cmds.setAttr(eyelidInvertFixMiddleCnd+".secondTerm", 1)
        cmds.setAttr(eyelidInvertFixMiddleCnd+".colorIfTrueR", 5)
        cmds.setAttr(eyelidInvertFixMiddleCnd+".colorIfFalseR", 3)
        cmds.setAttr(eyelidInvertFixMiddleCnd+".colorIfTrueG", -1)
        cmds.setAttr(eyelidInvertFixMiddleCnd+".colorIfFalseG", 1)
        cmds.setAttr(eyelidInvertFixMiddleCnd+".colorIfTrueB", 1)
        cmds.setAttr(eyelidInvertFixMiddleCnd+".colorIfFalseB", -1)
        cmds.setAttr(eyelidFixNegativeMD+".input2X", -1)
        cmds.setAttr(eyelidFixModulusXCnd+".operation", 3)
        cmds.setAttr(eyelidFixPMA+".input3D[0].input3Dx", 1)
        cmds.setAttr(eyelidFixNegativeMD+".input2Y", -1)
        cmds.setAttr(eyelidFixModulusYCnd+".operation", 3)
        cmds.setAttr(eyelidFixMiddleScaleClp+".minR", 1)
        cmds.setAttr(eyelidFixMiddleScaleClp+".maxR", 1000)
        cmds.setAttr(eyelidMiddleCnd+".colorIfFalseR", 1)
        # connecting eyelid control to nodes and joints:
        cmds.connectAttr(eyelidCtrl+".translateX", eyelidInvertMD+".input1X", force=True)
        cmds.connectAttr(eyelidCtrl+".translateY", eyelidInvertMD+".input1Y", force=True)
        # working with invert nodes in order to be able to adjust the control by User after the setup done:
        cmds.connectAttr(eyelidCtrl+"."+self.ar.data.lang['c053_invert']+"X", eyelidInvertXCnd+".firstTerm", force=True)
        cmds.connectAttr(eyelidCtrl+"."+self.ar.data.lang['c053_invert']+"Y", eyelidInvertYCnd+".firstTerm", force=True)
        cmds.connectAttr(eyelidCtrl+"."+self.ar.data.lang['c053_invert']+"Y", eyelidInvertYMiddleCnd+".firstTerm", force=True)
        cmds.connectAttr(eyelidCtrl+"."+self.ar.data.lang['c053_invert']+self.ar.data.lang['c029_middle'], eyelidInvertFixMiddleCnd+".firstTerm", force=True)
        cmds.connectAttr(eyelidInvertXCnd+".outColorR", eyelidInvertMD+".input2X", force=True)
        cmds.connectAttr(eyelidInvertYCnd+".outColorR", eyelidInvertMD+".input2Y", force=True)
        cmds.connectAttr(eyelidInvertMD+".outputX", eyelidIntensityMD+".input1X", force=True)
        cmds.connectAttr(eyelidInvertMD+".outputY", eyelidIntensityMD+".input1Y", force=True)
        # working with intensity attributes in order to chose the control force by User:
        cmds.connectAttr(eyelidCtrl+"."+self.ar.data.lang['c049_intensity']+"X", eyelidIntensityMD+".input2X", force=True)
        cmds.connectAttr(eyelidCtrl+"."+self.ar.data.lang['c049_intensity']+"Y", eyelidIntensityMD+".input2Y", force=True)
        cmds.connectAttr(eyelidIntensityMD+".outputX", eyelidPresetMD+".input1X", force=True)
        cmds.connectAttr(eyelidIntensityMD+".outputY", eyelidPresetMD+".input1Y", force=True)
        # working with the predefined values in order to help the Rigger calibrate the control intensity preset:
        cmds.connectAttr(eyelidCtrl+"."+self.ar.data.lang['c051_preset']+"X", eyelidPresetMD+".input2X", force=True)
        cmds.connectAttr(eyelidCtrl+"."+self.ar.data.lang['c051_preset']+"Y", eyelidPresetMD+".input2Y", force=True)
        cmds.connectAttr(eyelidPresetMD+".outputX", eyelidBaseJxt+".rotateZ", force=True)
        cmds.connectAttr(eyelidPresetMD+".outputY", eyelidBaseJxt+".rotateX", force=True)
        # setup the middle extra joint to be skinned as a helper to deform correctly the mesh following the main eyelid joint:
        cmds.connectAttr(eyelidPresetMD+".outputX", eyelidMiddleMD+".input1X", force=True)
        cmds.connectAttr(eyelidPresetMD+".outputY", eyelidMiddleMD+".input1Y", force=True)
        # using the proximity attribute to let User chose the good deformation on the skinning:
        cmds.connectAttr(eyelidCtrl+"."+self.ar.data.lang['c050_proximity']+self.ar.data.lang['c029_middle'], eyelidMiddleMD+".input2X", force=True)
        cmds.connectAttr(eyelidCtrl+"."+self.ar.data.lang['c050_proximity']+self.ar.data.lang['c029_middle'], eyelidMiddleCnd+".colorIfTrueR", force=True)
        cmds.connectAttr(eyelidBaseJxt+".rotateX", eyelidMiddleCnd+".firstTerm", force=True)
        cmds.connectAttr(eyelidMiddleCnd+".outColorR", eyelidMiddleMD+".input2Y", force=True)
        cmds.connectAttr(eyelidInvertYMiddleCnd+".outColorR", eyelidMiddleCnd+".operation", force=True)
        cmds.connectAttr(eyelidMiddleMD+".outputX", eyelidMiddleBaseJxt+".rotateZ", force=True)
        cmds.connectAttr(eyelidMiddleMD+".outputY", eyelidMiddleBaseJxt+".rotateX", force=True)
        if "lower" in lid:
            cmds.setAttr(eyelidInvertYMiddleCnd+".secondTerm", 1)
        # try to fix the maintain volume by mimic the SetDrivenKey and SculptDeform technique using nodes to scale and translate the skinned joints:
        cmds.connectAttr(eyelidIntensityMD+".outputY", eyelidFixMD+".input1X", force=True)
        cmds.connectAttr(eyelidIntensityMD+".outputY", eyelidFixMD+".input1Y", force=True)
        cmds.connectAttr(eyelidIntensityMD+".outputY", eyelidFixMiddleTZMD+".input1Y", force=True)
        cmds.connectAttr(eyelidCtrl+"."+self.ar.data.lang['c052_fix']+"ScaleX", eyelidFixMD+".input2X", force=True)
        cmds.connectAttr(eyelidCtrl+"."+self.ar.data.lang['c052_fix']+"TranslateZ", eyelidFixMD+".input2Y", force=True)
        cmds.connectAttr(eyelidCtrl+"."+self.ar.data.lang['c052_fix']+self.ar.data.lang['c029_middle']+"TranslateZ", eyelidFixMiddleTZMD+".input2Y", force=True)
        # modulus of fix values in order to avoid opositive values when the control pass to another direction from start position:
        cmds.connectAttr(eyelidFixMD+".outputX", eyelidFixModulusXCnd+".firstTerm", force=True)
        cmds.connectAttr(eyelidFixMD+".outputX", eyelidFixModulusXCnd+".colorIfTrueR", force=True)
        cmds.connectAttr(eyelidFixMD+".outputX", eyelidFixNegativeMD+".input1X", force=True)
        cmds.connectAttr(eyelidFixNegativeMD+".outputX", eyelidFixModulusXCnd+".colorIfFalseR", force=True)
        cmds.connectAttr(eyelidFixModulusXCnd+".outColorR", eyelidFixPMA+".input3D[1].input3Dx", force=True)
        cmds.connectAttr(eyelidFixMD+".outputY", eyelidFixModulusYCnd+".firstTerm", force=True)
        cmds.connectAttr(eyelidFixMD+".outputY", eyelidFixModulusYCnd+".colorIfTrueR", force=True)
        cmds.connectAttr(eyelidFixMD+".outputY", eyelidFixNegativeMD+".input1Y", force=True)
        cmds.connectAttr(eyelidFixNegativeMD+".outputY", eyelidFixModulusYCnd+".colorIfFalseR", force=True)
        cmds.connectAttr(eyelidFixPMA+".output3Dx", eyelidJnt+".scaleX", force=True)
        cmds.connectAttr(eyelidFixModulusYCnd+".outColorR", eyelidJnt+".translateZ", force=True)
        # fixing middle joint proximity:
        cmds.connectAttr(eyelidFixMiddleTZMD+".outputY", eyelidReduceOpenMiddleMD+".input1Y", force=True)
        cmds.connectAttr(eyelidCtrl+"."+self.ar.data.lang['c107_reduce']+self.ar.data.lang['c029_middle']+"Open", eyelidReduceOpenMiddleMD+".input2Y", force=True)
        cmds.connectAttr(eyelidReduceOpenMiddleMD+".outputY", eyelidInvertOpenMiddleMD+".input1Y", force=True)
        cmds.connectAttr(eyelidFixMiddleTZMD+".outputY", eyelidFixModulusYMiddleCnd+".firstTerm", force=True)
        cmds.connectAttr(eyelidFixMiddleTZMD+".outputY", eyelidFixInvertOpenMiddleMD+".input1Y", force=True)
        cmds.connectAttr(eyelidFixInvertOpenMiddleMD+".outputY", eyelidFixModulusYMiddleCnd+".colorIfTrueR", force=True)
        cmds.connectAttr(eyelidInvertOpenMiddleMD+".outputY", eyelidFixModulusYMiddleCnd+".colorIfFalseR", force=True)
        cmds.connectAttr(eyelidFixModulusYMiddleCnd+".outColorR", eyelidFixMiddleMD+".input1Y", force=True)
        cmds.connectAttr(eyelidCtrl+"."+self.ar.data.lang['c050_proximity']+self.ar.data.lang['c029_middle'], eyelidFixMiddleMD+".input2X", force=True)
        cmds.connectAttr(eyelidCtrl+"."+self.ar.data.lang['c050_proximity']+self.ar.data.lang['c029_middle'], eyelidFixMiddleMD+".input2Y", force=True)
        cmds.connectAttr(eyelidFixMiddleMD+".outputX", eyelidFixMiddleScaleClp+".inputR", force=True)
        cmds.connectAttr(eyelidFixMiddleScaleClp+".outputR", eyelidMiddleJnt+".scaleX", force=True)
        cmds.connectAttr(eyelidFixMiddleMD+".outputY", eyelidMiddleJnt+".translateZ", force=True)
        cmds.connectAttr(eyelidInvertFixMiddleCnd+".outColorR", eyelidFixModulusYMiddleCnd+".operation", force=True)
        cmds.connectAttr(eyelidInvertFixMiddleCnd+".outColorG", eyelidFixInvertOpenMiddleMD+".input2Y", force=True)
        cmds.connectAttr(eyelidInvertFixMiddleCnd+".outColorB", eyelidInvertOpenMiddleMD+".input2Y", force=True)
        # follow setup:
        eyelidBaseZeroJxt = cmds.listRelatives(eyelidBaseJxt, parent=True)[0]
        eyelidMiddleBaseZeroJxt = cmds.listRelatives(eyelidMiddleBaseJxt, parent=True)[0]
        followPC = cmds.parentConstraint(self.jxt, self.eyeScaleJnt, eyelidBaseZeroJxt, skipTranslate=["x", "y", "z"], skipRotate=["y", "z"], maintainOffset=1, name=baseName+"_Follow_PaC")[0]
        cmds.setAttr(followPC+".interpType", 2)
        cmds.connectAttr(eyelidCtrl+"."+self.ar.data.lang['c032_follow'], followPC+"."+self.jxt+"W0", force=True)
        cmds.connectAttr(eyelidCtrl+"."+self.ar.data.lang['c032_follow'], eyelidFollowRev+".inputX", force=True)
        cmds.connectAttr(eyelidFollowRev+".outputX", followPC+"."+self.eyeScaleJnt+"W1", force=True)
        cmds.connectAttr(eyelidBaseZeroJxt+".rotateX", eyelidMiddleBaseZeroJxt+".rotateX", force=True)
        # corrective network
        if self.corrective:
            self.setup_corrective_net(eyelidCtrl, eyelidBaseJxt, cmds.listRelatives(eyelidBaseJxt, parent=True)[0], baseName, 0, 0, -self.cValue)
        # calibration attribute:
        eyelidCalibrationList = [
            self.ar.data.lang['c049_intensity']+"X",
            self.ar.data.lang['c049_intensity']+"Y",
            self.ar.data.lang['c032_follow'],
            self.ar.data.lang['c053_invert']+"X",
            self.ar.data.lang['c053_invert']+"Y",
            self.ar.data.lang['c053_invert']+self.ar.data.lang['c029_middle'],
            self.ar.data.lang['c051_preset']+"X",
            self.ar.data.lang['c051_preset']+"Y",
            self.ar.data.lang['c050_proximity']+self.ar.data.lang['c029_middle'],
            self.ar.data.lang['c052_fix']+"ScaleX",
            self.ar.data.lang['c052_fix']+"TranslateZ",
            self.ar.data.lang['c052_fix']+self.ar.data.lang['c029_middle']+"TranslateZ",
            self.ar.data.lang['c107_reduce']+self.ar.data.lang['c029_middle']+"Open"
        ]
        eyelidNotMirrorList = [self.ar.data.lang['c053_invert']+"X",
                               self.ar.data.lang['c053_invert']+"Y",
                               self.ar.data.lang['c053_invert']+self.ar.data.lang['c029_middle']]
        self.ar.ctrls.setStringAttrFromList(eyelidCtrl, eyelidCalibrationList)
        self.ar.ctrls.setStringAttrFromList(eyelidCtrl, eyelidNotMirrorList, "notMirrorList") #useful to export calibrationIO and not mirror them
        return eyelidCtrl, eyelidCtrlZero
        
        
    def createIrisPupilSetup(self, s, side, type, codeName, jointLabelNumber, *args):
        ''' Predefined function to add Iris or Pupil setup.
            Returns control.
        '''
        # declare cv guides:
        cvLoc = side+self.number_name+"_Guide_"+type.capitalize()+"Loc"
        # creating joint:
        mainJnt = cmds.joint(name=side+self.number_name+"_"+self.ar.data.lang[codeName]+"_1_Jnt", scaleCompensate=False)
        cmds.addAttr(mainJnt, longName='dpAR_joint', attributeType='float', keyable=False)
        self.ar.utils.setJointLabel(mainJnt, jointLabelNumber, 18, self.number_name+"_"+self.ar.data.lang[codeName]+"_1")
        # joint position:
        cmds.delete(cmds.parentConstraint(cvLoc, mainJnt, maintainOffset=False))
        # create end joint:
        endJoint = cmds.joint(name=side+self.number_name+"_"+self.ar.data.lang[codeName]+"_"+self.ar.data.joint_end_attr, scaleCompensate=False, radius=0.5)
        self.ar.utils.addJointEndAttr([endJoint])
        cmds.delete(cmds.parentConstraint(mainJnt, endJoint, maintainOffset=False))
        cmds.setAttr(endJoint+".translateZ", self.radius)
        # creating control:
        if type == IRIS:
            ctrlId = "id_012_EyeIris"
            radius = 0.4*self.radius
        else:
            ctrlId = "id_013_EyePupil"
            radius = 0.2*self.radius
        ctrl = self.ar.ctrls.cvControl(ctrlId, side+self.number_name+"_"+self.ar.data.lang[codeName]+"_1_Ctrl", r=radius, d=self.curve_degree, headDef=self.headDefValue, guideSource=self.name_guide+"__"+cvLoc.replace("_Guide", ":Guide"), parentTag=self.fkEyeSubCtrl)
        self.ar.utils.originedFrom(objName=ctrl, attrString=cvLoc)
        cmds.makeIdentity(ctrl, rotate=True, apply=True)
        # create constraints and arrange hierarchy:
        ctrlZero = self.ar.utils.zeroOut([ctrl], offset=True)
        cmds.setAttr(cmds.listRelatives(ctrlZero, children=True, type="transform")[0]+".dpNotTransformIO", 0)
        cmds.delete(cmds.parentConstraint(cvLoc, ctrlZero[0], maintainOffset=False))
        cmds.parent(ctrlZero[0], self.baseEyeCtrl)
        # fixing flip mirror:
        if s == 1:
            if cmds.getAttr(self.guide_base+".flip") == 1:
                if not "X" == cmds.getAttr(self.guide_base+".aimDirectionName"):
                    cmds.setAttr(ctrlZero[0]+".scaleX", -1)
                else:
                    cmds.setAttr(ctrlZero[0]+".scaleX", 1)
                if not "Y" == cmds.getAttr(self.guide_base+".aimDirectionName"):
                    cmds.setAttr(ctrlZero[0]+".scaleY", -1)
                else:
                    cmds.setAttr(ctrlZero[0]+".scaleY", 1)
                if not "Z" == cmds.getAttr(self.guide_base+".aimDirectionName"):
                    cmds.setAttr(ctrlZero[0]+".scaleZ", -1)
                else:
                    cmds.setAttr(ctrlZero[0]+".scaleZ", 1)
            cmds.setAttr(endJoint+".translateZ", -self.radius)
        cmds.parentConstraint(self.fkEyeSubCtrl, ctrlZero[0], maintainOffset=True, name=ctrlZero[0]+"_PaC")
        cmds.scaleConstraint(self.fkEyeSubCtrl, ctrlZero[0], maintainOffset=True, name=ctrlZero[0]+"_ScC")
        cmds.parent(mainJnt, self.jnt)
        cmds.parentConstraint(ctrl, mainJnt, maintainOffset=False, name=mainJnt+"_PaC")
        cmds.scaleConstraint(ctrl, mainJnt, maintainOffset=True, name=mainJnt+"_ScC")
        return ctrl
    
    
    def rig_me(self, *args):
        standard.BaseStandard.rig_me(self)
        # verify if the guide exists:
        if cmds.objExists(self.guide_base):
            # create lists to export:
            self.eyeScaleGrpList, self.irisCtrlList, self.pupilCtrlList = [], [], []
            self.hasIris = False
            self.hasPupil = False
            # create the main control:
            self.eyeCtrl = self.ar.ctrls.cvControl("id_010_EyeLookAtMain", self.number_name+"_"+self.ar.data.lang['c058_main']+"_Ctrl", r=(2.25*self.radius), d=self.curve_degree, guideSource=self.name_guide+"_JointEnd")
            cmds.addAttr(self.eyeCtrl, longName=self.ar.data.lang['c032_follow'], attributeType='float', keyable=True, minValue=0, maxValue=1, defaultValue=1)
            cmds.delete(cmds.parentConstraint(self.sides[0]+self.number_name+"_Guide_JointEnd", self.eyeCtrl, maintainOffset=False))
            if self.mirror_axis != 'off':
                cmds.setAttr(self.eyeCtrl+".translate"+self.mirror_axis, 0)
            self.eyeGrp = cmds.group(self.eyeCtrl, name=self.number_name+"_"+self.ar.data.lang['c058_main']+"_Grp")
            self.ar.utils.zeroOut([self.eyeCtrl])
            self.upLocGrp = cmds.group(name=self.number_name+"_UpLoc_Grp", empty=True)
            self.to_ids.append(self.upLocGrp)
            # run for all sides:
            for s, side in enumerate(self.sides):
                cmds.select(clear=True)
                self.base = side+self.number_name+'_Guide_Base'
                # declare guide:
                self.guide = side+self.number_name+"_Guide_JointLoc1"
                self.cvEndJointZero = side+self.number_name+"_Guide_JointEnd_Grp"
                self.radiusGuide = side+self.number_name+"_Guide_Base_RadiusCtrl"
                self.cvSpecularLoc = side+self.number_name+"_Guide_SpecularLoc"
                self.headDefValue = cmds.getAttr(self.base+".deformedBy")
                # create a joint:
                self.jxt = cmds.joint(name=side+self.number_name+"_1_Jxt", scaleCompensate=False)
                self.subJnt = cmds.joint(name=side+self.number_name+"_1_Sub_Jxt", scaleCompensate=False)
                self.jnt = cmds.joint(name=side+self.number_name+"_1_Jnt", scaleCompensate=False)
                cmds.addAttr(self.jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                self.ar.utils.setJointLabel(self.jnt, s+self.joint_label_add, 18, self.number_name+"_1")
                if s == 1:
                    lEyeFkCtrlData = self.ar.utils.getTransformData(self.fkEyeCtrl)
                self.baseEyeCtrl = self.ar.ctrls.cvControl("id_009_EyeBase", ctrlName=side+self.number_name+"_Base_Ctrl", r=self.radius, d=self.curve_degree, headDef=self.headDefValue, guideSource=self.name_guide+"_JointLoc1")
                self.fkEyeCtrl = self.ar.ctrls.cvControl("id_014_EyeFk", side+self.number_name+"_Fk_Ctrl", r=self.radius, d=self.curve_degree, headDef=self.headDefValue, guideSource=self.name_guide+"_JointLoc1", parentTag=self.baseEyeCtrl)
                self.fkEyeSubCtrl = self.ar.ctrls.cvControl("id_070_EyeFkSub", side+self.number_name+"_Fk_Sub_Ctrl", r=(0.75*self.radius), d=self.curve_degree, headDef=self.headDefValue, guideSource=self.name_guide+"_JointLoc1", parentTag=self.fkEyeCtrl)
                self.ar.utils.originedFrom(objName=self.fkEyeCtrl, attrString=self.base+";"+self.guide+";"+self.radiusGuide)
                self.ar.utils.originedFrom(objName=self.baseEyeCtrl, attrString=self.base+";"+self.guide)
                cmds.parent(self.fkEyeSubCtrl, self.fkEyeCtrl)
                # position and orientation of joint and control:
                cmds.delete(cmds.pointConstraint(self.guide, self.jxt, maintainOffset=False))
                cmds.delete(cmds.orientConstraint(self.cvEndJointZero, self.jxt, maintainOffset=False))
                cmds.delete(cmds.pointConstraint(self.guide, self.fkEyeCtrl, maintainOffset=False))
                cmds.delete(cmds.orientConstraint(self.cvEndJointZero, self.fkEyeCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.guide, self.baseEyeCtrl, maintainOffset=False))
                # zeroOut controls:
                eyeZeroList = self.ar.utils.zeroOut([self.baseEyeCtrl])
                eyeZeroList.append(self.ar.utils.zeroOut([self.fkEyeCtrl], offset=True))
                eyeZeroOffsetGrp = cmds.listRelatives(eyeZeroList[1], children=True)[0]
                # fixing flip mirror:
                if s == 1:
                    if cmds.getAttr(self.guide_base+".flip") == 1:
                        cmds.setAttr(eyeZeroList[0]+".scaleX", -1)
                        cmds.setAttr(eyeZeroList[0]+".scaleY", -1)
                        cmds.setAttr(eyeZeroList[0]+".scaleZ", -1)                        
                cmds.parent(eyeZeroList[1], self.baseEyeCtrl)
                # calibrate offset rotate:
                for offsetAxis in ['X', 'Y', 'Z']:
                    cmds.addAttr(self.fkEyeCtrl, longName="calibrateR"+offsetAxis, attributeType='float', defaultValue=0, keyable=False)
                    cmds.connectAttr(self.fkEyeCtrl+".calibrateR"+offsetAxis, eyeZeroOffsetGrp+".rotate"+offsetAxis, force=True)
                fkCtrlCalibrationList = ["calibrateRX", "calibrateRY", "calibrateRZ"]
                self.ar.ctrls.setStringAttrFromList(self.fkEyeCtrl, fkCtrlCalibrationList)
                # hide visibility attribute:
                cmds.setAttr(self.fkEyeCtrl+'.visibility', keyable=False)
                self.ar.ctrls.setLockHide([self.fkEyeCtrl], ['tx', 'ty', 'tz'])
                # create end joint:
                self.cvEndJoint = side+self.number_name+"_Guide_JointEnd"
                self.endJoint = cmds.joint(name=side+self.number_name+"_"+self.ar.data.joint_end_attr, radius=0.5)
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.endJoint, maintainOffset=False))
                cmds.parent(self.endJoint, self.jnt, absolute=True)
                # create parent and scale constraint from ctrl to jxt:
                cmds.parentConstraint(self.fkEyeCtrl, self.jxt, maintainOffset=False, name=self.jxt+"_PaC")
                cmds.scaleConstraint(self.fkEyeCtrl, self.jxt, maintainOffset=True, name=self.jxt+"_ScC")
                # constraint from sub control to sub joint:
                cmds.parentConstraint(self.fkEyeSubCtrl, self.subJnt, maintainOffset=False, name=self.subJnt+"_PaC")
                cmds.scaleConstraint(self.fkEyeSubCtrl, self.subJnt, maintainOffset=True, name=self.subJnt+"_ScC")
                
                # lookAt control:
                self.lookAtCtrl = self.ar.ctrls.cvControl("id_011_EyeLookAt", side+self.number_name+"_LookAt_Ctrl", r=self.radius, d=self.curve_degree, guideSource=self.name_guide+"_JointEnd", parentTag=self.eyeCtrl)
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.lookAtCtrl, maintainOffset=False))
                lookAtCtrlZeroGrp = self.ar.utils.zeroOut([self.lookAtCtrl])
                cmds.parent(lookAtCtrlZeroGrp, self.eyeCtrl, relative=False)
                cmds.addAttr(self.lookAtCtrl, longName=self.ar.data.lang['c118_active'], attributeType="short", minValue=0, defaultValue=1, maxValue=1, keyable=True)
                self.ar.utils.originedFrom(objName=self.lookAtCtrl, attrString=side+self.number_name+"_Guide_JointEnd")
                
                # up locator:
                self.cvUpLocGuide = side+self.number_name+"_Guide_JointEnd_UpLoc"
                self.lUpGrpLoc = cmds.group(name=side+self.number_name+"_Up_Loc_Grp", empty=True)
                cmds.delete(cmds.pointConstraint(self.jnt, self.lUpGrpLoc, maintainOffset=False))
                cmds.delete(cmds.orientConstraint(self.cvEndJointZero, self.lUpGrpLoc, maintainOffset=False))
                self.lUpLoc = cmds.spaceLocator(name=side+self.number_name+"_Up_Loc")[0]
                cmds.delete(cmds.parentConstraint(self.cvUpLocGuide, self.lUpLoc, maintainOffset=False))
                cmds.parent(self.lUpLoc, self.lUpGrpLoc, relative=False)
                cmds.parent(self.lUpGrpLoc, self.upLocGrp, relative=False)
                
                # look at aim constraint:
                aimConst = cmds.aimConstraint(self.lookAtCtrl, eyeZeroList[1], worldUpType="object", worldUpObject=self.upLocGrp+"|"+self.lUpGrpLoc+"|"+self.lUpLoc, maintainOffset=True, name=self.fkEyeCtrl+"_Zero_0_Grp"+"_AiC")[0]
                cmds.connectAttr(self.lookAtCtrl+"."+self.ar.data.lang['c118_active'], aimConst+"."+self.lookAtCtrl+"W0", force=True)
                # eye aim rotation
                cmds.addAttr(self.fkEyeCtrl, longName="aimRotation", attributeType="float", keyable=True)
                cmds.connectAttr(self.fkEyeCtrl+".aimRotation", self.jnt+".rotateZ", force=True)
                cmds.pointConstraint(self.baseEyeCtrl, self.lUpGrpLoc, maintainOffset=True, name=self.lUpGrpLoc+"_PoC")
                
                # create eyeScale setup:
                cmds.select(clear=True)
                self.eyeScaleJnt = cmds.joint(name=side+self.number_name+"Scale_1_Jnt", scaleCompensate=False)
                cmds.addAttr(self.eyeScaleJnt, longName='dpAR_joint', attributeType='float', keyable=False)
                self.ar.utils.setJointLabel(self.eyeScaleJnt, s+self.joint_label_add, 18, self.number_name+"Scale_1")
                # jointScale position:
                cmds.delete(cmds.parentConstraint(self.guide, self.eyeScaleJnt, maintainOffset=False))
                # create endScale joint:
                self.endScaleJoint = cmds.joint(name=side+self.number_name+"Scale_"+self.ar.data.joint_end_attr, radius=0.5)
                cmds.delete(cmds.parentConstraint(self.eyeScaleJnt, self.endScaleJoint, maintainOffset=False))
                cmds.setAttr(self.endScaleJoint+".translateZ", self.radius)
                if s == 1:
                    cmds.setAttr(self.endScaleJoint+".translateZ", -self.radius)
                # create constraints to eyeScale:
                cmds.pointConstraint(self.jnt, self.eyeScaleJnt, maintainOffset=False, name=self.eyeScaleJnt+"_PoC")
                cmds.orientConstraint(self.baseEyeCtrl, self.eyeScaleJnt, maintainOffset=False, name=self.eyeScaleJnt+"_OrC")
                cmds.scaleConstraint(self.jnt, self.eyeScaleJnt, maintainOffset=True, name=self.eyeScaleJnt+"_ScC")
                self.eyeScaleGrp = cmds.group(self.eyeScaleJnt, name=self.eyeScaleJnt+"_Grp")
                self.eyeScaleGrpList.append(self.eyeScaleGrp)
                self.ar.utils.addJointEndAttr([self.endJoint, self.endScaleJoint])
                
                # create specular setup:
                if self.get_guide_attr(SPEC):
                    cmds.select(clear=True)
                    self.cvSpecularLoc = side+self.number_name+"_Guide_SpecularLoc"
                    # specular joint:
                    self.eyeSpecJnt = cmds.joint(name=side+self.number_name+"Specular_1_Jnt", scaleCompensate=False)
                    cmds.addAttr(self.eyeSpecJnt, longName='dpAR_joint', attributeType='float', keyable=False)
                    self.ar.utils.setJointLabel(self.eyeSpecJnt, s+self.joint_label_add, 18, self.number_name+"Specular_1")
                    # specular joint scale:
                    self.eyeSpecScaleJnt = cmds.joint(name=side+self.number_name+"Specular_2_Jnt", scaleCompensate=False)
                    cmds.addAttr(self.eyeSpecScaleJnt, longName='dpAR_joint', attributeType='float', keyable=False)
                    self.ar.utils.setJointLabel(self.eyeSpecScaleJnt, s+self.joint_label_add, 18, self.number_name+"Specular_2")
                    cmds.setAttr(self.eyeSpecScaleJnt+".translateZ", self.radius)
                    # create endSpecular joint:
                    self.endSpecJoint = cmds.joint(name=side+self.number_name+"Specular_"+self.ar.data.joint_end_attr, radius=0.5)
                    self.ar.utils.addJointEndAttr([self.endSpecJoint])
                    cmds.setAttr(self.endSpecJoint+".translateZ", 0.2*self.radius)
                    cmds.parent(self.eyeSpecJnt, self.eyeScaleJnt)
                    # specular control:
                    self.eyeSpecCtrl = self.ar.ctrls.cvControl("id_071_EyeSpec", ctrlName=side+self.number_name+"_Spec_Ctrl", r=self.radius, d=self.curve_degree, headDef=self.headDefValue, guideSource=self.name_guide+"_SpecularLoc", parentTag=self.fkEyeSubCtrl)
                    cmds.delete(cmds.parentConstraint(self.guide, self.eyeSpecCtrl, maintainOffset=False))
                    eyeSpecZeroGrp = self.ar.utils.zeroOut([self.eyeSpecCtrl])[0]
                    cmds.parent(eyeSpecZeroGrp, self.baseEyeCtrl)
                    cmds.parentConstraint(self.eyeSpecCtrl, self.eyeSpecJnt, maintainOffset=False, name=self.eyeSpecJnt+"_PaC")
                    cmds.scaleConstraint(self.eyeSpecCtrl, self.eyeSpecJnt, maintainOffset=True, name=self.eyeSpecJnt+"_ScC")
                    # specular follow subcontrol
                    cmds.addAttr(self.eyeSpecCtrl, longName=self.ar.data.lang['c032_follow'], attributeType='float', keyable=True, minValue=0, maxValue=1, defaultValue=1)
                    followSPC = cmds.parentConstraint(self.fkEyeSubCtrl, self.baseEyeCtrl, eyeSpecZeroGrp, maintainOffset=True, name=eyeSpecZeroGrp+"_PaC")[0]
                    eyeSpecFollowRev = cmds.createNode('reverse', name=side+self.number_name+"_Spec_Follow_Rev")
                    self.to_ids.append(eyeSpecFollowRev)
                    cmds.connectAttr(self.eyeSpecCtrl+"."+self.ar.data.lang['c032_follow'], followSPC+"."+self.fkEyeSubCtrl+"W0", force=True)
                    cmds.connectAttr(self.eyeSpecCtrl+"."+self.ar.data.lang['c032_follow'], eyeSpecFollowRev+".inputX", force=True)
                    cmds.connectAttr(eyeSpecFollowRev+".outputX", followSPC+"."+self.baseEyeCtrl+"W1", force=True)
                    # specular scale control:
                    self.eyeSpecScaleCtrl = self.ar.ctrls.cvControl("id_091_EyeSpecScale", ctrlName=side+self.number_name+"_SpecScale_Ctrl", r=0.2*self.radius, d=self.curve_degree, headDef=self.headDefValue, guideSource=self.name_guide+"_SpecularLoc", parentTag=self.eyeSpecCtrl)
                    cmds.delete(cmds.parentConstraint(self.cvSpecularLoc, self.eyeSpecScaleCtrl, maintainOffset=False))
                    if s == 1:
                        noWSLEyeSpecScaleZeroGrpData = self.ar.utils.getTransformData(self.eyeSpecScaleZeroGrp, useWorldSpace=False)
                        lEyeSpecScaleZeroGrpData = self.ar.utils.getTransformData(self.eyeSpecScaleZeroGrp)
                        rEyeFkCtrlData = self.ar.utils.getTransformData(self.fkEyeCtrl)
                    self.eyeSpecScaleZeroGrp = self.ar.utils.zeroOut([self.eyeSpecScaleCtrl])[0]
                    cmds.parent(self.eyeSpecScaleZeroGrp, self.eyeSpecCtrl)
                    cmds.parentConstraint(self.eyeSpecScaleCtrl, self.eyeSpecScaleJnt, maintainOffset=False, name=self.eyeSpecScaleJnt+"_PaC")
                    cmds.scaleConstraint(self.eyeSpecScaleCtrl, self.eyeSpecScaleJnt, maintainOffset=True, name=self.eyeSpecScaleJnt+"_ScC")
                    # fixing flip mirror:
                    if s == 1:
                        if cmds.getAttr(self.guide_base+".flip") == 0:
                            cmds.xform(self.eyeSpecScaleZeroGrp, translation=noWSLEyeSpecScaleZeroGrpData["translation"], worldSpace=False)
                        else:
                            translationList, tempList = [], []
                            for i, j in zip(lEyeSpecScaleZeroGrpData["translation"], lEyeFkCtrlData["translation"]):
                                tempList.append(i-j)
                            for k, w in zip(tempList, rEyeFkCtrlData["translation"]):
                                translationList.append(k+w)
                            cmds.xform(self.eyeSpecScaleZeroGrp, translation=translationList, worldSpace=True)
                            cmds.xform(self.eyeSpecScaleZeroGrp, rotation=lEyeSpecScaleZeroGrpData["rotation"], worldSpace=True)

                # create eyelid setup:
                if self.get_guide_attr(EYELID):
                    # declare eyelid guides:
                    self.cvUpperEyelidLoc = side+self.number_name+"_Guide_UpperEyelidLoc"
                    self.cvLowerEyelidLoc = side+self.number_name+"_Guide_LowerEyelidLoc"
                    self.cvLidPivotLoc = side+self.number_name+"_Guide_LidPivotLoc"
                    
                    # creating eyelids joints:
                    cmds.select(clear=True)
                    self.eyelidJxt = cmds.joint(name=side+self.number_name+"_"+self.ar.data.lang['c042_eyelid']+"_Jxt", scaleCompensate=False)
                    cmds.delete(cmds.parentConstraint(self.cvLidPivotLoc, self.eyelidJxt, mo=False))
                    cmds.parent(self.eyelidJxt, self.eyeScaleJnt)
                    self.upperEyelidBaseJxt, self.upperEyelidJnt = self.createEyelidJoints(side, 'c044_upper', "", self.cvUpperEyelidLoc, s+self.joint_label_add)
                    self.upperEyelidMiddleBaseJxt, self.upperEyelidMiddleJnt = self.createEyelidJoints(side, 'c044_upper', self.ar.data.lang['c029_middle'], self.cvUpperEyelidLoc, s+self.joint_label_add)
                    self.lowerEyelidBaseJxt, self.lowerEyelidJnt = self.createEyelidJoints(side, 'c045_lower', "", self.cvLowerEyelidLoc, s+self.joint_label_add)
                    self.lowerEyelidMiddleBaseJxt, self.lowerEyelidMiddleJnt = self.createEyelidJoints(side, 'c045_lower', self.ar.data.lang['c029_middle'], self.cvLowerEyelidLoc, s+self.joint_label_add)
                    
                    # creating eyelids controls and setup:
                    self.upperEyelidCtrl, self.upperEyelidCtrlZero = self.createEyelidSetup(side, 'c044_upper', self.upperEyelidJnt, self.upperEyelidBaseJxt, self.upperEyelidMiddleBaseJxt, self.upperEyelidMiddleJnt, 30, (0, 0, 0), self.cvUpperEyelidLoc)
                    self.lowerEyelidCtrl, self.lowerEyelidCtrlZero = self.createEyelidSetup(side, 'c045_lower', self.lowerEyelidJnt, self.lowerEyelidBaseJxt, self.lowerEyelidMiddleBaseJxt, self.lowerEyelidMiddleJnt, 30, (0, 0, 180), self.cvLowerEyelidLoc)
                    # fixing mirror behavior for side controls:
                    if s == 0: #left
                        cmds.setAttr(self.upperEyelidCtrl+"."+self.ar.data.lang['c053_invert']+"X", 1)
                        cmds.setAttr(self.upperEyelidCtrl+"."+self.ar.data.lang['c053_invert']+"Y", 1)
                        cmds.setAttr(self.lowerEyelidCtrl+"."+self.ar.data.lang['c053_invert']+"Y", 1)
                        cmds.setAttr(self.lowerEyelidCtrl+"."+self.ar.data.lang['c053_invert']+self.ar.data.lang['c029_middle'], 1)
                        if self.corrective:
                            cmds.setAttr(self.lowerEyelidCtrl.replace("_Ctrl", "_00_Net")+".inputEnd", self.cValue)
                    else: #right
                        if cmds.getAttr(self.guide_base+".flip") == 0:
                            cmds.setAttr(self.upperEyelidCtrl+"."+self.ar.data.lang['c053_invert']+"Y", 1)
                            cmds.setAttr(self.lowerEyelidCtrl+"."+self.ar.data.lang['c053_invert']+"X", 1)
                            cmds.setAttr(self.lowerEyelidCtrl+"."+self.ar.data.lang['c053_invert']+"Y", 1)
                            cmds.setAttr(self.lowerEyelidCtrl+"."+self.ar.data.lang['c053_invert']+self.ar.data.lang['c029_middle'], 1)
                            cmds.setAttr(self.upperEyelidCtrlZero+".rotateY", 180)
                            cmds.setAttr(self.lowerEyelidCtrlZero+".rotateY", 180)
                            if self.corrective:
                                cmds.setAttr(self.lowerEyelidCtrl.replace("_Ctrl", "_00_Net")+".inputEnd", self.cValue)
                        else:
                            cmds.setAttr(self.upperEyelidCtrl+"."+self.ar.data.lang['c053_invert']+self.ar.data.lang['c029_middle'], 1)
                            cmds.setAttr(self.lowerEyelidCtrl+"."+self.ar.data.lang['c053_invert']+"X", 1)
                            if self.corrective:
                                cmds.setAttr(self.upperEyelidCtrl.replace("_Ctrl", "_00_Net")+".inputEnd", self.cValue)
                    # set eyelid scale by Base control attribute:
                    cmds.addAttr(self.baseEyeCtrl, longName=self.ar.data.lang['c042_eyelid'].lower()+self.ar.data.lang['i115_size'], attributeType='float', minValue=0.001, defaultValue=1, keyable=True)
                    cmds.connectAttr(self.baseEyeCtrl+"."+self.ar.data.lang['c042_eyelid'].lower()+self.ar.data.lang['i115_size'], self.eyelidJxt+".scaleX", force=True)
                    cmds.connectAttr(self.baseEyeCtrl+"."+self.ar.data.lang['c042_eyelid'].lower()+self.ar.data.lang['i115_size'], self.eyelidJxt+".scaleY", force=True)
                    cmds.connectAttr(self.baseEyeCtrl+"."+self.ar.data.lang['c042_eyelid'].lower()+self.ar.data.lang['i115_size'], self.eyelidJxt+".scaleZ", force=True)
                    
                # create iris setup:
                if self.get_guide_attr(IRIS):
                    self.irisCtrl = self.createIrisPupilSetup(s, side, IRIS, 'i080_iris', s+self.joint_label_add)
                    self.irisCtrlList.append(self.irisCtrl)
                    self.hasIris = True
                    
                # create pupil setup:
                if self.get_guide_attr(PUPIL):
                    self.pupilCtrl = self.createIrisPupilSetup(s, side, PUPIL, 'i081_pupil', s+self.joint_label_add)
                    self.pupilCtrlList.append(self.pupilCtrl)
                    self.hasPupil = True
                # create a masterModuleGrp to be checked if this rig exists:
                self.create_hook_setup(side, [eyeZeroList[0]], [self.jxt, self.eyeScaleGrp])
                if s == 0:
                    cmds.parent(self.eyeGrp, self.ctrl_hook_grp)
                    cmds.parent(self.upLocGrp, self.scalable_hook_grp)
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.number_name+'_'+self.mirror_grp)
                self.ar.utils.addCustomAttr([self.eyeGrp, self.upLocGrp, self.lUpGrpLoc, self.eyeScaleGrp], self.ar.utils.ignoreTransformIOAttr)
                self.ar.custom_attr.addAttr(0, [self.static_hook_grp], descendents=True) #dpID
            # finalize this rig:
            self.serialize_guide()
            self.composing_info()
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and module_instance namespace:
        self.delete_guide()
        self.rename_unit_conversion()
        self.ar.custom_attr.addAttr(0, self.to_ids, descendents=True) #dpID
        
        
    def composing_info(self):
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.composed = {
                            "eyeCtrl"     : self.eyeCtrl,
                            "eyeGrp"      : self.eyeGrp,
                            "upLocGrp"    : self.upLocGrp,
                            "eyeScaleGrp" : self.eyeScaleGrpList,
                            "irisCtrl"    : self.irisCtrlList,
                            "pupilCtrl"   : self.pupilCtrlList,
                            "hasIris"     : self.hasIris,
                            "hasPupil"    : self.hasPupil,
                        }
