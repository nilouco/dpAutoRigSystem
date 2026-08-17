# importing libraries:
from maya import cmds
from ..base import standard

# global variables to this module:
CLASS_NAME = "FkLine"
TITLE = "m001_fkLine"
DESCRIPTION = "m002_fkLineDesc"
WIKI = "03-‐-Guides#-fk-line"



class FkLine(standard.BaseStandard):
    def __init__(self, ar):
        standard.BaseStandard.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.currentNJoints = 1
    
    
#    def create_module_layout(self):
#        standard.BaseStandard.create_module_layout(self)
    
    
    def create_guide(self, *args):
        self.create_guide_base()
        # Custom GUIDE:
        cmds.addAttr(self.guide_base, longName="nJoints", attributeType='long')
        cmds.setAttr(self.guide_base+".nJoints", 1)
        cmds.addAttr(self.guide_base, longName="flip", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="articulation", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="mainControls", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="nMain", minValue=1, defaultValue=1, attributeType='long')
        cmds.addAttr(self.guide_base, longName="deformedBy", minValue=0, defaultValue=0, maxValue=3, attributeType='long')
        cmds.addAttr(self.guide_base, longName="reorient", attributeType='bool')
        
        self.cvJointLoc = self.ar.ctrls.cvJointLoc(ctrlName=self.name_guide+"_JointLoc1", r=0.3, d=1, guide=True)
        self.jGuide1 = cmds.joint(name=self.name_guide+"_JGuide1", radius=0.001)
        cmds.setAttr(self.jGuide1+".template", 1)
        cmds.parent(self.jGuide1, self.guide_base, relative=True)
        
        self.cvEndJoint = self.ar.ctrls.cvLocator(ctrlName=self.name_guide+"_JointEnd", r=0.1, d=1, guide=True)
        cmds.parent(self.cvEndJoint, self.cvJointLoc)
        cmds.setAttr(self.cvEndJoint+".tz", 1.3)
        self.jGuideEnd = cmds.joint(name=self.name_guide+"_JGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        self.ar.ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
        
        cmds.parent(self.cvJointLoc, self.guide_base)
        cmds.parent(self.jGuideEnd, self.jGuide1)
        cmds.parentConstraint(self.cvJointLoc, self.jGuide1, maintainOffset=False, name=self.jGuide1+"_PaC")
        cmds.parentConstraint(self.cvEndJoint, self.jGuideEnd, maintainOffset=False, name=self.jGuideEnd+"_PaC")
        # include nodes into net
        self.add_node_to_guide_net([self.cvJointLoc, self.cvEndJoint], ["JointLoc1", "JointEnd"])


    def changeJointNumber(self, enteredNJoints, *args):
        """ Edit the number of joints in the guide.
        """
        self.ar.opt.check_use_default_render_layer()
        # get the number of joints entered by user:
        if enteredNJoints == 0:
            if self.ar.data.ui_state:
                self.enteredNJoints = cmds.intField("edit_guide_n_joints_if", query=True, value=True)
            else:
                return
        else:
            self.enteredNJoints = enteredNJoints
        # get the number of joints existing:
        self.currentNJoints = cmds.getAttr(self.guide_base+".nJoints")
        # start analisys the difference between values:
        if self.enteredNJoints != self.currentNJoints:
            # unparent temporarely the Ends:
            self.cvEndJoint = self.name_guide+"_JointEnd"
            cmds.parent(self.cvEndJoint, world=True)
            self.jGuideEnd = (self.name_guide+"_JGuideEnd")
            cmds.parent(self.jGuideEnd, world=True)
            # verify if the nJoints is greather or less than the current
            if self.enteredNJoints > self.currentNJoints:
                for n in range(self.currentNJoints+1, self.enteredNJoints+1):
                    # create another N cvJointLoc:
                    self.cvJointLoc = self.ar.ctrls.cvJointLoc(ctrlName=self.name_guide+"_JointLoc"+str(n), r=0.3, d=1, guide=True)
                    # set its nJoint value as n:
                    cmds.setAttr(self.cvJointLoc+".nJoint", n)
                    # parent it to the lastGuide:
                    cmds.parent(self.cvJointLoc, self.name_guide+"_JointLoc"+str(n-1), relative=True)
                    cmds.setAttr(self.cvJointLoc+".translateZ", 2)
                    # create a joint to use like an arrowLine:
                    self.jGuide = cmds.joint(name=self.name_guide+"_JGuide"+str(n), radius=0.001)
                    cmds.setAttr(self.jGuide+".template", 1)
                    #Prevent a intermidiate node to be added
                    cmds.parent(self.jGuide, self.name_guide+"_JGuide"+str(n-1), relative=True)
                    #Do not maintain offset and ensure cv will be at the same place than the joint
                    cmds.parentConstraint(self.cvJointLoc, self.jGuide, maintainOffset=False, name=self.jGuide+"_PaC")
                    cmds.scaleConstraint(self.cvJointLoc, self.jGuide, maintainOffset=False, name=self.jGuide+"_ScC")
                    self.add_node_to_guide_net([self.cvJointLoc], ["JointLoc"+str(n)])
            elif self.enteredNJoints < self.currentNJoints:
                # re-define cvEndJoint:
                self.cvJointLoc = self.name_guide+"_JointLoc"+str(self.enteredNJoints)
                self.cvEndJoint = self.name_guide+"_JointEnd"
                self.jGuide = self.name_guide+"_JGuide"+str(self.enteredNJoints)
                # re-parent the children guides:
                childrenGuideBellowList = self.ar.utils.getGuideChildrenList(self.cvJointLoc)
                if childrenGuideBellowList:
                    for childGuide in childrenGuideBellowList:
                        cmds.parent(childGuide, self.cvJointLoc)
                # delete difference of nJoints:
                cmds.delete(self.name_guide+"_JointLoc"+str(self.enteredNJoints+1))
                cmds.delete(self.name_guide+"_JGuide"+str(self.enteredNJoints+1))
                for j in range(self.enteredNJoints+1, self.currentNJoints+1):
                    self.remove_attr_from_guide_net(["JointLoc"+str(j)])
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

            cmds.setAttr(self.guide_base+".nJoints", self.enteredNJoints)
            self.currentNJoints = self.enteredNJoints
            self.change_main_ctrls_number(0)
            # re-build the preview mirror:
            self.create_mirror_preview()
        cmds.select(self.guide_base)


    def getJointLocList(self, guideBase, *args):
        """ Get the list of jointLocators from the guideBase.
        """
        if cmds.objExists(guideBase):
            children = cmds.listRelatives(guideBase, allDescendents=True, type="transform")
            upVectorObject = self.ar.utils.createLocatorInItemPosition(self.radiusGuide)  # using locator to avoid cycle error
            jointLocList = []
            for child in children:
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
                    posTempLoc = self.ar.utils.createLocatorInItemPosition(nJoint2)
                    # Aim guideBase and jointLoc to nJoint2
                    self.aimFunction(nJoint2, guideBase, upVectorObject)
                    # Parenting nJoint to world and reset jointLoc position
                    cmds.parent(nJoint2, world=True)
                    for axis in self.ar.data.axis:
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
        self.radiusGuide = self.name_guide + "_Base_RadiusCtrl"
        self.cvEndJoint = self.name_guide + "_JointEnd"
        # Check if the guideBase exists:
        if cmds.attributeQuery("guideBase", node=self.guide_base, exists=True):
            # Get the jointLocList and upVectorObject:
            self.jointLocList, self.upVectorObject = self.getJointLocList(self.guide_base)
            # Reorient the FK line:
            self.reOrientFkLine(self.jointLocList, self.upVectorObject, self.guide_base, self.cvEndJoint)


    def rig_me(self, *args):
        standard.BaseStandard.rig_me(self)
        # verify if the guide exists:
        if cmds.objExists(self.guide_base):
            # run for all sides
            for s, side in enumerate(self.sides):
                self.base = side+self.number_name+'_Guide_Base'
                self.ctrlZeroGrp = side+self.number_name+"_00_Ctrl_Zero_0_Grp"
                self.skinJointList = []
                self.fkCtrlList = []
                # get the number of joints to be created:
                self.nJoints = cmds.getAttr(self.base+".nJoints")
                for n in range(0, self.nJoints):
                    cmds.select(clear=True)
                    # declare guide:
                    self.guide = side+self.number_name+"_Guide_JointLoc"+str(n+1)
                    self.cvEndJoint = side+self.number_name+"_Guide_JointEnd"
                    self.radiusGuide = side+self.number_name+"_Guide_Base_RadiusCtrl"
                    # create a joint:
                    self.jnt = cmds.joint(name=side+self.number_name+"_%02d_Jnt"%(n), scaleCompensate=False)
                    cmds.addAttr(self.jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                    # joint labelling:
                    self.ar.utils.setJointLabel(self.jnt, s+self.joint_label_add, 18, self.number_name+"_%02d"%(n))
                    self.skinJointList.append(self.jnt)
                    # create a control:
                    self.jntCtrl = self.ar.ctrls.cvControl("id_007_FkLine", side+self.number_name+"_%02d_Ctrl"%(n), r=self.radius, d=self.curve_degree, headDef=cmds.getAttr(self.base+".deformedBy"), guideSource=self.name_guide+"_JointLoc"+str(n+1), parentTag=self.get_parent_to_tag(self.fkCtrlList))
                    self.fkCtrlList.append(self.jntCtrl)
                    # zeroOut controls:
                    self.zeroOutCtrlGrp = self.ar.utils.zeroOut([self.jntCtrl])[0]
                    # position and orientation of joint and control:
                    cmds.delete(cmds.parentConstraint(self.guide, self.jnt, maintainOffset=False))
                    cmds.delete(cmds.parentConstraint(self.guide, self.zeroOutCtrlGrp, maintainOffset=False))
                    # hide visibility attribute:
                    cmds.setAttr(self.jntCtrl+'.visibility', keyable=False)
                    # fixing flip mirror:
                    if s == 1:
                        if cmds.getAttr(self.guide_base+".flip") == 1:
                            cmds.setAttr(self.zeroOutCtrlGrp+".scaleX", -1)
                            cmds.setAttr(self.zeroOutCtrlGrp+".scaleY", -1)
                            cmds.setAttr(self.zeroOutCtrlGrp+".scaleZ", -1)
                    cmds.addAttr(self.jntCtrl, longName='scaleCompensate', attributeType="short", minValue=0, defaultValue=1, maxValue=1, keyable=False)
                    cmds.setAttr(self.jntCtrl+".scaleCompensate", channelBox=True)
                    cmds.connectAttr(self.jntCtrl+".scaleCompensate", self.jnt+".segmentScaleCompensate", force=True)
                    if n == 0:
                        self.ar.utils.originedFrom(objName=self.jntCtrl, attrString=self.base+";"+self.guide+";"+self.radiusGuide)
                        self.ctrlZeroGrp = self.zeroOutCtrlGrp
                    elif n == self.nJoints-1:
                        self.ar.utils.originedFrom(objName=self.jntCtrl, attrString=self.guide+";"+self.cvEndJoint)
                    else:
                        self.ar.utils.originedFrom(objName=self.jntCtrl, attrString=self.guide)
                    # grouping:
                    if n > 0:
                        # parent joints as a simple chain (line)
                        self.fatherJnt = side+self.number_name+"_%02d_Jnt"%(n-1)
                        cmds.parent(self.jnt, self.fatherJnt, absolute=True)
                        # parent zeroCtrl Group to the before jntCtrl:
                        self.fatherCtrl = side+self.number_name+"_%02d_Ctrl"%(n-1)
                        cmds.parent(self.zeroOutCtrlGrp, self.fatherCtrl, absolute=True)
                    # control drives joint:
                    cmds.parentConstraint(self.jntCtrl, self.jnt, maintainOffset=False, name=self.jnt+"_PaC")
                    cmds.scaleConstraint(self.jntCtrl, self.jnt, maintainOffset=True, name=self.jnt+"_ScC")
                    # add articulationJoint:
                    if n > 0:
                        if self.articulation:
                            artJntList = self.ar.utils.articulationJoint(self.fatherJnt, self.jnt) #could call to create corrective joints. See parameters to implement it, please.
                            self.ar.utils.setJointLabel(artJntList[0], s+self.joint_label_add, 18, self.number_name+"_%02d_Jar"%(n))
                    cmds.select(self.jnt)
                    # end chain:
                    if n == self.nJoints-1:
                        # create end joint:
                        self.endJoint = cmds.joint(name=side+self.number_name+"_"+self.ar.data.joint_end_attr, radius=0.5)
                        self.ar.utils.addJointEndAttr([self.endJoint])
                        cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.endJoint, maintainOffset=False))
                # work with main fk controllers
                if cmds.getAttr(self.base+".mainControls"):
                    self.add_fk_main_ctrls(side, self.fkCtrlList)
                # create a masterModuleGrp to be checked if this rig exists:
                self.create_hook_setup(side, [self.ctrlZeroGrp], [self.skinJointList[0]])
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.number_name+'_'+self.mirror_grp)
                self.ar.custom_attr.addAttr(0, [self.static_hook_grp], descendents=True) #dpID
            # finalize this rig:
            self.serialize_guide()
            self.composing_info()
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and module_instance namespace:
        self.delete_guide()
        self.rename_unit_conversion()
        self.ar.custom_attr.addAttr(0, self.to_ids) #dpID
    