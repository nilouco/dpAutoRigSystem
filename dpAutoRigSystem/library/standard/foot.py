# importing libraries:
from maya import cmds
from ..base import standard

# global variables to this module:
CLASS_NAME = "Foot"
TITLE = "m024_foot"
DESCRIPTION = "m025_footDesc"
WIKI = "03-‐-Guides#-foot"



class Foot(standard.BaseStandard):
    def __init__(self, ar):
        standard.BaseStandard.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        # declare variables
        self.foot_ctrls = []
        self.rev_foot_ctrl_grp_finals = []
        self.rev_foot_ctrl_shapes = []
        self.to_limb_ik_handle_grps = []
        self.pacs = []
        self.sccs = []
        self.foot_joints = []
        self.ball_rf_items = []
        self.reverse_foot_attrs = []
        self.scalable_grp = []


    def create_guide(self):
        self.create_guide_base()
        self.create_guide_elements()
        self.set_guide_base_initial_position()
        self.add_node_to_guide_net([self.guide_foot_loc, self.guide_rfa_loc, self.guide_rfb_loc, self.guide_rfc_loc, self.guide_rfd_loc, self.guide_rfe_loc, self.guide_rff_loc, self.guide_end_loc], 
                                   ["Foot", "RfA", "RfB", "RfC", "RfD", "RfE", "RfF", "JointEnd"])

    


    def create_guide_elements(self):
        """ Creates the controller locators of the standard module guide.
        """
        # locators
        self.guide_foot_loc = self.ar.ctrls.cvJointLoc(ctrlName=self.name_guide+"_Foot", r=0.3, d=1, guide=True)
        self.guide_rfa_loc = self.ar.ctrls.cvLocator(ctrlName=self.name_guide+"_RfA", r=0.3, d=1, guide=True)
        self.guide_rfb_loc = self.ar.ctrls.cvLocator(ctrlName=self.name_guide+"_RfB", r=0.3, d=1, guide=True)
        self.guide_rfc_loc = self.ar.ctrls.cvLocator(ctrlName=self.name_guide+"_RfC", r=0.3, d=1, guide=True)
        self.guide_rfd_loc = self.ar.ctrls.cvLocator(ctrlName=self.name_guide+"_RfD", r=0.3, d=1, guide=True)
        self.guide_rfe_loc = self.ar.ctrls.cvLocator(ctrlName=self.name_guide+"_RfE", r=0.3, d=1, guide=True)
        self.guide_rff_loc = self.ar.ctrls.cvLocator(ctrlName=self.name_guide+"_RfF", r=0.3, d=1, guide=True)
        self.guide_end_loc = self.ar.ctrls.cvLocator(ctrlName=self.name_guide+"_JointEnd", r=0.1, d=1, guide=True)
        # joints
        self.line_foot = cmds.joint(name=self.name_guide+"_JGuideFoot", radius=0.001)
        self.line_rff = cmds.joint(name=self.name_guide+"_JGuideRfF", radius=0.001)
        self.line_rfe = cmds.joint(name=self.name_guide+"_JGuideRfE", radius=0.001)
        cmds.select(clear=True)
        self.line_rfa = cmds.joint(name=self.name_guide+"_JGuideRfA", radius=0.001)
        self.line_rfd = cmds.joint(name=self.name_guide+"_JGuideRfD", radius=0.001)
        self.line_rfb = cmds.joint(name=self.name_guide+"_JGuideRfB", radius=0.001)
        self.line_rfc = cmds.joint(name=self.name_guide+"_JGuideRfC", radius=0.001)
        self.line_rfac = cmds.joint(name=self.name_guide+"_JGuideRfAC", radius=0.001)
        cmds.select(clear=True)
        self.line_end = cmds.joint(name=self.name_guide+"_JGuideEnd", radius=0.001)
        # setup
        self.ar.utils.set_template([self.line_foot, self.line_rfa, self.line_rfb, self.line_rfc, self.line_rfd, self.line_rfe, self.line_rff, self.line_end])
        cmds.setAttr(self.guide_end_loc+".tz", 1.3)
        cmds.setAttr(self.guide_foot_loc+".translateZ", 2)
        cmds.setAttr(self.guide_foot_loc+".rotateX", 90)
        cmds.setAttr(self.guide_foot_loc+".rotateZ", -90)
        cmds.setAttr(self.guide_rff_loc+".translateY", -1)
        cmds.setAttr(self.guide_rff_loc+".translateZ", 2.5)
        cmds.setAttr(self.guide_rfe_loc+".translateX", -2.5)
        cmds.setAttr(self.guide_rfe_loc+".rotateX", 90)
        cmds.setAttr(self.guide_rfe_loc+".rotateZ", -90)
        cmds.setAttr(self.guide_rfa_loc+".translateX", -0.6)
        cmds.setAttr(self.guide_rfa_loc+".translateY", -1)
        cmds.setAttr(self.guide_rfa_loc+".rotateX", 90)
        cmds.setAttr(self.guide_rfa_loc+".rotateZ", -90)
        cmds.setAttr(self.guide_rfb_loc+".translateX", -0.6)
        cmds.setAttr(self.guide_rfb_loc+".translateY", 1)
        cmds.setAttr(self.guide_rfb_loc+".rotateX", 90)
        cmds.setAttr(self.guide_rfb_loc+".rotateZ", -90)
        cmds.setAttr(self.guide_rfc_loc+".translateX", 1)
        cmds.setAttr(self.guide_rfc_loc+".rotateX", 90)
        cmds.setAttr(self.guide_rfc_loc+".rotateZ", -90)
        cmds.setAttr(self.guide_rfd_loc+".translateX", -3.5)
        cmds.setAttr(self.guide_rfd_loc+".rotateX", 90)
        cmds.setAttr(self.guide_rfd_loc+".rotateZ", -90)
        # parenting
        cmds.parent(self.line_foot, self.line_rfa, self.guide_foot_loc, self.guide_rfa_loc, self.guide_rfb_loc, self.guide_rfc_loc, self.guide_rfd_loc, self.guide_rfe_loc, self.guide_base, relative=True)
        cmds.parent(self.guide_end_loc, self.guide_rff_loc, relative=True)
        cmds.parent(self.guide_rff_loc, self.guide_foot_loc, relative=True)
        cmds.parent(self.line_end, self.line_rff)
        guide_rfe_zero = self.ar.utils.zeroOut([self.guide_rfe_loc], True)
        # edit
        guide_rfe_offset_grp = cmds.listRelatives(guide_rfe_zero, children=True)[0]
        cmds.parentConstraint(self.guide_rff_loc, guide_rfe_offset_grp, maintainOffset=True, skipTranslate="y", name=guide_rfe_offset_grp+"_PaC")
        cmds.parentConstraint(self.guide_rfa_loc, self.line_rfa, maintainOffset=False, name=self.line_rfa+"_PaC")
        cmds.parentConstraint(self.guide_rfb_loc, self.line_rfb, maintainOffset=False, name=self.line_rfb+"_PaC")
        cmds.parentConstraint(self.guide_rfc_loc, self.line_rfc, maintainOffset=False, name=self.line_rfc+"_PaC")
        cmds.parentConstraint(self.guide_rfd_loc, self.line_rfd, maintainOffset=False, name=self.line_rfd+"_PaC")
        cmds.parentConstraint(self.guide_rfe_loc, self.line_rfe, maintainOffset=False, name=self.line_rfe+"_PaC")
        cmds.parentConstraint(self.guide_rff_loc, self.line_rff, maintainOffset=False, name=self.line_rff+"_PaC")
        cmds.parentConstraint(self.guide_rfa_loc, self.line_rfac, maintainOffset=False, name=self.line_rfac+"_PaC")
        self.ar.ctrls.directConnect(self.guide_foot_loc, self.line_foot, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.directConnect(self.guide_end_loc, self.line_end, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.setLockHide([self.guide_end_loc], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
        cmds.transformLimits(self.guide_end_loc, tz=(0.01, 1), etz=(True, False))

 
    def set_guide_base_initial_position(self):
         cmds.setAttr(self.guide_base+".rotateX", -90)
         cmds.setAttr(self.guide_base+".rotateY", 90)


    def rig_me(self, *args):
        standard.BaseStandard.rig_me(self)
        # verify if the guide exists:
        if cmds.objExists(self.guide_base):
            # run for all sides
            for s, side in enumerate(self.sides):
                # redeclaring variables:
                self.base = side+self.number_name+"_Guide_Base"
                self.guide_foot_loc = side+self.number_name+"_Guide_Foot"
                self.guide_rfa_loc = side+self.number_name+"_Guide_RfA"
                self.guide_rfb_loc = side+self.number_name+"_Guide_RfB"
                self.guide_rfc_loc = side+self.number_name+"_Guide_RfC"
                self.guide_rfd_loc = side+self.number_name+"_Guide_RfD"
                self.guide_rfe_loc = side+self.number_name+"_Guide_RfE"
                self.guide_rff_loc = side+self.number_name+"_Guide_RfF"
                self.guide_end_loc = side+self.number_name+"_Guide_JointEnd"
                self.guide_radius = side+self.number_name+"_Guide_Base_RadiusCtrl"

                # declaring attributes reading from dictionary:
                ankle_rf_attr = self.ar.data.lang['c009_leg_extrem']
                middle_rf_attr = self.ar.data.lang['c017_revFoot_middle']
                outside_rf_attr = self.ar.data.lang['c010_revFoot_A']
                inside_rf_attr = self.ar.data.lang['c011_revFoot_B']
                heel_rf_attr = self.ar.data.lang['c012_revFoot_C']
                toe_rf_attr = self.ar.data.lang['c013_revFoot_D']
                ball_rf_attr = self.ar.data.lang['c014_revFoot_E']
                foot_rf_attr = self.ar.data.lang['c015_revFoot_F']
                side_rf_attr = self.ar.data.lang['c016_revFoot_G']
                bottom_rf_attr = self.ar.data.lang['c100_bottom'].lower()
                rf_roll = self.ar.data.lang['c018_revFoot_roll'].capitalize()
                rf_spin = self.ar.data.lang['c019_revFoot_spin'].capitalize()
                rf_turn = self.ar.data.lang['c020_revFoot_turn'].capitalize()
                rf_angle = self.ar.data.lang['c102_angle'].capitalize()
                rf_plant = self.ar.data.lang['c103_plant'].capitalize()
                show_ctrls_attr = self.ar.data.lang['c021_showControls']

                # creating joints:
                cmds.select(clear=True)
                foot_jnt = cmds.joint(name=side+self.number_name+"_"+ankle_rf_attr.capitalize()+"_Jnt")
                self.ar.utils.setJointLabel(foot_jnt, s+self.joint_label_add, 18, self.number_name+ "_"+ankle_rf_attr.capitalize())
                middle_foot_jxt = cmds.joint(name=side+self.number_name+"_"+middle_rf_attr.capitalize()+"_Jxt")
                end_jnt = cmds.joint(name=side+self.number_name+"_"+self.ar.data.joint_end_attr, radius=0.5)
                cmds.select(clear=True)
                middle_foot_jnt = cmds.joint(name=side+self.number_name+"_"+middle_rf_attr.capitalize()+"_Jnt")
                self.ar.utils.setJointLabel(middle_foot_jnt, s+self.joint_label_add, 18, self.number_name+"_"+middle_rf_attr.capitalize())
                end_b_jnt = cmds.joint(name=side+self.number_name+"B_"+self.ar.data.joint_end_attr, radius=0.5)
                cmds.parent(middle_foot_jnt, middle_foot_jxt)
                cmds.addAttr(foot_jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                cmds.addAttr(middle_foot_jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                cmds.select(clear=True)
                self.ar.utils.addJointEndAttr([end_jnt, end_b_jnt])
                
                #Deactivate the segment scale compensate on the bone to prevent scaling problem
                #It will prevent a double scale problem that will come from the upper parent in the rig
                cmds.setAttr(foot_jnt+".segmentScaleCompensate", 0)
                cmds.setAttr(middle_foot_jxt+".segmentScaleCompensate", 0)
                cmds.setAttr(middle_foot_jnt+".segmentScaleCompensate", 0)

                # creating Fk controls:
                foot_ctrl = self.ar.ctrls.cvControl("id_020_FootFk", side+self.number_name+"_"+self.ar.data.lang['c009_leg_extrem']+"_Ctrl", r=(self.radius*0.5), d=self.curve_degree, dir="+Z", guideSource=self.name_guide+"_Foot")
                self.foot_ctrls.append(foot_ctrl)
                cmds.setAttr(foot_ctrl+".rotateOrder", 1)
                self.rev_foot_ctrl_shapes.append(cmds.listRelatives(foot_ctrl, children=True, type='nurbsCurve')[0])
                self.middleFootCtrl = self.ar.ctrls.cvControl("id_021_FootMiddle", side+self.number_name+"_"+self.ar.data.lang['c017_revFoot_middle'].capitalize()+"_Ctrl", r=(self.radius*0.5), d=self.curve_degree, guideSource=self.name_guide+"_RfF")
                cmds.setAttr(self.middleFootCtrl+'.overrideEnabled', 1)
                cmds.setAttr(self.middleFootCtrl+".rotateOrder", 4)
                cmds.matchTransform(foot_ctrl, self.guide_foot_loc, position=True, rotation=True)
                cmds.matchTransform(self.middleFootCtrl, self.guide_rff_loc, position=True, rotation=True)
                if s == 1:
                    cmds.setAttr(self.middleFootCtrl+".scaleX", -1)
                    cmds.setAttr(self.middleFootCtrl+".scaleY", -1)
                    cmds.setAttr(self.middleFootCtrl+".scaleZ", -1)
                self.footCtrlZeroList = self.ar.utils.zeroOut([foot_ctrl, self.middleFootCtrl])

                # reverse foot controls:
                rfa_ctrl = self.ar.ctrls.cvControl("id_018_FootReverse", side+self.number_name+"_"+outside_rf_attr.capitalize()+"_Ctrl", r=(self.radius*0.1), d=self.curve_degree, parentTag=self.middleFootCtrl)
                rfb_ctrl = self.ar.ctrls.cvControl("id_018_FootReverse", side+self.number_name+"_"+inside_rf_attr.capitalize()+"_Ctrl", r=(self.radius*0.1), d=self.curve_degree, parentTag=self.middleFootCtrl)
                rfc_ctrl = self.ar.ctrls.cvControl("id_018_FootReverse", side+self.number_name+"_"+heel_rf_attr.capitalize()+"_Ctrl", r=(self.radius*0.1), d=self.curve_degree, dir="+Y", rot=(0, 90, 0), parentTag=self.middleFootCtrl)
                rfd_ctrl = self.ar.ctrls.cvControl("id_018_FootReverse", side+self.number_name+"_"+toe_rf_attr.capitalize()+"_Ctrl", r=(self.radius*0.1), d=self.curve_degree, dir="+Y", rot=(0, 90, 0), parentTag=self.middleFootCtrl)
                rfe_ctrl = self.ar.ctrls.cvControl("id_018_FootReverse", side+self.number_name+"_"+bottom_rf_attr.capitalize()+"_Ctrl", r=(self.radius*0.1), d=self.curve_degree, dir="+Y", rot=(0, 90, 0), parentTag=self.middleFootCtrl)
                rff_ctrl = self.ar.ctrls.cvControl("id_019_FootReverseE", side+self.number_name+"_"+ball_rf_attr.capitalize()+"_Ctrl", r=(self.radius*0.5), d=self.curve_degree, rot=(0, 90, 0), parentTag=foot_ctrl)
                self.ball_rf_items.append(rff_ctrl)
                cmds.connectAttr(rff_ctrl+".message", self.middleFootCtrl+".parentTag", force=True)
                
                # reverse foot groups:
                rfa_grp = cmds.group(rfa_ctrl, name=rfa_ctrl+"_Grp")
                rfb_grp = cmds.group(rfb_ctrl, name=rfb_ctrl+"_Grp")
                rfc_grp = cmds.group(rfc_ctrl, name=rfc_ctrl+"_Grp")
                rfd_grp = cmds.group(rfd_ctrl, name=rfd_ctrl+"_Grp")
                rfe_grp = cmds.group(rfe_ctrl, name=rfe_ctrl+"_Grp")
                rff_grp = cmds.group(rff_ctrl, name=rff_ctrl+"_Grp")
                rf_grps = [rfa_grp, rfb_grp, rfc_grp, rfd_grp, rfe_grp, rff_grp]
                
                # putting groups in the correct place:
                cmds.matchTransform(foot_jnt, self.guide_foot_loc, position=True, rotation=True)
                cmds.matchTransform(middle_foot_jxt, self.guide_rff_loc, position=True, rotation=True)
                cmds.matchTransform(end_jnt, self.guide_end_loc, position=True, rotation=True)
                cmds.matchTransform(end_b_jnt, self.guide_end_loc, position=True, rotation=True)
                cmds.matchTransform(rfa_grp, self.guide_rfa_loc, position=True, rotation=True)
                cmds.matchTransform(rfb_grp, self.guide_rfb_loc, position=True, rotation=True)
                cmds.matchTransform(rfc_grp, self.guide_rfc_loc, position=True, rotation=True)
                cmds.matchTransform(rfd_grp, self.guide_rfd_loc, position=True, rotation=True)
                cmds.matchTransform(rfe_grp, self.guide_rfe_loc, position=True, rotation=True)
                cmds.matchTransform(rff_grp, self.guide_rff_loc, position=True, rotation=True)
                
                # edit ball controller shape
                if s == 0: #left
                    tempBallCluster = cmds.cluster((cmds.listRelatives(rff_ctrl, children=True, type="shape")[0])+".cv[3:5]")[1]
                else: #right
                    tempBallCluster = cmds.cluster((cmds.listRelatives(rff_ctrl, children=True, type="shape")[0])+".cv[0:2]")[1]
                cmds.setAttr(tempBallCluster+".translateY", self.radius*0.3)
                cmds.delete(rff_ctrl, constructionHistory=True)
                tempBallClusterB = cmds.cluster(rff_ctrl)[1]
                cmds.parentConstraint(self.guide_foot_loc, self.guide_rff_loc, tempBallClusterB, maintainOffset=False)
                cmds.delete(rff_ctrl, constructionHistory=True)
                
                # mounting hierarchy:
                cmds.parent(rfb_grp, rfa_ctrl)
                cmds.parent(rfc_grp, rfb_ctrl)
                cmds.parent(rfd_grp, rfc_ctrl)
                cmds.parent(rfe_grp, rfd_ctrl)
                cmds.parent(rff_grp, rfe_ctrl)
                
                # reverse foot zero out groups:
                self.RFFZero = self.ar.utils.zeroOut([rff_grp])[0]
                self.RFFZeroExtra = self.ar.utils.zeroOut([self.RFFZero])[0]
                self.RFFZeroFollow = self.ar.utils.zeroOut([self.RFFZero])[0]
                self.RFEZero = self.ar.utils.zeroOut([rfe_grp])[0]
                self.RFDZero = self.ar.utils.zeroOut([rfd_grp])[0]
                self.RFCZero = self.ar.utils.zeroOut([rfc_grp])[0]
                self.RFBZero = self.ar.utils.zeroOut([rfb_grp])[0]
                self.RFAZero = self.ar.utils.zeroOut([rfa_grp])[0]
                self.RFAZeroExtra = self.ar.utils.zeroOut([self.RFAZero])[0]
                
                # fixing side rool rotation order:
                cmds.setAttr(self.RFBZero+".rotateOrder", 5)
                
                # creating ikHandles:
                ikHandleAnkleList = cmds.ikHandle(name=side+self.number_name+"_"+ankle_rf_attr.capitalize()+"_IKH", startJoint=foot_jnt, endEffector=middle_foot_jxt, solver='ikRPsolver')
                # match transformations again to avoid ikHandle rotate plane solver issue:
                cmds.matchTransform(middle_foot_jxt, self.guide_rff_loc, position=True, rotation=True)
                ikHandleMiddleList = cmds.ikHandle(name=side+self.number_name+"_"+middle_rf_attr.capitalize()+"_IKH", startJoint=middle_foot_jxt, endEffector=end_jnt, solver='ikRPsolver')
                cmds.rename(ikHandleAnkleList[1], ikHandleAnkleList[0]+"_Eff")
                cmds.rename(ikHandleMiddleList[1], ikHandleMiddleList[0]+"_Eff")
                cmds.setAttr(ikHandleAnkleList[0]+'.visibility', 0)
                cmds.setAttr(ikHandleMiddleList[0]+'.visibility', 0)

                # mount hierarchy:
                cmds.parent(self.footCtrlZeroList[1], rfe_ctrl, absolute=True)
                cmds.parent(ikHandleMiddleList[0], self.middleFootCtrl, absolute=True)
                self.toLimbIkHandleGrp = cmds.group(empty=True, name=side+self.number_name+"_"+self.ar.data.lang['c009_leg_extrem']+"_Grp")
                self.to_limb_ik_handle_grps.append(self.toLimbIkHandleGrp)
                cmds.parent(ikHandleAnkleList[0], self.toLimbIkHandleGrp, rff_ctrl, absolute=True)
                cmds.makeIdentity(self.toLimbIkHandleGrp, apply=True, translate=True, rotate=True, scale=True)
                parentConst = cmds.parentConstraint(rff_ctrl, foot_jnt, maintainOffset=True, name=foot_jnt+"_PaC")[0]
                self.pacs.append(parentConst)
                self.foot_joints.append(foot_jnt)
                cmds.parent(self.RFAZeroExtra, foot_ctrl, absolute=True)
                
                scaleConst = cmds.scaleConstraint(foot_ctrl, foot_jnt, maintainOffset=True, name=foot_jnt+"_ScC")
                self.sccs.append(scaleConst)
                cmds.parentConstraint(self.middleFootCtrl, middle_foot_jnt, maintainOffset=True, name=middle_foot_jnt+"_PaC")
                cmds.scaleConstraint(self.middleFootCtrl, middle_foot_jnt, maintainOffset=True, name=middle_foot_jnt+"_ScC")

                # add attributes to footCtrl and connect them to reverseFoot groups rotation:
                rfAttrList = [outside_rf_attr, inside_rf_attr, heel_rf_attr, toe_rf_attr, bottom_rf_attr, ball_rf_attr]
                rfTypeAttrList = [rf_roll, rf_spin]
                for j, rfAttr in enumerate(rfAttrList):
                    for t, rfType in enumerate(rfTypeAttrList):
                        if t == 1 and j == (len(rfAttrList) - 1):  # create turn attr to ball
                            cmds.addAttr(foot_ctrl, longName=rfAttr+rf_turn, attributeType='float', keyable=True)
                            cmds.connectAttr(foot_ctrl+"."+rfAttr+rf_turn, rf_grps[j]+".rotateZ", force=True)
                            self.reverse_foot_attrs.append(rfAttr+rf_turn)
                        cmds.addAttr(foot_ctrl, longName=rfAttr+rfType, attributeType='float', keyable=True)
                        self.reverse_foot_attrs.append(rfAttr+rfType)
                        if t == 0:
                            if j > 1:
                                cmds.connectAttr(foot_ctrl+"."+rfAttr+rfType, rf_grps[j]+".rotateX", force=True)
                            else:
                                cmds.connectAttr(foot_ctrl+"."+rfAttr+rfType, rf_grps[j]+".rotateZ", force=True)
                        else:
                            cmds.connectAttr(foot_ctrl+"."+rfAttr+rfType, rf_grps[j]+".rotateY", force=True)
                
                # creating the originedFrom attributes (in order to permit integrated parents in the future):
                self.ar.utils.originedFrom(objName=foot_ctrl, attrString=self.base+";"+self.guide_foot_loc+";"+self.guide_radius)
                self.ar.utils.originedFrom(objName=rfa_ctrl, attrString=self.guide_rfa_loc)
                self.ar.utils.originedFrom(objName=rfb_ctrl, attrString=self.guide_rfb_loc)
                self.ar.utils.originedFrom(objName=rfc_ctrl, attrString=self.guide_rfc_loc)
                self.ar.utils.originedFrom(objName=rfd_ctrl, attrString=self.guide_rfd_loc)
                self.ar.utils.originedFrom(objName=rfe_ctrl, attrString=self.guide_rfe_loc)
                self.ar.utils.originedFrom(objName=self.middleFootCtrl, attrString=self.guide_rff_loc+";"+self.guide_end_loc)

                # creating pre-defined attributes for footRoll and sideRoll attributes, also rollAngle:
                cmds.addAttr(foot_ctrl, longName=foot_rf_attr+rf_roll, attributeType='float', keyable=True)
                cmds.addAttr(foot_ctrl, longName=foot_rf_attr+rf_roll+rf_angle, attributeType='float', defaultValue=30, keyable=False)
                cmds.addAttr(foot_ctrl, longName=foot_rf_attr+rf_roll+rf_plant, attributeType='float', defaultValue=0, keyable=False)
                cmds.addAttr(foot_ctrl, longName=side_rf_attr+rf_roll, attributeType='float', keyable=True)
                cmds.setAttr(foot_ctrl+"."+foot_rf_attr+rf_roll+rf_angle, channelBox=True)
                cmds.setAttr(foot_ctrl+"."+foot_rf_attr+rf_roll+rf_plant, channelBox=True)

                # create clampNodes in order to limit the side rotations:
                sideClamp = cmds.createNode("clamp", name=side+self.number_name+"_Side_Clp")
                # outside values in R
                cmds.setAttr(sideClamp+".minR", -360)
                # inside values in G
                cmds.setAttr(sideClamp+".maxG", 360)
                # inverting sideRoll values:
                sideMD = cmds.createNode("multiplyDivide", name=side+self.number_name+"_Side_MD")
                cmds.setAttr(sideMD+".input2X", -1)
                # connections:
                cmds.connectAttr(foot_ctrl+"."+side_rf_attr+rf_roll, sideMD+".input1X", force=True)
                cmds.connectAttr(sideMD+".outputX", sideClamp+".inputR", force=True)
                cmds.connectAttr(sideMD+".outputX", sideClamp+".inputG", force=True)
                cmds.connectAttr(sideClamp+".outputR", self.RFAZero+".rotateZ", force=True)
                cmds.connectAttr(sideClamp+".outputG", self.RFBZero+".rotateZ", force=True)

                # for footRoll:
                footHeelClp = cmds.createNode("clamp", name=side+self.number_name+"_Roll_Heel_Clp")
                # heel values in R
                cmds.setAttr(footHeelClp+".minR", -360)
                cmds.connectAttr(foot_ctrl+"."+foot_rf_attr+rf_roll, footHeelClp+".inputR", force=True)
                cmds.connectAttr(footHeelClp+".outputR", self.RFCZero+".rotateX", force=True)
                
                # footRoll with angle limit:
                footPMA = cmds.createNode("plusMinusAverage", name=side+self.number_name+"_Roll_PMA")
                footSR = cmds.createNode("setRange", name=side+self.number_name+"_Roll_SR")
                cmds.setAttr(footSR+".oldMaxY", 180)
                cmds.setAttr(footPMA+".input1D[0]", 180)
                cmds.setAttr(footPMA+".operation", 2) #substract
                cmds.connectAttr(foot_ctrl+"."+foot_rf_attr+rf_roll, footSR+".valueX", force=True)
                cmds.connectAttr(foot_ctrl+"."+foot_rf_attr+rf_roll, footSR+".valueY", force=True)
                cmds.connectAttr(foot_ctrl+"."+foot_rf_attr+rf_roll+rf_angle, footSR+".maxX", force=True)
                cmds.connectAttr(foot_ctrl+"."+foot_rf_attr+rf_roll+rf_angle, footSR+".oldMinY", force=True)
                cmds.connectAttr(foot_ctrl+"."+foot_rf_attr+rf_roll+rf_angle, footSR+".oldMaxX", force=True)
                cmds.connectAttr(foot_ctrl+"."+foot_rf_attr+rf_roll+rf_angle, footPMA+".input1D[1]", force=True)
                cmds.connectAttr(footPMA+".output1D", footSR+".maxY", force=True)
                
                # plant angle for foot roll:
                footPlantClp = cmds.createNode("clamp", name=side+self.number_name+"_Roll_Plant_Clp")
                footPlantCnd = cmds.createNode("condition", name=side+self.number_name+"_Roll_Plant_Cnd")
                cmds.setAttr(footPlantCnd+".operation", 4) #less than
                cmds.connectAttr(foot_ctrl+"."+foot_rf_attr+rf_roll, footPlantClp+".inputR", force=True)
                cmds.connectAttr(foot_ctrl+"."+foot_rf_attr+rf_roll+rf_plant, footPlantClp+".maxR", force=True)
                cmds.connectAttr(footPlantClp+".outputR", footPlantCnd+".firstTerm", force=True)
                cmds.connectAttr(footPlantClp+".outputR", footPlantCnd+".colorIfTrueR", force=True)
                cmds.connectAttr(foot_ctrl+"."+foot_rf_attr+rf_roll+rf_plant, footPlantCnd+".secondTerm", force=True)
                cmds.connectAttr(foot_ctrl+"."+foot_rf_attr+rf_roll+rf_plant, footPlantCnd+".colorIfFalseR", force=True)
                
                # back to zero footRoll when greather then angle plus plant values:
                anglePlantPMA = cmds.createNode("plusMinusAverage", name=side+self.number_name+"_AnglePlant_PMA")
                anglePlantMD = cmds.createNode("multiplyDivide", name=side+self.number_name+"_AnglePlant_MD")
                anglePlantRmV = cmds.createNode("remapValue", name=side+self.number_name+"_AnglePlant_RmV")
                anglePlantCnd = cmds.createNode("condition", name=side+self.number_name+"_AnglePlant_Cnd")
                cmds.setAttr(anglePlantMD+".input2X", -1)
                cmds.setAttr(anglePlantRmV+".inputMax", 90)
                cmds.setAttr(anglePlantRmV+".value[0].value_Interp", 3) #spline
                cmds.setAttr(anglePlantRmV+".value[1].value_Interp", 3) #spline
                cmds.setAttr(anglePlantCnd+".operation", 2) #greather than
                cmds.connectAttr(foot_ctrl+"."+foot_rf_attr+rf_roll+rf_angle, anglePlantPMA+".input1D[0]", force=True)
                cmds.connectAttr(foot_ctrl+"."+foot_rf_attr+rf_roll+rf_plant, anglePlantPMA+".input1D[1]", force=True)
                cmds.connectAttr(foot_ctrl+"."+foot_rf_attr+rf_roll, anglePlantCnd+".firstTerm", force=True)
                cmds.connectAttr(anglePlantPMA+".output1D", anglePlantCnd+".secondTerm", force=True)
                cmds.connectAttr(anglePlantPMA+".output1D", anglePlantMD+".input1X", force=True)
                cmds.connectAttr(anglePlantPMA+".output1D", anglePlantRmV+".inputMin", force=True)
                cmds.connectAttr(anglePlantMD+".outputX", anglePlantRmV+".outputMax", force=True)
                cmds.connectAttr(foot_ctrl+"."+foot_rf_attr+rf_roll, anglePlantRmV+".inputValue", force=True)
                cmds.connectAttr(anglePlantRmV+".outColorR", anglePlantCnd+".colorIfTrueR", force=True)
                cmds.connectAttr(anglePlantCnd+".outColorR", self.RFFZeroExtra+".rotateX", force=True)
                
                # connect to groups in order to rotate them:
                cmds.connectAttr(footSR+".outValueY", self.RFDZero+".rotateX", force=True)
                cmds.connectAttr(footSR+".outValueX", self.RFFZero+".rotateX", force=True)
                if s == 0: #left
                    cmds.connectAttr(footPlantCnd+".outColorR", self.footCtrlZeroList[1]+".rotateX", force=True)
                else: #fix right side mirror
                    footPlantInvMD = cmds.createNode("multiplyDivide", name=side+self.number_name+"_Plant_Inv_MD")
                    cmds.setAttr(footPlantInvMD+".input2X", -1)
                    cmds.connectAttr(footPlantCnd+".outColorR", footPlantInvMD+".input1X", force=True)
                    cmds.connectAttr(footPlantInvMD+".outputX", self.footCtrlZeroList[1]+".rotateX", force=True)
                    self.to_ids.append(footPlantInvMD)
                
                # create follow attribute to footBall control to space switch to middle control space:
                cmds.addAttr(rff_ctrl, longName="follow", attributeType ="double", min=0, max=1, defaultValue=0, keyable=True)
                pacFootBall = cmds.parentConstraint(self.middleFootCtrl, rfe_ctrl, self.RFFZeroFollow, maintainOffset=True, name=self.RFFZeroFollow+"_PaC")[0]
                cmds.setAttr(pacFootBall+".interpType", 0)
                cmds.connectAttr(rff_ctrl+".follow", pacFootBall+"."+self.middleFootCtrl+"W0")
                footBallRevNode = cmds.createNode("reverse", name=rff_ctrl+"_PaC_Rev")
                cmds.connectAttr(rff_ctrl+".follow", footBallRevNode+".inputX")
                cmds.connectAttr(footBallRevNode+".outputX", pacFootBall+"."+rfe_ctrl+"W1")

                # organizing keyable attributes:
                self.ar.ctrls.setLockHide([self.middleFootCtrl, foot_ctrl], ['v'], l=False)
                
                # show or hide reverseFoot controls:
                cmds.addAttr(foot_ctrl, longName=show_ctrls_attr, attributeType='short', minValue=0, defaultValue=1, maxValue=1)
                cmds.setAttr(foot_ctrl+"."+show_ctrls_attr, keyable=False, channelBox=True)
                cmds.addAttr(foot_ctrl, longName="visIkFk", attributeType='float', minValue=0, defaultValue=1, maxValue=1, keyable=False)
                vis_md = cmds.createNode("multiplyDivide", name=side+self.number_name+"_Vis_MD")
                cmds.connectAttr(foot_ctrl+".visIkFk", vis_md+".input2X", force=True)
                cmds.connectAttr(foot_ctrl+"."+show_ctrls_attr, vis_md+".input1X", force=True)
                for rf_ctrl in [rfa_ctrl, rfb_ctrl, rfc_ctrl, rfd_ctrl, rfe_ctrl, rff_ctrl]: #showHideCtrlList
                    rf_ctrl_shape = cmds.listRelatives(rf_ctrl, children=True, type='nurbsCurve')[0]
                    cmds.connectAttr(vis_md+".outputX", rf_ctrl_shape+".visibility", force=True)
                # create a masterModuleGrp to be checked if this rig exists:
                temp_scalable_hook_grp = cmds.createNode("transform", name=side+self.number_name+"_TEMP_Grp")
                self.create_hook_setup(side, [self.footCtrlZeroList[0]], [temp_scalable_hook_grp])
                cmds.delete(temp_scalable_hook_grp)
                cmds.xform(self.scalable_hook_grp, matrix=cmds.getAttr(foot_jnt+".worldMatrix"), worldSpace=True)
                cmds.parent(foot_jnt, self.scalable_hook_grp, absolute=True)
                #Remove the Joint orient to make sure the bone is at the same orientation than it's parent
                cmds.setAttr(foot_jnt+".jointOrientX", 0)
                cmds.setAttr(foot_jnt+".jointOrientY", 0)
                cmds.setAttr(foot_jnt+".jointOrientZ", 0)
                self.scalable_grp.append(self.scalable_hook_grp)
                self.rev_foot_ctrl_grp_finals.append(self.ctrl_hook_grp)
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.number_name+'_'+self.mirror_grp)
                self.ar.utils.addCustomAttr([rfa_grp, rfb_grp, rfc_grp, rfd_grp, rfe_grp], self.ar.utils.ignoreTransformIOAttr)
                self.to_ids.extend([sideClamp, sideMD, footHeelClp, footPMA, footSR, footPlantClp, footPlantCnd, anglePlantPMA, anglePlantMD, anglePlantRmV, anglePlantCnd, footBallRevNode, vis_md])
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
                            "revFootCtrlList": self.foot_ctrls,
                            "revFootCtrlGrpList": self.rev_foot_ctrl_grp_finals,
                            "revFootCtrlShapeList": self.rev_foot_ctrl_shapes,
                            "toLimbIkHandleGrpList": self.to_limb_ik_handle_grps,
                            "parentConstList": self.pacs,
                            "scaleConstList": self.sccs,
                            "footJntList": self.foot_joints,
                            "ballRFList": self.ball_rf_items,
                            "reverseFootAttrList": self.reverse_foot_attrs,
                            "scalableGrp": self.scalable_grp,
                        }
