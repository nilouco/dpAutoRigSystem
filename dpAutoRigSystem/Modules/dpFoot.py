# importing libraries:
from maya import cmds
from . import dpBaseClass
from . import dpLayoutClass

# global variables to this module:
CLASS_NAME = "Foot"
TITLE = "m024_foot"
DESCRIPTION = "m025_footDesc"
ICON = "/Icons/dp_foot.png"

DP_FOOT_VERSION = 2.4


class Foot(dpBaseClass.StartClass, dpLayoutClass.LayoutClass):
    def __init__(self, *args, **kwargs):
        # Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseClass.StartClass.__init__(self, *args, **kwargs)

        self.footCtrlList = []
        self.revFootCtrlGrpFinalList = []
        self.revFootCtrlShapeList = []
        self.toLimbIkHandleGrpList = []
        self.parentConstList = []
        self.scaleConstList = []
        self.footJntList = []
        self.ballRFList = []
        self.middleFootCtrlList = []
        self.reverseFootAttrList = []
        self.aScalableGrp = []


    def createModuleLayout(self, *args):
        dpBaseClass.StartClass.createModuleLayout(self)
        dpLayoutClass.LayoutClass.basicModuleLayout(self)


    def createGuide(self, *args):
        dpBaseClass.StartClass.createGuide(self)
        # Custom GUIDE:
        # create cvJointLoc and cvLocators:
        self.cvFootLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_Foot", r=0.3, d=1, guide=True)
        self.cvRFALoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_RfA", r=0.3, d=1, guide=True)
        self.cvRFBLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_RfB", r=0.3, d=1, guide=True)
        self.cvRFCLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_RfC", r=0.3, d=1, guide=True)
        self.cvRFDLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_RfD", r=0.3, d=1, guide=True)
        self.cvRFELoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_RfE", r=0.3, d=1, guide=True)
        self.cvRFFLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_RfF", r=0.3, d=1, guide=True)
        # create jointGuides:
        self.jGuideFoot = cmds.joint(name=self.guideName+"_JGuideFoot", radius=0.001)
        self.jGuideRFF = cmds.joint(name=self.guideName+"_JGuideRfF", radius=0.001)
        self.jGuideRFE = cmds.joint(name=self.guideName+"_JGuideRfE", radius=0.001)
        cmds.select(clear=True)
        self.jGuideRFA = cmds.joint(name=self.guideName+"_JGuideRfA", radius=0.001)
        self.jGuideRFD = cmds.joint(name=self.guideName+"_JGuideRfD", radius=0.001)
        self.jGuideRFB = cmds.joint(name=self.guideName+"_JGuideRfB", radius=0.001)
        self.jGuideRFC = cmds.joint(name=self.guideName+"_JGuideRfC", radius=0.001)
        self.jGuideRFAC = cmds.joint(name=self.guideName+"_JGuideRfAC", radius=0.001)
        # set jointGuides as templates:
        cmds.setAttr(self.jGuideFoot+".template", 1)
        cmds.setAttr(self.jGuideRFA+".template", 1)
        cmds.setAttr(self.jGuideRFB+".template", 1)
        cmds.setAttr(self.jGuideRFC+".template", 1)
        cmds.setAttr(self.jGuideRFD+".template", 1)
        cmds.setAttr(self.jGuideRFE+".template", 1)
        cmds.setAttr(self.jGuideRFF+".template", 1)
        cmds.parent(self.jGuideFoot, self.jGuideRFA, self.moduleGrp, relative=True)
        # create cvEnd:
        self.cvEndJoint = self.ctrls.cvLocator(ctrlName=self.guideName+"_JointEnd", r=0.1, d=1, guide=True)
        cmds.parent(self.cvEndJoint, self.cvRFFLoc)
        cmds.setAttr(self.cvEndJoint+".tz", 1.3)
        self.jGuideEnd = cmds.joint(name=self.guideName+"_JGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.parent(self.jGuideEnd, self.jGuideRFF)
        # make parents between cvLocs:
        cmds.parent(self.cvFootLoc, self.cvRFALoc, self.cvRFBLoc, self.cvRFCLoc, self.cvRFDLoc, self.cvRFELoc, self.moduleGrp)
        cmds.parent(self.cvRFFLoc, self.cvFootLoc)
        # connect cvLocs in jointGuides:
        self.ctrls.directConnect(self.cvFootLoc, self.jGuideFoot, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        cmds.parentConstraint(self.cvRFALoc, self.jGuideRFA, maintainOffset=False, name=self.jGuideRFA+"_PaC")
        cmds.parentConstraint(self.cvRFBLoc, self.jGuideRFB, maintainOffset=False, name=self.jGuideRFB+"_PaC")
        cmds.parentConstraint(self.cvRFCLoc, self.jGuideRFC, maintainOffset=False, name=self.jGuideRFC+"_PaC")
        cmds.parentConstraint(self.cvRFDLoc, self.jGuideRFD, maintainOffset=False, name=self.jGuideRFD+"_PaC")
        cmds.parentConstraint(self.cvRFELoc, self.jGuideRFE, maintainOffset=False, name=self.jGuideRFE+"_PaC")
        cmds.parentConstraint(self.cvRFFLoc, self.jGuideRFF, maintainOffset=False, name=self.jGuideRFF+"_PaC")
        cmds.parentConstraint(self.cvRFALoc, self.jGuideRFAC, maintainOffset=False, name=self.jGuideRFAC+"_PaC")
        self.ctrls.directConnect(self.cvEndJoint, self.jGuideEnd, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        # limit, lock and hide cvEnd:
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        self.ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
        # transform cvLocs in order to put as a good foot guide:
        cmds.setAttr(self.cvFootLoc+".translateZ", 2)
        cmds.setAttr(self.cvFootLoc+".rotateX", 90)
        cmds.setAttr(self.cvFootLoc+".rotateZ", -90)
        cmds.setAttr(self.cvRFFLoc+".translateY", -1)
        cmds.setAttr(self.cvRFFLoc+".translateZ", 2.5)
        cmds.setAttr(self.cvRFELoc+".translateX", -2.5)
        cmds.setAttr(self.cvRFELoc+".rotateX", 90)
        cmds.setAttr(self.cvRFELoc+".rotateZ", -90)
        cmds.setAttr(self.cvRFALoc+".translateX", -0.6)
        cmds.setAttr(self.cvRFALoc+".translateY", -1)
        cmds.setAttr(self.cvRFALoc+".rotateX", 90)
        cmds.setAttr(self.cvRFALoc+".rotateZ", -90)
        cmds.setAttr(self.cvRFBLoc+".translateX", -0.6)
        cmds.setAttr(self.cvRFBLoc+".translateY", 1)
        cmds.setAttr(self.cvRFBLoc+".rotateX", 90)
        cmds.setAttr(self.cvRFBLoc+".rotateZ", -90)
        cmds.setAttr(self.cvRFCLoc+".translateX", 1)
        cmds.setAttr(self.cvRFCLoc+".rotateX", 90)
        cmds.setAttr(self.cvRFCLoc+".rotateZ", -90)
        cmds.setAttr(self.cvRFDLoc+".translateX", -3.5)
        cmds.setAttr(self.cvRFDLoc+".rotateX", 90)
        cmds.setAttr(self.cvRFDLoc+".rotateZ", -90)
        cmds.setAttr(self.moduleGrp+".rotateX", -90)
        cmds.setAttr(self.moduleGrp+".rotateY", 90)
        # include nodes into net
        self.addNodeToGuideNet([self.cvFootLoc, self.cvRFALoc, self.cvRFBLoc, self.cvRFCLoc, self.cvRFDLoc, self.cvRFELoc, self.cvRFFLoc, self.cvEndJoint], ["Foot", "RfA", "RfB", "RfC", "RfD", "RfE", "RfF", "JointEnd"])

        # bottom setup
        cvRFEZeroOut = self.utils.zeroOut([self.cvRFELoc], True)
        cvRFEOffsetGrp = cmds.listRelatives(cvRFEZeroOut, children=True)[0]
        cmds.parentConstraint(self.cvRFFLoc, cvRFEOffsetGrp, maintainOffset=True, skipTranslate="y", name=cvRFEOffsetGrp+"_PaC")
        

    def rigModule(self, *args):
        dpBaseClass.StartClass.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            # run for all sides
            for s, side in enumerate(self.sideList):
                # redeclaring variables:
                self.base = side+self.userGuideName+"_Guide_Base"
                self.cvFootLoc = side+self.userGuideName+"_Guide_Foot"
                self.cvRFALoc = side+self.userGuideName+"_Guide_RfA"
                self.cvRFBLoc = side+self.userGuideName+"_Guide_RfB"
                self.cvRFCLoc = side+self.userGuideName+"_Guide_RfC"
                self.cvRFDLoc = side+self.userGuideName+"_Guide_RfD"
                self.cvRFELoc = side+self.userGuideName+"_Guide_RfE"
                self.cvRFFLoc = side+self.userGuideName+"_Guide_RfF"
                self.cvEndJoint = side+self.userGuideName+"_Guide_JointEnd"
                self.radiusGuide = side+self.userGuideName+"_Guide_Base_RadiusCtrl"

                # declaring attributes reading from dictionary:
                ankleRFAttr = self.dpUIinst.lang['c009_leg_extrem']
                middleRFAttr = self.dpUIinst.lang['c017_revFoot_middle']
                outsideRFAttr = self.dpUIinst.lang['c010_revFoot_A']
                insideRFAttr = self.dpUIinst.lang['c011_revFoot_B']
                heelRFAttr = self.dpUIinst.lang['c012_revFoot_C']
                toeRFAttr = self.dpUIinst.lang['c013_revFoot_D']
                ballRFAttr = self.dpUIinst.lang['c014_revFoot_E']
                footRFAttr = self.dpUIinst.lang['c015_revFoot_F']
                sideRFAttr = self.dpUIinst.lang['c016_revFoot_G']
                bottomRFAttr = self.dpUIinst.lang['c100_bottom'].lower()
                rfRoll = self.dpUIinst.lang['c018_revFoot_roll'].capitalize()
                rfSpin = self.dpUIinst.lang['c019_revFoot_spin'].capitalize()
                rfTurn = self.dpUIinst.lang['c020_revFoot_turn'].capitalize()
                rfAngle = self.dpUIinst.lang['c102_angle'].capitalize()
                rfPlant = self.dpUIinst.lang['c103_plant'].capitalize()
                showCtrlsAttr = self.dpUIinst.lang['c021_showControls']

                # creating joints:
                cmds.select(clear=True)
                self.footJnt = cmds.joint(name=side+self.userGuideName+"_"+ankleRFAttr.capitalize()+"_Jnt")
                self.utils.setJointLabel(self.footJnt, s+self.jointLabelAdd, 18, self.userGuideName+ "_"+ankleRFAttr.capitalize())
                self.middleFootJxt = cmds.joint(name=side+self.userGuideName+"_"+middleRFAttr.capitalize()+"_Jxt")
                self.endJnt = cmds.joint(name=side+self.userGuideName+"_JEnd", radius=0.5)
                cmds.select(clear=True)
                self.middleFootJnt = cmds.joint(name=side+self.userGuideName+"_"+middleRFAttr.capitalize()+"_Jnt")
                self.utils.setJointLabel(self.middleFootJnt, s+self.jointLabelAdd, 18, self.userGuideName+"_"+middleRFAttr.capitalize())
                self.endBJnt = cmds.joint(name=side+self.userGuideName+"B_JEnd", radius=0.5)
                cmds.parent(self.middleFootJnt, self.middleFootJxt)
                cmds.addAttr(self.footJnt, longName='dpAR_joint', attributeType='float', keyable=False)
                cmds.addAttr(self.middleFootJnt, longName='dpAR_joint', attributeType='float', keyable=False)
                cmds.select(clear=True)
                
                #Deactivate the segment scale compensate on the bone to prevent scaling problem
                #It will prevent a double scale problem that will come from the upper parent in the rig
                cmds.setAttr(self.footJnt+".segmentScaleCompensate", 0)
                cmds.setAttr(self.middleFootJxt+".segmentScaleCompensate", 0)
                cmds.setAttr(self.middleFootJnt+".segmentScaleCompensate", 0)

                # reverse foot controls:
                self.RFACtrl = self.ctrls.cvControl("id_018_FootReverse", side+self.userGuideName+"_"+outsideRFAttr.capitalize()+"_Ctrl", r=(self.ctrlRadius*0.1), d=self.curveDegree)
                self.RFBCtrl = self.ctrls.cvControl("id_018_FootReverse", side+self.userGuideName+"_"+insideRFAttr.capitalize()+"_Ctrl", r=(self.ctrlRadius*0.1), d=self.curveDegree)
                self.RFCCtrl = self.ctrls.cvControl("id_018_FootReverse", side+self.userGuideName+"_"+heelRFAttr.capitalize()+"_Ctrl", r=(self.ctrlRadius*0.1), d=self.curveDegree, dir="+Y", rot=(0, 90, 0))
                self.RFDCtrl = self.ctrls.cvControl("id_018_FootReverse", side+self.userGuideName+"_"+toeRFAttr.capitalize()+"_Ctrl", r=(self.ctrlRadius*0.1), d=self.curveDegree, dir="+Y", rot=(0, 90, 0))
                self.RFECtrl = self.ctrls.cvControl("id_018_FootReverse", side+self.userGuideName+"_"+bottomRFAttr.capitalize()+"_Ctrl", r=(self.ctrlRadius*0.1), d=self.curveDegree, dir="+Y", rot=(0, 90, 0))
                self.RFFCtrl = self.ctrls.cvControl("id_019_FootReverseE", side+self.userGuideName+"_"+ballRFAttr.capitalize()+"_Ctrl", r=(self.ctrlRadius*0.5), d=self.curveDegree, rot=(0, 90, 0))
                self.ballRFList.append(self.RFFCtrl)
                
                # reverse foot groups:
                self.RFAGrp = cmds.group(self.RFACtrl, name=self.RFACtrl+"_Grp")
                self.RFBGrp = cmds.group(self.RFBCtrl, name=self.RFBCtrl+"_Grp")
                self.RFCGrp = cmds.group(self.RFCCtrl, name=self.RFCCtrl+"_Grp")
                self.RFDGrp = cmds.group(self.RFDCtrl, name=self.RFDCtrl+"_Grp")
                self.RFEGrp = cmds.group(self.RFECtrl, name=self.RFECtrl+"_Grp")
                self.RFFGrp = cmds.group(self.RFFCtrl, name=self.RFFCtrl+"_Grp")
                rfGrpList = [self.RFAGrp, self.RFBGrp, self.RFCGrp, self.RFDGrp, self.RFEGrp, self.RFFGrp]
                
                # putting groups in the correct place:
                cmds.matchTransform(self.footJnt, self.cvFootLoc, position=True, rotation=True)
                cmds.matchTransform(self.middleFootJxt, self.cvRFFLoc, position=True, rotation=True)
                cmds.matchTransform(self.endJnt, self.cvEndJoint, position=True, rotation=True)
                cmds.matchTransform(self.endBJnt, self.cvEndJoint, position=True, rotation=True)
                cmds.matchTransform(self.RFAGrp, self.cvRFALoc, position=True, rotation=True)
                cmds.matchTransform(self.RFBGrp, self.cvRFBLoc, position=True, rotation=True)
                cmds.matchTransform(self.RFCGrp, self.cvRFCLoc, position=True, rotation=True)
                cmds.matchTransform(self.RFDGrp, self.cvRFDLoc, position=True, rotation=True)
                cmds.matchTransform(self.RFEGrp, self.cvRFELoc, position=True, rotation=True)
                cmds.matchTransform(self.RFFGrp, self.cvRFFLoc, position=True, rotation=True)

                # edit ball controller shape
                if s == 0: #left
                    tempBallCluster = cmds.cluster((cmds.listRelatives(self.RFFCtrl, children=True, type="shape")[0])+".cv[3:5]")[1]
                else: #right
                    tempBallCluster = cmds.cluster((cmds.listRelatives(self.RFFCtrl, children=True, type="shape")[0])+".cv[0:2]")[1]
                cmds.setAttr(tempBallCluster+".translateY", self.ctrlRadius*0.3)
                cmds.delete(self.RFFCtrl, constructionHistory=True)
                tempBallClusterB = cmds.cluster(self.RFFCtrl)[1]
                cmds.parentConstraint(self.cvFootLoc, self.cvRFFLoc, tempBallClusterB, maintainOffset=False)
                cmds.delete(self.RFFCtrl, constructionHistory=True)
                
                # mounting hierarchy:
                cmds.parent(self.RFBGrp, self.RFACtrl)
                cmds.parent(self.RFCGrp, self.RFBCtrl)
                cmds.parent(self.RFDGrp, self.RFCCtrl)
                cmds.parent(self.RFEGrp, self.RFDCtrl)
                cmds.parent(self.RFFGrp, self.RFECtrl)
                
                # reverse foot zero out groups:
                self.RFFZero = self.utils.zeroOut([self.RFFGrp])[0]
                self.RFFZeroExtra = self.utils.zeroOut([self.RFFZero])[0]
                self.RFFZeroFollow = self.utils.zeroOut([self.RFFZero])[0]
                self.RFEZero = self.utils.zeroOut([self.RFEGrp])[0]
                self.RFDZero = self.utils.zeroOut([self.RFDGrp])[0]
                self.RFCZero = self.utils.zeroOut([self.RFCGrp])[0]
                self.RFBZero = self.utils.zeroOut([self.RFBGrp])[0]
                self.RFAZero = self.utils.zeroOut([self.RFAGrp])[0]
                self.RFAZeroExtra = self.utils.zeroOut([self.RFAZero])[0]
                
                # fixing side rool rotation order:
                cmds.setAttr(self.RFBZero+".rotateOrder", 5)
                
                # creating ikHandles:
                ikHandleAnkleList = cmds.ikHandle(name=side+self.userGuideName+"_"+ankleRFAttr.capitalize()+"_IKH", startJoint=self.footJnt, endEffector=self.middleFootJxt, solver='ikSCsolver')
                ikHandleMiddleList = cmds.ikHandle(name=side+self.userGuideName+"_"+middleRFAttr.capitalize()+"_IKH", startJoint=self.middleFootJxt, endEffector=self.endJnt, solver='ikSCsolver')
                cmds.rename(ikHandleAnkleList[1], ikHandleAnkleList[0]+"_Eff")
                cmds.rename(ikHandleMiddleList[1], ikHandleMiddleList[0]+"_Eff")
                cmds.setAttr(ikHandleAnkleList[0]+'.visibility', 0)
                cmds.setAttr(ikHandleMiddleList[0]+'.visibility', 0)

                # creating Fk controls:
                self.footCtrl = self.ctrls.cvControl("id_020_FootFk", side+self.userGuideName+"_"+self.dpUIinst.lang['c009_leg_extrem']+"_Ctrl", r=(self.ctrlRadius*0.5), d=self.curveDegree, dir="+Z", guideSource=self.guideName+"_Foot")
                self.footCtrlList.append(self.footCtrl)
                cmds.setAttr(self.footCtrl+".rotateOrder", 1)

                self.revFootCtrlShapeList.append(cmds.listRelatives(self.footCtrl, children=True, type='nurbsCurve')[0])

                self.middleFootCtrl = self.ctrls.cvControl("id_021_FootMiddle", side+self.userGuideName+"_"+self.dpUIinst.lang['c017_revFoot_middle'].capitalize()+"_Ctrl", r=(self.ctrlRadius*0.5), d=self.curveDegree, guideSource=self.guideName+"_RfF")
                cmds.setAttr(self.middleFootCtrl+'.overrideEnabled', 1)
                cmds.setAttr(self.middleFootCtrl+".rotateOrder", 4)
                cmds.matchTransform(self.footCtrl, self.cvFootLoc, position=True, rotation=True)
                cmds.matchTransform(self.middleFootCtrl, self.cvRFFLoc, position=True, rotation=True)
                if s == 1:
                    cmds.setAttr(self.middleFootCtrl+".scaleX", -1)
                    cmds.setAttr(self.middleFootCtrl+".scaleY", -1)
                    cmds.setAttr(self.middleFootCtrl+".scaleZ", -1)
                self.footCtrlZeroList = self.utils.zeroOut([self.footCtrl, self.middleFootCtrl])
                self.middleFootCtrlList.append(self.middleFootCtrl)

                # mount hierarchy:
                cmds.parent(self.footCtrlZeroList[1], self.RFECtrl, absolute=True)
                cmds.parent(ikHandleMiddleList[0], self.middleFootCtrl, absolute=True)
                self.toLimbIkHandleGrp = cmds.group(empty=True, name=side+self.userGuideName+"_"+self.dpUIinst.lang['c009_leg_extrem']+"_Grp")
                self.toLimbIkHandleGrpList.append(self.toLimbIkHandleGrp)
                cmds.parent(ikHandleAnkleList[0], self.toLimbIkHandleGrp, self.RFFCtrl, absolute=True)
                cmds.makeIdentity(self.toLimbIkHandleGrp, apply=True, translate=True, rotate=True, scale=True)
                parentConst = cmds.parentConstraint(self.RFFCtrl, self.footJnt, maintainOffset=True, name=self.footJnt+"_PaC")[0]
                self.parentConstList.append(parentConst)
                self.footJntList.append(self.footJnt)
                cmds.parent(self.RFAZeroExtra, self.footCtrl, absolute=True)
                
                scaleConst = cmds.scaleConstraint(self.footCtrl, self.footJnt, maintainOffset=True, name=self.footJnt+"_ScC")
                self.scaleConstList.append(scaleConst)
                cmds.parentConstraint(self.middleFootCtrl, self.middleFootJnt, maintainOffset=True, name=self.middleFootJnt+"_PaC")
                cmds.scaleConstraint(self.middleFootCtrl, self.middleFootJnt, maintainOffset=True, name=self.middleFootJnt+"_ScC")

                # add attributes to footCtrl and connect them to reverseFoot groups rotation:
                rfAttrList = [outsideRFAttr, insideRFAttr, heelRFAttr, toeRFAttr, bottomRFAttr, ballRFAttr]
                rfTypeAttrList = [rfRoll, rfSpin]
                for j, rfAttr in enumerate(rfAttrList):
                    for t, rfType in enumerate(rfTypeAttrList):
                        if t == 1 and j == (len(rfAttrList) - 1):  # create turn attr to ball
                            cmds.addAttr(self.footCtrl, longName=rfAttr+rfTurn, attributeType='float', keyable=True)
                            cmds.connectAttr(self.footCtrl+"."+rfAttr+rfTurn, rfGrpList[j]+".rotateZ", force=True)
                            self.reverseFootAttrList.append(rfAttr+rfTurn)
                        cmds.addAttr(self.footCtrl, longName=rfAttr+rfType, attributeType='float', keyable=True)
                        self.reverseFootAttrList.append(rfAttr+rfType)
                        if t == 0:
                            if j > 1:
                                cmds.connectAttr(self.footCtrl+"."+rfAttr+rfType, rfGrpList[j]+".rotateX", force=True)
                            else:
                                cmds.connectAttr(self.footCtrl+"."+rfAttr+rfType, rfGrpList[j]+".rotateZ", force=True)
                        else:
                            cmds.connectAttr(self.footCtrl+"."+rfAttr+rfType, rfGrpList[j]+".rotateY", force=True)

                # creating the originedFrom attributes (in order to permit integrated parents in the future):
                self.utils.originedFrom(objName=self.footCtrl, attrString=self.base+";"+self.cvFootLoc+";"+self.radiusGuide)
                self.utils.originedFrom(objName=self.RFACtrl, attrString=self.cvRFALoc)
                self.utils.originedFrom(objName=self.RFBCtrl, attrString=self.cvRFBLoc)
                self.utils.originedFrom(objName=self.RFCCtrl, attrString=self.cvRFCLoc)
                self.utils.originedFrom(objName=self.RFDCtrl, attrString=self.cvRFDLoc)
                self.utils.originedFrom(objName=self.RFECtrl, attrString=self.cvRFELoc)
                self.utils.originedFrom(objName=self.middleFootCtrl, attrString=self.cvRFFLoc+";"+self.cvEndJoint)

                # creating pre-defined attributes for footRoll and sideRoll attributes, also rollAngle:
                cmds.addAttr(self.footCtrl, longName=footRFAttr+rfRoll, attributeType='float', keyable=True)
                cmds.addAttr(self.footCtrl, longName=footRFAttr+rfRoll+rfAngle, attributeType='float', defaultValue=30, keyable=False)
                cmds.addAttr(self.footCtrl, longName=footRFAttr+rfRoll+rfPlant, attributeType='float', defaultValue=0, keyable=False)
                cmds.addAttr(self.footCtrl, longName=sideRFAttr+rfRoll, attributeType='float', keyable=True)
                cmds.setAttr(self.footCtrl+"."+footRFAttr+rfRoll+rfAngle, channelBox=True)
                cmds.setAttr(self.footCtrl+"."+footRFAttr+rfRoll+rfPlant, channelBox=True)

                # create clampNodes in order to limit the side rotations:
                sideClamp = cmds.createNode("clamp", name=side+self.userGuideName+"_Side_Clp")
                # outside values in R
                cmds.setAttr(sideClamp+".minR", -360)
                # inside values in G
                cmds.setAttr(sideClamp+".maxG", 360)
                # inverting sideRoll values:
                sideMD = cmds.createNode("multiplyDivide", name=side+self.userGuideName+"_Side_MD")
                cmds.setAttr(sideMD+".input2X", -1)
                # connections:
                cmds.connectAttr(self.footCtrl+"."+sideRFAttr+rfRoll, sideMD+".input1X", force=True)
                cmds.connectAttr(sideMD+".outputX", sideClamp+".inputR", force=True)
                cmds.connectAttr(sideMD+".outputX", sideClamp+".inputG", force=True)
                cmds.connectAttr(sideClamp+".outputR", self.RFAZero+".rotateZ", force=True)
                cmds.connectAttr(sideClamp+".outputG", self.RFBZero+".rotateZ", force=True)

                # for footRoll:
                footHeelClp = cmds.createNode("clamp", name=side+self.userGuideName+"_Roll_Heel_Clp")
                # heel values in R
                cmds.setAttr(footHeelClp+".minR", -360)
                cmds.connectAttr(self.footCtrl+"."+footRFAttr+rfRoll, footHeelClp+".inputR", force=True)
                cmds.connectAttr(footHeelClp+".outputR", self.RFCZero+".rotateX", force=True)
                
                # footRoll with angle limit:
                footPMA = cmds.createNode("plusMinusAverage", name=side+self.userGuideName+"_Roll_PMA")
                footSR = cmds.createNode("setRange", name=side+self.userGuideName+"_Roll_SR")
                cmds.setAttr(footSR+".oldMaxY", 180)
                cmds.setAttr(footPMA+".input1D[0]", 180)
                cmds.setAttr(footPMA+".operation", 2) #substract
                cmds.connectAttr(self.footCtrl+"."+footRFAttr+rfRoll, footSR+".valueX", force=True)
                cmds.connectAttr(self.footCtrl+"."+footRFAttr+rfRoll, footSR+".valueY", force=True)
                cmds.connectAttr(self.footCtrl+"."+footRFAttr+rfRoll+rfAngle, footSR+".maxX", force=True)
                cmds.connectAttr(self.footCtrl+"."+footRFAttr+rfRoll+rfAngle, footSR+".oldMinY", force=True)
                cmds.connectAttr(self.footCtrl+"."+footRFAttr+rfRoll+rfAngle, footSR+".oldMaxX", force=True)
                cmds.connectAttr(self.footCtrl+"."+footRFAttr+rfRoll+rfAngle, footPMA+".input1D[1]", force=True)
                cmds.connectAttr(footPMA+".output1D", footSR+".maxY", force=True)
                
                # plant angle for foot roll:
                footPlantClp = cmds.createNode("clamp", name=side+self.userGuideName+"_Roll_Plant_Clp")
                footPlantCnd = cmds.createNode("condition", name=side+self.userGuideName+"_Roll_Plant_Cnd")
                cmds.setAttr(footPlantCnd+".operation", 4) #less than
                cmds.connectAttr(self.footCtrl+"."+footRFAttr+rfRoll, footPlantClp+".inputR", force=True)
                cmds.connectAttr(self.footCtrl+"."+footRFAttr+rfRoll+rfPlant, footPlantClp+".maxR", force=True)
                cmds.connectAttr(footPlantClp+".outputR", footPlantCnd+".firstTerm", force=True)
                cmds.connectAttr(footPlantClp+".outputR", footPlantCnd+".colorIfTrueR", force=True)
                cmds.connectAttr(self.footCtrl+"."+footRFAttr+rfRoll+rfPlant, footPlantCnd+".secondTerm", force=True)
                cmds.connectAttr(self.footCtrl+"."+footRFAttr+rfRoll+rfPlant, footPlantCnd+".colorIfFalseR", force=True)
                
                # back to zero footRoll when greather then angle plus plant values:
                anglePlantPMA = cmds.createNode("plusMinusAverage", name=side+self.userGuideName+"_AnglePlant_PMA")
                anglePlantMD = cmds.createNode("multiplyDivide", name=side+self.userGuideName+"_AnglePlant_MD")
                anglePlantRmV = cmds.createNode("remapValue", name=side+self.userGuideName+"_AnglePlant_RmV")
                anglePlantCnd = cmds.createNode("condition", name=side+self.userGuideName+"_AnglePlant_Cnd")
                cmds.setAttr(anglePlantMD+".input2X", -1)
                cmds.setAttr(anglePlantRmV+".inputMax", 90)
                cmds.setAttr(anglePlantRmV+".value[0].value_Interp", 3) #spline
                cmds.setAttr(anglePlantRmV+".value[1].value_Interp", 3) #spline
                cmds.setAttr(anglePlantCnd+".operation", 2) #greather than
                cmds.connectAttr(self.footCtrl+"."+footRFAttr+rfRoll+rfAngle, anglePlantPMA+".input1D[0]", force=True)
                cmds.connectAttr(self.footCtrl+"."+footRFAttr+rfRoll+rfPlant, anglePlantPMA+".input1D[1]", force=True)
                cmds.connectAttr(self.footCtrl+"."+footRFAttr+rfRoll, anglePlantCnd+".firstTerm", force=True)
                cmds.connectAttr(anglePlantPMA+".output1D", anglePlantCnd+".secondTerm", force=True)
                cmds.connectAttr(anglePlantPMA+".output1D", anglePlantMD+".input1X", force=True)
                cmds.connectAttr(anglePlantPMA+".output1D", anglePlantRmV+".inputMin", force=True)
                cmds.connectAttr(anglePlantMD+".outputX", anglePlantRmV+".outputMax", force=True)
                cmds.connectAttr(self.footCtrl+"."+footRFAttr+rfRoll, anglePlantRmV+".inputValue", force=True)
                cmds.connectAttr(anglePlantRmV+".outColorR", anglePlantCnd+".colorIfTrueR", force=True)
                cmds.connectAttr(anglePlantCnd+".outColorR", self.RFFZeroExtra+".rotateX", force=True)
                
                # connect to groups in order to rotate them:
                cmds.connectAttr(footSR+".outValueY", self.RFDZero+".rotateX", force=True)
                cmds.connectAttr(footSR+".outValueX", self.RFFZero+".rotateX", force=True)
                if s == 0: #left
                    cmds.connectAttr(footPlantCnd+".outColorR", self.footCtrlZeroList[1]+".rotateX", force=True)
                else: #fix right side mirror
                    footPlantInvMD = cmds.createNode("multiplyDivide", name=side+self.userGuideName+"_Plant_Inv_MD")
                    cmds.setAttr(footPlantInvMD+".input2X", -1)
                    cmds.connectAttr(footPlantCnd+".outColorR", footPlantInvMD+".input1X", force=True)
                    cmds.connectAttr(footPlantInvMD+".outputX", self.footCtrlZeroList[1]+".rotateX", force=True)
                    self.toIDList.append(footPlantInvMD)
                
                # create follow attribute to footBall control to space switch to middle control space:
                cmds.addAttr(self.RFFCtrl, longName="follow", attributeType ="double", min=0, max=1, defaultValue=0, keyable=True)
                pacFootBall = cmds.parentConstraint(self.middleFootCtrl, self.RFECtrl, self.RFFZeroFollow, maintainOffset=True, name=self.RFFZeroFollow+"_PaC")[0]
                cmds.setAttr(pacFootBall+".interpType", 0)
                cmds.connectAttr(self.RFFCtrl+".follow", pacFootBall+"."+self.middleFootCtrl+"W0")
                footBallRevNode = cmds.createNode("reverse", name=self.RFFCtrl+"_PaC_Rev")
                cmds.connectAttr(self.RFFCtrl+".follow", footBallRevNode+".inputX")
                cmds.connectAttr(footBallRevNode+".outputX", pacFootBall+"."+self.RFECtrl+"W1")

                # organizing keyable attributes:
                self.ctrls.setLockHide([self.middleFootCtrl, self.footCtrl], ['v'], l=False)
                
                # show or hide reverseFoot controls:
                cmds.addAttr(self.footCtrl, longName=showCtrlsAttr, attributeType='short', minValue=0, defaultValue=1, maxValue=1)
                cmds.setAttr(self.footCtrl+"."+showCtrlsAttr, keyable=False, channelBox=True)
                cmds.addAttr(self.footCtrl, longName="visIkFk", attributeType='float', minValue=0, defaultValue=1, maxValue=1, keyable=False)
                mdNode = cmds.createNode("multiplyDivide", name=side+self.userGuideName+"_Vis_MD")
                cmds.connectAttr(self.footCtrl+".visIkFk", mdNode+".input2X", force=True)
                cmds.connectAttr(self.footCtrl+"."+showCtrlsAttr, mdNode+".input1X", force=True)
                showHideCtrlList = [self.RFACtrl, self.RFBCtrl, self.RFCCtrl, self.RFDCtrl, self.RFECtrl, self.RFFCtrl]
                for rfCtrl in showHideCtrlList:
                    rfCtrlShape = cmds.listRelatives(rfCtrl, children=True, type='nurbsCurve')[0]
                    cmds.connectAttr(mdNode+".outputX", rfCtrlShape+".visibility", force=True)
                # create a masterModuleGrp to be checked if this rig exists:
                tempScalableHookGrp = cmds.createNode("transform", name=side+self.userGuideName+"_TEMP_Grp")
                self.hookSetup(side, [self.footCtrlZeroList[0]], [tempScalableHookGrp])
                cmds.delete(tempScalableHookGrp)
                mWorldFoot = cmds.getAttr(self.footJnt+".worldMatrix")
                cmds.xform(self.toScalableHookGrp, matrix=mWorldFoot, worldSpace=True)
                cmds.parent(self.footJnt, self.toScalableHookGrp, absolute=True)
                #Remove the Joint orient to make sure the bone is at the same orientation than it's parent
                cmds.setAttr(self.footJnt+".jointOrientX", 0)
                cmds.setAttr(self.footJnt+".jointOrientY", 0)
                cmds.setAttr(self.footJnt+".jointOrientZ", 0)
                self.aScalableGrp.append(self.toScalableHookGrp)
                self.revFootCtrlGrpFinalList.append(self.toCtrlHookGrp)
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.userGuideName+'_'+self.mirrorGrp)
                self.utils.addCustomAttr([self.RFAGrp, self.RFBGrp, self.RFCGrp, self.RFDGrp, self.RFEGrp], self.utils.ignoreTransformIOAttr)
                self.toIDList.extend([sideClamp, sideMD, footHeelClp, footPMA, footSR, footPlantClp, footPlantCnd, anglePlantPMA, anglePlantMD, anglePlantRmV, anglePlantCnd, footBallRevNode, mdNode])
            # finalize this rig:
            self.serializeGuide()
            self.integratingInfo()
            self.dpUIinst.customAttr.addAttr(0, [self.toStaticHookGrp], descendents=True) #dpID
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and moduleInstance namespace:
        self.deleteModule()
        self.renameUnitConversion()
        self.dpUIinst.customAttr.addAttr(0, self.toIDList) #dpID


    def integratingInfo(self, *args):
        dpBaseClass.StartClass.integratingInfo(self)
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.integratedActionsDic = {
            "module": {
                "revFootCtrlList": self.footCtrlList,
                "revFootCtrlGrpList": self.revFootCtrlGrpFinalList,
                "revFootCtrlShapeList": self.revFootCtrlShapeList,
                "toLimbIkHandleGrpList": self.toLimbIkHandleGrpList,
                "parentConstList": self.parentConstList,
                "scaleConstList": self.scaleConstList,
                "footJntList": self.footJntList,
                "ballRFList": self.ballRFList,
                "middleFootCtrlList": self.middleFootCtrlList,
                "reverseFootAttrList": self.reverseFootAttrList,
                "scalableGrp": self.aScalableGrp,
            }
        }