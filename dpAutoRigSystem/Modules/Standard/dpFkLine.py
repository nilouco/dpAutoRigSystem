# importing libraries:
from maya import cmds
from ..Base import dpBaseStandard
from ..Base import dpBaseLayout

# global variables to this module:
CLASS_NAME = "FkLine"
TITLE = "m001_fkLine"
DESCRIPTION = "m002_fkLineDesc"
ICON = "/Icons/dp_fkLine.png"
WIKI = "03-‐-Guides#-finger"

DP_FKLINE_VERSION = 2.08


class FkLine(dpBaseStandard.BaseStandard, dpBaseLayout.BaseLayout):
    def __init__(self,  *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseStandard.BaseStandard.__init__(self, *args, **kwargs)
        self.currentNJoints = 1
    
    
    def createModuleLayout(self, *args):
        dpBaseStandard.BaseStandard.createModuleLayout(self)
        dpBaseLayout.BaseLayout.basicModuleLayout(self)
    
    
    def createGuide(self, *args):
        dpBaseStandard.BaseStandard.createGuide(self)
        # Custom GUIDE:
        cmds.addAttr(self.moduleGrp, longName="nJoints", attributeType='long')
        cmds.setAttr(self.moduleGrp+".nJoints", 1)
        cmds.addAttr(self.moduleGrp, longName="flip", attributeType='bool')
        cmds.addAttr(self.moduleGrp, longName="articulation", attributeType='bool')
        cmds.addAttr(self.moduleGrp, longName="mainControls", attributeType='bool')
        cmds.addAttr(self.moduleGrp, longName="nMain", minValue=1, defaultValue=1, attributeType='long')
        cmds.addAttr(self.moduleGrp, longName="deformedBy", minValue=0, defaultValue=0, maxValue=3, attributeType='long')
        
        self.cvJointLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_JointLoc1", r=0.3, d=1, guide=True)
        self.jGuide1 = cmds.joint(name=self.guideName+"_JGuide1", radius=0.001)
        cmds.setAttr(self.jGuide1+".template", 1)
        cmds.parent(self.jGuide1, self.moduleGrp, relative=True)
        
        self.cvEndJoint = self.ctrls.cvLocator(ctrlName=self.guideName+"_JointEnd", r=0.1, d=1, guide=True)
        cmds.parent(self.cvEndJoint, self.cvJointLoc)
        cmds.setAttr(self.cvEndJoint+".tz", 1.3)
        self.jGuideEnd = cmds.joint(name=self.guideName+"_JGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        self.ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
        
        cmds.parent(self.cvJointLoc, self.moduleGrp)
        cmds.parent(self.jGuideEnd, self.jGuide1)
        cmds.parentConstraint(self.cvJointLoc, self.jGuide1, maintainOffset=False, name=self.jGuide1+"_PaC")
        cmds.parentConstraint(self.cvEndJoint, self.jGuideEnd, maintainOffset=False, name=self.jGuideEnd+"_PaC")
        # include nodes into net
        self.addNodeToGuideNet([self.cvJointLoc, self.cvEndJoint], ["JointLoc1", "JointEnd"])


    def changeJointNumber(self, enteredNJoints, *args):
        """ Edit the number of joints in the guide.
        """
        self.utils.useDefaultRenderLayer()
        # get the number of joints entered by user:
        if enteredNJoints == 0:
            try:
                self.enteredNJoints = cmds.intField(self.nJointsIF, query=True, value=True)
            except:
                return
        else:
            self.enteredNJoints = enteredNJoints
        # get the number of joints existing:
        self.currentNJoints = cmds.getAttr(self.moduleGrp+".nJoints")
        # start analisys the difference between values:
        if self.enteredNJoints != self.currentNJoints:
            # unparent temporarely the Ends:
            self.cvEndJoint = self.guideName+"_JointEnd"
            cmds.parent(self.cvEndJoint, world=True)
            self.jGuideEnd = (self.guideName+"_JGuideEnd")
            cmds.parent(self.jGuideEnd, world=True)
            # verify if the nJoints is greather or less than the current
            if self.enteredNJoints > self.currentNJoints:
                for n in range(self.currentNJoints+1, self.enteredNJoints+1):
                    # create another N cvJointLoc:
                    self.cvJointLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_JointLoc"+str(n), r=0.3, d=1, guide=True)
                    # set its nJoint value as n:
                    cmds.setAttr(self.cvJointLoc+".nJoint", n)
                    # parent it to the lastGuide:
                    cmds.parent(self.cvJointLoc, self.guideName+"_JointLoc"+str(n-1), relative=True)
                    cmds.setAttr(self.cvJointLoc+".translateZ", 2)
                    # create a joint to use like an arrowLine:
                    self.jGuide = cmds.joint(name=self.guideName+"_JGuide"+str(n), radius=0.001)
                    cmds.setAttr(self.jGuide+".template", 1)
                    #Prevent a intermidiate node to be added
                    cmds.parent(self.jGuide, self.guideName+"_JGuide"+str(n-1), relative=True)
                    #Do not maintain offset and ensure cv will be at the same place than the joint
                    cmds.parentConstraint(self.cvJointLoc, self.jGuide, maintainOffset=False, name=self.jGuide+"_PaC")
                    cmds.scaleConstraint(self.cvJointLoc, self.jGuide, maintainOffset=False, name=self.jGuide+"_ScC")
                    self.addNodeToGuideNet([self.cvJointLoc], ["JointLoc"+str(n)])
            elif self.enteredNJoints < self.currentNJoints:
                # re-define cvEndJoint:
                self.cvJointLoc = self.guideName+"_JointLoc"+str(self.enteredNJoints)
                self.cvEndJoint = self.guideName+"_JointEnd"
                self.jGuide = self.guideName+"_JGuide"+str(self.enteredNJoints)
                # re-parent the children guides:
                childrenGuideBellowList = self.utils.getGuideChildrenList(self.cvJointLoc)
                if childrenGuideBellowList:
                    for childGuide in childrenGuideBellowList:
                        cmds.parent(childGuide, self.cvJointLoc)
                # delete difference of nJoints:
                cmds.delete(self.guideName+"_JointLoc"+str(self.enteredNJoints+1))
                cmds.delete(self.guideName+"_JGuide"+str(self.enteredNJoints+1))
                for j in range(self.enteredNJoints+1, self.currentNJoints+1):
                    self.removeAttrFromGuideNet(["JointLoc"+str(j)])
            # re-parent cvEndJoint:
            pTempParent = cmds.listRelatives(self.cvEndJoint, p=True)
            cmds.parent(self.cvEndJoint, self.cvJointLoc)

            #Ensure to remove temp parent from the unparenting done on the end joint
            if pTempParent:
                cmds.delete(pTempParent)
            cmds.setAttr(self.cvEndJoint+".tz", 1.3)
            pTempParent = cmds.listRelatives(self.jGuideEnd, p=True)
            cmds.parent(self.jGuideEnd, self.jGuide, relative=True)
            if pTempParent:
                cmds.delete(pTempParent)

            cmds.setAttr(self.moduleGrp+".nJoints", self.enteredNJoints)
            self.currentNJoints = self.enteredNJoints
            self.changeMainCtrlsNumber(0)
            # re-build the preview mirror:
            dpBaseLayout.BaseLayout.createPreviewMirror(self)
        cmds.select(self.moduleGrp)


    def getJointLocList(self, guideBase, *args):
        """ Get the list of jointLocators from the guideBase.
        """
        if cmds.objExists(guideBase):
            childrenList = cmds.listRelatives(guideBase, allDescendents=True, type="transform")
            upVectorObject = self.utils.createLocatorInItemPosition(self.radiusGuide)  # using locator to avoid cycle error
            jointLocList = []
            for child in childrenList:
                # Check if the child is a joint locator, with nJoint attribute
                if cmds.attributeQuery("nJoint", node=child, exists=True):
                    jointLocList.append(child)
            return jointLocList, upVectorObject


    def aimFunction(self, target, aimed, upObject, *args):
        """ Aim the target towards the aimed object using the upObject(RadiusCtrl) for orientation.
        """ 
        # If it's JointEnd, unlock translateX and translateY attributes to allow unparenting to world with no translation issues.
        # The JointEnd will be unlocked after pressing the reOrient button only.
        if target == self.cvEndJoint:
            cmds.setAttr(target + ".translateX", lock=False, keyable=True)
            cmds.setAttr(target + ".translateY", lock=False, keyable=True)
        fatherJointLoc = cmds.listRelatives(target, parent=True, type="transform")[0]
        cmds.parent(target, world=True)
        # Aim Constraint without maintain offset
        cmds.delete(cmds.aimConstraint(target, aimed, aimVector=(0, 0, 1), upVector=(0, 1, 0), worldUpType="objectrotation", worldUpVector=(0, 1, 0), worldUpObject=upObject, maintainOffset=False))
        # Get back to the original parent
        cmds.parent(target, fatherJointLoc)


    def reOrientFkLine(self, jointLocList, upVectorObject, guideBase, *args):
        """ Reorient the FK line based on the jointLocList and upVectorObject.
        """ 
        if jointLocList:
            for jointLoc in jointLocList:
                # jointLocPos = createLocatorInPosition(jointLoc)
                backGuide = cmds.listRelatives(jointLoc, parent=True)[0]
                # Check if the backGuide is not the guideBase
                if not backGuide == guideBase:
                    self.aimFunction(jointLoc, backGuide, upVectorObject)
                # If the backGuide is the guideBase, align the jointLoc1 to the guideBase
                if backGuide == guideBase:
                    nJoint2 = cmds.listRelatives(jointLoc, children=True, type="transform")[0]
                    posTempLoc = self.utils.createLocatorInItemPosition(nJoint2)
                    # Aim guideBase and jointLoc to nJoint2
                    self.aimFunction(nJoint2, guideBase, upVectorObject)
                    # Parenting nJoint to world and reset jointLoc position
                    cmds.parent(nJoint2, world=True)
                    for axis in ["X", "Y", "Z"]:
                        cmds.setAttr(jointLoc + ".translate" + axis, 0)
                        cmds.setAttr(jointLoc + ".rotate" + axis, 0)
                    cmds.parent(nJoint2, jointLoc)
                    # Delete the temporary locators
                    cmds.delete(upVectorObject)
                    cmds.delete(posTempLoc)
                cmds.select(guideBase)


    def reOrientGuideButton(self, *args):
        """ reOrient dpFkLine button. 
            Each guide will point to the next guide using Radius_Ctrl position as a Object Rotation Up Vector.
        """
        # re-declaring guides names:
        self.guideBase = self.moduleGrp
        self.radiusGuide = self.guideName + "_Base_RadiusCtrl"
        self.cvEndJoint = self.guideName + "_JointEnd"
        # Check if the guideBase exists:
        if cmds.attributeQuery("guideBase", node=self.guideBase, exists=True):
            # Get the jointLocList and upVectorObject:
            self.jointLocList, self.upVectorObject = self.getJointLocList(self.guideBase)
            # Reorient the FK line:
            self.reOrientFkLine(self.jointLocList, self.upVectorObject, self.guideBase, self.cvEndJoint)


    def reCreateEditSelectedModuleLayout(self, bSelect=False, *args):
        dpBaseLayout.BaseLayout.reCreateEditSelectedModuleLayout(self, bSelect)
        # Create the reOrien button in the flip layout:
        self.reOrientBT = cmds.button(label=self.dpUIinst.lang["m022_reOrient"], annotation=self.dpUIinst.lang["m023_reOrientDesc"], command=self.reOrientGuideButton, parent=self.flipLayout)


    def rigModule(self, *args):
        dpBaseStandard.BaseStandard.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            # articulation joint:
            self.addArticJoint = self.getArticulation()
            # run for all sides
            for s, side in enumerate(self.sideList):
                self.base = side+self.userGuideName+'_Guide_Base'
                self.ctrlZeroGrp = side+self.userGuideName+"_00_Ctrl_Zero_0_Grp"
                self.skinJointList = []
                self.fkCtrlList = []
                # get the number of joints to be created:
                self.nJoints = cmds.getAttr(self.base+".nJoints")
                for n in range(0, self.nJoints):
                    cmds.select(clear=True)
                    # declare guide:
                    self.guide = side+self.userGuideName+"_Guide_JointLoc"+str(n+1)
                    self.cvEndJoint = side+self.userGuideName+"_Guide_JointEnd"
                    self.radiusGuide = side+self.userGuideName+"_Guide_Base_RadiusCtrl"
                    # create a joint:
                    self.jnt = cmds.joint(name=side+self.userGuideName+"_%02d_Jnt"%(n), scaleCompensate=False)
                    cmds.addAttr(self.jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                    # joint labelling:
                    self.utils.setJointLabel(self.jnt, s+self.jointLabelAdd, 18, self.userGuideName+"_%02d"%(n))
                    self.skinJointList.append(self.jnt)
                    # create a control:
                    self.jntCtrl = self.ctrls.cvControl("id_007_FkLine", side+self.userGuideName+"_%02d_Ctrl"%(n), r=self.ctrlRadius, d=self.curveDegree, headDef=cmds.getAttr(self.base+".deformedBy"), guideSource=self.guideName+"_JointLoc"+str(n+1), parentTag=self.getParentToTag(self.fkCtrlList))
                    self.fkCtrlList.append(self.jntCtrl)
                    # zeroOut controls:
                    self.zeroOutCtrlGrp = self.utils.zeroOut([self.jntCtrl])[0]
                    # position and orientation of joint and control:
                    cmds.delete(cmds.parentConstraint(self.guide, self.jnt, maintainOffset=False))
                    cmds.delete(cmds.parentConstraint(self.guide, self.zeroOutCtrlGrp, maintainOffset=False))
                    # hide visibility attribute:
                    cmds.setAttr(self.jntCtrl+'.visibility', keyable=False)
                    # fixing flip mirror:
                    if s == 1:
                        if cmds.getAttr(self.moduleGrp+".flip") == 1:
                            cmds.setAttr(self.zeroOutCtrlGrp+".scaleX", -1)
                            cmds.setAttr(self.zeroOutCtrlGrp+".scaleY", -1)
                            cmds.setAttr(self.zeroOutCtrlGrp+".scaleZ", -1)
                    cmds.addAttr(self.jntCtrl, longName='scaleCompensate', attributeType="short", minValue=0, defaultValue=1, maxValue=1, keyable=False)
                    cmds.setAttr(self.jntCtrl+".scaleCompensate", channelBox=True)
                    cmds.connectAttr(self.jntCtrl+".scaleCompensate", self.jnt+".segmentScaleCompensate", force=True)
                    if n == 0:
                        self.utils.originedFrom(objName=self.jntCtrl, attrString=self.base+";"+self.guide+";"+self.radiusGuide)
                        self.ctrlZeroGrp = self.zeroOutCtrlGrp
                    elif n == self.nJoints-1:
                        self.utils.originedFrom(objName=self.jntCtrl, attrString=self.guide+";"+self.cvEndJoint)
                    else:
                        self.utils.originedFrom(objName=self.jntCtrl, attrString=self.guide)
                    # grouping:
                    if n > 0:
                        # parent joints as a simple chain (line)
                        self.fatherJnt = side+self.userGuideName+"_%02d_Jnt"%(n-1)
                        cmds.parent(self.jnt, self.fatherJnt, absolute=True)
                        # parent zeroCtrl Group to the before jntCtrl:
                        self.fatherCtrl = side+self.userGuideName+"_%02d_Ctrl"%(n-1)
                        cmds.parent(self.zeroOutCtrlGrp, self.fatherCtrl, absolute=True)
                    # control drives joint:
                    cmds.parentConstraint(self.jntCtrl, self.jnt, maintainOffset=False, name=self.jnt+"_PaC")
                    cmds.scaleConstraint(self.jntCtrl, self.jnt, maintainOffset=True, name=self.jnt+"_ScC")
                    # add articulationJoint:
                    if n > 0:
                        if self.addArticJoint:
                            artJntList = self.utils.articulationJoint(self.fatherJnt, self.jnt) #could call to create corrective joints. See parameters to implement it, please.
                            self.utils.setJointLabel(artJntList[0], s+self.jointLabelAdd, 18, self.userGuideName+"_%02d_Jar"%(n))
                    cmds.select(self.jnt)
                    # end chain:
                    if n == self.nJoints-1:
                        # create end joint:
                        self.endJoint = cmds.joint(name=side+self.userGuideName+"_"+self.dpUIinst.jointEndAttr, radius=0.5)
                        self.utils.addJointEndAttr([self.endJoint])
                        cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.endJoint, maintainOffset=False))
                # work with main fk controllers
                if cmds.getAttr(self.base+".mainControls"):
                    self.addFkMainCtrls(side, self.fkCtrlList)
                # create a masterModuleGrp to be checked if this rig exists:
                self.hookSetup(side, [self.ctrlZeroGrp], [self.skinJointList[0]])
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.userGuideName+'_'+self.mirrorGrp)
                self.dpUIinst.customAttr.addAttr(0, [self.toStaticHookGrp], descendents=True) #dpID
            # finalize this rig:
            self.serializeGuide()
            self.integratingInfo()
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and moduleInstance namespace:
        self.deleteModule()
        self.renameUnitConversion()
        self.dpUIinst.customAttr.addAttr(0, self.toIDList) #dpID
    