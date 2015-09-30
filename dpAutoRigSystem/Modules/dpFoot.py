# importing libraries:
import maya.cmds as cmds
import dpControls as ctrls
import dpUtils as utils
import dpBaseClass as Base
import dpLayoutClass as Layout

# global variables to this module:    
CLASS_NAME = "Foot"
TITLE = "m024_foot"
DESCRIPTION = "m025_footDesc"
ICON = "/Icons/dp_foot.png"


class Foot(Base.StartClass, Layout.LayoutClass):
    def __init__(self, dpUIinst, langDic, langName, userGuideName):
        Base.StartClass.__init__(self, dpUIinst, langDic, langName, userGuideName, CLASS_NAME, TITLE, DESCRIPTION, ICON)
        pass
    
    
    def createModuleLayout(self, *args):
        Base.StartClass.createModuleLayout(self)
        Layout.LayoutClass.basicModuleLayout(self)
    
    
    def createGuide(self, *args):
        Base.StartClass.createGuide(self)
        # Custom GUIDE:
        cmds.setAttr(self.moduleGrp+".moduleNamespace", self.moduleGrp[:self.moduleGrp.rfind(":")], type='string')
        # create cvJointLoc and cvLocators:
        self.cvFootLoc, shapeSizeCH = ctrls.cvJointLoc(ctrlName=self.guideName+"_foot", r=0.3)
        self.connectShapeSize(shapeSizeCH)
        self.cvRFALoc, shapeSizeCH  = ctrls.cvLocator(ctrlName=self.guideName+"_RfA", r=0.3)
        self.connectShapeSize(shapeSizeCH)
        self.cvRFBLoc, shapeSizeCH  = ctrls.cvLocator(ctrlName=self.guideName+"_RfB", r=0.3)
        self.connectShapeSize(shapeSizeCH)
        self.cvRFCLoc, shapeSizeCH  = ctrls.cvLocator(ctrlName=self.guideName+"_RfC", r=0.3)
        self.connectShapeSize(shapeSizeCH)
        self.cvRFDLoc, shapeSizeCH  = ctrls.cvLocator(ctrlName=self.guideName+"_RfD", r=0.3)
        self.connectShapeSize(shapeSizeCH)
        self.cvRFELoc, shapeSizeCH  = ctrls.cvLocator(ctrlName=self.guideName+"_RfE", r=0.3)
        self.connectShapeSize(shapeSizeCH)
        # create jointGuides:
        self.jGuideFoot = cmds.joint(name=self.guideName+"_JGuideFoot", radius=0.001)
        self.jGuideRFE  = cmds.joint(name=self.guideName+"_JGuideRfE", radius=0.001)
        cmds.select(clear=True)
        self.jGuideRFA  = cmds.joint(name=self.guideName+"_JGuideRfA", radius=0.001)
        self.jGuideRFD  = cmds.joint(name=self.guideName+"_JGuideRfD", radius=0.001)
        self.jGuideRFB  = cmds.joint(name=self.guideName+"_JGuideRfB", radius=0.001)        
        self.jGuideRFC  = cmds.joint(name=self.guideName+"_JGuideRfC", radius=0.001)
        self.jGuideRFAC = cmds.joint(name=self.guideName+"_JGuideRfAC", radius=0.001)
        # set jointGuides as templates:
        cmds.setAttr(self.jGuideFoot+".template", 1)
        cmds.setAttr(self.jGuideRFA+".template", 1)
        cmds.setAttr(self.jGuideRFB+".template", 1)
        cmds.setAttr(self.jGuideRFC+".template", 1)
        cmds.setAttr(self.jGuideRFD+".template", 1)
        cmds.setAttr(self.jGuideRFE+".template", 1)
        cmds.parent(self.jGuideFoot, self.jGuideRFA, self.moduleGrp, relative=True)
        # create cvEnd:
        self.cvEndJoint, shapeSizeCH = ctrls.cvLocator(ctrlName=self.guideName+"_JointEnd", r=0.1)
        self.connectShapeSize(shapeSizeCH)
        cmds.parent(self.cvEndJoint, self.cvRFELoc)
        cmds.setAttr(self.cvEndJoint+".tz", 1.3)
        self.jGuideEnd = cmds.joint(name=self.guideName+"_JGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.parent(self.jGuideEnd, self.jGuideRFE)
        # make parents between cvLocs:
        cmds.parent(self.cvFootLoc, self.cvRFALoc, self.cvRFBLoc, self.cvRFCLoc, self.cvRFDLoc, self.moduleGrp)
        cmds.parent(self.cvRFELoc, self.cvFootLoc)
        # connect cvLocs in jointGuides:
        ctrls.directConnect(self.cvFootLoc, self.jGuideFoot, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        cmds.parentConstraint(self.cvRFALoc, self.jGuideRFA, maintainOffset=False, name=self.jGuideRFA+"_ParentConstraint")
        cmds.parentConstraint(self.cvRFBLoc, self.jGuideRFB, maintainOffset=False, name=self.jGuideRFB+"_ParentConstraint")
        cmds.parentConstraint(self.cvRFCLoc, self.jGuideRFC, maintainOffset=False, name=self.jGuideRFC+"_ParentConstraint")
        cmds.parentConstraint(self.cvRFDLoc, self.jGuideRFD, maintainOffset=False, name=self.jGuideRFD+"_ParentConstraint")
        cmds.parentConstraint(self.cvRFELoc, self.jGuideRFE, maintainOffset=False, name=self.jGuideRFE+"_ParentConstraint")
        cmds.parentConstraint(self.cvRFALoc, self.jGuideRFAC, maintainOffset=False, name=self.jGuideRFAC+"_ParentConstraint")
        ctrls.directConnect(self.cvEndJoint, self.jGuideEnd, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        # limit, lock and hide cvEnd:
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        # transform cvLocs in order to put as a good foot guide:
        cmds.setAttr(self.cvFootLoc+".translateZ", 2)
        cmds.setAttr(self.cvFootLoc+".rotateY", -90)
        cmds.setAttr(self.cvRFELoc+".translateX", -1)
        cmds.setAttr(self.cvRFELoc+".translateZ", 2.5)
        cmds.setAttr(self.cvRFCLoc+".translateX", 1)
        cmds.setAttr(self.cvRFALoc+".translateX", -0.6)
        cmds.setAttr(self.cvRFALoc+".translateY", -1)
        cmds.setAttr(self.cvRFBLoc+".translateX", -0.6)
        cmds.setAttr(self.cvRFBLoc+".translateY", 1)
        cmds.setAttr(self.cvRFDLoc+".translateX", -3.5)
        cmds.setAttr(self.moduleGrp+".rotateX", -90)
        cmds.setAttr(self.moduleGrp+".rotateY", 90)
    
    
    def rigModule(self, *args):
        Base.StartClass.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            try:
                hideJoints = cmds.checkBox('hideJointsCB', query=True, value=True)
            except:
                hideJoints = 1
            # create lists to be integrated:
            self.footCtrlList, self.revFootCtrlZeroFinalList, self.revFootCtrlShapeList, self.toLimbIkHandleGrpList, self.parentConstList, self.footJntList, self.ballRFList, self.middleFootCtrlList, self.reverseFootAttrList = [], [], [], [], [], [], [], [], []
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
                self.cvFootLoc  = side+self.userGuideName+"_Guide_foot"
                self.cvRFALoc   = side+self.userGuideName+"_Guide_RfA"
                self.cvRFBLoc   = side+self.userGuideName+"_Guide_RfB"
                self.cvRFCLoc   = side+self.userGuideName+"_Guide_RfC"
                self.cvRFDLoc   = side+self.userGuideName+"_Guide_RfD"
                self.cvRFELoc   = side+self.userGuideName+"_Guide_RfE"
                self.cvEndJoint = side+self.userGuideName+"_Guide_JointEnd"
                
                # declaring attributes reading from dictionary:
                ankleRFAttr   = self.langDic[self.langName]['c_leg_extrem']
                middleRFAttr  = self.langDic[self.langName]['c_RevFoot_middle']
                outsideRFAttr = self.langDic[self.langName]['c_RevFoot_A']
                insideRFAttr  = self.langDic[self.langName]['c_RevFoot_B']
                heelRFAttr    = self.langDic[self.langName]['c_RevFoot_C']
                toeRFAttr     = self.langDic[self.langName]['c_RevFoot_D']
                ballRFAttr    = self.langDic[self.langName]['c_RevFoot_E']
                footRFAttr    = self.langDic[self.langName]['c_RevFoot_F']
                sideRFAttr    = self.langDic[self.langName]['c_RevFoot_G']
                rfRoll        = self.langDic[self.langName]['c_RevFoot_roll']
                rfSpin        = self.langDic[self.langName]['c_RevFoot_spin']
                rfTurn        = self.langDic[self.langName]['c_RevFoot_turn']
                
                # creating joints:
                cmds.select(clear=True)
                self.footJnt       = cmds.joint(name=side+self.userGuideName+"_"+ankleRFAttr.capitalize()+"_Jnt")
                self.middleFootJxt = cmds.joint(name=side+self.userGuideName+"_"+middleRFAttr.capitalize()+"_Jxt")
                self.endJnt        = cmds.joint(name=side+self.userGuideName+"_JEnd")
                cmds.select(clear=True)
                self.middleFootJnt = cmds.joint(name=side+self.userGuideName+"_"+middleRFAttr.capitalize()+"_Jnt")
                self.endBJnt       = cmds.joint(name=side+self.userGuideName+"B_JEnd")
                cmds.parent(self.middleFootJnt, self.middleFootJxt)
                cmds.addAttr(self.footJnt, longName='dpAR_joint', attributeType='float', keyable=False)
                cmds.addAttr(self.middleFootJnt, longName='dpAR_joint', attributeType='float', keyable=False)
                cmds.select(clear=True)
                
                # reverse foot joints:
                self.RFAJxt   = cmds.joint(name=side+self.userGuideName+"_"+outsideRFAttr.capitalize()+"_Jxt")
                self.RFBJxt   = cmds.joint(name=side+self.userGuideName+"_"+insideRFAttr.capitalize()+"_Jxt")
                self.RFCJxt   = cmds.joint(name=side+self.userGuideName+"_"+heelRFAttr.capitalize()+"_Jxt")
                self.RFDJxt   = cmds.joint(name=side+self.userGuideName+"_"+toeRFAttr.capitalize()+"_Jxt")
                self.RFEJxt   = cmds.joint(name=side+self.userGuideName+"_"+ballRFAttr.capitalize()+"_Jxt")
                self.RFEndJxt = cmds.joint(name=side+self.userGuideName+"_RFEnd_Jxt")
                rfJointList = [self.RFAJxt, self.RFBJxt, self.RFCJxt, self.RFDJxt, self.RFEJxt]
                self.ballRFList.append(self.RFEJxt)
                # set as template using overrides in order to permit no template children:
                for rfJoint in rfJointList:
                    cmds.setAttr(rfJoint+'.overrideEnabled', 1)
                    cmds.setAttr(rfJoint+'.overrideDisplayType', 1)
                cmds.setAttr(self.footJnt+'.overrideEnabled', 1)
                cmds.setAttr(self.middleFootJnt+'.overrideEnabled', 1)
                # reverse foot zero out joints:
                self.RFEJzt   = utils.zeroOutJoints([self.RFEJxt])[0]
                self.RFDJzt   = utils.zeroOutJoints([self.RFDJxt])[0]
                self.RFCJzt   = utils.zeroOutJoints([self.RFCJxt])[0]
                self.RFBJzt   = utils.zeroOutJoints([self.RFBJxt])[0]
                self.RFAJzt   = utils.zeroOutJoints([self.RFAJxt])[0]
                rfJointZeroList = [self.RFAJzt, self.RFBJzt, self.RFCJzt, self.RFDJzt, self.RFEJzt]
                
                # putting joints in the correct place:
                tempToDelA = cmds.parentConstraint(self.cvFootLoc, self.footJnt, maintainOffset=False)
                tempToDelB = cmds.parentConstraint(self.cvRFELoc, self.middleFootJxt, maintainOffset=False)
                tempToDelC = cmds.parentConstraint(self.cvEndJoint, self.endJnt, maintainOffset=False)
                tempToDelD = cmds.parentConstraint(self.cvEndJoint, self.endBJnt, maintainOffset=False)
                tempToDelE = cmds.parentConstraint(self.cvRFALoc, self.RFAJzt, maintainOffset=False)
                tempToDelF = cmds.parentConstraint(self.cvRFBLoc, self.RFBJzt, maintainOffset=False)
                tempToDelG = cmds.parentConstraint(self.cvRFCLoc, self.RFCJzt, maintainOffset=False)
                tempToDelH = cmds.parentConstraint(self.cvRFDLoc, self.RFDJzt, maintainOffset=False)
                tempToDelI = cmds.parentConstraint(self.cvRFELoc, self.RFEJzt, maintainOffset=False)
                tempToDelJ = cmds.parentConstraint(self.cvEndJoint, self.RFEndJxt, maintainOffset=False)
                cmds.delete(tempToDelA, tempToDelB, tempToDelC, tempToDelD, tempToDelE, tempToDelF, tempToDelG, tempToDelH, tempToDelI, tempToDelJ)
                cmds.makeIdentity(rfJointZeroList, apply=True, translate=True, rotate=True, scale=True)
                
                # creating ikHandles:
                ikHandleAnkleList = cmds.ikHandle(name=side+self.userGuideName+"_"+ankleRFAttr.capitalize()+"_IkHandle", startJoint=self.footJnt, endEffector=self.middleFootJxt, solver='ikSCsolver')
                ikHandleMiddleList = cmds.ikHandle(name=side+self.userGuideName+"_"+middleRFAttr.capitalize()+"_IkHandle", startJoint=self.middleFootJxt, endEffector=self.endJnt, solver='ikSCsolver')
                cmds.rename(ikHandleAnkleList[1], ikHandleAnkleList[0]+"_Effector")
                cmds.rename(ikHandleMiddleList[1], ikHandleMiddleList[0]+"_Effector")
                cmds.setAttr(ikHandleAnkleList[0]+'.visibility', 0)
                cmds.setAttr(ikHandleMiddleList[0]+'.visibility', 0)
                
                # creating Fk controls:
                self.footCtrl = cmds.circle(name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_leg_extrem']+"_Ctrl", ch=False, o=True, nr=(1, 0, 0), d=3, s=8, radius=self.ctrlRadius/2.0)[0]
                self.footCtrlList.append(self.footCtrl)
                self.revFootCtrlShapeList.append(cmds.listRelatives(self.footCtrl, children=True, type='nurbsCurve')[0])
                
                self.middleFootCtrl = cmds.circle(name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_RevFoot_middle'].capitalize()+"_Ctrl", ch=False, o=True, nr=(0, 0, 1), d=1, s=8, radius=self.ctrlRadius/2.0)[0]
                cmds.setAttr(self.middleFootCtrl+'.overrideEnabled', 1)
                tempToDelA = cmds.parentConstraint(self.cvFootLoc, self.footCtrl, maintainOffset=False)
                tempToDelB = cmds.parentConstraint(self.cvRFELoc, self.middleFootCtrl, maintainOffset=False)
                cmds.delete(tempToDelA, tempToDelB)
                self.footCtrlZeroList = utils.zeroOut([self.footCtrl, self.middleFootCtrl])
                self.revFootCtrlZeroFinalList.append(self.footCtrlZeroList[0])
                self.middleFootCtrlList.append(self.middleFootCtrl)
                
                # mount hierarchy:
                cmds.parent(self.footCtrlZeroList[1], self.RFDJxt, absolute=True)
                cmds.parent(ikHandleMiddleList[0], self.middleFootCtrl, absolute=True)
                self.toLimbIkHandleGrp = cmds.group(empty=True, name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_leg_extrem']+"_Grp")
                self.toLimbIkHandleGrpList.append(self.toLimbIkHandleGrp)
                cmds.parent(ikHandleAnkleList[0], self.toLimbIkHandleGrp, self.RFEJxt, absolute=True)
                cmds.makeIdentity(self.toLimbIkHandleGrp, apply=True, translate=True, rotate=True, scale=True)
                parentConst = cmds.parentConstraint(self.RFEJxt, self.footJnt, maintainOffset=True, name=self.footJnt+"_ParentConstraint")[0]
                self.parentConstList.append(parentConst)
                self.footJntList.append(self.footJnt)
                cmds.parent(self.RFAJzt, self.footCtrl, absolute=True)
                cmds.scaleConstraint(self.footCtrl, self.footJnt, maintainOffset=True, name=self.footJnt+"_ScaleConstraint")
                cmds.parentConstraint(self.middleFootCtrl, self.middleFootJnt, maintainOffset=True, name=self.middleFootJnt+"_ParentConstraint")
                cmds.scaleConstraint(self.middleFootCtrl, self.middleFootJnt, maintainOffset=True, name=self.middleFootJnt+"_ScaleConstraint")
                
                # add attributes to footCtrl and connect them to joint rotation:
                rfAttrList = [outsideRFAttr, insideRFAttr, heelRFAttr, toeRFAttr, ballRFAttr]
                rfTypeAttrList = [rfRoll, rfSpin]
                for j, rfAttr in enumerate(rfAttrList):
                    for t, rfType in enumerate(rfTypeAttrList):
                        if t == 1 and j == (len(rfAttrList)-1): # create turn attr to ball
                            cmds.addAttr(self.footCtrl, longName=rfAttr+"_"+rfTurn, attributeType='float', keyable=True)
                            cmds.connectAttr(self.footCtrl+"."+rfAttr+"_"+rfTurn, rfJointList[j]+".rotateX", force=True)
                            self.reverseFootAttrList.append(rfAttr+"_"+rfTurn)
                        cmds.addAttr(self.footCtrl, longName=rfAttr+"_"+rfType, attributeType='float', keyable=True)
                        self.reverseFootAttrList.append(rfAttr+"_"+rfType)
                        if t == 0:
                            if j > 1:
                                cmds.connectAttr(self.footCtrl+"."+rfAttr+"_"+rfType, rfJointList[j]+".rotateY", force=True)
                            else:
                                cmds.connectAttr(self.footCtrl+"."+rfAttr+"_"+rfType, rfJointList[j]+".rotateX", force=True)
                        else:
                            cmds.connectAttr(self.footCtrl+"."+rfAttr+"_"+rfType, rfJointList[j]+".rotateZ", force=True)
                
                # creating the originedFrom attributes (in order to permit integrated parents in the future):
                utils.originedFrom(objName=self.footCtrl, attrString=self.base+";"+self.cvFootLoc+";"+self.cvRFALoc+";"+self.cvRFBLoc+";"+self.cvRFCLoc+";"+self.cvRFDLoc)
                utils.originedFrom(objName=self.middleFootCtrl, attrString=self.cvRFELoc+";"+self.cvEndJoint)
                
                # creating pre-defined attributes for footRoll and sideRoll attributes:
                cmds.addAttr(self.footCtrl, longName=footRFAttr+"_"+rfRoll, attributeType='float', keyable=True)
                cmds.addAttr(self.footCtrl, longName=sideRFAttr+"_"+rfRoll, attributeType='float', keyable=True)
                
                # create clampNodes in order to limit the side rotations:
                sideClamp = cmds.createNode("clamp", name=side+self.userGuideName+"_Side_Clp")
                # outside values in R
                cmds.setAttr(sideClamp+".maxR", 360)
                # inside values in G
                cmds.setAttr(sideClamp+".minG", -360)
                # connections:
                cmds.connectAttr(self.footCtrl+"."+sideRFAttr+"_"+rfRoll, sideClamp+".inputR", force=True)
                cmds.connectAttr(self.footCtrl+"."+sideRFAttr+"_"+rfRoll, sideClamp+".inputG", force=True)
                cmds.connectAttr(sideClamp+".outputR", self.RFAJzt+".rotateX", force=True)
                cmds.connectAttr(sideClamp+".outputG", self.RFBJzt+".rotateX", force=True)
                # for footRoll:
                footClamp = cmds.createNode("clamp", name=side+self.userGuideName+"_Foot_Clp")
                # heel values in R
                cmds.setAttr(footClamp+".maxR", 360)
                cmds.connectAttr(self.footCtrl+"."+footRFAttr+"_"+rfRoll, footClamp+".inputR", force=True)
                cmds.connectAttr(footClamp+".outputR", self.RFCJzt+".rotateY", force=True)
                # set driven keys
                cmds.setDrivenKeyframe(self.RFEJzt+".rotateY", currentDriver=self.footCtrl+"."+footRFAttr+"_"+rfRoll, driverValue=0, value=0, inTangentType="flat", outTangentType="flat")
                cmds.setDrivenKeyframe(self.RFEJzt+".rotateY", currentDriver=self.footCtrl+"."+footRFAttr+"_"+rfRoll, driverValue=-45, value=-45, inTangentType="spline", outTangentType="spline")
                cmds.setDrivenKeyframe(self.RFEJzt+".rotateY", currentDriver=self.footCtrl+"."+footRFAttr+"_"+rfRoll, driverValue=-200, value=0, inTangentType="flat", outTangentType="flat")
                cmds.setDrivenKeyframe(self.RFDJzt+".rotateY", currentDriver=self.footCtrl+"."+footRFAttr+"_"+rfRoll, driverValue=-30, value=0, inTangentType="flat", outTangentType="flat")
                cmds.setDrivenKeyframe(self.RFDJzt+".rotateY", currentDriver=self.footCtrl+"."+footRFAttr+"_"+rfRoll, driverValue=-60, value=-30, inTangentType="spline", outTangentType="spline")
                cmds.setDrivenKeyframe(self.RFDJzt+".rotateY", currentDriver=self.footCtrl+"."+footRFAttr+"_"+rfRoll, driverValue=-360, value=-180, inTangentType="flat", outTangentType="flat")
                
                # organizing keyable attributes:
                ctrls.setLockHide([self.middleFootCtrl, self.footCtrl], ['v'], l=False)
                
                # create a masterModuleGrp to be checked if this rig exists:
                self.toCtrlHookGrp     = cmds.group(self.footCtrlZeroList[0], name=side+self.userGuideName+"_Control_Grp")
                self.toScalableHookGrp = cmds.group(self.footJnt, name=side+self.userGuideName+"_Joint_Grp")
                self.toStaticHookGrp   = cmds.group(self.toCtrlHookGrp, self.toScalableHookGrp, name=side+self.userGuideName+"_Grp")
                cmds.addAttr(self.toStaticHookGrp, longName="dpAR_name", dataType="string")
                cmds.addAttr(self.toStaticHookGrp, longName="dpAR_type", dataType="string")
                cmds.setAttr(self.toStaticHookGrp+".dpAR_name", self.userGuideName, type="string")
                cmds.setAttr(self.toStaticHookGrp+".dpAR_type", CLASS_NAME, type="string")
                # add module type counter value
                cmds.addAttr(self.toStaticHookGrp, longName='dpAR_count', attributeType='long', keyable=False)
                cmds.setAttr(self.toStaticHookGrp+'.dpAR_count', dpAR_count)
                # create a locator in order to avoid delete static group
                loc = cmds.spaceLocator(name=side+self.userGuideName+"_DO_NOT_DELETE")[0]
                cmds.parent(loc, self.toStaticHookGrp, absolute=True)
                cmds.setAttr(loc+".visibility", 0)
                ctrls.setLockHide([loc], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
                # add hook attributes to be read when rigging integrated modules:
                utils.addHook(objName=self.toCtrlHookGrp, hookType='ctrlHook')
                utils.addHook(objName=self.toScalableHookGrp, hookType='scalableHook')
                utils.addHook(objName=self.toStaticHookGrp, hookType='staticHook')
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
                                                "revFootCtrlList"       : self.footCtrlList,
                                                "revFootCtrlZeroList"   : self.revFootCtrlZeroFinalList,
                                                "revFootCtrlShapeList"  : self.revFootCtrlShapeList,
                                                "toLimbIkHandleGrpList" : self.toLimbIkHandleGrpList,
                                                "parentConstList"       : self.parentConstList,
                                                "footJntList"           : self.footJntList,
                                                "ballRFList"            : self.ballRFList,
                                                "middleFootCtrlList"    : self.middleFootCtrlList,
                                                "reverseFootAttrList"   : self.reverseFootAttrList,
                                                }
                                    }