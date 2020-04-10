# importing libraries:
import maya.cmds as cmds

from Library import dpUtils as utils
import dpBaseClass as Base
import dpLayoutClass as Layout


# global variables to this module:    
CLASS_NAME = "Eye"
TITLE = "m063_eye"
DESCRIPTION = "m064_eyeDesc"
ICON = "/Icons/dp_eye.png"

EYELID = "eyelid"
IRIS = "iris"
PUPIL = "pupil"

class Eye(Base.StartClass, Layout.LayoutClass):
    def __init__(self,  *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        Base.StartClass.__init__(self, *args, **kwargs)
    
    
    def createModuleLayout(self, *args):
        Base.StartClass.createModuleLayout(self)
        Layout.LayoutClass.basicModuleLayout(self)
    
    
    def getModuleAttr(self, moduleAttr, *args):
        return cmds.getAttr(self.moduleGrp + "." + moduleAttr)
        
    
    def createGuide(self, *args):
        Base.StartClass.createGuide(self)
        # Custom GUIDE:
        cmds.addAttr(self.moduleGrp, longName="flip", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".flip", 0)
        # adding extra attributes
        cmds.addAttr(self.moduleGrp, longName="aimDirection", attributeType='enum', enumName="+X:-X:+Y:-Y:+Z:-Z")
        cmds.setAttr(self.moduleGrp+".aimDirection", 4)
        cmds.addAttr(self.moduleGrp, longName="aimDirectionName", dataType='string')
        cmds.setAttr(self.moduleGrp+".aimDirectionName", "Z", type="string")
        cmds.addAttr(self.moduleGrp, longName="aimDirectionPositive", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".aimDirectionPositive", 1)
        cmds.addAttr(self.moduleGrp, longName=EYELID, attributeType='bool')
        cmds.setAttr(self.moduleGrp+"."+EYELID, 1)
        cmds.addAttr(self.moduleGrp, longName=IRIS, attributeType='bool')
        cmds.setAttr(self.moduleGrp+"."+IRIS, 1)
        cmds.addAttr(self.moduleGrp, longName=PUPIL, attributeType='bool')
        cmds.setAttr(self.moduleGrp+"."+PUPIL, 1)
        cmds.setAttr(self.moduleGrp+".moduleNamespace", self.moduleGrp[:self.moduleGrp.rfind(":")], type='string')
        # main joint (center of eye globe)
        self.cvJointLoc, shapeSizeCH = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_JointLoc1", r=0.3, d=1, guide=True)
        self.connectShapeSize(shapeSizeCH)
        self.jGuide1 = cmds.joint(name=self.guideName+"_JGuide1", radius=0.001)
        cmds.setAttr(self.jGuide1+".template", 1)
        cmds.parent(self.jGuide1, self.moduleGrp, relative=True)
        # eyelid
        self.jEyelid = cmds.joint(name=self.guideName+"_JEyelid", radius=0.001)
        # end joints (to aim)
        self.cvEndJoint = self.ctrls.cvControl("id_059_AimLoc", ctrlName=self.guideName+"_JointEnd", r=0.5, d=1, rot=(-90, 0, -90))
        self.ctrls.colorShape([self.cvEndJoint], "blue")
        shapeSizeCH = self.ctrls.shapeSizeSetup(self.cvEndJoint)
        self.connectShapeSize(shapeSizeCH)
        self.cvUpLocGuide = cmds.spaceLocator(name=self.cvEndJoint+"_UpLoc")[0]
        self.cvEndJointZero = cmds.group(self.cvEndJoint, self.cvUpLocGuide, name=self.cvEndJoint+"_Grp")
        self.cvEndBackRotGrp = cmds.group(self.cvEndJointZero, name=self.cvEndJointZero+"_Back_Grp")
        cmds.parent(self.cvEndBackRotGrp, self.moduleGrp)
        cmds.setAttr(self.cvEndJoint+".tz", 13)
        cmds.setAttr(self.cvUpLocGuide+".ty", 13)
        cmds.setAttr(self.cvUpLocGuide+".visibility", 0)
        cmds.orientConstraint(self.tempGrpName, self.cvEndBackRotGrp, maintainOffset=False, name=self.cvEndBackRotGrp+"_OrientConstraint")
        self.jGuideEnd = cmds.joint(name=self.guideName+"_JGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        self.ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        # upper eyelid guide
        self.cvUpperEyelidLoc, shapeSizeCH = self.ctrls.cvLocator(ctrlName=self.guideName+"_UpperEyelidLoc", r=0.2, d=1, guide=True)
        self.connectShapeSize(shapeSizeCH)
        cmds.parent(self.cvUpperEyelidLoc, self.cvJointLoc)
        cmds.setAttr(self.cvUpperEyelidLoc+".ty", 0.5)
        cmds.setAttr(self.cvUpperEyelidLoc+".tz", 0.5)
        self.jUpperEyelid = cmds.joint(name=self.guideName+"_JUpperEyelid", radius=0.001)
        cmds.setAttr(self.jUpperEyelid+".template", 1)
        # lower eyelid guide
        self.cvLowerEyelidLoc, shapeSizeCH = self.ctrls.cvLocator(ctrlName=self.guideName+"_LowerEyelidLoc", r=0.2, d=1, guide=True)
        self.connectShapeSize(shapeSizeCH)
        cmds.parent(self.cvLowerEyelidLoc, self.cvJointLoc)
        cmds.setAttr(self.cvLowerEyelidLoc+".ty", -0.5)
        cmds.setAttr(self.cvLowerEyelidLoc+".tz", 0.5)
        self.jLowerEyelid = cmds.joint(name=self.guideName+"_JLowerEyelid", radius=0.001)
        cmds.setAttr(self.jLowerEyelid+".template", 1)
        # iris guide
        self.cvIrisLoc, shapeSizeCH = self.ctrls.cvLocator(ctrlName=self.guideName+"_IrisLoc", r=0.15, d=1, guide=True)
        self.connectShapeSize(shapeSizeCH)
        cmds.parent(self.cvIrisLoc, self.cvJointLoc)
        cmds.setAttr(self.cvIrisLoc+".tz", 0.4)
        # pupil guide
        self.cvPupilLoc, shapeSizeCH = self.ctrls.cvLocator(ctrlName=self.guideName+"_PupilLoc", r=0.12, d=1, guide=True)
        self.connectShapeSize(shapeSizeCH)
        cmds.parent(self.cvPupilLoc, self.cvJointLoc)
        cmds.setAttr(self.cvPupilLoc+".tz", 0.3)
        # hierarchy mounting
        cmds.parent(self.cvJointLoc, self.moduleGrp)
        cmds.parent(self.jUpperEyelid, self.jLowerEyelid, self.jEyelid)
        cmds.parent(self.jGuideEnd, self.jGuide1)
        cmds.parentConstraint(self.cvJointLoc, self.jGuide1, maintainOffset=True, name=self.jGuide1+"_ParentConstraint")
        cmds.parentConstraint(self.cvUpperEyelidLoc, self.jUpperEyelid, maintainOffset=True, name=self.jUpperEyelid+"_ParentConstraint")
        cmds.parentConstraint(self.cvLowerEyelidLoc, self.jLowerEyelid, maintainOffset=True, name=self.jLowerEyelid+"_ParentConstraint")
        cmds.parentConstraint(self.cvEndJoint, self.jGuideEnd, maintainOffset=False, name=self.jGuideEnd+"_ParentConstraint")
    
    
    def changeEyelid(self, *args):
        """ Set the attribute value for eyelid.
        """
        # re-declaring variables:
        self.cvUpperEyelidLoc = self.guideName+"_UpperEyelidLoc"
        self.cvLowerEyelidLoc = self.guideName+"_LowerEyelidLoc"
        self.jEyelid = self.guideName+"_JEyelid"
        self.jUpperEyelid = self.guideName+"_JUpperEyelid"
        self.jLowerEyelid = self.guideName+"_JLowerEyelid"
        # getting value:
        currentEyelidValue = cmds.checkBox(self.eyelidCB, query=True, value=True)
        # setting values:
        cmds.setAttr(self.moduleGrp+".eyelid", currentEyelidValue)
        cmds.setAttr(self.cvUpperEyelidLoc+".visibility", currentEyelidValue)
        cmds.setAttr(self.cvLowerEyelidLoc+".visibility", currentEyelidValue)
        cmds.setAttr(self.jEyelid+".visibility", currentEyelidValue)
        cmds.setAttr(self.jUpperEyelid+".visibility", currentEyelidValue)
        cmds.setAttr(self.jLowerEyelid+".visibility", currentEyelidValue)
        
        
    def changeIris(self, *args):
        """ Set the attribute value for iris.
        """
        self.cvIrisLoc = self.guideName+"_IrisLoc"
        cmds.setAttr(self.moduleGrp+".iris", cmds.checkBox(self.irisCB, query=True, value=True))
        cmds.setAttr(self.cvIrisLoc+".visibility", cmds.checkBox(self.irisCB, query=True, value=True))
        
    
    def changePupil(self, *args):
        """ Set the attribute value for pupil.
        """
        self.cvPupilLoc = self.guideName+"_PupilLoc"
        cmds.setAttr(self.moduleGrp+".pupil", cmds.checkBox(self.pupilCB, query=True, value=True))
        cmds.setAttr(self.cvPupilLoc+".visibility", cmds.checkBox(self.pupilCB, query=True, value=True))
        
    
    def changeAimDirection(self, item, *args):
        """ Set the good direction for Eye look at Aim setup.
        """
        # verify integrity of the guideModule:
        if self.verifyGuideModuleIntegrity():
            # re-declaring variables:
            self.jGuideEnd = self.guideName+"_JGuideEnd"
            self.cvEndJointZero = self.guideName+"_JointEnd_Grp"
            # setting attributes:
            cmds.setAttr(self.moduleGrp+".aimDirection", self.aimMenuItemList.index(item))
            cmds.setAttr(self.moduleGrp+".aimDirectionName", item[1], type='string')
            cmds.setAttr(self.moduleGrp+".aimDirectionPositive", 0)
            if item[0] == "+":
                cmds.setAttr(self.moduleGrp+".aimDirectionPositive", 1)
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
        baseName = side+self.userGuideName+"_"+self.langDic[self.langName][lid]+"_"+self.langDic[self.langName]['c042_eyelid']+middle
        # creating joints:
        eyelidBaseZeroJxt = cmds.joint(name=baseName+"_Base_Zero_Jxt", rotationOrder="yzx", scaleCompensate=False)
        eyelidBaseJxt = cmds.joint(name=baseName+"_Base_Jxt", rotationOrder="yzx", scaleCompensate=False)
        eyelidZeroJxt = cmds.joint(name=baseName+"_Zero_Jxt", rotationOrder="yzx", scaleCompensate=False)
        eyelidJnt = cmds.joint(name=baseName+"_Jnt", rotationOrder="yzx", scaleCompensate=False)
        cmds.addAttr(eyelidJnt, longName='dpAR_joint', attributeType='float', keyable=False)
        utils.setJointLabel(eyelidJnt, jointLabelNumber, 18, self.userGuideName+"_"+self.langDic[self.langName][lid]+"_"+self.langDic[self.langName]['c042_eyelid']+middle)
        cmds.select(eyelidZeroJxt)
        eyelidSupportJxt = cmds.joint(name=baseName+"_Jxt", rotationOrder="yzx", scaleCompensate=False)
        cmds.setAttr(eyelidSupportJxt+".translateX", self.ctrlRadius*0.1)
        # positioning and orienting correctely eyelid joints:
        cmds.delete(cmds.aimConstraint(cvEyelidLoc, eyelidBaseZeroJxt, aimVector=(0,0,1), worldUpType="objectrotation", worldUpObject=self.eyelidJxt))
        cmds.delete(cmds.parentConstraint(cvEyelidLoc, eyelidZeroJxt, mo=False))
        cmds.setAttr(eyelidZeroJxt+".rotateX", 0)
        cmds.setAttr(eyelidZeroJxt+".rotateY", 0)
        cmds.setAttr(eyelidZeroJxt+".rotateZ", 0)
        cmds.select(self.eyelidJxt)
        return eyelidBaseJxt, eyelidJnt


    def createEyelidSetup(self, side, lid, eyelidJnt, eyelidBaseJxt, eyelidMiddleBaseJxt, eyelidMiddleJnt, preset, rotCtrl, *args):
        ''' Work with the joints created in order to develop a solid and stable eyelid setup for blink and facial eye expressions using direct skinning process in the final render mesh.
            Returns the main control and its zeroOut group.
        '''
        # declating a concatenated name used for base to compose:
        baseName = side+self.userGuideName+"_"+self.langDic[self.langName][lid]+"_"+self.langDic[self.langName]['c042_eyelid']
        # creating eyelid control:
        eyelidCtrl = self.ctrls.cvControl("id_008_Eyelid", baseName+"_Ctrl", self.ctrlRadius*0.4, d=self.curveDegree, rot=rotCtrl)
        utils.originedFrom(objName=eyelidCtrl, attrString=self.base+";"+self.guide)
        eyelidCtrlZero = utils.zeroOut([eyelidCtrl])[0]
        self.ctrls.setLockHide([eyelidCtrl], ['tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
        cmds.parent(eyelidCtrlZero, self.baseEyeCtrl)
        # positioning correctely eyelid control:
        cmds.delete(cmds.parentConstraint(self.eyelidJxt, eyelidCtrlZero, mo=False))
        cmds.delete(cmds.pointConstraint(eyelidJnt, eyelidCtrlZero, mo=False))
        cmds.xform(eyelidCtrlZero, translation=(0,0,self.ctrlRadius), relative=True)
        # adding useful control attributes to calibrate eyelid setup:
        cmds.addAttr(eyelidCtrl, longName=self.langDic[self.langName]['c049_intensity']+"X", attributeType="float", minValue=0, defaultValue=1)
        cmds.addAttr(eyelidCtrl, longName=self.langDic[self.langName]['c049_intensity']+"Y", attributeType="float", minValue=0, defaultValue=1)
        cmds.setAttr(eyelidCtrl+"."+self.langDic[self.langName]['c049_intensity']+"X", keyable=False, channelBox=True)
        cmds.setAttr(eyelidCtrl+"."+self.langDic[self.langName]['c049_intensity']+"Y", keyable=False, channelBox=True)
        cmds.addAttr(eyelidCtrl, longName=self.langDic[self.langName]['c053_invert']+"X", attributeType="bool", defaultValue=0)
        cmds.addAttr(eyelidCtrl, longName=self.langDic[self.langName]['c053_invert']+"Y", attributeType="bool", defaultValue=0)
        cmds.addAttr(eyelidCtrl, longName=self.langDic[self.langName]['c051_preset']+"X", attributeType="float", defaultValue=preset, keyable=False)
        cmds.addAttr(eyelidCtrl, longName=self.langDic[self.langName]['c051_preset']+"Y", attributeType="float", defaultValue=preset, keyable=False)
        cmds.addAttr(eyelidCtrl, longName=self.langDic[self.langName]['c050_proximity']+self.langDic[self.langName]['c029_middle'], attributeType="float", minValue=0, defaultValue=0.5, maxValue=1, keyable=False)
        cmds.addAttr(eyelidCtrl, longName=self.langDic[self.langName]['c052_fix']+"ScaleX", attributeType="float", defaultValue=0.01, minValue=0, keyable=False)
        cmds.addAttr(eyelidCtrl, longName=self.langDic[self.langName]['c052_fix']+"TranslateZ", attributeType="float", defaultValue=0.15, minValue=0, keyable=False)
        # creating utility nodes to eyelid setup:
        eyelidIntensityMD = cmds.createNode('multiplyDivide', name=baseName+"_Intensity_MD")
        eyelidInvertMD = cmds.createNode('multiplyDivide', name=baseName+"_Invert_MD")
        eyelidInvertXCnd = cmds.createNode('condition', name=baseName+"_InvertX_Cnd")
        eyelidInvertYCnd = cmds.createNode('condition', name=baseName+"_InvertY_Cnd")
        eyelidPresetMD = cmds.createNode('multiplyDivide', name=baseName+"_Preset_MD")
        eyelidMiddleMD = cmds.createNode('multiplyDivide', name=baseName+"_Middle_MD")
        eyelidFixMD = cmds.createNode('multiplyDivide', name=baseName+"_Fix_MD")
        eyelidFixPMA = cmds.createNode('plusMinusAverage', name=baseName+"_Fix_PMA")
        eyelidFixModulusXCnd = cmds.createNode('condition', name=baseName+"_Fix_ModulusX_Cnd")
        eyelidFixModulusYCnd = cmds.createNode('condition', name=baseName+"_Fix_ModulusY_Cnd")
        eyelidFixNegativeMD = cmds.createNode('multiplyDivide', name=baseName+"_Fix_Negative_MD")
        eyelidFixMiddleMD = cmds.createNode('multiplyDivide', name=baseName+"_Fix_Middle_MD")
        eyelidFixMiddleScaleClp = cmds.createNode('clamp', name=baseName+"_Fix_Middle_Clp")
        # seting up the node attributes:
        cmds.setAttr(eyelidInvertXCnd+".colorIfTrueR", 1)
        cmds.setAttr(eyelidInvertXCnd+".colorIfFalseR", -1)
        cmds.setAttr(eyelidInvertYCnd+".colorIfTrueR", 1)
        cmds.setAttr(eyelidInvertYCnd+".colorIfFalseR", -1)
        cmds.setAttr(eyelidFixNegativeMD+".input2X", -1)
        cmds.setAttr(eyelidFixModulusXCnd+".operation", 3)
        cmds.setAttr(eyelidFixPMA+".input3D[0].input3Dx", 1)
        cmds.setAttr(eyelidFixNegativeMD+".input2Y", -1)
        cmds.setAttr(eyelidFixModulusYCnd+".operation", 3)
        cmds.setAttr(eyelidFixMiddleScaleClp+".minR", 1)
        cmds.setAttr(eyelidFixMiddleScaleClp+".maxR", 1000)
        # connecting eyelid control to nodes and joints:
        cmds.connectAttr(eyelidCtrl+".translateX", eyelidInvertMD+".input1X", force=True)
        cmds.connectAttr(eyelidCtrl+".translateY", eyelidInvertMD+".input1Y", force=True)
        # working with invert nodes in order to be able to adjust the control by User after the setup done:
        cmds.connectAttr(eyelidCtrl+"."+self.langDic[self.langName]['c053_invert']+"X", eyelidInvertXCnd+".firstTerm", force=True)
        cmds.connectAttr(eyelidCtrl+"."+self.langDic[self.langName]['c053_invert']+"Y", eyelidInvertYCnd+".firstTerm", force=True)
        cmds.connectAttr(eyelidInvertXCnd+".outColorR", eyelidInvertMD+".input2X", force=True)
        cmds.connectAttr(eyelidInvertYCnd+".outColorR", eyelidInvertMD+".input2Y", force=True)
        cmds.connectAttr(eyelidInvertMD+".outputX", eyelidIntensityMD+".input1X", force=True)
        cmds.connectAttr(eyelidInvertMD+".outputY", eyelidIntensityMD+".input1Y", force=True)
        # working with intensity attributes in order to chose the control force by User:
        cmds.connectAttr(eyelidCtrl+"."+self.langDic[self.langName]['c049_intensity']+"X", eyelidIntensityMD+".input2X", force=True)
        cmds.connectAttr(eyelidCtrl+"."+self.langDic[self.langName]['c049_intensity']+"Y", eyelidIntensityMD+".input2Y", force=True)
        cmds.connectAttr(eyelidIntensityMD+".outputX", eyelidPresetMD+".input1X", force=True)
        cmds.connectAttr(eyelidIntensityMD+".outputY", eyelidPresetMD+".input1Y", force=True)
        # working with the predefined values in order to help the Rigger calibrate the control intensity preset:
        cmds.connectAttr(eyelidCtrl+"."+self.langDic[self.langName]['c051_preset']+"X", eyelidPresetMD+".input2X", force=True)
        cmds.connectAttr(eyelidCtrl+"."+self.langDic[self.langName]['c051_preset']+"Y", eyelidPresetMD+".input2Y", force=True)
        cmds.connectAttr(eyelidPresetMD+".outputX", eyelidBaseJxt+".rotateZ", force=True)
        cmds.connectAttr(eyelidPresetMD+".outputY", eyelidBaseJxt+".rotateX", force=True)
        # setup the middle extra joint to be skinned as a helper to deform correctly the mesh following the main eyelid joint:
        cmds.connectAttr(eyelidPresetMD+".outputX", eyelidMiddleMD+".input1X", force=True)
        cmds.connectAttr(eyelidPresetMD+".outputY", eyelidMiddleMD+".input1Y", force=True)
        # using the proximity attribute to let User chose the good deformation on the skinning:
        cmds.connectAttr(eyelidCtrl+"."+self.langDic[self.langName]['c050_proximity']+self.langDic[self.langName]['c029_middle'], eyelidMiddleMD+".input2X", force=True)
        cmds.connectAttr(eyelidCtrl+"."+self.langDic[self.langName]['c050_proximity']+self.langDic[self.langName]['c029_middle'], eyelidMiddleMD+".input2Y", force=True)
        cmds.connectAttr(eyelidMiddleMD+".outputX", eyelidMiddleBaseJxt+".rotateZ", force=True)
        cmds.connectAttr(eyelidMiddleMD+".outputY", eyelidMiddleBaseJxt+".rotateX", force=True)
        # try to fix the maintain volume by mimic the SetDrivenKey and SculptDeform technique using nodes to scale and translate the skinned joints:
        cmds.connectAttr(eyelidIntensityMD+".outputY", eyelidFixMD+".input1X", force=True)
        cmds.connectAttr(eyelidIntensityMD+".outputY", eyelidFixMD+".input1Y", force=True)
        cmds.connectAttr(eyelidCtrl+"."+self.langDic[self.langName]['c052_fix']+"ScaleX", eyelidFixMD+".input2X", force=True)
        cmds.connectAttr(eyelidCtrl+"."+self.langDic[self.langName]['c052_fix']+"TranslateZ", eyelidFixMD+".input2Y", force=True)
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
        cmds.connectAttr(eyelidFixPMA+".output3Dx", eyelidFixMiddleMD+".input1X", force=True)
        cmds.connectAttr(eyelidFixModulusYCnd+".outColorR", eyelidFixMiddleMD+".input1Y", force=True)
        cmds.connectAttr(eyelidCtrl+"."+self.langDic[self.langName]['c050_proximity']+self.langDic[self.langName]['c029_middle'], eyelidFixMiddleMD+".input2X", force=True)
        cmds.connectAttr(eyelidCtrl+"."+self.langDic[self.langName]['c050_proximity']+self.langDic[self.langName]['c029_middle'], eyelidFixMiddleMD+".input2Y", force=True)
        cmds.connectAttr(eyelidFixMiddleMD+".outputX", eyelidFixMiddleScaleClp+".inputR", force=True)
        cmds.connectAttr(eyelidFixMiddleScaleClp+".outputR", eyelidMiddleJnt+".scaleX", force=True)
        cmds.connectAttr(eyelidFixMiddleMD+".outputY", eyelidMiddleJnt+".translateZ", force=True)
        return eyelidCtrl, eyelidCtrlZero
        
        
    def createIrisPupilSetup(self, s, side, type, codeName, sec, jointLabelNumber, *args):
        ''' Predefined function to add Iris or Pupil setup.
            Returns control.
        '''
        # declare cv guides:
        cvLoc = side+self.userGuideName+"_Guide_"+type.capitalize()+"Loc"
        # creating joint:
        mainJnt = cmds.joint(name=side+self.userGuideName+"_"+self.langDic[self.langName][codeName]+"_1_Jnt", scaleCompensate=False)
        cmds.addAttr(mainJnt, longName='dpAR_joint', attributeType='float', keyable=False)
        utils.setJointLabel(mainJnt, jointLabelNumber, 18, self.userGuideName+"_"+self.langDic[self.langName][codeName]+"_1")
        # joint position:
        cmds.delete(cmds.parentConstraint(cvLoc, mainJnt, maintainOffset=False))
        # create end joint:
        endJoint = cmds.joint(name=side+self.userGuideName+"_"+self.langDic[self.langName][codeName]+"_JEnd", scaleCompensate=False)
        cmds.delete(cmds.parentConstraint(mainJnt, endJoint, maintainOffset=False))
        cmds.setAttr(endJoint+".translateZ", 1)
        # creating control:
        if type == IRIS:
            ctrlId = "id_012_EyeIris"
        else:
            ctrlId = "id_013_EyePupil"
        ctrl = self.ctrls.cvControl(ctrlId, side+self.userGuideName+"_"+self.langDic[self.langName][codeName]+"_1_Ctrl", r=(self.ctrlRadius*0.3), d=self.curveDegree)
        utils.originedFrom(objName=ctrl, attrString=self.base+";"+self.guide)
        cmds.makeIdentity(ctrl, rotate=True, apply=True)
        # create constraints and arrange hierarchy:
        ctrlZero = utils.zeroOut([ctrl])
        cmds.delete(cmds.parentConstraint(cvLoc, ctrlZero[0], maintainOffset=False))
        cmds.parent(ctrlZero[0], self.baseEyeCtrl)
        # fixing flip mirror:
        if s == 1:
            if cmds.getAttr(self.moduleGrp+".flip") == 1:
                if not "X" == cmds.getAttr(self.moduleGrp+".aimDirectionName"):
                    cmds.setAttr(ctrlZero[0]+".scaleX", -1)
                else:
                    cmds.setAttr(ctrlZero[0]+".scaleX", 1)
                if not "Y" == cmds.getAttr(self.moduleGrp+".aimDirectionName"):
                    cmds.setAttr(ctrlZero[0]+".scaleY", -1)
                else:
                    cmds.setAttr(ctrlZero[0]+".scaleY", 1)
                if not "Z" == cmds.getAttr(self.moduleGrp+".aimDirectionName"):
                    cmds.setAttr(ctrlZero[0]+".scaleZ", -1)
                else:
                    cmds.setAttr(ctrlZero[0]+".scaleZ", 1)
        cmds.parentConstraint(self.fkEyeCtrl, ctrlZero[0], maintainOffset=True, name=ctrlZero[0]+"_ParentConstraint")
        cmds.scaleConstraint(self.fkEyeCtrl, ctrlZero[0], maintainOffset=True, name=ctrlZero[0]+"_ScaleConstraint")
        cmds.parent(mainJnt, self.jnt)
        cmds.parentConstraint(ctrl, mainJnt, maintainOffset=False, name=mainJnt+"_ParentConstraint")
        cmds.scaleConstraint(ctrl, mainJnt, maintainOffset=True, name=mainJnt+"_ScaleConstraint")
        return ctrl
        
    
    def rigModule(self, *args):
        Base.StartClass.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            try:
                hideJoints = cmds.checkBox('hideJointsCB', query=True, value=True)
            except:
                hideJoints = 1
            # start as no having mirror:
            sideList = [""]
            # analisys the mirror module:
            self.mirrorAxis = cmds.getAttr(self.moduleGrp+".mirrorAxis")
            if self.mirrorAxis != 'off':
                # get rigs names:
                self.mirrorNames = cmds.getAttr(self.moduleGrp+".mirrorName")
                # get first and last letters to use as side initials (prefix):
                sideList = [ self.mirrorNames[0]+'_', self.mirrorNames[len(self.mirrorNames)-1]+'_' ]
                for s, side in enumerate(sideList):
                    duplicated = cmds.duplicate(self.moduleGrp, name=side+self.userGuideName+'_Guide_Base')[0]
                    allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                    for item in allGuideList:
                        cmds.rename(item, side+self.userGuideName+"_"+item)
                    self.mirrorGrp = cmds.group(name="Guide_Base_Grp", empty=True)
                    cmds.parent(side+self.userGuideName+'_Guide_Base', self.mirrorGrp, absolute=True)
                    # re-rename grp:
                    cmds.rename(self.mirrorGrp, side+self.userGuideName+'_'+self.mirrorGrp)
                    # do a group mirror with negative scaling:
                    if s == 1:
                        if cmds.getAttr(self.moduleGrp+".flip") == 0:
                            for axis in self.mirrorAxis:
                                gotValue = cmds.getAttr(side+self.userGuideName+"_Guide_Base.translate"+axis)
                                flipedValue = gotValue*(-2)
                                cmds.setAttr(side+self.userGuideName+'_'+self.mirrorGrp+'.translate'+axis, flipedValue)
                        else:
                            for axis in self.mirrorAxis:
                                cmds.setAttr(side+self.userGuideName+'_'+self.mirrorGrp+'.scale'+axis, -1)
                # joint labelling:
                jointLabelAdd = 1
            else: # if not mirror:
                duplicated = cmds.duplicate(self.moduleGrp, name=self.userGuideName+'_Guide_Base')[0]
                allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                for item in allGuideList:
                    cmds.rename(item, self.userGuideName+"_"+item)
                self.mirrorGrp = cmds.group(self.userGuideName+'_Guide_Base', name="Guide_Base_Grp", relative=True)
                #for Maya2012: self.userGuideName+'_'+self.moduleGrp+"_Grp"
                # re-rename grp:
                cmds.rename(self.mirrorGrp, self.userGuideName+'_'+self.mirrorGrp)
                # joint labelling:
                jointLabelAdd = 0
            # store the number of this guide by module type:
            dpAR_count = utils.findModuleLastNumber(CLASS_NAME, "dpAR_type") + 1
            # create lists to export:
            self.eyeScaleGrpList, self.irisCtrlList, self.pupilCtrlList = [], [], []
            self.hasIris = False
            self.hasPupil = False
            # create the main control:
            self.eyeCtrl = self.ctrls.cvControl("id_010_EyeLookAtMain", self.userGuideName+"_A_Ctrl", r=(2.25*self.ctrlRadius), d=self.curveDegree)
            cmds.addAttr(self.eyeCtrl, longName=self.langDic[self.langName]['c032_Follow'], attributeType='float', keyable=True, minValue=0, maxValue=1)
            cmds.setAttr(self.eyeCtrl+"."+self.langDic[self.langName]['c032_Follow'], 1)
            cmds.delete(cmds.parentConstraint(sideList[0]+self.userGuideName+"_Guide_JointEnd", self.eyeCtrl, maintainOffset=False))
            if self.mirrorAxis != 'off':
                cmds.setAttr(self.eyeCtrl+".translate"+self.mirrorAxis, 0)
            self.eyeGrp = cmds.group(self.eyeCtrl, name=self.userGuideName+"_A_Grp")
            utils.zeroOut([self.eyeCtrl])
            self.upLocGrp = cmds.group(name=self.userGuideName+"_UpLoc_Grp", empty=True)
            # run for all sides:
            for s, side in enumerate(sideList):
                cmds.select(clear=True)
                self.base = side+self.userGuideName+'_Guide_Base'
                # declare guide:
                self.guide = side+self.userGuideName+"_Guide_JointLoc1"
                self.cvEndJointZero = side+self.userGuideName+"_Guide_JointEnd_Grp"
                # create a joint:
                self.jxt = cmds.joint(name=side+self.userGuideName+"_1_Jxt", scaleCompensate=False)
                self.jnt = cmds.joint(name=side+self.userGuideName+"_1_Jnt", scaleCompensate=False)
                cmds.addAttr(self.jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                utils.setJointLabel(self.jnt, s+jointLabelAdd, 18, self.userGuideName+"_1")
                self.fkEyeCtrl = self.ctrls.cvControl("id_014_EyeFk", side+self.userGuideName+"_Fk_Ctrl", r=self.ctrlRadius, d=self.curveDegree)
                utils.originedFrom(objName=self.fkEyeCtrl, attrString=self.base+";"+self.guide)
                self.baseEyeCtrl = self.ctrls.cvControl("id_009_EyeBase", ctrlName=side+self.userGuideName+"_Base_Ctrl", r=self.ctrlRadius, d=self.curveDegree)
                utils.originedFrom(objName=self.baseEyeCtrl, attrString=self.base+";"+self.guide)
                # position and orientation of joint and control:
                cmds.delete(cmds.pointConstraint(self.guide, self.jxt, maintainOffset=False))
                cmds.delete(cmds.orientConstraint(self.cvEndJointZero, self.jxt, maintainOffset=False))
                cmds.delete(cmds.pointConstraint(self.guide, self.fkEyeCtrl, maintainOffset=False))
                cmds.delete(cmds.orientConstraint(self.cvEndJointZero, self.fkEyeCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.guide, self.baseEyeCtrl, maintainOffset=False))
                # zeroOut controls:
                eyeZeroList = utils.zeroOut([self.baseEyeCtrl, self.fkEyeCtrl])
                # fixing flip mirror:
                if s == 1:
                    if cmds.getAttr(self.moduleGrp+".flip") == 1:
                        cmds.setAttr(eyeZeroList[0]+".scaleX", -1)
                        cmds.setAttr(eyeZeroList[0]+".scaleY", -1)
                        cmds.setAttr(eyeZeroList[0]+".scaleZ", -1)
                cmds.parent(eyeZeroList[1], self.baseEyeCtrl)
                
                # hide visibility attribute:
                cmds.setAttr(self.fkEyeCtrl+'.visibility', keyable=False)
                self.ctrls.setLockHide([self.fkEyeCtrl], ['tx', 'ty', 'tz'])
                # create end joint:
                self.cvEndJoint = side+self.userGuideName+"_Guide_JointEnd"
                self.endJoint = cmds.joint(name=side+self.userGuideName+"_JEnd")
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.endJoint, maintainOffset=False))
                cmds.parent(self.endJoint, self.jnt, absolute=True)
                # create parentConstraint from ctrl to jxt:
                cmds.parentConstraint(self.fkEyeCtrl, self.jxt, maintainOffset=False, name=self.jnt+"_ParentConstraint")
                # create scaleConstraint from ctrl to jnt:
                cmds.scaleConstraint(self.fkEyeCtrl, self.jxt, maintainOffset=True, name=self.jnt+"_ScaleConstraint")
                
                # lookAt control:
                self.lookAtCtrl = self.ctrls.cvControl("id_011_EyeLookAt", side+self.userGuideName+"_LookAt_Ctrl", r=self.ctrlRadius, d=self.curveDegree)
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.lookAtCtrl, maintainOffset=False))
                cmds.parent(self.lookAtCtrl, self.eyeCtrl, relative=False)
                cmds.makeIdentity(self.lookAtCtrl, apply=True)
                cmds.addAttr(self.lookAtCtrl, longName="active", attributeType="bool", defaultValue=1, keyable=True)
                
                # up locator:
                self.cvUpLocGuide = side+self.userGuideName+"_Guide_JointEnd_UpLoc"
                self.lUpGrpLoc = cmds.group(name=side+self.userGuideName+"_Up_Loc_Grp", empty=True)
                cmds.delete(cmds.pointConstraint(self.jnt, self.lUpGrpLoc, maintainOffset=False))
                cmds.delete(cmds.orientConstraint(self.cvEndJointZero, self.lUpGrpLoc, maintainOffset=False))
                self.lUpLoc = cmds.spaceLocator(name=side+self.userGuideName+"_Up_Loc")[0]
                cmds.delete(cmds.parentConstraint(self.cvUpLocGuide, self.lUpLoc, maintainOffset=False))
                cmds.parent(self.lUpLoc, self.lUpGrpLoc, relative=False)
                cmds.parent(self.lUpGrpLoc, self.upLocGrp, relative=False)
                
                # look at aim constraint:
                aimConst = cmds.aimConstraint(self.lookAtCtrl, self.fkEyeCtrl+"_Zero", worldUpType="object", worldUpObject=self.upLocGrp+"|"+self.lUpGrpLoc+"|"+self.lUpLoc, maintainOffset=True, name=self.fkEyeCtrl+"_Zero"+"_AimConstraint")[0]
                cmds.connectAttr(self.lookAtCtrl+".active", aimConst+"."+self.lookAtCtrl+"W0", force=True)
                # eye aim rotation
                cmds.addAttr(self.fkEyeCtrl, longName="aimRotation", attributeType="float", keyable=True)
                cmds.connectAttr(self.fkEyeCtrl+".aimRotation", self.jnt+".rotateZ", force=True)
                cmds.pointConstraint(self.baseEyeCtrl, self.lUpGrpLoc, maintainOffset=True, name=self.lUpGrpLoc+"_PointConstraint")
                
                # create eyeScale setup:
                cmds.select(clear=True)
                self.eyeScaleJnt = cmds.joint(name=side+self.userGuideName+"Scale_1_Jnt", scaleCompensate=False)
                cmds.addAttr(self.eyeScaleJnt, longName='dpAR_joint', attributeType='float', keyable=False)
                utils.setJointLabel(self.eyeScaleJnt, s+jointLabelAdd, 18, self.userGuideName+"Scale_1")
                # jointScale position:
                cmds.delete(cmds.parentConstraint(self.guide, self.eyeScaleJnt, maintainOffset=False))
                # create endScale joint:
                self.endScaleJoint = cmds.joint(name=side+self.userGuideName+"Scale_JEnd")
                cmds.delete(cmds.parentConstraint(self.eyeScaleJnt, self.endScaleJoint, maintainOffset=False))
                cmds.setAttr(self.endScaleJoint+".translateZ", 1)
                # create constraints to eyeScale:
                cmds.pointConstraint(self.jnt, self.eyeScaleJnt, maintainOffset=False, name=self.eyeScaleJnt+"_PointConstraint")
                cmds.orientConstraint(self.baseEyeCtrl, self.eyeScaleJnt, maintainOffset=False, name=self.eyeScaleJnt+"_OrientConstraint")
                cmds.scaleConstraint(self.jnt, self.eyeScaleJnt, maintainOffset=True, name=self.eyeScaleJnt+"_ScaleConstraint")
                self.eyeScaleGrp = cmds.group(self.eyeScaleJnt, name=self.eyeScaleJnt+"_Grp")
                self.eyeScaleGrpList.append(self.eyeScaleGrp)
                
                # create eyelid setup:
                if self.getModuleAttr(EYELID):
                    # declare eyelid guides:
                    self.cvUpperEyelidLoc = side+self.userGuideName+"_Guide_UpperEyelidLoc"
                    self.cvLowerEyelidLoc = side+self.userGuideName+"_Guide_LowerEyelidLoc"
                    
                    # creating eyelids joints:
                    cmds.select(clear=True)
                    self.eyelidJxt = cmds.joint(name=side+self.userGuideName+"_"+self.langDic[self.langName]['c042_eyelid']+"_Jxt", scaleCompensate=False)
                    cmds.delete(cmds.parentConstraint(self.guide, self.eyelidJxt, mo=False))
                    cmds.parent(self.eyelidJxt, self.eyeScaleJnt)
                    self.upperEyelidBaseJxt, self.upperEyelidJnt = self.createEyelidJoints(side, 'c044_upper', "", self.cvUpperEyelidLoc, s+jointLabelAdd)
                    self.upperEyelidMiddleBaseJxt, self.upperEyelidMiddleJnt = self.createEyelidJoints(side, 'c044_upper', self.langDic[self.langName]['c029_middle'], self.cvUpperEyelidLoc, s+jointLabelAdd)
                    self.lowerEyelidBaseJxt, self.lowerEyelidJnt = self.createEyelidJoints(side, 'c045_lower', "", self.cvLowerEyelidLoc, s+jointLabelAdd)
                    self.lowerEyelidMiddleBaseJxt, self.lowerEyelidMiddleJnt = self.createEyelidJoints(side, 'c045_lower', self.langDic[self.langName]['c029_middle'], self.cvLowerEyelidLoc, s+jointLabelAdd)
                    
                    # creating eyelids controls and setup:
                    self.upperEyelidCtrl, self.upperEyelidCtrlZero = self.createEyelidSetup(side, 'c044_upper', self.upperEyelidJnt, self.upperEyelidBaseJxt, self.upperEyelidMiddleBaseJxt, self.upperEyelidMiddleJnt, 30, (0, 0, 0))
                    self.lowerEyelidCtrl, self.lowerEyelidCtrlZero = self.createEyelidSetup(side, 'c045_lower', self.lowerEyelidJnt, self.lowerEyelidBaseJxt, self.lowerEyelidMiddleBaseJxt, self.lowerEyelidMiddleJnt, 30, (0, 0, 180))
                    # fixing mirror behavior for side controls:
                    if s == 0: #left
                        cmds.setAttr(self.upperEyelidCtrl+"."+self.langDic[self.langName]['c053_invert']+"X", 1)
                        cmds.setAttr(self.upperEyelidCtrl+"."+self.langDic[self.langName]['c053_invert']+"Y", 1)
                        cmds.setAttr(self.lowerEyelidCtrl+"."+self.langDic[self.langName]['c053_invert']+"Y", 1)
                    else: #right
                        if cmds.getAttr(self.moduleGrp+".flip") == 0:
                            cmds.setAttr(self.upperEyelidCtrl+"."+self.langDic[self.langName]['c053_invert']+"Y", 1)
                            cmds.setAttr(self.lowerEyelidCtrl+"."+self.langDic[self.langName]['c053_invert']+"X", 1)
                            cmds.setAttr(self.lowerEyelidCtrl+"."+self.langDic[self.langName]['c053_invert']+"Y", 1)
                            cmds.setAttr(self.upperEyelidCtrlZero+".rotateY", 180)
                            cmds.setAttr(self.lowerEyelidCtrlZero+".rotateY", 180)
                        else:
                            cmds.setAttr(self.lowerEyelidCtrl+"."+self.langDic[self.langName]['c053_invert']+"X", 1)
                
                # create iris setup:
                if self.getModuleAttr(IRIS):
                    self.irisCtrl = self.createIrisPupilSetup(s, side, IRIS, 'i080_iris', 12, s+jointLabelAdd)
                    self.irisCtrlList.append(self.irisCtrl)
                    self.hasIris = True
                    
                # create pupil setup:
                if self.getModuleAttr(PUPIL):
                    self.pupilCtrl = self.createIrisPupilSetup(s, side, PUPIL, 'i081_pupil', 4, s+jointLabelAdd)
                    self.pupilCtrlList.append(self.pupilCtrl)
                    self.hasPupil = True
                    
                # create a masterModuleGrp to be checked if this rig exists:
                self.toCtrlHookGrp     = cmds.group(eyeZeroList[0], name=side+self.userGuideName+"_Control_Grp")
                self.toScalableHookGrp = cmds.group(self.jxt, self.eyeScaleGrp, name=side+self.userGuideName+"_Joint_Grp")
                self.toStaticHookGrp   = cmds.group(self.toCtrlHookGrp, self.toScalableHookGrp, name=side+self.userGuideName+"_Grp")
                if s == 0:
                    cmds.parent(self.eyeGrp, self.toCtrlHookGrp)
                    cmds.parent(self.upLocGrp, self.toScalableHookGrp)
                # create a locator in order to avoid delete static group:
                loc = cmds.spaceLocator(name=side+self.userGuideName+"_DO_NOT_DELETE")[0]
                cmds.parent(loc, self.toStaticHookGrp, absolute=True)
                cmds.setAttr(loc+".visibility", 0)
                self.ctrls.setLockHide([loc], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
                # add hook attributes to be read when rigging integrated modules:
                utils.addHook(objName=self.toCtrlHookGrp, hookType='ctrlHook')
                utils.addHook(objName=self.toScalableHookGrp, hookType='scalableHook')
                utils.addHook(objName=self.toStaticHookGrp, hookType='staticHook')
                cmds.addAttr(self.toStaticHookGrp, longName="dpAR_name", dataType="string")
                cmds.addAttr(self.toStaticHookGrp, longName="dpAR_type", dataType="string")
                cmds.setAttr(self.toStaticHookGrp+".dpAR_name", self.userGuideName, type="string")
                cmds.setAttr(self.toStaticHookGrp+".dpAR_type", CLASS_NAME, type="string")
                # add module type counter value
                cmds.addAttr(self.toStaticHookGrp, longName='dpAR_count', attributeType='long', keyable=False)
                cmds.setAttr(self.toStaticHookGrp+'.dpAR_count', dpAR_count)
                if hideJoints:
                    cmds.setAttr(self.toScalableHookGrp+".visibility", 0)
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.userGuideName+'_'+self.mirrorGrp)
            # finalize this rig:
            self.integratingInfo()
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and moduleInstance namespace:
        self.deleteModule()
        
        
    def integratingInfo(self, *args):
        Base.StartClass.integratingInfo(self)
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.integratedActionsDic = {
                                    "module": {
                                                "eyeCtrl"     : self.eyeCtrl,
                                                "eyeGrp"      : self.eyeGrp,
                                                "upLocGrp"    : self.upLocGrp,
                                                "eyeScaleGrp" : self.eyeScaleGrpList,
                                                "irisCtrl"    : self.irisCtrlList,
                                                "pupilCtrl"   : self.pupilCtrlList,
                                                "hasIris"     : self.hasIris,
                                                "hasPupil"    : self.hasPupil,
                                              }
                                    }