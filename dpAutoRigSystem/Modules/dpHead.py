# importing libraries:
import maya.cmds as cmds

from Library import dpControls as ctrls
from Library import dpUtils as utils
import dpBaseClass as Base
import dpLayoutClass as Layout


# global variables to this module:    
CLASS_NAME = "Head"
TITLE = "m017_head"
DESCRIPTION = "m018_headDesc"
ICON = "/Icons/dp_head.png"


class Head(Base.StartClass, Layout.LayoutClass):
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
    
    
    def createGuide(self, *args):
        Base.StartClass.createGuide(self)
        # Custom GUIDE:
        cmds.setAttr(self.moduleGrp+".moduleNamespace", self.moduleGrp[:self.moduleGrp.rfind(":")], type='string')
        # create cvJointLoc and cvLocators:
        self.cvNeckLoc, shapeSizeCH = ctrls.cvJointLoc(ctrlName=self.guideName+"_neck", r=0.5)
        self.connectShapeSize(shapeSizeCH)
        self.cvHeadLoc, shapeSizeCH = ctrls.cvLocator(ctrlName=self.guideName+"_head", r=0.4)
        self.connectShapeSize(shapeSizeCH)
        self.cvJawLoc, shapeSizeCH  = ctrls.cvLocator(ctrlName=self.guideName+"_jaw", r=0.3)
        self.connectShapeSize(shapeSizeCH)
        self.cvChinLoc, shapeSizeCH = ctrls.cvLocator(ctrlName=self.guideName+"_chin", r=0.3)
        self.connectShapeSize(shapeSizeCH)
        self.cvLLipLoc, shapeSizeCH = ctrls.cvLocator(ctrlName=self.guideName+"_lLip", r=0.1)
        self.connectShapeSize(shapeSizeCH)
        self.cvRLipLoc, shapeSizeCH = ctrls.cvLocator(ctrlName=self.guideName+"_rLip", r=0.1)
        self.connectShapeSize(shapeSizeCH)
        # create jointGuides:
        self.jGuideNeck = cmds.joint(name=self.guideName+"_JGuideNeck", radius=0.001)
        self.jGuideHead = cmds.joint(name=self.guideName+"_JGuideHead", radius=0.001)
        self.jGuideJaw  = cmds.joint(name=self.guideName+"_JGuideJaw", radius=0.001)
        self.jGuideChin = cmds.joint(name=self.guideName+"_JGuideChin", radius=0.001)
        # set jointGuides as templates:
        cmds.setAttr(self.jGuideNeck+".template", 1)
        cmds.setAttr(self.jGuideHead+".template", 1)
        cmds.setAttr(self.jGuideJaw+".template", 1)
        cmds.setAttr(self.jGuideChin+".template", 1)
        cmds.parent(self.jGuideNeck, self.moduleGrp, relative=True)
        # create cvEnd:
        self.cvEndJoint, shapeSizeCH = ctrls.cvLocator(ctrlName=self.guideName+"_JointEnd", r=0.1)
        self.connectShapeSize(shapeSizeCH)
        cmds.parent(self.cvEndJoint, self.cvChinLoc)
        cmds.setAttr(self.cvEndJoint+".tz", ctrls.dpCheckLinearUnit(1.3))
        self.jGuideEnd = cmds.joint(name=self.guideName+"_JGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.parent(self.jGuideEnd, self.jGuideChin)
        # make parents between cvLocs:
        cmds.parent(self.cvNeckLoc, self.moduleGrp)
        cmds.parent(self.cvHeadLoc, self.cvNeckLoc)
        cmds.parent(self.cvJawLoc, self.cvHeadLoc)
        cmds.parent(self.cvChinLoc, self.cvJawLoc)
        cmds.parent(self.cvLLipLoc, self.cvJawLoc)
        cmds.parent(self.cvRLipLoc, self.cvJawLoc)
        # connect cvLocs in jointGuides:
        ctrls.directConnect(self.cvNeckLoc, self.jGuideNeck, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        ctrls.directConnect(self.cvHeadLoc, self.jGuideHead, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        ctrls.directConnect(self.cvJawLoc, self.jGuideJaw, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        ctrls.directConnect(self.cvChinLoc, self.jGuideChin, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        ctrls.directConnect(self.cvEndJoint, self.jGuideEnd, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        # limit, lock and hide cvEnd:
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        # transform cvLocs in order to put as a good head guide:
        cmds.setAttr(self.cvNeckLoc+".rotateY", -10)
        cmds.setAttr(self.cvHeadLoc+".translateZ", 2)
        cmds.setAttr(self.cvHeadLoc+".rotateY", 5)
        cmds.setAttr(self.cvJawLoc+".translateX", -0.5)
        cmds.setAttr(self.cvJawLoc+".translateZ", 1.25)
        cmds.setAttr(self.cvJawLoc+".rotateY", -95)
        cmds.setAttr(self.cvChinLoc+".translateZ", 0.25)
        cmds.setAttr(self.moduleGrp+".rotateX", -90)
        cmds.setAttr(self.moduleGrp+".rotateY", 90)
        # lip cvLocs:
        cmds.setAttr(self.cvLLipLoc+".translateY", -0.5)
        cmds.setAttr(self.cvLLipLoc+".translateZ", 1)
        self.lipMD = cmds.createNode("multiplyDivide", name=self.guideName+"_lip_MD")
        cmds.connectAttr(self.cvLLipLoc+".translateX", self.lipMD+".input1X", force=True)
        cmds.connectAttr(self.cvLLipLoc+".translateY", self.lipMD+".input1Y", force=True)
        cmds.connectAttr(self.cvLLipLoc+".translateZ", self.lipMD+".input1Z", force=True)
        cmds.connectAttr(self.lipMD+".outputX", self.cvRLipLoc+".translateX", force=True)
        cmds.connectAttr(self.lipMD+".outputY", self.cvRLipLoc+".translateY", force=True)
        cmds.connectAttr(self.lipMD+".outputZ", self.cvRLipLoc+".translateZ", force=True)
        cmds.setAttr(self.lipMD+".input2Y", -1)

        
    def rigModule(self, *args):
        Base.StartClass.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            try:
                hideJoints = cmds.checkBox('hideJointsCB', query=True, value=True)
            except:
                hideJoints = 1
            # declare lists to store names and attributes:
            self.worldRefList, self.headCtrlList = [], []
            self.aCtrls = []
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
                        for axis in self.mirrorAxis:
                            cmds.setAttr(side+self.userGuideName+'_'+self.mirrorGrp+'.scale'+axis, -1)
            else: # if not mirror:
                duplicated = cmds.duplicate(self.moduleGrp, name=self.userGuideName+'_Guide_Base')[0]
                allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                for item in allGuideList:
                    cmds.rename(item, self.userGuideName+"_"+item)
                self.mirrorGrp = cmds.group(self.userGuideName+'_Guide_Base', name="Guide_Base_Grp", relative=True)
                # re-rename grp:
                cmds.rename(self.mirrorGrp, self.userGuideName+'_'+self.mirrorGrp)
            # store the number of this guide by module type
            dpAR_count = utils.findModuleLastNumber(CLASS_NAME, "dpAR_type") + 1
            # run for all sides
            for s, side in enumerate(sideList):
                # redeclaring variables:
                self.base       = side+self.userGuideName+"_Guide_Base"
                self.cvNeckLoc  = side+self.userGuideName+"_Guide_neck"
                self.cvHeadLoc  = side+self.userGuideName+"_Guide_head"
                self.cvJawLoc   = side+self.userGuideName+"_Guide_jaw"
                self.cvChinLoc  = side+self.userGuideName+"_Guide_chin"
                self.cvLLipLoc  = side+self.userGuideName+"_Guide_lLip"
                self.cvRLipLoc  = side+self.userGuideName+"_Guide_rLip"
                self.cvEndJoint = side+self.userGuideName+"_Guide_JointEnd"
                
                # creating joints:
                self.neckJnt = cmds.joint(name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_neck']+"_Jnt")
                self.headJxt = cmds.joint(name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_head']+"_Jxt")
                cmds.select(clear=True)
                self.headJnt = cmds.joint(name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_head']+"_Jnt", scaleCompensate=False)
                self.jawJnt  = cmds.joint(name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_jaw']+"_Jnt", scaleCompensate=False)
                self.chinJnt = cmds.joint(name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_chin']+"_Jnt", scaleCompensate=False)
                self.endJnt  = cmds.joint(name=side+self.userGuideName+"_JEnd", scaleCompensate=False)
                cmds.select(clear=True)
                self.lLipJnt = cmds.joint(name=side+self.userGuideName+"_"+self.langDic[self.langName]['p002_left']+"_"+self.langDic[self.langName]['c_lip']+"_Jnt", scaleCompensate=False)
                cmds.select(clear=True)
                self.rLipJnt = cmds.joint(name=side+self.userGuideName+"_"+self.langDic[self.langName]['p003_right']+"_"+self.langDic[self.langName]['c_lip']+"_Jnt", scaleCompensate=False)
                dpARJointList = [self.neckJnt, self.headJnt, self.jawJnt, self.chinJnt, self.lLipJnt, self.rLipJnt]
                for dpARJoint in dpARJointList:
                    cmds.addAttr(dpARJoint, longName='dpAR_joint', attributeType='float', keyable=False)
                # creating controls:
                self.neckCtrl = ctrls.cvNeck(ctrlName=side+self.userGuideName+"_"+self.langDic[self.langName]['c_neck']+"_Ctrl", r=self.ctrlRadius/2.0)
                self.headCtrl = ctrls.cvHead(ctrlName=side+self.userGuideName+"_"+self.langDic[self.langName]['c_head']+"_Ctrl", r=self.ctrlRadius/2.0)
                self.jawCtrl  = ctrls.cvJaw( ctrlName=side+self.userGuideName+"_"+self.langDic[self.langName]['c_jaw']+"_Ctrl",  r=self.ctrlRadius/2.0)
                self.chinCtrl = ctrls.cvChin(ctrlName=side+self.userGuideName+"_"+self.langDic[self.langName]['c_chin']+"_Ctrl", r=self.ctrlRadius/2.0)
                self.lLipCtrl = cmds.circle(name=side+self.userGuideName+"_"+self.langDic[self.langName]['p002_left']+"_"+self.langDic[self.langName]['c_lip']+"_Ctrl", ch=False, o=True, nr=(0, 0, 1), d=3, s=8, radius=(self.ctrlRadius * 0.25))[0]
                self.rLipCtrl = cmds.circle(name=side+self.userGuideName+"_"+self.langDic[self.langName]['p003_right']+"_"+self.langDic[self.langName]['c_lip']+"_Ctrl", ch=False, o=True, nr=(0, 0, 1), d=3, s=8, radius=(self.ctrlRadius * 0.25))[0]
                self.headCtrlList.append(self.headCtrl)
                self.aCtrls.append([self.neckCtrl, self.headCtrl, self.jawCtrl, self.chinCtrl, self.lLipCtrl, self.rLipCtrl])

                #Setup Axis Order
                if self.rigType == Base.RigType.quadruped:
                    cmds.setAttr(self.neckCtrl + ".rotateOrder", 1)
                    cmds.setAttr(self.headCtrl + ".rotateOrder", 1)
                    cmds.setAttr(self.jawCtrl + ".rotateOrder", 1)
                else:
                    cmds.setAttr(self.neckCtrl + ".rotateOrder", 4)
                    cmds.setAttr(self.headCtrl + ".rotateOrder", 4)
                    cmds.setAttr(self.jawCtrl + ".rotateOrder", 4)

                # creating the originedFrom attributes (in order to permit integrated parents in the future):
                utils.originedFrom(objName=self.neckCtrl, attrString=self.base+";"+self.cvNeckLoc)
                utils.originedFrom(objName=self.headCtrl, attrString=self.cvHeadLoc)
                utils.originedFrom(objName=self.jawCtrl, attrString=self.cvJawLoc)
                utils.originedFrom(objName=self.chinCtrl, attrString=self.cvChinLoc+";"+self.cvEndJoint)
                
                # orientation of controls:
                ctrls.setAndFreeze(nodeName=self.neckCtrl, rx=90, rz=-90)
                ctrls.setAndFreeze(nodeName=self.headCtrl, rx=90, rz=-90)
                ctrls.setAndFreeze(nodeName=self.jawCtrl, rz=-90)
                ctrls.setAndFreeze(nodeName=self.chinCtrl, rz=-90)
                
                # edit the mirror shape to a good direction of controls:
                ctrlList = [ self.neckCtrl, self.headCtrl, self.jawCtrl, self.chinCtrl ]
                if s == 1:
                    for ctrl in ctrlList:
                        if self.mirrorAxis == 'X':
                            cmds.setAttr(ctrl+'.rotateY', 180)
                        elif self.mirrorAxis == 'Y':
                            cmds.setAttr(ctrl+'.rotateY', 180)
                        elif self.mirrorAxis == 'Z':
                            cmds.setAttr(ctrl+'.rotateX', 180)
                            cmds.setAttr(ctrl+'.rotateZ', 180)
                        elif self.mirrorAxis == 'XYZ':
                            cmds.setAttr(ctrl+'.rotateX', 180)
                            cmds.setAttr(ctrl+'.rotateZ', 180)
                    cmds.makeIdentity(ctrlList, apply=True, translate=False, rotate=True, scale=False)

                # temporary parentConstraints:
                tempDelNeck = cmds.parentConstraint(self.cvNeckLoc, self.neckCtrl, maintainOffset=False)
                tempDelHead = cmds.parentConstraint(self.cvHeadLoc, self.headCtrl, maintainOffset=False)
                tempDelJaw  = cmds.parentConstraint(self.cvJawLoc, self.jawCtrl, maintainOffset=False)
                tempDelChin = cmds.parentConstraint(self.cvChinLoc, self.chinCtrl, maintainOffset=False)
                tempDelLLip = cmds.parentConstraint(self.cvLLipLoc, self.lLipCtrl, maintainOffset=False)
                tempDelRLip = cmds.parentConstraint(self.cvRLipLoc, self.rLipCtrl, maintainOffset=False)
                cmds.delete(tempDelNeck, tempDelHead, tempDelJaw, tempDelChin, tempDelLLip, tempDelRLip)
                
                # zeroOut controls:
                self.zeroLipCtrlList = utils.zeroOut([self.lLipCtrl, self.rLipCtrl])
                self.lLipGrp = cmds.group(self.lLipCtrl, name=self.lLipCtrl+"_Grp")
                self.rLipGrp = cmds.group(self.rLipCtrl, name=self.rLipCtrl+"_Grp")
                self.zeroCtrlList = utils.zeroOut([self.neckCtrl, self.headCtrl, self.jawCtrl, self.chinCtrl, self.zeroLipCtrlList[0], self.zeroLipCtrlList[1]])

                # make joints be ride by controls:
                cmds.makeIdentity(self.neckJnt, self.headJxt, self.headJnt, self.jawJnt, self.chinJnt, self.endJnt, rotate=True, apply=True)
                cmds.parentConstraint(self.neckCtrl, self.neckJnt, maintainOffset=False, name=self.neckJnt+"_ParentConstraint")
                cmds.scaleConstraint(self.neckCtrl, self.neckJnt, maintainOffset=False, name=self.neckJnt+"_ScaleConstraint")
                cmds.delete(cmds.parentConstraint(self.headCtrl, self.headJxt, maintainOffset=False))
                cmds.parentConstraint(self.headCtrl, self.headJnt, maintainOffset=False, name=self.headJnt+"_ParentConstraint")
                cmds.parentConstraint(self.jawCtrl, self.jawJnt, maintainOffset=False, name=self.jawJnt+"_ParentConstraint")
                cmds.parentConstraint(self.chinCtrl, self.chinJnt, maintainOffset=False, name=self.chinJnt+"_ParentConstraint")
                cmds.parentConstraint(self.lLipCtrl, self.lLipJnt, maintainOffset=False, name=self.lLipJnt+"_ParentConstraint")
                cmds.parentConstraint(self.rLipCtrl, self.rLipJnt, maintainOffset=False, name=self.rLipJnt+"_ParentConstraint")
                cmds.scaleConstraint(self.headCtrl, self.headJnt, maintainOffset=False, name=self.headJnt+"_ScaleConstraint")
                cmds.scaleConstraint(self.jawCtrl, self.jawJnt, maintainOffset=False, name=self.jawJnt+"_ScaleConstraint")
                cmds.scaleConstraint(self.chinCtrl, self.chinJnt, maintainOffset=False, name=self.chinJnt+"_ScaleConstraint")
                cmds.scaleConstraint(self.lLipCtrl, self.lLipJnt, maintainOffset=False, name=self.lLipJnt+"_ScaleConstraint")
                cmds.scaleConstraint(self.rLipCtrl, self.rLipJnt, maintainOffset=False, name=self.rLipJnt+"_ScaleConstraint")
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.endJnt, maintainOffset=False))
                cmds.setAttr(self.jawJnt+".segmentScaleCompensate", 0)
                cmds.setAttr(self.chinJnt+".segmentScaleCompensate", 0)

                # create interations between neck and head:
                self.grpNeck = cmds.group(self.zeroCtrlList[0], name=self.neckCtrl+"_Grp")
                self.grpHeadA = cmds.group(empty=True, name=self.headCtrl+"_A_Grp")
                self.grpHead = cmds.group(self.grpHeadA, name=self.headCtrl+"_Grp")
                # arrange pivots:
                self.neckPivot = cmds.xform(self.neckCtrl, query=True, worldSpace=True, translation=True)
                self.headPivot = cmds.xform(self.headCtrl, query=True, worldSpace=True, translation=True)
                cmds.xform(self.grpNeck, pivots=(self.neckPivot[0], self.neckPivot[1], self.neckPivot[2]))
                cmds.xform(self.grpHead, self.grpHeadA, pivots=(self.headPivot[0], self.headPivot[1], self.headPivot[2]))
                
                self.worldRef = cmds.group(empty=True, name=side+self.userGuideName+"_WorldRef")
                self.worldRefList.append(self.worldRef)
                cmds.delete(cmds.parentConstraint(self.neckCtrl, self.worldRef, maintainOffset=False))
                cmds.parentConstraint(self.neckCtrl, self.grpHeadA, maintainOffset=True, skipRotate=["x", "y", "z"], name=self.grpHeadA+"_ParentConstraint")
                orientConst = cmds.orientConstraint(self.neckCtrl, self.worldRef, self.grpHeadA, maintainOffset=False, name=self.grpHeadA+"_OrientConstraint")[0]
                cmds.scaleConstraint(self.neckCtrl, self.grpHeadA, maintainOffset=True, name=self.grpHeadA+"_ScaleConstraint")
                cmds.parent(self.zeroCtrlList[1], self.grpHeadA, absolute=True)

                # connect reverseNode:
                cmds.addAttr(self.headCtrl, longName=self.langDic[self.langName]['c_Follow'], attributeType='float', minValue=0, maxValue=1, keyable=True)
                cmds.connectAttr(self.headCtrl+'.'+self.langDic[self.langName]['c_Follow'], orientConst+"."+self.neckCtrl+"W0", force=True)
                self.headRevNode = cmds.createNode('reverse', name=side+self.userGuideName+"_Rev")
                cmds.connectAttr(self.headCtrl+'.'+self.langDic[self.langName]['c_Follow'], self.headRevNode+".inputX", force=True)
                cmds.connectAttr(self.headRevNode+'.outputX', orientConst+"."+self.worldRef+"W1", force=True)
                
                # mount controls hierarchy:
                cmds.parent(self.zeroCtrlList[3], self.jawCtrl, absolute=True)
                
                # jaw follow head or root ctrl (using worldRef)
                jawParentConst = cmds.parentConstraint(self.headCtrl, self.worldRef, self.zeroCtrlList[2], maintainOffset=True, name=self.zeroCtrlList[2]+"_ParentConstraint")[0]
                cmds.setAttr(jawParentConst+".interpType", 2) #Shortest, no flip cause problem with scrubing
                cmds.addAttr(self.jawCtrl, longName=self.langDic[self.langName]['c_Follow'], attributeType="float", minValue=0, maxValue=1, defaultValue=1, keyable=True)
                cmds.connectAttr(self.jawCtrl+"."+self.langDic[self.langName]['c_Follow'], jawParentConst+"."+self.headCtrl+"W0", force=True)
                jawFollowRev = cmds.createNode("reverse", name=self.jawCtrl+"_Rev")
                cmds.connectAttr(self.jawCtrl+"."+self.langDic[self.langName]['c_Follow'], jawFollowRev+".inputX", force=True)
                cmds.connectAttr(jawFollowRev+".outputX", jawParentConst+"."+self.worldRef+"W1", force=True)
                cmds.scaleConstraint(self.headCtrl, self.zeroCtrlList[2], maintainOffset=True, name=self.zeroCtrlList[2]+"_ScaleConstraint")[0]

                # setup jaw auto translation
                self.jawSdkGrp = cmds.group(self.jawCtrl, name=self.jawCtrl+"_SDK_Grp")
                cmds.addAttr(self.jawCtrl, longName=self.langDic[self.langName]['c_moveIntensity']+"Y", attributeType='float', keyable=True)
                cmds.addAttr(self.jawCtrl, longName=self.langDic[self.langName]['c_moveIntensity']+"Z", attributeType='float', keyable=True)
                cmds.addAttr(self.jawCtrl, longName=self.langDic[self.langName]['c_moveStartRotation'], attributeType='float', keyable=True)
                cmds.setAttr(self.jawCtrl+"."+self.langDic[self.langName]['c_moveIntensity']+"Y", keyable=False, channelBox=True)
                cmds.setAttr(self.jawCtrl+"."+self.langDic[self.langName]['c_moveIntensity']+"Z", keyable=False, channelBox=True)
                cmds.setAttr(self.jawCtrl+"."+self.langDic[self.langName]['c_moveStartRotation'], keyable=False, channelBox=True)
                cmds.setAttr(self.jawCtrl+"."+self.langDic[self.langName]['c_moveIntensity']+"Y", 0.01)
                cmds.setAttr(self.jawCtrl+"."+self.langDic[self.langName]['c_moveIntensity']+"Z", 0.02)
                cmds.setAttr(self.jawCtrl+"."+self.langDic[self.langName]['c_moveStartRotation'], -10)
                self.jawIntensityMD = cmds.createNode('multiplyDivide', name="JawMoveIntensity_MD")
                self.jawIntensityZMD = cmds.createNode('multiplyDivide', name="JawMoveIntensityZ_MD")
                self.jawIntensityZInvMD = cmds.createNode('multiplyDivide', name="JawMoveIntensityZInv_MD")
                self.jawStartIntensityMD = cmds.createNode('multiplyDivide', name="JawMoveIntensityStart_MD")
                self.jawIntensityPMA = cmds.createNode('plusMinusAverage', name="JawMoveIntensity_PMA")
                self.jawIntensityCnd = cmds.createNode('condition', name="JawMoveIntensity_Cnd")
                cmds.connectAttr(self.jawCtrl+".rotateY", self.jawIntensityMD+".input1Y", force=True)
                cmds.connectAttr(self.jawCtrl+"."+self.langDic[self.langName]['c_moveIntensity']+"Y", self.jawIntensityMD+".input2Y", force=True)
                cmds.connectAttr(self.jawCtrl+"."+self.langDic[self.langName]['c_moveIntensity']+"Y", self.jawStartIntensityMD+".input1X", force=True)
                cmds.connectAttr(self.jawCtrl+"."+self.langDic[self.langName]['c_moveStartRotation'], self.jawStartIntensityMD+".input2X", force=True)
                cmds.setAttr(self.jawIntensityPMA+".operation", 2)
                cmds.connectAttr(self.jawIntensityMD+".outputY", self.jawIntensityPMA+".input1D[0]", force=True)
                cmds.connectAttr(self.jawStartIntensityMD+".outputX", self.jawIntensityPMA+".input1D[1]", force=True)
                cmds.connectAttr(self.jawIntensityPMA+".output1D", self.jawIntensityCnd+".colorIfTrueG", force=True)
                cmds.connectAttr(self.jawCtrl+".rotateY", self.jawIntensityCnd+".firstTerm", force=True)
                cmds.connectAttr(self.jawCtrl+"."+self.langDic[self.langName]['c_moveStartRotation'], self.jawIntensityCnd+".secondTerm", force=True)
                cmds.setAttr(self.jawIntensityCnd+".operation", 4)
                cmds.setAttr(self.jawIntensityCnd+".colorIfFalseG", 0)
                cmds.connectAttr(self.jawIntensityCnd+".outColorG", self.jawSdkGrp+".translateX", force=True)
                cmds.connectAttr(self.jawIntensityCnd+".outColorG", self.jawIntensityZMD+".input1Z", force=True)
                cmds.connectAttr(self.jawCtrl+"."+self.langDic[self.langName]['c_moveIntensity']+"Z", self.jawIntensityZMD+".input2Z", force=True)
                cmds.connectAttr(self.jawIntensityZMD+".outputZ", self.jawIntensityZInvMD+".input1Z", force=True)
                cmds.setAttr(self.jawIntensityZInvMD+".input2Z", -1)
                cmds.connectAttr(self.jawIntensityZInvMD+".outputZ", self.jawSdkGrp+".translateZ", force=True)

                # create lip setup:
                # left side lip:
                lLipParentConst = cmds.parentConstraint(self.jawCtrl, self.headCtrl, self.lLipGrp, maintainOffset=True, name=self.lLipGrp+"_ParentConstraint")[0]
                cmds.setAttr(lLipParentConst+".interpType", 2)
                cmds.addAttr(self.lLipCtrl, longName=self.langDic[self.langName]['c_Follow'], attributeType='float', minValue=0, maxValue=1, defaultValue=0.5, keyable=True)
                cmds.connectAttr(self.lLipCtrl+'.'+self.langDic[self.langName]['c_Follow'], lLipParentConst+"."+self.jawCtrl+"W0", force=True)
                self.lLipRevNode = cmds.createNode('reverse', name=side+self.userGuideName+"_"+self.langDic[self.langName]['p002_left']+"_"+self.langDic[self.langName]['c_lip']+"_Rev")
                cmds.connectAttr(self.lLipCtrl+'.'+self.langDic[self.langName]['c_Follow'], self.lLipRevNode+".inputX", force=True)
                cmds.connectAttr(self.lLipRevNode+'.outputX', lLipParentConst+"."+self.headCtrl+"W1", force=True)
                cmds.scaleConstraint(self.headCtrl, self.lLipGrp, maintainOffset=True, name=self.lLipGrp+"_ScaleConstraint")[0]
                # right side lip:
                rLipParentConst = cmds.parentConstraint(self.jawCtrl, self.headCtrl, self.rLipGrp, maintainOffset=True, name=self.rLipGrp+"_ParentConstraint")[0]
                cmds.setAttr(rLipParentConst+".interpType", 2)
                cmds.addAttr(self.rLipCtrl, longName=self.langDic[self.langName]['c_Follow'], attributeType='float', minValue=0, maxValue=1, defaultValue=0.5, keyable=True)
                cmds.connectAttr(self.rLipCtrl+'.'+self.langDic[self.langName]['c_Follow'], rLipParentConst+"."+self.jawCtrl+"W0", force=True)
                self.rLipRevNode = cmds.createNode('reverse', name=side+self.userGuideName+"_"+self.langDic[self.langName]['p003_right']+"_"+self.langDic[self.langName]['c_lip']+"_Rev")
                cmds.connectAttr(self.rLipCtrl+'.'+self.langDic[self.langName]['c_Follow'], self.rLipRevNode+".inputX", force=True)
                cmds.connectAttr(self.rLipRevNode+'.outputX', rLipParentConst+"."+self.headCtrl+"W1", force=True)
                cmds.scaleConstraint(self.headCtrl, self.rLipGrp, maintainOffset=True, name=self.rLipGrp+"_ScaleConstraint")[0]
                
                # create a locator in order to avoid delete static group
                loc = cmds.spaceLocator(name=side+self.userGuideName+"_DO_NOT_DELETE")[0]
                cmds.parent(loc, self.worldRef, absolute=True)
                cmds.setAttr(loc+".visibility", 0)
                ctrls.setLockHide([loc], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
                
                # hiding visibility attributes:
                ctrls.setLockHide([self.headCtrl, self.neckCtrl, self.jawCtrl, self.chinCtrl], ['v'], l=False)
                
                # create a masterModuleGrp to be checked if this rig exists:
                self.toCtrlHookGrp     = cmds.group(self.grpNeck, self.grpHead, self.zeroCtrlList[2], self.zeroCtrlList[4], self.zeroCtrlList[5], name=side+self.userGuideName+"_Control_Grp")
                self.toScalableHookGrp = cmds.group(self.neckJnt, self.headJnt, self.lLipJnt, self.rLipJnt, name=side+self.userGuideName+"_Joint_Grp")
                self.toStaticHookGrp   = cmds.group(self.toCtrlHookGrp, self.toScalableHookGrp, self.grpHead, self.worldRef, name=side+self.userGuideName+"_Grp")
                cmds.addAttr(self.toStaticHookGrp, longName="dpAR_name", dataType="string")
                cmds.addAttr(self.toStaticHookGrp, longName="dpAR_type", dataType="string")
                cmds.setAttr(self.toStaticHookGrp+".dpAR_name", self.userGuideName, type="string")
                cmds.setAttr(self.toStaticHookGrp+".dpAR_type", CLASS_NAME, type="string")
                # add module type counter value
                cmds.addAttr(self.toStaticHookGrp, longName='dpAR_count', attributeType='long', keyable=False)
                cmds.setAttr(self.toStaticHookGrp+'.dpAR_count', dpAR_count)
                # add hook attributes to be read when rigging integrated modules:
                utils.addHook(objName=self.toCtrlHookGrp, hookType='ctrlHook')
                utils.addHook(objName=self.grpHead, hookType='rootHook')
                utils.addHook(objName=self.toScalableHookGrp, hookType='scalableHook')
                utils.addHook(objName=self.toStaticHookGrp, hookType='staticHook')

                #Ensure head Jxt matrix
                mHead = cmds.getAttr(self.headCtrl + ".worldMatrix")
                cmds.xform(self.headJxt, m=mHead, ws=True)

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
                                                "worldRefList" : self.worldRefList,
                                                "headCtrlList" : self.headCtrlList,
                                                "ctrls"        : self.aCtrls,
                                              }
                                    }