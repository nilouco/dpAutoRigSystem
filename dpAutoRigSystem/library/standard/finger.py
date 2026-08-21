# importing libraries:
from maya import cmds
from ..base import standard

# global variables to this module:
CLASS_NAME = "Finger"
TITLE = "m007_finger"
DESCRIPTION = "m008_fingerDesc"
WIKI = "03-‐-Guides#-finger"



class Finger(standard.BaseStandard):
    def __init__(self, ar):
        standard.BaseStandard.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.correctiveCtrlGrpList = []


    def create_guide(self):
        self.create_guide_base()
        self.create_guide_custom_attr()
        self.create_guide_elements()
        self.change_joint_number(3)
        self.set_guide_base_initial_position()
        self.add_node_to_guide_net([self.cvBaseJoint, self.cvJointLoc1, self.guide_loc, self.guide_end_loc], 
                                   ["JointLoc0", "JointLoc1", "JointLoc2", "JointEnd"])


    def create_guide_custom_attr(self):
        """ Add guide_base attributes and set them.
        """
        cmds.addAttr(self.guide_base, longName="nJoints", attributeType='long', minValue=2, defaultValue=2)
        cmds.addAttr(self.guide_base, longName="articulation", defaultValue=1, attributeType='bool')
        cmds.addAttr(self.guide_base, longName="corrective", attributeType='bool')


    def create_guide_elements(self):
        """ Creates the controller locators of the standard module guide.
        """
        # locators
        self.cvBaseJoint = self.ar.ctrls.cvLocator(ctrlName=self.name_guide+"_JointLoc0", r=0.2, d=1, guide=True)
        self.cvJointLoc1 = self.ar.ctrls.cvJointLoc(ctrlName=self.name_guide+"_JointLoc1", r=0.3, d=1, guide=True)
        self.guide_loc = self.ar.ctrls.cvJointLoc(ctrlName=self.name_guide+"_JointLoc2", r=0.25, d=1, guide=True)
        self.guide_end_loc = self.ar.ctrls.cvLocator(ctrlName=self.name_guide+"_JointEnd", r=0.2, d=1, guide=True)
        # joints
        self.line1 = cmds.joint(name=self.name_guide+"_JGuide1", radius=0.001)
        self.jGuide0 = cmds.joint(name=self.name_guide+"_JGuide0", radius=0.001)
        self.line = cmds.joint(name=self.name_guide+"_JGuide2", radius=0.001)
        self.line_end = cmds.joint(name=self.name_guide+"_JGuideEnd", radius=0.001)
        # setup
        self.ar.utils.set_template([self.jGuide0, self.line, self.line, self.line_end])
        cmds.setAttr(self.cvBaseJoint+".translateZ", -1)
        cmds.setAttr(self.cvBaseJoint+".rotateZ", lock=True)
        cmds.setAttr(self.guide_loc+".translateZ", 1)
        cmds.setAttr(self.guide_loc+".translateX", -0.01)
        cmds.setAttr(self.guide_loc+".rotateY", -1)
        cmds.setAttr(self.guide_end_loc+".translateZ", 1.3)
        # parenting
        cmds.parent(self.line1, self.cvBaseJoint, self.cvJointLoc1, self.guide_base, relative=True)
        cmds.parent(self.guide_loc, self.cvJointLoc1, relative=True)
        cmds.parent(self.line, self.line_end, self.line1)
        cmds.parent(self.guide_end_loc, self.guide_loc)
        # edit
        cmds.transformLimits(self.guide_end_loc, tz=(0.01, 1), etz=(True, False))
        cmds.parentConstraint(self.cvBaseJoint, self.jGuide0, maintainOffset=False, name=self.jGuide0+"_PaC")
        self.ar.ctrls.directConnect(self.guide_loc, self.line, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.directConnect(self.cvJointLoc1, self.line, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.directConnect(self.guide_end_loc, self.line_end, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.setLockHide([self.guide_end_loc], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])


    def set_guide_base_initial_position(self):
        cmds.setAttr(self.guide_base+".rotateX", 90)
        cmds.setAttr(self.guide_base+".rotateZ", 90)


        

    def change_joint_number(self, inputted, *args):
        """ Edit the number of joints in the guide.
        """
        joint_number = self.parse_inputted_joint_number(inputted)
        if joint_number and joint_number >= 2:
            self.ar.opt.check_use_default_render_layer()
            self.current_joint_number = cmds.getAttr(self.guide_base+".nJoints")
            if joint_number != self.current_joint_number:
                self.guide_end_loc = self.name_guide+"_JointEnd"
                self.line_end = self.name_guide+"_JGuideEnd"
                cmds.parent(self.guide_end_loc, self.line_end, world=True)
                if joint_number > self.current_joint_number:
                    for n in range(self.current_joint_number+1, joint_number+1):
                        self.guide_loc = self.ar.ctrls.cvJointLoc(ctrlName=self.name_guide+"_JointLoc"+str(n), r=0.2, d=1, guide=True)
                        self.increment_joint_number(n)
                        cmds.setAttr(self.guide_loc+".translateZ", 1)
                        cmds.setAttr(self.guide_loc+".rotateY", -1)
                        self.ar.ctrls.directConnect(self.guide_loc, self.line, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
                        self.add_node_to_guide_net([self.guide_loc], ["JointLoc"+str(n)])
                elif joint_number < self.current_joint_number:
                    self.line = self.name_guide+"_JGuide"+str(joint_number)
                    self.guide_loc = self.reduce_joint_number(joint_number)
                cmds.parent(self.guide_end_loc, self.guide_loc)
                cmds.setAttr(self.guide_end_loc+".tz", 1.3)
                cmds.parent(self.line_end, self.line)
                cmds.setAttr(self.guide_base+".nJoints", joint_number)
                self.current_joint_number = joint_number
                self.create_mirror_preview()
            cmds.select(self.guide_base)
        else:
            self.change_joint_number(2)


    def getCalibratePresetList(self, s, *args):
        """ Returns the calibration preset and invert lists for finger joints.
        """
        invertList = None
        presetList = [{}, {"calibrateTX":1}]
        if s == 1:
           invertList = [[], ["invertTX"]]
        return presetList, invertList


    def rig_me(self, *args):
        standard.BaseStandard.rig_me(self)
        # verify if the guide exists:
        if cmds.objExists(self.guide_base):
            # declaring lists to send information for integration:
            self.scalableGrpList, self.ikCtrlZeroList = [], []
            # run for all sides
            for s, side in enumerate(self.sides):
                skin_joints, self.controllers = [], []
                self.base = side+self.number_name+'_Guide_Base'
                if self.articulation:
                    if self.corrective:
                        # corrective controls group
                        self.corrective_ctrls_grp = cmds.group(name=side+self.number_name+"_Corrective_Grp", empty=True)
                        self.correctiveCtrlGrpList.append(self.corrective_ctrls_grp)
                        phalangeCalibratePresetList, invertList = self.getCalibratePresetList(s)
                # get the number of joints to be created:
                self.n_joints = cmds.getAttr(self.base+".nJoints")
                for n in range(0, self.n_joints+1):
                    cmds.select(clear=True)
                    # declare guide:
                    self.guide = side+self.number_name+"_Guide_JointLoc"+str(n)
                    self.guide_end_loc = side+self.number_name+"_Guide_JointEnd"
                    self.guide_radius = side+self.number_name+"_Guide_Base_RadiusCtrl"
                    # create a joint:
                    self.jnt = cmds.joint(name=side+self.number_name+"_%02d_Jnt"%(n), scaleCompensate=False)
                    skin_joints.append(self.jnt)
                    cmds.addAttr(self.jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                    self.ar.utils.setJointLabel(self.jnt, s+self.joint_label_add, 18, self.number_name+"_%02d"%(n))
                    # create a control:
                    if n == 1:
                        self.fingerCtrl = self.ar.ctrls.cvControl("id_015_FingerMain", ctrlName=side+self.number_name+"_%02d_Ctrl"%(n), r=(self.radius * 2.0), d=self.curve_degree, rot=(0, 0, -90), guideSource=self.name_guide+"_JointLoc"+str(n), parentTag=self.controllers[0])
                        cmds.setAttr(self.fingerCtrl+".rotateOrder", 1)
                        self.ar.utils.originedFrom(objName=self.fingerCtrl, attrString=self.base+";"+self.guide)   
                        # edit the mirror shape to a good direction of controls:
                        if s == 1:
                            if self.mirror_axis == 'X':
                                cmds.setAttr(self.fingerCtrl+'.rotateZ', 180)
                            elif self.mirror_axis == 'Y':
                                cmds.setAttr(self.fingerCtrl+'.rotateY', 180)
                            elif self.mirror_axis == 'Z':
                                cmds.setAttr(self.fingerCtrl+'.rotateZ', 180)
                            elif self.mirror_axis == 'XY':
                                cmds.setAttr(self.fingerCtrl+'.rotateX', 180)
                            elif self.mirror_axis == 'XYZ':
                                cmds.setAttr(self.fingerCtrl+'.rotateZ', 180)
                            cmds.makeIdentity(self.fingerCtrl, apply=True, translate=False, rotate=True, scale=False)
                        # scale compensate attribute:
                        if not cmds.objExists(self.fingerCtrl+'.ikFkBlend'):
                            cmds.addAttr(self.fingerCtrl, longName="ikFkBlend", attributeType='float', keyable=True, minValue=0.0, maxValue=1.0, defaultValue=1.0)
                            self.ikFkRevNode = cmds.createNode("reverse", name=side+self.number_name+"_ikFk_Rev")
                            self.to_ids.append(self.ikFkRevNode)
                            cmds.connectAttr(self.fingerCtrl+".ikFkBlend", self.ikFkRevNode+".inputX", force=True)
                        if not cmds.objExists(self.fingerCtrl+'.scaleCompensate'):
                            cmds.addAttr(self.fingerCtrl, longName="scaleCompensate", attributeType='short', minValue=0, defaultValue=1, maxValue=1, keyable=False)
                            cmds.setAttr(self.fingerCtrl+".scaleCompensate", channelBox=True)
                            scaleCompensateMD = cmds.createNode("multiplyDivide", name=side+self.number_name+"_%02d_ScaleCompensate_MD"%(n))
                            self.scaleCompensateCond = cmds.createNode("condition", name=side+self.number_name+"_%02d_ScaleCompensate_Cnd"%(n))
                            self.to_ids.extend([scaleCompensateMD, self.scaleCompensateCond])
                            cmds.connectAttr(self.fingerCtrl+".scaleCompensate", scaleCompensateMD+".input1X", force=True)
                            cmds.connectAttr(self.ikFkRevNode+".outputX", scaleCompensateMD+".input2X", force=True)
                            cmds.connectAttr(scaleCompensateMD+".outputX", self.scaleCompensateCond+".firstTerm", force=True)
                            cmds.setAttr(self.scaleCompensateCond+".secondTerm", 1)
                            cmds.setAttr(self.scaleCompensateCond+".colorIfFalseR", 0)
                            cmds.connectAttr(self.fingerCtrl+".scaleCompensate", self.scaleCompensateCond+".colorIfTrueR", force=True)
                            cmds.connectAttr(self.scaleCompensateCond+".outColorR", self.jnt+".segmentScaleCompensate", force=True)
                            cmds.connectAttr(self.scaleCompensateCond+".outColorR", skin_joints[0]+".segmentScaleCompensate", force=True)
                    else:
                        self.fingerCtrl = self.ar.ctrls.cvControl("id_016_FingerFk", ctrlName=side+self.number_name+"_%02d_Ctrl"%(n), r=self.radius, d=self.curve_degree, guideSource=self.name_guide+"_JointLoc"+str(n), parentTag=self.get_parent_to_tag(self.controllers))
                        cmds.setAttr(self.fingerCtrl+".rotateOrder", 1)
                        if n == self.n_joints:
                            self.ar.utils.originedFrom(objName=self.fingerCtrl, attrString=self.guide+";"+self.guide_end_loc+";"+self.guide_radius)
                        else:
                            self.ar.utils.originedFrom(objName=self.fingerCtrl, attrString=self.guide)
                        if n == 0:
                            if self.n_joints == 2:
                                # problably we are creating the first control to a thumb
                                cmds.scale(2, 2, 2, self.fingerCtrl, relative=True)
                                cmds.makeIdentity(self.fingerCtrl, apply=True)
                            else:
                                # problably we are creating other base controls
                                cmds.scale(2, 0.5, 1, self.fingerCtrl, relative=True)
                                cmds.makeIdentity(self.fingerCtrl, apply=True)
                    self.controllers.append(self.fingerCtrl)

                    # scaleCompensate attribute:
                    if n > 1:
                        cmds.connectAttr(self.scaleCompensateCond+".outColorR", self.jnt+".segmentScaleCompensate", force=True)

                    # hide visibility attribute:
                    cmds.setAttr(self.fingerCtrl+'.visibility', keyable=False)
                    # put another group over the control in order to use this to connect values from mainFingerCtrl:
                    self.poseGrp = cmds.group(self.fingerCtrl, name=side+self.number_name+"_%02d_Pose_Grp"%(n))
                    self.sdkGrp = cmds.group(self.poseGrp, name=side+self.number_name+"_%02d_SDK_Grp"%(n))
                    self.ar.utils.addCustomAttr([self.poseGrp, self.sdkGrp], self.ar.utils.ignoreTransformIOAttr)
                    if n == 1:
                        # change pivot of those groups to control pivot:
                        pivotPos = cmds.xform(self.fingerCtrl, query=True, worldSpace=True, rotatePivot=True)
                        for grp in [self.poseGrp, self.sdkGrp]:
                            cmds.setAttr(grp+'.rotatePivotX', pivotPos[0])
                            cmds.setAttr(grp+'.rotatePivotY', pivotPos[1])
                            cmds.setAttr(grp+'.rotatePivotZ', pivotPos[2])
                    # position and orientation of joint and control:
                    tempDel = cmds.parentConstraint(self.guide, self.jnt, maintainOffset=False)
                    cmds.delete(tempDel)
                    tempDel = cmds.parentConstraint(self.guide, self.sdkGrp, maintainOffset=False)
                    cmds.delete(tempDel)
                    # zeroOut controls:
                    self.zeroGrp = self.ar.utils.zeroOut([self.sdkGrp])
                    
                    # grouping:
                    if n > 0:
                        if n == 1:
                            if not cmds.objExists(self.fingerCtrl+'.'+self.ar.data.lang['c021_showControls']):
                                cmds.addAttr(self.fingerCtrl, longName=self.ar.data.lang['c021_showControls'], attributeType='float', keyable=True, minValue=0.0, maxValue=1.0, defaultValue=1.0)
                                self.ctrlShape0 = cmds.listRelatives(side+self.number_name+"_00_Ctrl", children=True, type='nurbsCurve')[0]
                                cmds.connectAttr(self.fingerCtrl+"."+self.ar.data.lang['c021_showControls'], self.ctrlShape0+".visibility", force=True)
                                cmds.setAttr(self.fingerCtrl+'.'+self.ar.data.lang['c021_showControls'], keyable=False, channelBox=True)
                            for j in range(1, self.n_joints+1):
                                cmds.addAttr(self.fingerCtrl, longName=self.ar.data.lang['c022_phalange']+str(j), attributeType='float', keyable=True)
                        # parent joints as a simple chain (line)
                        father_joint = side+self.number_name+"_%02d_Jnt"%(n-1)
                        cmds.parent(self.jnt, father_joint, absolute=True)
                        # parent zeroGrp Group to the before ctrl:
                        cmds.parent(self.zeroGrp, side+self.number_name+"_%02d_Ctrl"%(n-1), absolute=True)
                    # freeze joints rotation
                    cmds.makeIdentity(self.jnt, apply=True)
                    # create parent and scale constraints from ctrl to jnt:
                    cmds.delete(cmds.parentConstraint(self.fingerCtrl, self.jnt, maintainOffset=False, name=self.jnt+"_PaC"))
                    
                    # add articulationJoint:
                    if n > 0:
                        if self.articulation:
                            if self.corrective:
                                correctiveNetList = [None]
                                correctiveNetList.append(self.setup_corrective_net(side+self.number_name+"_01_Ctrl", skin_joints[n-1], skin_joints[n], side+self.number_name+"_"+str(n)+"_PitchDown", 1, 1, -90))
                                articJntList = self.ar.utils.articulationJoint(father_joint, self.jnt, 1, [(0.3*self.radius, 0, 0)])
                                self.setup_corrective_controllers(articJntList, s, self.number_name+"_"+str(n), correctiveNetList, phalangeCalibratePresetList, invertList)
                                if s == 1:
                                    cmds.setAttr(articJntList[0]+".scaleX", -1)
                                    cmds.setAttr(articJntList[0]+".scaleY", -1)
                                    cmds.setAttr(articJntList[0]+".scaleZ", -1)
                            else:
                                articJntList = self.ar.utils.articulationJoint(father_joint, self.jnt)
                                cmds.connectAttr(self.scaleCompensateCond+".outColorR", articJntList[0]+".segmentScaleCompensate", force=True)
                            self.ar.utils.setJointLabel(articJntList[0], s+self.joint_label_add, 18, self.number_name+"_%02d_Jar"%(n))
                    cmds.select(self.jnt)
                    
                    if n == self.n_joints:
                        self.create_end_joint(side)
                
                # make first phalange be leads from base finger control:
                cmds.parentConstraint(side+self.number_name+"_00_Ctrl", side+self.number_name+"_01_SDK_Zero_0_Grp", maintainOffset=True, name=side+self.number_name+"_01_SDK_Zero_0_Grp"+"_PaC")
                cmds.scaleConstraint(side+self.number_name+"_00_Ctrl", side+self.number_name+"_01_SDK_Zero_0_Grp", maintainOffset=True, name=side+self.number_name+"_01_SDK_Zero_0_Grp"+"_ScC")
                if self.n_joints != 2:
                    cmds.parentConstraint(side+self.number_name+"_00_Ctrl", side+self.number_name+"_00_Jnt", maintainOffset=True, name=side+self.number_name+"_PaC")
                    cmds.scaleConstraint(side+self.number_name+"_00_Ctrl", side+self.number_name+"_00_Jnt", maintainOffset=True, name=side+self.number_name+"_ScC")
                # connecting the attributes from control 1 to phalanges rotate:
                for n in range(1, self.n_joints+1):
                    self.fingerCtrl = side+self.number_name+"_01_Ctrl"
                    self.sdkGrp = side+self.number_name+"_%02d_SDK_Grp"%(n)
                    cmds.connectAttr(self.fingerCtrl+"."+self.ar.data.lang['c022_phalange']+str(n), self.sdkGrp+".rotateY", force=True)
                    if n > 1:
                        self.ctrlShape = cmds.listRelatives(side+self.number_name+"_%02d_Ctrl"%(n), children=True, type='nurbsCurve')[0]
                        cmds.connectAttr(self.fingerCtrl+"."+self.ar.data.lang['c021_showControls'], self.ctrlShape+".visibility", force=True)

                # ik and Fk setup
                if self.n_joints == 2:
                    dupIk = cmds.duplicate(skin_joints[0])[0]
                    dupFk = cmds.duplicate(skin_joints[0])[0]
                else:
                    dupIk = cmds.duplicate(skin_joints[1])[0]
                    dupFk = cmds.duplicate(skin_joints[1])[0]
                
                # hide ik and fk joints in order to be Rigger friendly while skinning
                cmds.setAttr(dupIk+".visibility", 0)
                cmds.setAttr(dupFk+".visibility", 0)
                
                # ik setup
                childrenIkList = cmds.listRelatives(dupIk, children=True, allDescendents=True, fullPath=True)
                if childrenIkList:
                    for child in childrenIkList:
                        if not cmds.objectType(child) == "joint":
                            cmds.delete(child)
                        if child.endswith("_Jax"):
                            cmds.delete(child)
                jointIkList = cmds.listRelatives(dupIk, children=True, allDescendents=True, fullPath=True)
                for jointNode in jointIkList:
                    if "_Jnt" in jointNode[jointNode.rfind("|"):]:
                        # set joint preferred angle
                        currentRY = cmds.getAttr(jointNode+".rotateY")
                        cmds.setAttr(jointNode+".rotateY", -90)
                        cmds.joint(jointNode, edit=True, setPreferredAngles=True)
                        cmds.setAttr(jointNode+".rotateY", currentRY)
                        cmds.rename(jointNode, jointNode[jointNode.rfind("|")+1:].replace("_Jnt", "_Ik_Jxt"))
                    elif "_"+self.ar.data.joint_end_attr in jointNode[jointNode.rfind("|"):]:
                        cmds.rename(jointNode, jointNode[jointNode.rfind("|")+1:].replace("_"+self.ar.data.joint_end_attr, "_Ik_"+self.ar.data.joint_end_attr))
                ikBaseJoint = cmds.rename(dupIk, dupIk.replace("_Jnt1", "_Ik_Jxt"))
                ik_joints = cmds.listRelatives(ikBaseJoint, children=True, allDescendents=True)
                ik_joints.append(ikBaseJoint)

                # Fk setup
                childrenFkList = cmds.listRelatives(dupFk, children=True, allDescendents=True, fullPath=True)
                if childrenFkList:
                    for child in childrenFkList:
                        if not cmds.objectType(child) == "joint":
                            cmds.delete(child)
                        if child.endswith("_Jax"):
                            cmds.delete(child)
                jointFkList = cmds.listRelatives(dupFk, children=True, allDescendents=True, fullPath=True)
                for jointNode in jointFkList:
                    if "_Jnt" in jointNode[jointNode.rfind("|"):]:
                        cmds.rename(jointNode, jointNode[jointNode.rfind("|")+1:].replace("_Jnt", "_Fk_Jxt"))
                    elif "_"+self.ar.data.joint_end_attr in jointNode[jointNode.rfind("|"):]:
                        cmds.rename(jointNode, jointNode[jointNode.rfind("|")+1:].replace("_"+self.ar.data.joint_end_attr, "_Fk_"+self.ar.data.joint_end_attr))
                fkBaseJoint = cmds.rename(dupFk, dupFk.replace("_Jnt2", "_Fk_Jxt"))
                fk_joints = cmds.listRelatives(fkBaseJoint, children=True, allDescendents=True)
                fk_joints.append(fkBaseJoint)

                # fk control drives fk joints
                for i, fkJoint in enumerate(fk_joints):
                    if not "_"+self.ar.data.joint_end_attr in fkJoint:
                        self.ar.utils.clearDpArAttr([fkJoint])
                        fkCtrl = fkJoint.replace("_Fk_Jxt", "_Ctrl")
                        self.scaleCompensateCond = fkCtrl.replace("_Ctrl", "_ScaleCompensate_Cnd")
                        cmds.parentConstraint(fkCtrl, fkJoint, maintainOffset=True, name=fkJoint+"_PaC")
                        cmds.scaleConstraint(fkCtrl, fkJoint, maintainOffset=True, name=fkJoint+"_ScC")
                        cmds.setAttr(fkJoint+".segmentScaleCompensate", 0)
                        cmds.setAttr(fkCtrl+".rotateOrder", 1)

                # ik handle
                if self.n_joints >= 2:
                    if self.n_joints == 2:
                        ikHandleList = cmds.ikHandle(startJoint=side+self.number_name+"_00_Ik_Jxt", endEffector=side+self.number_name+"_%02d_Ik_Jxt"%(self.n_joints), solver="ikRPsolver", name=side+self.number_name+"_IKH")
                    else:
                        ikHandleList = cmds.ikHandle(startJoint=side+self.number_name+"_01_Ik_Jxt", endEffector=side+self.number_name+"_%02d_Ik_Jxt"%(self.n_joints), solver="ikRPsolver", name=side+self.number_name+"_IKH")
                    cmds.rename(ikHandleList[1], side+self.number_name+"_Eff")
                    endIkHandleList = cmds.ikHandle(startJoint=side+self.number_name+"_%02d_Ik_Jxt"%(self.n_joints), endEffector=side+self.number_name+"_Ik_"+self.ar.data.joint_end_attr, solver="ikSCsolver", name=side+self.number_name+"_EndIkHandle")
                    cmds.rename(endIkHandleList[1], side+self.number_name+"_End_Eff")
                    self.ikCtrl = self.ar.ctrls.cvControl("id_017_FingerIk", ctrlName=side+self.number_name+"_Ik_Ctrl", r=(self.radius * 0.3), d=self.curve_degree, guideSource=self.name_guide+"_JointEnd", parentTag=self.controllers[1])
                    cmds.addAttr(self.ikCtrl, longName='twist', attributeType='float', keyable=True)
                    cmds.connectAttr(self.ikCtrl+".twist", ikHandleList[0]+".twist", force=True)
                    cmds.setAttr(self.ikCtrl+".rotateOrder", 1)
                    self.ik_ctrl_zero = self.ar.utils.zeroOut([self.ikCtrl])[0]
                    self.ikCtrlZeroList.append(self.ik_ctrl_zero)
                    cmds.delete(cmds.parentConstraint(skin_joints[-1], self.ik_ctrl_zero, maintainOffset=False))
                    cmds.delete(cmds.pointConstraint(self.guide_end_loc, self.ik_ctrl_zero, maintainOffset=False))
                    cmds.connectAttr(self.ikFkRevNode+".outputX", self.ik_ctrl_zero+".visibility", force=True)
                    for q in range(2, self.n_joints+1):
                        cmds.connectAttr(side+self.number_name+"_01_Ctrl.ikFkBlend", side+self.number_name+"_%02d_Ctrl.visibility"%(q), force=True)
                    cmds.parentConstraint(self.ikCtrl, ikHandleList[0], name=side+self.number_name+"_IKH_PaC", maintainOffset=True)
                    cmds.parentConstraint(self.ikCtrl, endIkHandleList[0], name=side+self.number_name+"_EndIkHandle_PaC", maintainOffset=True)
                    ikHandleGrp = cmds.group(ikHandleList[0], endIkHandleList[0], name=side+self.number_name+"_IKH_Grp")
                    cmds.setAttr(ikHandleGrp+".visibility", 0)
                    self.ar.ctrls.setLockHide([self.ikCtrl], ['sx', 'sy', 'sz', 'v'])

                    if self.n_joints == 2:
                        cmds.parentConstraint(side+self.number_name+"_00_Ctrl", side+self.number_name+"_00_Ik_Jxt", maintainOffset=True, name=side+self.number_name+"_00_Ik_Jxt_PaC")
                        cmds.scaleConstraint(side+self.number_name+"_00_Ctrl", side+self.number_name+"_00_Ik_Jxt", maintainOffset=True, name=side+self.number_name+"_00_Ik_Jxt_ScC")

                # ik stretch
                cmds.addAttr(self.ikCtrl, longName='stretchable', attributeType='float', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                stretchNormMD = cmds.createNode("multiplyDivide", name=side+self.number_name+"_StretchNormalize_MD")
                cmds.setAttr(stretchNormMD+".operation", 2)
                distBetweenList = self.ar.utils.distanceBet(side+self.number_name+"_01_Ctrl", self.ikCtrl, name=side+self.number_name+"_DistBet", keep=True)
                cmds.connectAttr(self.ikFkRevNode+".outputX", distBetweenList[5]+"."+self.ikCtrl+"W0", force=True)
                cmds.connectAttr(self.fingerCtrl+".ikFkBlend", distBetweenList[5]+"."+distBetweenList[4]+"W1", force=True)
                cmds.connectAttr(distBetweenList[1]+".distance", stretchNormMD+".input1X", force=True)
                # TO DO? stretch compensate to ik Z axis
                ikStretchZUniformScaleMD = cmds.createNode("multiplyDivide", name=side+self.number_name+"_IkStretchZ_MD")
                cmds.setAttr(ikStretchZUniformScaleMD+".input2X", distBetweenList[0])
                cmds.connectAttr(skin_joints[0]+".scaleZ", ikStretchZUniformScaleMD+".input1X", force=True)
                cmds.connectAttr(ikStretchZUniformScaleMD+".outputX", stretchNormMD+".input2X", force=True)
                stretchScaleMD = cmds.createNode("multiplyDivide", name=side+self.number_name+"_StretchScale_MD")
                cmds.connectAttr(stretchNormMD+".outputX", stretchScaleMD+".input1X", force=True)
                cmds.connectAttr(self.ikCtrl+".stretchable", stretchScaleMD+".input2X", force=True)
                self.stretchCond = cmds.createNode("condition", name=side+self.number_name+"_Stretch_Cnd")
                cmds.connectAttr(stretchScaleMD+".outputX", self.stretchCond+".firstTerm", force=True)
                cmds.setAttr(self.stretchCond+".secondTerm", 1)
                cmds.setAttr(self.stretchCond+".operation", 2)
                cmds.connectAttr(stretchScaleMD+".outputX", self.stretchCond+".colorIfTrueR", force=True)
                self.to_ids.extend([stretchNormMD, ikStretchZUniformScaleMD, stretchScaleMD, self.stretchCond])

                # ik fk blend connnections
                for i, ikJoint in enumerate(ik_joints):
                    if not "_"+self.ar.data.joint_end_attr in ikJoint:
                        self.ar.utils.clearDpArAttr([ikJoint])
                        fkJoint = ikJoint.replace("_Ik_Jxt", "_Fk_Jxt")
                        skin_joint = ikJoint.replace("_Ik_Jxt", "_Jnt")
                        self.fingerCtrl = side+self.number_name+"_01_Ctrl"
                        self.scaleCompensateCond = ikJoint.replace("_Ik_Jxt", "_ScaleCompensate_Cnd")
                        ikFkParentConst = cmds.parentConstraint(ikJoint, fkJoint, skin_joint, maintainOffset=True, name=skin_joint+"_PaC")[0]
                        cmds.connectAttr(self.fingerCtrl+".ikFkBlend", ikFkParentConst+"."+fkJoint+"W1", force=True)
                        cmds.connectAttr(self.ikFkRevNode+".outputX", ikFkParentConst+"."+ikJoint+"W0", force=True)
                        scaleBC = cmds.createNode("blendColors", name=skin_joint+"_BC")
                        self.to_ids.append(scaleBC)
                        cmds.connectAttr(fkJoint+".scaleX", scaleBC+".color1R", force=True)
                        cmds.connectAttr(fkJoint+".scaleY", scaleBC+".color1G", force=True)
                        cmds.connectAttr(fkJoint+".scaleZ", scaleBC+".color1B", force=True)
                        cmds.connectAttr(ikJoint+".scaleX", scaleBC+".color2R", force=True)
                        cmds.connectAttr(ikJoint+".scaleY", scaleBC+".color2G", force=True)
                        cmds.connectAttr(ikJoint+".scaleZ", scaleBC+".color2B", force=True)
                        if self.n_joints == 2:
                            if not "00_Ik_Jxt" in ikJoint: # to avoid thumb cycle error about the stretch
                                cmds.connectAttr(self.stretchCond+".outColorR", ikJoint+".scaleZ", force=True)
                        else:
                            cmds.connectAttr(self.stretchCond+".outColorR", ikJoint+".scaleZ", force=True)
                        cmds.connectAttr(self.fingerCtrl+".ikFkBlend", scaleBC+".blender", force=True)
                        cmds.connectAttr(scaleBC+".output.outputR", skin_joint+".scaleX", force=True)
                        cmds.connectAttr(scaleBC+".output.outputG", skin_joint+".scaleY", force=True)
                        cmds.connectAttr(scaleBC+".output.outputB", skin_joint+".scaleZ", force=True)
                        cmds.setAttr(ikJoint+".segmentScaleCompensate", 1)
                        if "01_Ik_Jxt" in ikJoint:
                            if not self.n_joints == 2: # to avoid thumb cycle error when parenting All_Grp transform node
                                cmds.pointConstraint(self.fingerCtrl, ikJoint, maintainOffset=True, name=ikJoint+"_PoC")
                        if self.n_joints > 2:
                            if i > 0:
                                # fix ik scale
                                cmds.connectAttr(skin_joints[0]+".scaleX", ik_joints[i]+".scaleX", force=True)
                                cmds.connectAttr(skin_joints[0]+".scaleY", ik_joints[i]+".scaleY", force=True)
                # create a masterModuleGrp to be checked if this rig exists:
                ctrlHookList = [side+self.number_name+"_00_SDK_Zero_0_Grp", side+self.number_name+"_01_SDK_Zero_0_Grp"]
                if self.n_joints >= 2:
                    if self.n_joints == 2:
                        scalableHookList = [skin_joints[0], ikBaseJoint, fkBaseJoint, ikHandleGrp, distBetweenList[2], distBetweenList[3], distBetweenList[4]]
                    else:
                        scalableHookList = [skin_joints[0], ikHandleGrp, distBetweenList[2], distBetweenList[3], distBetweenList[4]]
                else:
                    ctrlHookList.append(self.ik_ctrl_zero)
                    scalableHookList = [side+self.number_name+"_00_Jnt"]
                self.create_hook_setup(side, ctrlHookList, scalableHookList)
                if self.corrective:
                    cmds.parent(self.corrective_ctrls_grp, self.ctrl_hook_grp)
                self.scalableGrpList.append(self.scalable_hook_grp)
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


    def composing_info(self):
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.composed = {
                            "scalableGrpList": self.scalableGrpList,
                            "ikCtrlZeroList": self.ikCtrlZeroList,
                            "correctiveCtrlGrpList": self.correctiveCtrlGrpList
                        }
