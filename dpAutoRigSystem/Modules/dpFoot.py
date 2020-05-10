# importing libraries:
import maya.cmds as cmds

from Library import dpUtils as utils
import dpBaseClass as Base
import dpLayoutClass as Layout

# global variables to this module:
CLASS_NAME = "Foot"
TITLE = "m024_foot"
DESCRIPTION = "m025_footDesc"
ICON = "/Icons/dp_foot.png"


class Foot(Base.StartClass, Layout.LayoutClass):
    def __init__(self, *args, **kwargs):
        # Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        Base.StartClass.__init__(self, *args, **kwargs)

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
        Base.StartClass.createModuleLayout(self)
        Layout.LayoutClass.basicModuleLayout(self)

    def createGuide(self, *args):
        Base.StartClass.createGuide(self)
        # Custom GUIDE:
        cmds.setAttr(self.moduleGrp+".moduleNamespace", self.moduleGrp[:self.moduleGrp.rfind(":")], type='string')
        # create cvJointLoc and cvLocators:
        self.cvFootLoc, shapeSizeCH = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_Foot", r=0.3, d=1, guide=True)
        self.connectShapeSize(shapeSizeCH)
        self.cvRFALoc, shapeSizeCH = self.ctrls.cvLocator(ctrlName=self.guideName+"_RfA", r=0.3, d=1, guide=True)
        self.connectShapeSize(shapeSizeCH)
        self.cvRFBLoc, shapeSizeCH = self.ctrls.cvLocator(ctrlName=self.guideName+"_RfB", r=0.3, d=1, guide=True)
        self.connectShapeSize(shapeSizeCH)
        self.cvRFCLoc, shapeSizeCH = self.ctrls.cvLocator(ctrlName=self.guideName+"_RfC", r=0.3, d=1, guide=True)
        self.connectShapeSize(shapeSizeCH)
        self.cvRFDLoc, shapeSizeCH = self.ctrls.cvLocator(ctrlName=self.guideName+"_RfD", r=0.3, d=1, guide=True)
        self.connectShapeSize(shapeSizeCH)
        self.cvRFELoc, shapeSizeCH = self.ctrls.cvLocator(ctrlName=self.guideName+"_RfE", r=0.3, d=1, guide=True)
        self.connectShapeSize(shapeSizeCH)
        # create jointGuides:
        self.jGuideFoot = cmds.joint(name=self.guideName+"_JGuideFoot", radius=0.001)
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
        cmds.parent(self.jGuideFoot, self.jGuideRFA, self.moduleGrp, relative=True)
        # create cvEnd:
        self.cvEndJoint, shapeSizeCH = self.ctrls.cvLocator(ctrlName=self.guideName+"_JointEnd", r=0.1, d=1, guide=True)
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
        self.ctrls.directConnect(self.cvFootLoc, self.jGuideFoot, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        cmds.parentConstraint(self.cvRFALoc, self.jGuideRFA, maintainOffset=False, name=self.jGuideRFA+"_ParentConstraint")
        cmds.parentConstraint(self.cvRFBLoc, self.jGuideRFB, maintainOffset=False, name=self.jGuideRFB+"_ParentConstraint")
        cmds.parentConstraint(self.cvRFCLoc, self.jGuideRFC, maintainOffset=False, name=self.jGuideRFC+"_ParentConstraint")
        cmds.parentConstraint(self.cvRFDLoc, self.jGuideRFD, maintainOffset=False, name=self.jGuideRFD+"_ParentConstraint")
        cmds.parentConstraint(self.cvRFELoc, self.jGuideRFE, maintainOffset=False, name=self.jGuideRFE+"_ParentConstraint")
        cmds.parentConstraint(self.cvRFALoc, self.jGuideRFAC, maintainOffset=False, name=self.jGuideRFAC+"_ParentConstraint")
        self.ctrls.directConnect(self.cvEndJoint, self.jGuideEnd, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        # limit, lock and hide cvEnd:
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        self.ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
        # transform cvLocs in order to put as a good foot guide:
        cmds.setAttr(self.cvFootLoc+".translateZ", 2)
        cmds.setAttr(self.cvFootLoc+".rotateX", 90)
        cmds.setAttr(self.cvFootLoc+".rotateZ", -90)
        cmds.setAttr(self.cvRFELoc+".translateY", -1)
        cmds.setAttr(self.cvRFELoc+".translateZ", 2.5)
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

    def rigModule(self, *args):
        Base.StartClass.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            try:
                hideJoints = cmds.checkBox('hideJointsCB', query=True, value=True)
            except:
                hideJoints = 1
            # create lists to be integrated:
            # start as no having mirror:
            sideList = [""]
            # analisys the mirror module:
            self.mirrorAxis = cmds.getAttr(self.moduleGrp+".mirrorAxis")
            if self.mirrorAxis != 'off':
                # get rigs names:
                self.mirrorNames = cmds.getAttr(self.moduleGrp+".mirrorName")
                # get first and last letters to use as side initials (prefix):
                sideList = [self.mirrorNames[0]+'_', self.mirrorNames[len(self.mirrorNames) - 1]+'_']
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
                # joint labelling:
                jointLabelAdd = 1
            else:  # if not mirror:
                duplicated = cmds.duplicate(self.moduleGrp, name=self.userGuideName+'_Guide_Base')[0]
                allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                for item in allGuideList:
                    cmds.rename(item, self.userGuideName+"_"+item)
                self.mirrorGrp = cmds.group(self.userGuideName+'_Guide_Base', name="Guide_Base_Grp", relative=True)
                # re-rename grp:
                cmds.rename(self.mirrorGrp, self.userGuideName+'_'+self.mirrorGrp)
                # joint labelling:
                jointLabelAdd = 0
            # store the number of this guide by module type
            dpAR_count = utils.findModuleLastNumber(CLASS_NAME, "dpAR_type")+1
            # run for all sides
            for s, side in enumerate(sideList):
                # redeclaring variables:
                self.base = side+self.userGuideName+"_Guide_Base"
                self.cvFootLoc = side+self.userGuideName+"_Guide_Foot"
                self.cvRFALoc = side+self.userGuideName+"_Guide_RfA"
                self.cvRFBLoc = side+self.userGuideName+"_Guide_RfB"
                self.cvRFCLoc = side+self.userGuideName+"_Guide_RfC"
                self.cvRFDLoc = side+self.userGuideName+"_Guide_RfD"
                self.cvRFELoc = side+self.userGuideName+"_Guide_RfE"
                self.cvEndJoint = side+self.userGuideName+"_Guide_JointEnd"

                # declaring attributes reading from dictionary:
                ankleRFAttr = self.langDic[self.langName]['c009_leg_extrem']
                middleRFAttr = self.langDic[self.langName]['c017_RevFoot_middle']
                outsideRFAttr = self.langDic[self.langName]['c010_RevFoot_A']
                insideRFAttr = self.langDic[self.langName]['c011_RevFoot_B']
                heelRFAttr = self.langDic[self.langName]['c012_RevFoot_C']
                toeRFAttr = self.langDic[self.langName]['c013_RevFoot_D']
                ballRFAttr = self.langDic[self.langName]['c014_RevFoot_E']
                footRFAttr = self.langDic[self.langName]['c015_RevFoot_F']
                sideRFAttr = self.langDic[self.langName]['c016_RevFoot_G']
                rfRoll = self.langDic[self.langName]['c018_RevFoot_roll']
                rfSpin = self.langDic[self.langName]['c019_RevFoot_spin']
                rfTurn = self.langDic[self.langName]['c020_RevFoot_turn']
                showCtrlsAttr = self.langDic[self.langName]['c021_showControls']

                # creating joints:
                cmds.select(clear=True)
                self.footJnt = cmds.joint(name=side+self.userGuideName+"_"+ankleRFAttr.capitalize()+"_Jnt")
                utils.setJointLabel(self.footJnt, s+jointLabelAdd, 18, self.userGuideName+ "_"+ankleRFAttr.capitalize())
                self.middleFootJxt = cmds.joint(name=side+self.userGuideName+"_"+middleRFAttr.capitalize()+"_Jxt")
                self.endJnt = cmds.joint(name=side+self.userGuideName+"_JEnd")
                cmds.select(clear=True)
                self.middleFootJnt = cmds.joint(name=side+self.userGuideName+"_"+middleRFAttr.capitalize()+"_Jnt")
                utils.setJointLabel(self.middleFootJnt, s+jointLabelAdd, 18, self.userGuideName+"_"+middleRFAttr.capitalize())
                self.endBJnt = cmds.joint(name=side+self.userGuideName+"B_JEnd")
                cmds.parent(self.middleFootJnt, self.middleFootJxt)
                cmds.addAttr(self.footJnt, longName='dpAR_joint', attributeType='float', keyable=False)
                cmds.addAttr(self.middleFootJnt, longName='dpAR_joint', attributeType='float', keyable=False)
                cmds.select(clear=True)
                '''
                Deactivate the segment scale compensate on the bone to prevent scaling problem in maya 2016
                It will prevent a double scale problem that will come from the upper parent in the rig
                '''
                if (int(cmds.about(version=True)[:4]) >= 2016):
                    cmds.setAttr(self.footJnt+".segmentScaleCompensate", 0)
                    cmds.setAttr(self.middleFootJxt+".segmentScaleCompensate", 0)
                    cmds.setAttr(self.middleFootJnt+".segmentScaleCompensate", 0)

                # reverse foot controls:
                self.RFACtrl = self.ctrls.cvControl("id_018_FootReverse", side+self.userGuideName+"_"+outsideRFAttr.capitalize()+"_Ctrl", r=(self.ctrlRadius*0.1), d=self.curveDegree)
                self.RFBCtrl = self.ctrls.cvControl("id_018_FootReverse", side+self.userGuideName+"_"+insideRFAttr.capitalize()+"_Ctrl", r=(self.ctrlRadius*0.1), d=self.curveDegree)
                self.RFCCtrl = self.ctrls.cvControl("id_018_FootReverse", side+self.userGuideName+"_"+heelRFAttr.capitalize()+"_Ctrl", r=(self.ctrlRadius*0.1), d=self.curveDegree, dir="+Y", rot=(0, 90, 0))
                self.RFDCtrl = self.ctrls.cvControl("id_018_FootReverse", side+self.userGuideName+"_"+toeRFAttr.capitalize()+"_Ctrl", r=(self.ctrlRadius*0.1), d=self.curveDegree, dir="+Y", rot=(0, 90, 0))
                self.RFECtrl = self.ctrls.cvControl("id_019_FootReverseE", side+self.userGuideName+"_"+ballRFAttr.capitalize()+"_Ctrl", r=(self.ctrlRadius*0.1), d=self.curveDegree, rot=(0, 90, 0))
                
                # reverse foot groups:
                self.RFAGrp = cmds.group(self.RFACtrl, name=self.RFACtrl+"_Grp")
                self.RFBGrp = cmds.group(self.RFBCtrl, name=self.RFBCtrl+"_Grp")
                self.RFCGrp = cmds.group(self.RFCCtrl, name=self.RFCCtrl+"_Grp")
                self.RFDGrp = cmds.group(self.RFDCtrl, name=self.RFDCtrl+"_Grp")
                self.RFEGrp = cmds.group(self.RFECtrl, name=self.RFECtrl+"_Grp")
                rfGrpList = [self.RFAGrp, self.RFBGrp, self.RFCGrp, self.RFDGrp, self.RFEGrp]
                self.ballRFList.append(self.RFEGrp)
                
                # putting groups in the correct place:
                tempToDelA = cmds.parentConstraint(self.cvFootLoc, self.footJnt, maintainOffset=False)
                tempToDelB = cmds.parentConstraint(self.cvRFELoc, self.middleFootJxt, maintainOffset=False)
                tempToDelC = cmds.parentConstraint(self.cvEndJoint, self.endJnt, maintainOffset=False)
                tempToDelD = cmds.parentConstraint(self.cvEndJoint, self.endBJnt, maintainOffset=False)
                tempToDelE = cmds.parentConstraint(self.cvRFALoc, self.RFAGrp, maintainOffset=False)
                tempToDelF = cmds.parentConstraint(self.cvRFBLoc, self.RFBGrp, maintainOffset=False)
                tempToDelG = cmds.parentConstraint(self.cvRFCLoc, self.RFCGrp, maintainOffset=False)
                tempToDelH = cmds.parentConstraint(self.cvRFDLoc, self.RFDGrp, maintainOffset=False)
                tempToDelI = cmds.parentConstraint(self.cvRFELoc, self.RFEGrp, maintainOffset=False)
                cmds.delete(tempToDelA, tempToDelB, tempToDelC, tempToDelD, tempToDelE, tempToDelF, tempToDelG, tempToDelH, tempToDelI)
                
                # mounting hierarchy:
                cmds.parent(self.RFBGrp, self.RFACtrl)
                cmds.parent(self.RFCGrp, self.RFBCtrl)
                cmds.parent(self.RFDGrp, self.RFCCtrl)
                cmds.parent(self.RFEGrp, self.RFDCtrl)
                
                # reverse foot zero out groups:
                self.RFEZero = utils.zeroOut([self.RFEGrp])[0]
                self.RFDZero = utils.zeroOut([self.RFDGrp])[0]
                self.RFCZero = utils.zeroOut([self.RFCGrp])[0]
                self.RFBZero = utils.zeroOut([self.RFBGrp])[0]
                self.RFAZero = utils.zeroOut([self.RFAGrp])[0]
                self.RFAZeroExtra = utils.zeroOut([self.RFAZero])[0]
                rfJointZeroList = [self.RFAZero, self.RFBZero, self.RFCZero, self.RFDZero, self.RFEZero]
                
                # fixing side rool rotation order:
                cmds.setAttr(self.RFBZero+".rotateOrder", 5)
                
                # creating ikHandles:
                ikHandleAnkleList = cmds.ikHandle(name=side+self.userGuideName+"_"+ankleRFAttr.capitalize()+"_IkHandle", startJoint=self.footJnt, endEffector=self.middleFootJxt, solver='ikSCsolver')
                ikHandleMiddleList = cmds.ikHandle(name=side+self.userGuideName+"_"+middleRFAttr.capitalize()+"_IkHandle", startJoint=self.middleFootJxt, endEffector=self.endJnt, solver='ikSCsolver')
                cmds.rename(ikHandleAnkleList[1], ikHandleAnkleList[0]+"_Effector")
                cmds.rename(ikHandleMiddleList[1], ikHandleMiddleList[0]+"_Effector")
                cmds.setAttr(ikHandleAnkleList[0]+'.visibility', 0)
                cmds.setAttr(ikHandleMiddleList[0]+'.visibility', 0)

                # creating Fk controls:
                self.footCtrl = self.ctrls.cvControl("id_020_FootFk", side+self.userGuideName+"_"+self.langDic[self.langName]['c009_leg_extrem']+"_Ctrl", r=(self.ctrlRadius*0.5), d=self.curveDegree, dir="+Z")
                self.footCtrlList.append(self.footCtrl)
                cmds.setAttr(self.footCtrl+".rotateOrder", 1)

                self.revFootCtrlShapeList.append(cmds.listRelatives(self.footCtrl, children=True, type='nurbsCurve')[0])

                self.middleFootCtrl = self.ctrls.cvControl("id_021_FootMiddle", side+self.userGuideName+"_"+self.langDic[self.langName]['c017_RevFoot_middle'].capitalize()+"_Ctrl", r=(self.ctrlRadius*0.5), d=self.curveDegree)
                cmds.setAttr(self.middleFootCtrl+'.overrideEnabled', 1)
                cmds.setAttr(self.middleFootCtrl+".rotateOrder", 4)
                tempToDelA = cmds.parentConstraint(self.cvFootLoc, self.footCtrl, maintainOffset=False)
                tempToDelB = cmds.parentConstraint(self.cvRFELoc, self.middleFootCtrl, maintainOffset=False)
                cmds.delete(tempToDelA, tempToDelB)
                if s == 1:
                    cmds.setAttr(self.middleFootCtrl+".scaleX", -1)
                    cmds.setAttr(self.middleFootCtrl+".scaleY", -1)
                    cmds.setAttr(self.middleFootCtrl+".scaleZ", -1)
                self.footCtrlZeroList = utils.zeroOut([self.footCtrl, self.middleFootCtrl])
                self.middleFootCtrlList.append(self.middleFootCtrl)

                # mount hierarchy:
                cmds.parent(self.footCtrlZeroList[1], self.RFDCtrl, absolute=True)
                cmds.parent(ikHandleMiddleList[0], self.middleFootCtrl, absolute=True)
                self.toLimbIkHandleGrp = cmds.group(empty=True, name=side+self.userGuideName+"_"+self.langDic[self.langName]['c009_leg_extrem']+"_Grp")
                self.toLimbIkHandleGrpList.append(self.toLimbIkHandleGrp)
                cmds.parent(ikHandleAnkleList[0], self.toLimbIkHandleGrp, self.RFECtrl, absolute=True)
                cmds.makeIdentity(self.toLimbIkHandleGrp, apply=True, translate=True, rotate=True, scale=True)
                parentConst = cmds.parentConstraint(self.RFECtrl, self.footJnt, maintainOffset=True, name=self.footJnt+"_ParentConstraint")[0]
                self.parentConstList.append(parentConst)
                self.footJntList.append(self.footJnt)
                cmds.parent(self.RFAZeroExtra, self.footCtrl, absolute=True)
                
                scaleConst = cmds.scaleConstraint(self.footCtrl, self.footJnt, maintainOffset=True, name=self.footJnt+"_ScaleConstraint")
                self.scaleConstList.append(scaleConst)
                cmds.parentConstraint(self.middleFootCtrl, self.middleFootJnt, maintainOffset=True, name=self.middleFootJnt+"_ParentConstraint")
                cmds.scaleConstraint(self.middleFootCtrl, self.middleFootJnt, maintainOffset=True, name=self.middleFootJnt+"_ScaleConstraint")

                # add attributes to footCtrl and connect them to reverseFoot groups rotation:
                rfAttrList = [outsideRFAttr, insideRFAttr, heelRFAttr, toeRFAttr, ballRFAttr]
                rfTypeAttrList = [rfRoll, rfSpin]
                for j, rfAttr in enumerate(rfAttrList):
                    for t, rfType in enumerate(rfTypeAttrList):
                        if t == 1 and j == (len(rfAttrList) - 1):  # create turn attr to ball
                            cmds.addAttr(self.footCtrl, longName=rfAttr+"_"+rfTurn, attributeType='float', keyable=True)
                            cmds.connectAttr(self.footCtrl+"."+rfAttr+"_"+rfTurn, rfGrpList[j]+".rotateZ", force=True)
                            self.reverseFootAttrList.append(rfAttr+"_"+rfTurn)
                        cmds.addAttr(self.footCtrl, longName=rfAttr+"_"+rfType, attributeType='float', keyable=True)
                        self.reverseFootAttrList.append(rfAttr+"_"+rfType)
                        if t == 0:
                            if j > 1:
                                cmds.connectAttr(self.footCtrl+"."+rfAttr+"_"+rfType, rfGrpList[j]+".rotateX", force=True)
                            else:
                                cmds.connectAttr(self.footCtrl+"."+rfAttr+"_"+rfType, rfGrpList[j]+".rotateZ", force=True)
                        else:
                            cmds.connectAttr(self.footCtrl+"."+rfAttr+"_"+rfType, rfGrpList[j]+".rotateY", force=True)

                # creating the originedFrom attributes (in order to permit integrated parents in the future):
                utils.originedFrom(objName=self.footCtrl, attrString=self.base+";"+self.cvFootLoc+";"+self.cvRFALoc+";"+self.cvRFBLoc+";"+self.cvRFCLoc+";"+self.cvRFDLoc)
                utils.originedFrom(objName=self.middleFootCtrl, attrString=self.cvRFELoc+";"+self.cvEndJoint)

                # creating pre-defined attributes for footRoll and sideRoll attributes:
                cmds.addAttr(self.footCtrl, longName=footRFAttr+"_"+rfRoll, attributeType='float', keyable=True)
                cmds.addAttr(self.footCtrl, longName=sideRFAttr+"_"+rfRoll, attributeType='float', keyable=True)

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
                cmds.connectAttr(self.footCtrl+"."+sideRFAttr+"_"+rfRoll, sideMD+".input1X", force=True)
                cmds.connectAttr(sideMD+".outputX", sideClamp+".inputR", force=True)
                cmds.connectAttr(sideMD+".outputX", sideClamp+".inputG", force=True)
                cmds.connectAttr(sideClamp+".outputR", self.RFAZero+".rotateZ", force=True)
                cmds.connectAttr(sideClamp+".outputG", self.RFBZero+".rotateZ", force=True)

                # for footRoll:
                footClamp = cmds.createNode("clamp", name=side+self.userGuideName+"_Foot_Clp")
                # heel values in R
                cmds.setAttr(footClamp+".minR", -360)
                cmds.connectAttr(self.footCtrl+"."+footRFAttr+"_"+rfRoll, footClamp+".inputR", force=True)
                cmds.connectAttr(footClamp+".outputR", self.RFCZero+".rotateX", force=True)
                
                # set driven keys
                cmds.setDrivenKeyframe(self.RFEZero+".rotateX", currentDriver=self.footCtrl+"."+footRFAttr+"_"+rfRoll, driverValue=0, value=0, inTangentType="flat", outTangentType="flat")
                cmds.setDrivenKeyframe(self.RFEZero+".rotateX", currentDriver=self.footCtrl+"."+footRFAttr+"_"+rfRoll, driverValue=45, value=45, inTangentType="spline", outTangentType="spline")
                cmds.setDrivenKeyframe(self.RFEZero+".rotateX", currentDriver=self.footCtrl+"."+footRFAttr+"_"+rfRoll, driverValue=200, value=0, inTangentType="flat", outTangentType="flat")
                cmds.setDrivenKeyframe(self.RFDZero+".rotateX", currentDriver=self.footCtrl+"."+footRFAttr+"_"+rfRoll, driverValue=30, value=0, inTangentType="flat", outTangentType="flat")
                cmds.setDrivenKeyframe(self.RFDZero+".rotateX", currentDriver=self.footCtrl+"."+footRFAttr+"_"+rfRoll, driverValue=60, value=30, inTangentType="spline", outTangentType="spline")
                cmds.setDrivenKeyframe(self.RFDZero+".rotateX", currentDriver=self.footCtrl+"."+footRFAttr+"_"+rfRoll, driverValue=360, value=180, inTangentType="flat", outTangentType="flat")
                
                # organizing keyable attributes:
                self.ctrls.setLockHide([self.middleFootCtrl, self.footCtrl], ['v'], l=False)
                
                # show or hide reverseFoot controls:
                cmds.addAttr(self.footCtrl, longName=showCtrlsAttr, attributeType='long', min=0, max=1, defaultValue=1)
                cmds.setAttr(self.footCtrl+"."+showCtrlsAttr, keyable=False, channelBox=True)
                showHideCtrlList = [self.RFACtrl, self.RFBCtrl, self.RFCCtrl, self.RFDCtrl]
                for rfCtrl in showHideCtrlList:
                    rfCtrlShape = cmds.listRelatives(rfCtrl, children=True, type='nurbsCurve')[0]
                    cmds.connectAttr(self.footCtrl+"."+showCtrlsAttr, rfCtrlShape+".visibility", force=True)
                
                # create a masterModuleGrp to be checked if this rig exists:
                self.toCtrlHookGrp = cmds.group(self.footCtrlZeroList[0], name=side+self.userGuideName+"_Control_Grp")
                self.revFootCtrlGrpFinalList.append(self.toCtrlHookGrp)
                
                self.toScalableHookGrp = cmds.createNode("transform", name=side+self.userGuideName+"_Joint_Grp")
                mWorldFoot = cmds.getAttr(self.footJnt+".worldMatrix")
                cmds.xform(self.toScalableHookGrp, matrix=mWorldFoot, worldSpace=True)
                cmds.parent(self.footJnt, self.toScalableHookGrp, absolute=True)
                #Remove the Joint orient to make sure the bone is at the same orientation than it's parent
                cmds.setAttr(self.footJnt+".jointOrientX", 0)
                cmds.setAttr(self.footJnt+".jointOrientY", 0)
                cmds.setAttr(self.footJnt+".jointOrientZ", 0)
                self.aScalableGrp.append(self.toScalableHookGrp)
                
                self.toStaticHookGrp = cmds.group(self.toCtrlHookGrp, self.toScalableHookGrp, name=side+self.userGuideName+"_Grp")
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
                self.ctrls.setLockHide([loc], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
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
