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
        self.cvFootLoc = ctrls.cvJointLoc(ctrlName=self.guideName+"_foot", r=0.3)
        self.cvRFALoc  = ctrls.cvLocator(ctrlName=self.guideName+"_rfA", r=0.3)
        self.cvRFBLoc  = ctrls.cvLocator(ctrlName=self.guideName+"_rfB", r=0.3)
        self.cvRFCLoc  = ctrls.cvLocator(ctrlName=self.guideName+"_rfC", r=0.3)
        self.cvRFDLoc  = ctrls.cvLocator(ctrlName=self.guideName+"_rfD", r=0.3)
        self.cvRFELoc  = ctrls.cvLocator(ctrlName=self.guideName+"_rfE", r=0.3)
        # create jointGuides:
        self.jGuideFoot = cmds.joint(name=self.guideName+"_jGuideFoot", radius=0.001)
        self.jGuideRFE  = cmds.joint(name=self.guideName+"_jGuideRfE", radius=0.001)
        cmds.select(clear=True)
        self.jGuideRFA  = cmds.joint(name=self.guideName+"_jGuideRfA", radius=0.001)
        self.jGuideRFD  = cmds.joint(name=self.guideName+"_jGuideRfD", radius=0.001)
        self.jGuideRFB  = cmds.joint(name=self.guideName+"_jGuideRfB", radius=0.001)        
        self.jGuideRFC  = cmds.joint(name=self.guideName+"_jGuideRfC", radius=0.001)
        self.jGuideRFAC = cmds.joint(name=self.guideName+"_jGuideRfAC", radius=0.001)
        # set jointGuides as templates:
        cmds.setAttr(self.jGuideFoot+".template", 1)
        cmds.setAttr(self.jGuideRFA+".template", 1)
        cmds.setAttr(self.jGuideRFB+".template", 1)
        cmds.setAttr(self.jGuideRFC+".template", 1)
        cmds.setAttr(self.jGuideRFD+".template", 1)
        cmds.setAttr(self.jGuideRFE+".template", 1)
        cmds.parent(self.jGuideFoot, self.jGuideRFA, self.moduleGrp, relative=True)
        # create cvEnd:
        self.cvEndJoint = ctrls.cvLocator(ctrlName=self.guideName+"_jointEnd", r=0.1)
        cmds.parent(self.cvEndJoint, self.cvRFELoc)
        cmds.setAttr(self.cvEndJoint+".tz", 1.3)
        self.jGuideEnd = cmds.joint(name=self.guideName+"_jGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.parent(self.jGuideEnd, self.jGuideRFE)
        # make parents between cvLocs:
        cmds.parent(self.cvFootLoc, self.cvRFALoc, self.cvRFBLoc, self.cvRFCLoc, self.cvRFDLoc, self.moduleGrp)
        cmds.parent(self.cvRFELoc, self.cvFootLoc)
        # connect cvLocs in jointGuides:
        ctrls.directConnect(self.cvFootLoc, self.jGuideFoot, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        cmds.parentConstraint(self.cvRFALoc, self.jGuideRFA, maintainOffset=False, name=self.jGuideRFA+"_parentConstraint")
        cmds.parentConstraint(self.cvRFBLoc, self.jGuideRFB, maintainOffset=False, name=self.jGuideRFB+"_parentConstraint")
        cmds.parentConstraint(self.cvRFCLoc, self.jGuideRFC, maintainOffset=False, name=self.jGuideRFC+"_parentConstraint")
        cmds.parentConstraint(self.cvRFDLoc, self.jGuideRFD, maintainOffset=False, name=self.jGuideRFD+"_parentConstraint")
        cmds.parentConstraint(self.cvRFELoc, self.jGuideRFE, maintainOffset=False, name=self.jGuideRFE+"_parentConstraint")
        cmds.parentConstraint(self.cvRFALoc, self.jGuideRFAC, maintainOffset=False, name=self.jGuideRFAC+"_parentConstraint")
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
            self.footCtrlList, self.revFootCtrlZeroFinalList, self.revFootCtrlShapeList, self.toLimbIkHandleGrpList, self.parentConstList, self.footJntList = [], [], [], [], [], []
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
                    duplicated = cmds.duplicate(self.moduleGrp, name=side+self.userGuideName+'_guide_base')[0]
                    allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                    for item in allGuideList:
                        cmds.rename(item, side+self.userGuideName+"_"+item)
                    self.mirrorGrp = cmds.group(name="guide_base_grp", empty=True)
                    cmds.parent(side+self.userGuideName+'_guide_base', self.mirrorGrp, absolute=True)
                    # re-rename grp:
                    cmds.rename(self.mirrorGrp, side+self.userGuideName+'_'+self.mirrorGrp)
                    # do a group mirror with negative scaling:
                    if s == 1:
                        for axis in self.mirrorAxis:
                            cmds.setAttr(side+self.userGuideName+'_'+self.mirrorGrp+'.scale'+axis, -1)
            else: # if not mirror:
                duplicated = cmds.duplicate(self.moduleGrp, name=self.userGuideName+'_guide_base')[0]
                allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                for item in allGuideList:
                    cmds.rename(item, self.userGuideName+"_"+item)
                self.mirrorGrp = cmds.group(self.userGuideName+'_guide_base', name="guide_base_grp", relative=True)
                # re-rename grp:
                cmds.rename(self.mirrorGrp, self.userGuideName+'_'+self.mirrorGrp)
            # store the number of this guide by module type
            dpAR_count = utils.findModuleLastNumber(CLASS_NAME, "dpAR_type") + 1
            # run for all sides
            for s, side in enumerate(sideList):
                # redeclaring variables:
                self.base       = side+self.userGuideName+"_guide_base"
                self.cvFootLoc  = side+self.userGuideName+"_guide_foot"
                self.cvRFALoc   = side+self.userGuideName+"_guide_rfA"
                self.cvRFBLoc   = side+self.userGuideName+"_guide_rfB"
                self.cvRFCLoc   = side+self.userGuideName+"_guide_rfC"
                self.cvRFDLoc   = side+self.userGuideName+"_guide_rfD"
                self.cvRFELoc   = side+self.userGuideName+"_guide_rfE"
                self.cvEndJoint = side+self.userGuideName+"_guide_jointEnd"
                
                # declaring attributes reading from dictionary:
                ankleRFAttr   = self.langDic[self.langName]['c_leg_extrem']
                middleRFAttr  = self.langDic[self.langName]['c_revFoot_middle']
                outsideRFAttr = self.langDic[self.langName]['c_revFoot_A']
                insideRFAttr  = self.langDic[self.langName]['c_revFoot_B']
                heelRFAttr    = self.langDic[self.langName]['c_revFoot_C']
                toeRFAttr     = self.langDic[self.langName]['c_revFoot_D']
                ballRFAttr    = self.langDic[self.langName]['c_revFoot_E']
                rfRoll        = self.langDic[self.langName]['c_revFoot_roll']
                rfSpin        = self.langDic[self.langName]['c_revFoot_spin']
                
                # creating joints:
                cmds.select(clear=True)
                self.footJnt       = cmds.joint(name=side+self.userGuideName+"_"+ankleRFAttr+"_jnt")
                self.middleFootJnt = cmds.joint(name=side+self.userGuideName+"_"+middleRFAttr+"_jnt")
                self.endJnt        = cmds.joint(name=side+self.userGuideName+"_jEnd")
                cmds.addAttr(self.footJnt, longName='dpAR_joint', attributeType='float', keyable=False)
                cmds.addAttr(self.middleFootJnt, longName='dpAR_joint', attributeType='float', keyable=False)
                cmds.select(clear=True)
                self.RFAJxt   = cmds.joint(name=side+self.userGuideName+"_"+outsideRFAttr+"_jxt")
                self.RFBJxt   = cmds.joint(name=side+self.userGuideName+"_"+insideRFAttr+"_jxt")
                self.RFCJxt   = cmds.joint(name=side+self.userGuideName+"_"+heelRFAttr+"_jxt")
                self.RFDJxt   = cmds.joint(name=side+self.userGuideName+"_"+toeRFAttr+"_jxt")
                self.RFEJxt   = cmds.joint(name=side+self.userGuideName+"_"+ballRFAttr+"_jxt")
                self.RFEndJxt = cmds.joint(name=side+self.userGuideName+"_RFEnd_jxt")
                rfJointList = [self.RFAJxt, self.RFBJxt, self.RFCJxt, self.RFDJxt, self.RFEJxt]
                # set as template using overrides in order to permit children no templates:
                for rfJoint in rfJointList:
                    cmds.setAttr(rfJoint+'.overrideEnabled', 1)
                    cmds.setAttr(rfJoint+'.overrideDisplayType', 1)
                cmds.setAttr(self.footJnt+'.overrideEnabled', 1)
                cmds.setAttr(self.middleFootJnt+'.overrideEnabled', 1)
                
                # putting joints in the correct place:
                tempToDelA = cmds.parentConstraint(self.cvFootLoc, self.footJnt, maintainOffset=False)
                tempToDelB = cmds.parentConstraint(self.cvRFELoc, self.middleFootJnt, maintainOffset=False)
                tempToDelC = cmds.parentConstraint(self.cvEndJoint, self.endJnt, maintainOffset=False)
                tempToDelD = cmds.parentConstraint(self.cvRFALoc, self.RFAJxt, maintainOffset=False)
                tempToDelE = cmds.parentConstraint(self.cvRFBLoc, self.RFBJxt, maintainOffset=False)
                tempToDelF = cmds.parentConstraint(self.cvRFCLoc, self.RFCJxt, maintainOffset=False)
                tempToDelG = cmds.parentConstraint(self.cvRFDLoc, self.RFDJxt, maintainOffset=False)
                tempToDelH = cmds.parentConstraint(self.cvRFELoc, self.RFEJxt, maintainOffset=False)
                tempToDelI = cmds.parentConstraint(self.cvEndJoint, self.RFEndJxt, maintainOffset=False)
                cmds.delete(tempToDelA, tempToDelB, tempToDelC, tempToDelD, tempToDelE, tempToDelF, tempToDelG, tempToDelH, tempToDelI)
                cmds.makeIdentity(rfJointList, apply=True, translate=True, rotate=True, scale=True)
                
                # creating ikHandles:
                ikHandleAnkleList = cmds.ikHandle(name=side+self.userGuideName+"_"+ankleRFAttr+"_ikHandle", startJoint=self.footJnt, endEffector=self.middleFootJnt, solver='ikSCsolver')
                ikHandleMiddleList = cmds.ikHandle(name=side+self.userGuideName+"_"+middleRFAttr+"_ikHandle", startJoint=self.middleFootJnt, endEffector=self.endJnt, solver='ikSCsolver')
                cmds.rename(ikHandleAnkleList[1], ikHandleAnkleList[0]+"_effector")
                cmds.rename(ikHandleMiddleList[1], ikHandleMiddleList[0]+"_effector")
                cmds.setAttr(ikHandleAnkleList[0]+'.visibility', 0)
                cmds.setAttr(ikHandleMiddleList[0]+'.visibility', 0)
                
                # creating Fk controls:
                self.footCtrl = cmds.circle(name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_leg_extrem']+"_ctrl", ch=False, o=True, nr=(1, 0, 0), d=3, s=8, radius=self.ctrlRadius/2.0)[0]
                self.footCtrlList.append(self.footCtrl)
                self.revFootCtrlShapeList.append(cmds.listRelatives(self.footCtrl, children=True, type='nurbsCurve')[0])
                self.middleFootCtrl = cmds.circle(name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_revFoot_middle']+"_ctrl", ch=False, o=True, nr=(0, 0, 1), d=1, s=8, radius=self.ctrlRadius/2.0)[0]
                cmds.setAttr(self.middleFootCtrl+'.overrideEnabled', 1)
                tempToDelA = cmds.parentConstraint(self.cvFootLoc, self.footCtrl, maintainOffset=False)
                tempToDelB = cmds.parentConstraint(self.cvRFELoc, self.middleFootCtrl, maintainOffset=False)
                cmds.delete(tempToDelA, tempToDelB)
                self.footCtrlZeroList = utils.zeroOut([self.footCtrl, self.middleFootCtrl])
                self.revFootCtrlZeroFinalList.append(self.footCtrlZeroList[0])
                
                # mount hierarchy:
                cmds.parent(self.footCtrlZeroList[1], self.RFDJxt, absolute=True)
                cmds.parent(ikHandleMiddleList[0], self.middleFootCtrl, absolute=True)
                self.toLimbIkHandleGrp = cmds.group(empty=True, name=side+self.userGuideName+"_"+self.langDic[self.langName]['c_leg_extrem']+"_grp")
                self.toLimbIkHandleGrpList.append(self.toLimbIkHandleGrp)
                cmds.parent(ikHandleAnkleList[0], self.toLimbIkHandleGrp, self.RFEJxt, absolute=True)
                cmds.makeIdentity(self.toLimbIkHandleGrp, apply=True, translate=True, rotate=True, scale=True)
                parentConst = cmds.parentConstraint(self.RFEJxt, self.footJnt, maintainOffset=True, name=self.footJnt+"_parentConstraint")[0]
                self.parentConstList.append(parentConst)
                self.footJntList.append(self.footJnt)
                cmds.parent(self.RFAJxt, self.footCtrl, absolute=True)
                cmds.scaleConstraint(self.footCtrl, self.footJnt, maintainOffset=True, name=self.footJnt+"_scaleConstraint")
                cmds.scaleConstraint(self.middleFootCtrl, self.middleFootJnt, maintainOffset=True, name=self.middleFootJnt+"_scaleConstraint")
                
                # add attributes to footCtrl and connect them to joint rotation:
                rfAttrList = [outsideRFAttr, insideRFAttr, heelRFAttr, toeRFAttr, ballRFAttr]
                rfTypeAttrList = [rfRoll, rfSpin]
                for j, rfAttr in enumerate(rfAttrList):
                    for t, rfType in enumerate(rfTypeAttrList):
                        if t == 1 and j == (len(rfAttrList)-1): # do not create ball spin attribute.
                            pass
                        else:
                            cmds.addAttr(self.footCtrl, longName=rfAttr+"_"+rfType, attributeType='float', keyable=True)
                        if t == 0:
                            if j > 1:
                                cmds.connectAttr(self.footCtrl+"."+rfAttr+"_"+rfType, rfJointList[j]+".rotateY", force=True)
                            else:
                                cmds.connectAttr(self.footCtrl+"."+rfAttr+"_"+rfType, rfJointList[j]+".rotateX", force=True)
                        else:
                            if j < (len(rfAttrList)-1):
                                cmds.connectAttr(self.footCtrl+"."+rfAttr+"_"+rfType, rfJointList[j]+".rotateZ", force=True)
                
                # creating the originedFrom attributes (in order to permit integrated parents in the future):
                utils.originedFrom(objName=self.footCtrl, attrString=self.base+";"+self.cvFootLoc+";"+self.cvRFALoc+";"+self.cvRFBLoc+";"+self.cvRFCLoc+";"+self.cvRFDLoc)
                utils.originedFrom(objName=self.middleFootCtrl, attrString=self.cvRFELoc+";"+self.cvEndJoint)
                
                # organizing keyable attributes:
                ctrls.setLockHide([self.middleFootCtrl], ['tx', 'ty', 'tz'])
                ctrls.setLockHide([self.middleFootCtrl, self.footCtrl], ['v'], l=False)
                
                # create a masterModuleGrp to be checked if this rig exists:
                self.toCtrlHookGrp     = cmds.group(self.footCtrlZeroList[0], name=side+self.userGuideName+"_control_grp")
                self.toScalableHookGrp = cmds.group(self.footJnt, name=side+self.userGuideName+"_joint_grp")
                self.toStaticHookGrp   = cmds.group(self.toCtrlHookGrp, self.toScalableHookGrp, name=side+self.userGuideName+"_grp")
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
                                                }
                                    }
