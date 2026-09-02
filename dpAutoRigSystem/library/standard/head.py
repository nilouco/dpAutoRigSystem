# importing libraries:
from maya import cmds
from ..base import standard

# global variables to this module:    
CLASS_NAME = "Head"
TITLE = "m017_head"
DESCRIPTION = "m018_headDesc"
WIKI = "03-‐-Guides#-head"

JAW = "jaw"
CHIN = "chin"
LIPS = "lips"
UPPERHEAD = "upperHead"



class Head(standard.BaseStandard):
    def __init__(self, ar):
        standard.BaseStandard.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.facial_attributes = ["facialBrow", "facialEyelid", "facialMouth", "facialLips", "facialSneer", "facialGrimace", "facialFace"]
        self.load_variables()


    def load_variables(self, *args):
        """ Just load class variables here.
        """
        self.declare_guide_elements(self.name_guide)
        self.corrective_ctrl_grps = []
        self.inner_ctrls = []
        self.facial_factor = 0.15
    
    
    def create_guide(self):
        self.create_guide_base()
        self.create_guide_custom_attr()
        self.create_guide_elements()
        self.create_guide_deformer_cube()
        self.add_node_to_guide_net([self.guide_neck_loc, self.guide_head_loc, self.guide_jaw_loc, self.guide_chin_loc, self.guide_chew_loc, self.guide_left_corner_lip_loc, self.guide_upper_jaw_loc, self.guide_upper_head_loc, self.guide_upper_lip_loc, self.guide_lower_lip_loc, self.guide_deformer_center_loc, self.guide_deformer_radius_loc, self.guide_brow_loc, self.guide_eyelid_loc, self.guide_mouth_loc, self.guide_lips_loc, self.guide_sneer_loc, self.guide_grimace_loc, self.guide_face_loc, self.guide_end_loc],\
                                ["Neck0", "Head", "Jaw", "Chin", "Chew", "LCornerLip", "UpperJaw", "UpperHead", "UpperLip", "LowerLip", "DeformerCenter", "DeformerRadius", "Brow", "Eyelid", "Mouth", "Lips", "Sneer", "Grimace", "Face", "JointEnd"])

    
    def create_guide_custom_attr(self):
        """ Add guide_base attributes and set them.
        """
        cmds.addAttr(self.guide_base, longName="nJoints", defaultValue=1, attributeType='long')
        cmds.addAttr(self.guide_base, longName="flip", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="articulation", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="corrective", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="deformer", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="facial", attributeType='bool')
        for attr in self.facial_attributes:
            cmds.addAttr(self.guide_base, longName=attr, attributeType='bool', defaultValue=1)
        cmds.addAttr(self.guide_base, longName="connectUserType", attributeType='long', defaultValue=0) #bs
        cmds.addAttr(self.guide_base, longName=JAW, attributeType='bool', defaultValue=1)
        cmds.addAttr(self.guide_base, longName=CHIN, attributeType='bool', defaultValue=1)
        cmds.addAttr(self.guide_base, longName=LIPS, attributeType='bool', defaultValue=1)
        cmds.addAttr(self.guide_base, longName=UPPERHEAD, attributeType='bool', defaultValue=1)
        cmds.addAttr(self.guide_base, longName="style", attributeType='enum', enumName=self.ar.data.lang['m042_default']+':'+self.ar.data.lang['m026_biped']+":"+self.ar.data.lang['m037_quadruped'])


    def create_guide_elements(self):
        """ Creates the controller locators of the standard module guide.
        """
        # locators
        self.guide_neck_loc = self.ar.ctrls.create_joint_locator(ctrl_name=self.name_guide+"_Neck0", r=0.5, d=1, rot=(-90, 90, 0), guide=True)
        self.guide_head_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_Head", r=0.4, d=1, guide=True)
        self.guide_jaw_loc  = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_Jaw", r=0.3, d=1, guide=True)
        self.guide_chin_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_Chin", r=0.3, d=1, guide=True)
        self.guide_chew_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_Chew", r=0.3, d=1, guide=True)
        self.guide_left_corner_lip_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_LCornerLip", r=0.1, d=1, guide=True)
        self.guide_right_corner_lip_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_RCornerLip", r=0.1, d=1, guide=True)
        self.guide_upper_jaw_loc  = self.ar.ctrls.create_joint_locator(ctrl_name=self.name_guide+"_UpperJaw", r=0.2, d=1, rot=(0, 0, 90), guide=True)
        self.guide_upper_head_loc = self.ar.ctrls.create_joint_locator(ctrl_name=self.name_guide+"_UpperHead", r=0.2, d=1, rot=(0, 0, 90), guide=True)
        self.guide_upper_lip_loc  = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_UpperLip", r=0.15, d=1, guide=True)
        self.guide_lower_lip_loc  = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_LowerLip", r=0.15, d=1, guide=True)
        self.guide_brow_loc    = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_Brow", r=0.2, d=1, guide=True, color="cyan", cvType=self.ar.ctrls.get_controller_module_by_id("id_046_FacialBrow"))
        self.guide_eyelid_loc  = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_Eyelid", r=0.2, d=1, guide=True, rot=(0, 0, 90), color="cyan", cvType=self.ar.ctrls.get_controller_module_by_id("id_047_FacialEyelid"))
        self.guide_mouth_loc   = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_Mouth", r=0.2, d=1, guide=True, rot=(0, 0, -90), color="cyan", cvType=self.ar.ctrls.get_controller_module_by_id("id_048_FacialMouth"))
        self.guide_lips_loc    = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_Lips", r=0.1, d=1, guide=True, color="cyan", cvType=self.ar.ctrls.get_controller_module_by_id("id_049_FacialLips"))
        self.guide_sneer_loc   = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_Sneer", r=0.2, d=1, guide=True, color="cyan", cvType=self.ar.ctrls.get_controller_module_by_id("id_050_FacialSneer"))
        self.guide_grimace_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_Grimace", r=0.2, d=1, guide=True, rot=(0, 0, 180), color="cyan", cvType=self.ar.ctrls.get_controller_module_by_id("id_051_FacialGrimace"))
        self.guide_face_loc    = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_Face", r=0.2, d=1, guide=True, color="cyan", cvType=self.ar.ctrls.get_controller_module_by_id("id_052_FacialFace"))
        self.guide_deformer_center_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_DeformerCenter", r=0.6, d=1, guide=True, color="cyan")
        self.guide_deformer_radius_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_DeformerRadius", r=0.3, d=1, guide=True, color="cyan", cvType=self.ar.ctrls.get_controller_module_by_id("id_100_HeadDeformerRadius"))
        self.guide_end_loc = self.ar.ctrls.create_curve_locator(ctrl_name=self.name_guide+"_JointEnd", r=0.1, d=1, guide=True)
        # joints
        self.line_neck_0 = cmds.joint(name=self.name_guide+"_JGuideNeck0", radius=0.001)
        self.line_head = cmds.joint(name=self.name_guide+"_JGuideHead", radius=0.001)
        self.line_upper_jaw = cmds.joint(name=self.name_guide+"_JGuideUpperJaw", radius=0.001)
        self.line_upper_lip = cmds.joint(name=self.name_guide+"_JGuideUpperLip", radius=0.001)
        cmds.select(self.line_upper_jaw)
        self.line_upper_head = cmds.joint(name=self.name_guide+"_JGuideUpperHead", radius=0.001)
        cmds.select(self.line_head)
        self.line_jaw  = cmds.joint(name=self.name_guide+"_JGuideJaw", radius=0.001)
        self.line_chin = cmds.joint(name=self.name_guide+"_JGuideChin", radius=0.001)
        self.line_chew = cmds.joint(name=self.name_guide+"_JGuideChew", radius=0.001)
        cmds.select(self.line_chin)
        self.line_lower_lip = cmds.joint(name=self.name_guide+"_JGuideLowerLip", radius=0.001)
        cmds.select(self.line_jaw)
        self.line_left_lip = cmds.joint(name=self.name_guide+"_JGuideLLip", radius=0.001)
        cmds.select(self.line_chew)
        self.line_end = cmds.joint(name=self.name_guide+"_JGuideEnd", radius=0.001)
        # setup
        self.ar.utils.set_template([self.line_neck_0, self.line_head, self.line_upper_jaw, self.line_upper_head, self.line_jaw, self.line_chin, self.line_chew, self.line_upper_lip, self.line_lower_lip, self.line_end])
        cmds.setAttr(self.guide_end_loc+".tz", self.ar.ctrls.dpCheckLinearUnit(0.6, boundingBox=False))
        # transform cvLocs in order to put as a good head guide:
        cmds.setAttr(self.guide_base+".rotateX", -90)
        cmds.setAttr(self.guide_base+".rotateY", 90)
        cmds.setAttr(self.guide_neck_loc+".rotateZ", 90)
        cmds.makeIdentity(self.guide_neck_loc, rotate=True, apply=False)
        cmds.setAttr(self.guide_head_loc+".translateY", 2)
        cmds.setAttr(self.guide_upper_jaw_loc+".translateY", 3.5)
        cmds.setAttr(self.guide_upper_jaw_loc+".translateZ", 0.25)
        cmds.setAttr(self.guide_upper_head_loc+".translateY", 4.2)
        cmds.setAttr(self.guide_upper_head_loc+".translateZ", 0.5)
        cmds.setAttr(self.guide_jaw_loc+".translateY", 2.7)
        cmds.setAttr(self.guide_jaw_loc+".translateZ", 0.7)
        cmds.setAttr(self.guide_chin_loc+".translateY", 2.5)
        cmds.setAttr(self.guide_chin_loc+".translateZ", 1.0)
        cmds.setAttr(self.guide_chew_loc+".translateY", 2.3)
        cmds.setAttr(self.guide_chew_loc+".translateZ", 1.3)
        # deformers
        cmds.setAttr(self.guide_deformer_center_loc+".translateY", 4.0)
        cmds.setAttr(self.guide_deformer_center_loc+".translateZ", 0.5)
        cmds.setAttr(self.guide_deformer_radius_loc+".translateX", 3.0)
        cmds.setAttr(self.guide_deformer_radius_loc+".translateY", 7.0)
        cmds.setAttr(self.guide_deformer_radius_loc+".translateZ", 3.5)
        cmds.transformLimits(self.guide_deformer_radius_loc, enableTranslationX=(1, 0), translationX=(0.001, 1), enableTranslationY=(1, 0), translationY=(0.001, 1), enableTranslationZ=(1, 0), translationZ=(0.001, 1))
        # lip cvLocs:
        cmds.setAttr(self.guide_upper_lip_loc+".translateY", 2.9)
        cmds.setAttr(self.guide_upper_lip_loc+".translateZ", 3.5)
        cmds.setAttr(self.guide_lower_lip_loc+".translateY", 2.3)
        cmds.setAttr(self.guide_lower_lip_loc+".translateZ", 3.5)
        cmds.setAttr(self.guide_left_corner_lip_loc+".translateX", 0.6)
        cmds.setAttr(self.guide_left_corner_lip_loc+".translateY", 2.6)
        cmds.setAttr(self.guide_left_corner_lip_loc+".translateZ", 3.4)
        # mirror right Lip:
        lip_t_md = cmds.createNode("multiplyDivide", name=self.name_guide+"_LipTMD")
        lip_r_md = cmds.createNode("multiplyDivide", name=self.name_guide+"_LipRMD")
        cmds.connectAttr(self.guide_left_corner_lip_loc+".translateX", lip_t_md+".input1X", force=True)
        cmds.connectAttr(self.guide_left_corner_lip_loc+".translateY", lip_t_md+".input1Y", force=True)
        cmds.connectAttr(self.guide_left_corner_lip_loc+".translateZ", lip_t_md+".input1Z", force=True)
        cmds.connectAttr(self.guide_left_corner_lip_loc+".rotateX", lip_r_md+".input1X", force=True)
        cmds.connectAttr(self.guide_left_corner_lip_loc+".rotateY", lip_r_md+".input1Y", force=True)
        cmds.connectAttr(self.guide_left_corner_lip_loc+".rotateZ", lip_r_md+".input1Z", force=True)
        cmds.connectAttr(lip_t_md+".outputX", self.guide_right_corner_lip_loc+".translateX", force=True)
        cmds.connectAttr(lip_t_md+".outputY", self.guide_right_corner_lip_loc+".translateY", force=True)
        cmds.connectAttr(lip_t_md+".outputZ", self.guide_right_corner_lip_loc+".translateZ", force=True)
        cmds.connectAttr(lip_r_md+".outputX", self.guide_right_corner_lip_loc+".rotateX", force=True)
        cmds.connectAttr(lip_r_md+".outputY", self.guide_right_corner_lip_loc+".rotateY", force=True)
        cmds.connectAttr(lip_r_md+".outputZ", self.guide_right_corner_lip_loc+".rotateZ", force=True)
        cmds.setAttr(lip_t_md+".input2X", -1)
        cmds.setAttr(lip_r_md+".input2Y", -1)
        cmds.setAttr(lip_r_md+".input2Z", -1)
        cmds.setAttr(self.guide_right_corner_lip_loc+".template", 1)
        # facial cvLocs
        cmds.setAttr(self.guide_brow_loc+".translateX", 0.9)
        cmds.setAttr(self.guide_brow_loc+".translateY", 4.7)
        cmds.setAttr(self.guide_brow_loc+".translateZ", 3.5)
        cmds.setAttr(self.guide_eyelid_loc+".translateX", 0.3)
        cmds.setAttr(self.guide_eyelid_loc+".translateY", 4.15)
        cmds.setAttr(self.guide_eyelid_loc+".translateZ", 3.5)
        cmds.setAttr(self.guide_mouth_loc+".translateX", 1)
        cmds.setAttr(self.guide_mouth_loc+".translateY", 2.6)
        cmds.setAttr(self.guide_mouth_loc+".translateZ", 3.4)
        cmds.setAttr(self.guide_lips_loc+".translateY", 2.6)
        cmds.setAttr(self.guide_lips_loc+".translateZ", 3.9)
        cmds.setAttr(self.guide_sneer_loc+".translateY", 3.15)
        cmds.setAttr(self.guide_sneer_loc+".translateZ", 3.9)
        cmds.setAttr(self.guide_grimace_loc+".translateY", 2)
        cmds.setAttr(self.guide_grimace_loc+".translateZ", 3.9)
        cmds.setAttr(self.guide_face_loc+".translateX", 2.4)
        cmds.setAttr(self.guide_face_loc+".translateY", 1.5)
        cmds.setAttr(self.guide_face_loc+".translateZ", 0.7)
        for facial_loc in [self.guide_brow_loc, self.guide_eyelid_loc, self.guide_mouth_loc, self.guide_lips_loc, self.guide_sneer_loc, self.guide_grimace_loc, self.guide_face_loc, self.guide_deformer_center_loc]:
            cmds.setAttr(facial_loc+".visibility", 0)
        # parenting
        cmds.parent(self.line_neck_0, self.guide_base, relative=True)
        cmds.parent(self.guide_end_loc, self.guide_chew_loc, relative=True)
        cmds.parent(self.guide_neck_loc, self.guide_base)
        cmds.parent(self.guide_head_loc, self.guide_neck_loc)
        cmds.parent(self.guide_upper_jaw_loc, self.guide_jaw_loc, self.guide_head_loc)
        cmds.parent(self.guide_chin_loc, self.guide_jaw_loc)
        cmds.parent(self.guide_chew_loc, self.guide_lower_lip_loc, self.guide_chin_loc)
        cmds.parent(self.guide_left_corner_lip_loc, self.guide_jaw_loc)
        cmds.parent(self.guide_right_corner_lip_loc, self.guide_jaw_loc)
        cmds.parent(self.guide_upper_lip_loc, self.guide_upper_head_loc, self.guide_lips_loc, self.guide_upper_jaw_loc)
        cmds.parent(self.guide_brow_loc, self.guide_eyelid_loc, self.guide_upper_head_loc)
        cmds.parent(self.guide_mouth_loc, self.guide_left_corner_lip_loc)
        cmds.parent(self.guide_sneer_loc, self.guide_upper_lip_loc)
        cmds.parent(self.guide_grimace_loc, self.guide_lower_lip_loc)
        cmds.parent(self.guide_face_loc, self.guide_head_loc)
        cmds.parent(self.guide_deformer_center_loc, self.guide_upper_head_loc)
        cmds.parent(self.guide_deformer_radius_loc, self.guide_deformer_center_loc)
        # edit
        self.ar.ctrls.direct_connect(self.guide_neck_loc, self.line_neck_0, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.direct_connect(self.guide_head_loc, self.line_head, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.direct_connect(self.guide_upper_jaw_loc, self.line_upper_jaw, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.direct_connect(self.guide_upper_head_loc, self.line_upper_head, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.direct_connect(self.guide_jaw_loc, self.line_jaw, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.direct_connect(self.guide_chin_loc, self.line_chin, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.direct_connect(self.guide_chew_loc, self.line_chew, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.direct_connect(self.guide_upper_lip_loc, self.line_upper_lip, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.direct_connect(self.guide_lower_lip_loc, self.line_lower_lip, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.direct_connect(self.guide_end_loc, self.line_end, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ar.ctrls.direct_connect(self.guide_left_corner_lip_loc, self.line_left_lip, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        cmds.transformLimits(self.guide_end_loc, tz=(0.01, 1), etz=(True, False))
        self.ar.ctrls.set_lock_hide([self.guide_end_loc], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])


    def create_guide_deformer_cube(self):
        # deformer cube setup
        def_cubes = cmds.polyCube(name=self.name_guide+"_DeformerCube_Geo", constructionHistory=True)
        self.deformer_cube = def_cubes[0]
        def_poly_cube = cmds.rename(def_cubes[1], self.name_guide+"_DeformerCube_PCu")
        cmds.setAttr(self.deformer_cube+".translateY", 4.0)
        cmds.setAttr(self.deformer_cube+".translateZ", 0.5)
        cmds.parent(self.deformer_cube, self.guide_deformer_center_loc)
        def_radius_md = cmds.createNode("multiplyDivide", name=self.name_guide+"_DeformerCube_MD")
        for axis, attr in zip(self.ar.data.axes, ["width", "height", "depth"]):
            cmds.setAttr(def_radius_md+".input2"+axis, 2)
            cmds.connectAttr(self.guide_deformer_radius_loc+".translate"+axis, def_radius_md+".input1"+axis)
            cmds.connectAttr(def_radius_md+".output"+axis, def_poly_cube+"."+attr)
        cmds.setAttr(self.deformer_cube+".template", 1)
        self.ar.utils.add_attr_to_items([self.deformer_cube], self.ar.skin.ignore_skinning_attr)
        


    def change_joint_number(self, inputted, *args):
        """ Edit the number of joints in the guide.
        """
        self.current_joint_number = cmds.getAttr(self.guide_base+".nJoints")
        joint_number = self.parse_inputted_joint_number(inputted)
        if joint_number and joint_number != self.current_joint_number:
            self.ar.opt.check_use_default_render_layer()
            if joint_number > self.current_joint_number:
                for n in range(self.current_joint_number+1, joint_number+1):
                    self.guide_neck_loc = self.ar.ctrls.create_joint_locator(ctrl_name=self.name_guide+"_Neck"+str(n-1), r=0.2, d=1, rot=(-90, 90, 0), guide=True)
                    cmds.setAttr(self.guide_neck_loc+".nJoint", n)
                    cmds.parent(self.guide_neck_loc, self.name_guide+"_Neck"+str(n-2), relative=True)
                    self.line = cmds.joint(name=self.name_guide+"_JGuideNeck"+str(n-1), radius=0.001)
                    cmds.setAttr(self.line+".template", 1)
                    cmds.parent(self.line, self.name_guide+"_JGuideNeck"+str(n-2), relative=True)
                    cmds.parentConstraint(self.guide_neck_loc, self.line, maintainOffset=False, name=self.line+"_PaC")
                    cmds.scaleConstraint(self.guide_neck_loc, self.line, maintainOffset=False, name=self.line+"_ScC")
                    self.add_node_to_guide_net([self.guide_neck_loc], ["Neck"+str(n-1)])
            elif joint_number < self.current_joint_number:
                self.guide_neck_loc = self.reduce_joint_number(joint_number, "Neck", "Neck", 0, 0)
            # get the length of the neck to position segments.
            dist = self.ar.utils.create_dist_between(self.name_guide+"_Neck0", self.name_guide+"_Head")[0]
            # translateY to input on each create_curve_locator
            dit_bet = dist/joint_number
            for n in range(1, joint_number):
                # translate the locators to the calculated position:
                cmds.setAttr(self.name_guide+"_Neck"+str(n)+".translateY", dit_bet)
            cmds.setAttr(self.guide_base+".nJoints", joint_number)
            self.current_joint_number = joint_number
            self.create_mirror_preview()
        cmds.select(self.guide_base)


    def change_deformer(self, value, *args):
        """ Set the attribute value for deformer and show or hide guide locators.
        """
        cmds.setAttr(self.guide_base+".deformer", value)
        cmds.setAttr(self.guide_deformer_center_loc+".visibility", value)


    def change_facial(self, value, *args):
        """ Enable or disable the Facial Controls UI.
            Set the main facial value as well.
        """
        collapsed = False
        if not value:
            collapsed = True
        if self.ar.data.ui_state:
            cmds.frameLayout("edit_guide_facial_fl", edit=True, collapse=collapsed, enable=value)
        cmds.setAttr(self.guide_base+".facial", value)
        for item in list(self.facial_loc_data.keys()):
            cmds.setAttr(self.facial_loc_data[item]+".visibility", False)
            if value:
                cmds.setAttr(self.facial_loc_data[item]+".visibility", cmds.getAttr(self.guide_base+"."+item))


    def change_facial_element(self, attr, value, *args):
        """ Activate or disactivate the facial elements by the given value.
        """
        cmds.setAttr(self.guide_base+"."+attr, value)
        cmds.setAttr(self.facial_loc_data[attr]+".visibility", value)


    def set_change_facial(self, value, *args):
        """ Set display of facial controllers.
        """
        if not value:
            self.change_facial(value)
        if self.ar.data.ui_state:
            self.ar.guide_ui.set_head_facial_ui(value)
            

    def change_jaw(self, value, *args):
        """ Change creation for Jaw.
            Affects: Chin, Chew, UpperLip, LowerLip, LipsSide, UpperJaw, LowerJaw.
        """
        if self.ar.data.ui_state:
            self.ar.guide_ui.set_head_jaw_ui(value)
        cmds.setAttr(self.guide_jaw_loc+".visibility", value)
        cmds.setAttr(self.line_head+".visibility", value)
        self.change_lips(value)
        self.change_chin(value)
        cmds.setAttr(self.guide_base+"."+JAW, value)
        self.set_change_facial(value)
        self.ar.utils.parent_guide_children_to(self.guide_jaw_loc, self.guide_head_loc)
        cmds.select(self.guide_base)
        

    def change_chin(self, value, *args):
        """ Change creation for Chin.
            Affects: Chew, LoweLip.
        """
        cmds.setAttr(self.guide_chin_loc+".visibility", value)
        cmds.setAttr(self.guide_base+"."+CHIN, value)
        self.set_change_facial(value)
        self.ar.utils.parent_guide_children_to(self.guide_chin_loc, self.guide_jaw_loc)
        cmds.select(self.guide_base)
        

    def change_lips(self, value, *args):
        """ Change creation for Lips.
            Affects: UpperLip, LowerLip, LipsSide
        """
        cmds.setAttr(self.guide_left_corner_lip_loc+".visibility", value)
        cmds.setAttr(self.guide_right_corner_lip_loc+".visibility", value)
        cmds.setAttr(self.guide_upper_lip_loc+".visibility", value)
        cmds.setAttr(self.guide_lower_lip_loc+".visibility", value)
        cmds.setAttr(self.line_jaw+".visibility", value)
        cmds.setAttr(self.line_upper_jaw+".visibility", value)
        cmds.setAttr(self.guide_base+"."+LIPS, value)
        self.set_change_facial(value)
        self.ar.utils.parent_guide_children_to(self.guide_left_corner_lip_loc, self.guide_head_loc)
        self.ar.utils.parent_guide_children_to(self.guide_right_corner_lip_loc, self.guide_head_loc)
        self.ar.utils.parent_guide_children_to(self.guide_upper_lip_loc, self.guide_head_loc)
        self.ar.utils.parent_guide_children_to(self.guide_lower_lip_loc, self.guide_jaw_loc)
        cmds.select(self.guide_base)
        

    def change_upper_head(self, value, *args):
        """ Change creation for UpperHead.
        """
        if self.ar.data.ui_state:
            self.ar.guide_ui.set_head_upper_head_ui(value)
        cmds.setAttr(self.guide_upper_jaw_loc+".visibility", value)
        cmds.setAttr(self.line_upper_jaw+".visibility", value)
        cmds.setAttr(self.guide_base+"."+UPPERHEAD, value)
        self.set_change_facial(value)
        if not value:
            self.change_deformer(value)
        self.ar.utils.parent_guide_children_to(self.guide_upper_jaw_loc, self.guide_head_loc)
        self.ar.utils.parent_guide_children_to(self.guide_upper_head_loc, self.guide_head_loc)
        cmds.select(self.guide_base)
        

    def setup_jaw_move(self, attr_ctrl, open_close_id, positive_rotation=True, axis="Y", int_attr_id="c049_intensity", invert_rot=False, create_output=False, fix_value=0.01):
        """ Create the setup for move jaw group when jaw control rotates for open or close adjustements.
            Depends on axis and rotation done.
        """
        # declaring naming:
        base_attr = self.ar.utils.extract_suffix(attr_ctrl)
        driven_grp = base_attr+"_"+self.ar.data.lang[open_close_id]+self.ar.data.lang['c034_move']+"_Grp"
        # attribute names:
        int_attr = self.ar.data.lang[open_close_id].lower()+self.ar.data.lang[int_attr_id].capitalize()+axis
        start_rot_attr = self.ar.data.lang[open_close_id].lower()+self.ar.data.lang['c110_start'].capitalize()+"Rotation"
        unit_fix_attr = self.ar.data.lang[open_close_id].lower()+"UnitFix"+axis
        calib_attr = self.ar.data.lang[open_close_id].lower()+self.ar.data.lang['c111_calibrate']+axis
        calib_output_attr = self.ar.data.lang[open_close_id].lower()+self.ar.data.lang['c111_calibrate']+self.ar.data.lang['c112_output']
        output_attr = self.ar.data.lang[open_close_id].lower()+self.ar.data.lang['c112_output']
        # utility node names:
        calib_md = base_attr+self.ar.data.lang[open_close_id]+"_"+self.ar.data.lang[int_attr_id].capitalize()+"_"+self.ar.data.lang['c111_calibrate']+"_"+axis+"_MD"
        unit_fix_md = base_attr+self.ar.data.lang[open_close_id]+"_UnitFix_"+axis+"_MD"
        int_md = base_attr+self.ar.data.lang[open_close_id]+"_"+self.ar.data.lang[int_attr_id].capitalize()+"_"+axis+"_MD"
        start_md = base_attr+self.ar.data.lang[open_close_id]+"_Start_"+axis+"_MD"
        int_pma = base_attr+self.ar.data.lang[open_close_id]+"_"+self.ar.data.lang[int_attr_id].capitalize()+"_Start_"+axis+"_PMA"
        int_cond = base_attr+self.ar.data.lang[open_close_id]+"_"+self.ar.data.lang[int_attr_id].capitalize()+"_"+axis+"_Cnd"
        output_rmv = base_attr+self.ar.data.lang[open_close_id]+"_"+self.ar.data.lang['c112_output']+"_RmV"
        
        # create move group and its attributes:
        if not cmds.objExists(driven_grp):
            driven_grp = cmds.group(attr_ctrl, name=driven_grp)
            self.ar.utils.add_attr_to_items([driven_grp], self.ar.utils.ignore_transform_io_attr)
        if not start_rot_attr in cmds.listAttr(self.jaw_ctrl):
            if positive_rotation: #open
                cmds.addAttr(self.jaw_ctrl, longName=start_rot_attr, attributeType='float', defaultValue=5, minValue=0, keyable=True)
            else: #close
                cmds.addAttr(self.jaw_ctrl, longName=start_rot_attr, attributeType='float', defaultValue=0, maxValue=0, keyable=True)
            cmds.setAttr(self.jaw_ctrl+"."+start_rot_attr, keyable=False, channelBox=True)
        if not unit_fix_attr in cmds.listAttr(attr_ctrl):
            if positive_rotation: #open
                cmds.addAttr(attr_ctrl, longName=unit_fix_attr, attributeType='float', defaultValue=fix_value)
            else:
                cmds.addAttr(attr_ctrl, longName=unit_fix_attr, attributeType='float', defaultValue=-fix_value)
            cmds.setAttr(attr_ctrl+"."+unit_fix_attr, lock=True)
        if not calib_attr in cmds.listAttr(attr_ctrl):
            cmds.addAttr(attr_ctrl, longName=calib_attr, attributeType='float', defaultValue=1)
        if not int_attr in cmds.listAttr(attr_ctrl):
            cmds.addAttr(attr_ctrl, longName=int_attr, attributeType='float', defaultValue=1, keyable=True)
            cmds.setAttr(attr_ctrl+"."+int_attr, keyable=False, channelBox=True)
        
        # create utility nodes:
        jaw_calibrate_md = cmds.createNode('multiplyDivide', name=calib_md)
        jaw_unit_fix_md = cmds.createNode('multiplyDivide', name=unit_fix_md)
        jaw_int_md = cmds.createNode('multiplyDivide', name=int_md)
        jaw_start_md = cmds.createNode('multiplyDivide', name=start_md)
        jaw_int_pma = cmds.createNode('plusMinusAverage', name=int_pma)
        jaw_int_cnd = cmds.createNode('condition', name=int_cond)
        self.to_ids.extend([jaw_calibrate_md, jaw_unit_fix_md, jaw_int_md, jaw_start_md, jaw_int_pma, jaw_int_cnd])
        
        # set attributes to move jaw group when open or close:
        cmds.setAttr(jaw_int_pma+".operation", 2) #substract
        cmds.setAttr(jaw_int_cnd+".operation", 4) #less than
        if positive_rotation: #open
            cmds.setAttr(jaw_int_cnd+".operation", 2) #greater than
        cmds.setAttr(jaw_int_cnd+".colorIfFalseR", 0)
        
        # connect utility nodes:
        cmds.connectAttr(self.jaw_ctrl+".rotateX", jaw_int_md+".input1"+axis, force=True)
        cmds.connectAttr(self.jaw_ctrl+".rotateX", jaw_int_cnd+".firstTerm", force=True)
        cmds.connectAttr(self.jaw_ctrl+"."+start_rot_attr, jaw_start_md+".input2"+axis, force=True)
        cmds.connectAttr(self.jaw_ctrl+"."+start_rot_attr, jaw_int_cnd+".secondTerm", force=True)
        cmds.connectAttr(attr_ctrl+"."+int_attr, jaw_calibrate_md+".input1"+axis, force=True)
        cmds.connectAttr(attr_ctrl+"."+calib_attr, jaw_calibrate_md+".input2"+axis, force=True)
        cmds.connectAttr(attr_ctrl+"."+unit_fix_attr, jaw_unit_fix_md+".input2"+axis, force=True)
        cmds.connectAttr(jaw_calibrate_md+".output"+axis, jaw_unit_fix_md+".input1"+axis, force=True)
        cmds.connectAttr(jaw_unit_fix_md+".output"+axis, jaw_int_md+".input2"+axis, force=True)
        cmds.connectAttr(jaw_unit_fix_md+".output"+axis, jaw_start_md+".input1"+axis, force=True)
        cmds.connectAttr(jaw_int_md+".output"+axis, jaw_int_pma+".input1D[0]", force=True)
        cmds.connectAttr(jaw_start_md+".output"+axis, jaw_int_pma+".input1D[1]", force=True)
        cmds.connectAttr(jaw_int_pma+".output1D", jaw_int_cnd+".colorIfTrueR", force=True)
        cmds.connectAttr(jaw_int_cnd+".outColorR", driven_grp+".translate"+axis, force=True)
        
        # invert rotation for lower lip exception:
        if invert_rot:
            invert_rot_pma = base_attr+self.ar.data.lang[open_close_id]+self.ar.data.lang[int_attr_id].capitalize()+"_"+axis+"_InvertRot_PMA"
            invert_rot_md = base_attr+self.ar.data.lang[open_close_id]+self.ar.data.lang[int_attr_id].capitalize()+"_"+axis+"_InvertRot_MD"
            invert_rot_pma = cmds.createNode('plusMinusAverage', name=invert_rot_pma)
            invert_rot_md = cmds.createNode('multiplyDivide', name=invert_rot_md)
            self.to_ids.extend([invert_rot_pma, invert_rot_md])
            cmds.setAttr(invert_rot_pma+".operation", 2) #substract
            cmds.setAttr(invert_rot_md+".input2X", -1)
            cmds.setAttr(jaw_int_cnd+".colorIfFalseG", 0)
            cmds.connectAttr(self.jaw_ctrl+".rotateX", invert_rot_pma+".input1D[0]", force=True)
            cmds.connectAttr(self.jaw_ctrl+"."+start_rot_attr, invert_rot_pma+".input1D[1]", force=True)
            cmds.connectAttr(invert_rot_pma+".output1D", jaw_int_cnd+".colorIfTrueG", force=True)
            cmds.connectAttr(jaw_int_cnd+".outColorG", invert_rot_md+".input1X", force=True)
            cmds.connectAttr(invert_rot_md+".outputX", driven_grp+".rotateX", force=True)
            
        # output to a blendShape target value setup:
        if create_output:
            if not output_attr in cmds.listAttr(self.jaw_ctrl):
                cmds.addAttr(self.jaw_ctrl, longName=calib_output_attr, attributeType='float', defaultValue=1)
                cmds.addAttr(self.jaw_ctrl, longName=output_attr, attributeType='float', defaultValue=1)
            jaw_output_rmv = cmds.createNode('remapValue', name=output_rmv)
            self.to_ids.append(jaw_output_rmv)
            cmds.connectAttr(self.jaw_ctrl+".rotateX", jaw_output_rmv+".inputValue", force=True)
            cmds.connectAttr(self.jaw_ctrl+"."+calib_output_attr, jaw_output_rmv+".inputMax", force=True)
            cmds.connectAttr(jaw_output_rmv+".outValue", self.jaw_ctrl+"."+output_attr, force=True)
            cmds.setAttr(self.jaw_ctrl+"."+output_attr, lock=True)

    
    def get_calibrate_presets(self, s):
        """ Returns the calibration preset and invert lists for neck and head joints.
        """
        inverts = [[], [], ["invertTX", "invertRY", "invertRZ"], [], []]
        presets = [{}, {"calibrateTX":1}, {"calibrateTX":1}, {"calibrateTZ":1}, {"calibrateTZ":-1}]
        if s == 1:
            if self.flip:
                inverts = [[], ["invertTX"], ["invertTX"], ["invertTZ"], ["invertTZ"]]
        return presets, inverts


    def get_neck_auto_rotate(self, n):
        if self.n_joints < 7:
            return 0.15*(n+1)
        else:
            if n == 0:
                return (2**(1/self.n_joints))-1
            else:
                return (2**(n/self.n_joints))-(1-(1/self.n_joints))

    
    def declare_guide_elements(self, middle, side="", guide="", *args):
        """ Just redeclare main locators and dictionary to use it again after reloading code.
        """
        self.base            = side+middle+guide+"_Base"
        self.guide_head_loc       = side+middle+guide+"_Head"
        self.guide_upper_jaw_loc   = side+middle+guide+"_UpperJaw"
        self.guide_upper_head_loc  = side+middle+guide+"_UpperHead"
        self.guide_jaw_loc        = side+middle+guide+"_Jaw"
        self.guide_chin_loc       = side+middle+guide+"_Chin"
        self.guide_chew_loc       = side+middle+guide+"_Chew"
        self.guide_left_corner_lip_loc = side+middle+guide+"_LCornerLip"
        self.guide_right_corner_lip_loc = side+middle+guide+"_RCornerLip"
        self.guide_upper_lip_loc   = side+middle+guide+"_UpperLip"
        self.guide_lower_lip_loc   = side+middle+guide+"_LowerLip"
        self.guide_end_loc      = side+middle+guide+"_JointEnd"
        self.guide_radius     = side+middle+guide+"_Base_RadiusCtrl"
        self.guide_brow_loc       = side+middle+guide+"_Brow"
        self.guide_eyelid_loc     = side+middle+guide+"_Eyelid"
        self.guide_mouth_loc      = side+middle+guide+"_Mouth"
        self.guide_lips_loc       = side+middle+guide+"_Lips"
        self.guide_sneer_loc      = side+middle+guide+"_Sneer"
        self.guide_grimace_loc    = side+middle+guide+"_Grimace"
        self.guide_face_loc       = side+middle+guide+"_Face"
        self.facial_loc_data = {
                                self.facial_attributes[0] : self.guide_brow_loc,
                                self.facial_attributes[1] : self.guide_eyelid_loc,
                                self.facial_attributes[2] : self.guide_mouth_loc,
                                self.facial_attributes[3] : self.guide_lips_loc,
                                self.facial_attributes[4] : self.guide_sneer_loc,
                                self.facial_attributes[5] : self.guide_grimace_loc,
                                self.facial_attributes[6] : self.guide_face_loc
                            }
        self.guide_deformer_center_loc = side+middle+guide+"_DeformerCenter"
        self.guide_deformer_radius_loc = side+middle+guide+"_DeformerRadius"
        self.deformer_cube = side+middle+guide+"_DeformerCube_Geo"
        self.line_jaw = side+middle+guide+"_JGuideJaw"
        self.line_head = side+middle+guide+"_JGuideHead"
        self.line_upper_jaw = side+middle+guide+"_JGuideUpperJaw"
        

    def rig_me(self, *args):
        standard.BaseStandard.rig_me(self)
        # verify if the guide exists:
        if cmds.objExists(self.guide_base):
            style = cmds.getAttr(self.guide_base+".style")
            # declare lists to store names and attributes:
            self.world_refs, self.upper_ctrls, self.upper_jaw_ctrls, self.facial_ctrl_grps = [], [], [], []
            self.ctrls, self.left_ctrls, self.right_ctrls = [], [], []
            # run for all sides
            for s, side in enumerate(self.sides):
                neck_locs, neck_ctrls, neck_joints = [], [], []
                # redeclaring variables:
                self.declare_guide_elements(self.number_name, side, "_Guide")
                
                # generating naming:
                head_joint_name = side+self.number_name+"_01_"+self.ar.data.lang['c024_head']+"_Jnt"
                if self.articulation:
                    head_joint_name = side+self.number_name+"_02_"+self.ar.data.lang['c024_head']+"_Jnt"
                upper_jaw_joint_name = side+self.number_name+"_"+self.ar.data.lang['c044_upper']+self.ar.data.lang['c025_jaw']+"_Jnt"
                upper_head_joint_name = side+self.number_name+"_"+self.ar.data.lang['c044_upper']+self.ar.data.lang['c024_head']+"_Jnt"
                upper_end_joint_name = side+self.number_name+"_"+self.ar.data.lang['c044_upper']+self.ar.data.lang['c024_head']+"_"+self.ar.data.joint_end_attr
                jaw_joint_name = side+self.number_name+"_"+self.ar.data.lang['c025_jaw']+"_Jnt"
                chin_joint_name = side+self.number_name+"_"+self.ar.data.lang['c026_chin']+"_Jnt"
                chew_joint_name = side+self.number_name+"_"+self.ar.data.lang['c048_chew']+"_Jnt"
                end_joint_name = side+self.number_name+"_"+self.ar.data.joint_end_attr
                left_corner_lip_joint_name = side+self.number_name+"_"+self.ar.data.lang['p002_left']+"_"+self.ar.data.lang['c043_corner']+self.ar.data.lang['c039_lip']+"_Jnt"
                right_corner_lip_joint_name = side+self.number_name+"_"+self.ar.data.lang['p003_right']+"_"+self.ar.data.lang['c043_corner']+self.ar.data.lang['c039_lip']+"_Jnt"
                upper_lip_joint_name = side+self.number_name+"_"+self.ar.data.lang['c044_upper']+self.ar.data.lang['c039_lip']+"_Jnt"
                lower_lip_joint_name = side+self.number_name+"_"+self.ar.data.lang['c045_lower']+self.ar.data.lang['c039_lip']+"_Jnt"
                neck_ctrl_base_name = side+self.number_name+"_"+self.ar.data.lang['c023_neck']
                head_ctrl_name = side+self.number_name+"_"+self.ar.data.lang['c024_head']+"_Ctrl"
                head_sub_ctrl_name = side+self.number_name+"_"+self.ar.data.lang['c024_head']+"_Sub_Ctrl"
                upper_jaw_ctrl_name = side+self.number_name+"_"+self.ar.data.lang['c044_upper']+self.ar.data.lang['c025_jaw']+"_Ctrl"
                upper_head_ctrl_name = side+self.number_name+"_"+self.ar.data.lang['c044_upper']+self.ar.data.lang['c024_head']+"_Ctrl"
                jaw_ctrl_name  = side+self.number_name+"_"+self.ar.data.lang['c025_jaw']+"_Ctrl"
                chin_ctrl_name = side+self.number_name+"_"+self.ar.data.lang['c026_chin']+"_Ctrl"
                chew_ctrl_name = side+self.number_name+"_"+self.ar.data.lang['c048_chew']+"_Ctrl"
                left_corner_lip_ctrl_name = self.ar.data.lang['p002_left']+"_"+self.number_name+"_"+self.ar.data.lang['c043_corner']+self.ar.data.lang['c039_lip']+"_Ctrl"
                right_corner_lip_ctrl_name = self.ar.data.lang['p003_right']+"_"+self.number_name+"_"+self.ar.data.lang['c043_corner']+self.ar.data.lang['c039_lip']+"_Ctrl"
                upper_lip_ctrl_name = side+self.number_name+"_"+self.ar.data.lang['c044_upper']+self.ar.data.lang['c039_lip']+"_Ctrl"
                lower_lip_ctrl_name = side+self.number_name+"_"+self.ar.data.lang['c045_lower']+self.ar.data.lang['c039_lip']+"_Ctrl"
                self.calibrate_name = self.ar.data.lang["c111_calibrate"].lower()
                
                # connect facial controllers to blendShape node or joints based tweakers:
                self.facial_connect_type = self.ar.data.facial_connect_types[cmds.getAttr(self.guide_base+".connectUserType")]

                # get the number of joints to be created for the neck:
                self.n_joints = cmds.getAttr(self.base+".nJoints")

                # get items to be created
                has_jaw = cmds.getAttr(self.guide_base+"."+JAW)
                has_chin = cmds.getAttr(self.guide_base+"."+CHIN)
                has_lips = cmds.getAttr(self.guide_base+"."+LIPS)
                has_upper_head = cmds.getAttr(self.guide_base+"."+UPPERHEAD)

                # creating controllers:
                for n in range(0, self.n_joints):
                    neck_ctrl = self.ar.ctrls.create_controller("id_022_HeadNeck", ctrl_name=neck_ctrl_base_name+"_"+str(n).zfill(2)+"_Ctrl", r=(self.radius/((n*0.2)+1)), d=self.curve_degree, dir="-Z", guide_source=self.name_guide+"_Neck"+str(n), parent_tag=self.get_parent_to_tag(neck_ctrls))
                    if n > 0:
                        cmds.parent(neck_ctrl, neck_ctrls[-1])
                    neck_ctrls.append(neck_ctrl)
                head_ctrl = self.ar.ctrls.create_controller("id_023_HeadHead", ctrl_name=head_ctrl_name, r=(self.radius * 2.5), d=self.curve_degree, guide_source=self.name_guide+"_Head", parent_tag=neck_ctrls[-1])
                self.head_sub_ctrl = self.ar.ctrls.create_controller("id_093_HeadSub", ctrl_name=head_sub_ctrl_name, r=(self.radius * 2.2), d=self.curve_degree, guide_source=self.name_guide+"_Head", parent_tag=head_ctrl)
                to_flip_items = [head_ctrl, self.head_sub_ctrl]
                # hiding visibility attributes:
                self.ar.ctrls.set_lock_hide([head_ctrl, self.head_sub_ctrl], ['v'], l=False)
                self.ar.ctrls.set_lock_hide(neck_ctrls, ['v'], l=False)

                # creating joints:
                cmds.select(clear=True)
                for n in range(0, self.n_joints):
                    # neck segments:
                    neck_locs.append(side+self.number_name+"_Guide_Neck"+str(n))
                    neck_joints.append(cmds.joint(name=neck_ctrl_base_name+"_"+str(n).zfill(2)+"_Jnt", scaleCompensate=False))
                head_joint = cmds.joint(name=head_joint_name, scaleCompensate=False)
                dpar_joints = [head_joint]
                if has_upper_head:
                    upper_jaw_joint = cmds.joint(name=upper_jaw_joint_name, scaleCompensate=False)
                    upper_head_joint = cmds.joint(name=upper_head_joint_name, scaleCompensate=False)
                    upper_end_joint = cmds.joint(name=upper_end_joint_name, scaleCompensate=False, radius=0.5)
                    self.ar.utils.set_joint_label(upper_jaw_joint, s+self.joint_label_add, 18, self.number_name+"_"+self.ar.data.lang['c044_upper']+self.ar.data.lang['c025_jaw'])
                    self.ar.utils.set_joint_label(upper_head_joint, s+self.joint_label_add, 18, self.number_name+"_"+self.ar.data.lang['c044_upper']+self.ar.data.lang['c024_head'])
                    cmds.setAttr(upper_end_joint+".translateY", 0.3*self.radius)
                    dpar_joints.extend([upper_jaw_joint, upper_head_joint])
                    upper_jaw_ctrl = self.ar.ctrls.create_controller("id_069_HeadUpperJaw", ctrl_name=upper_jaw_ctrl_name, r=self.radius, d=self.curve_degree, head_def=1, guide_source=self.name_guide+"_UpperJaw", parent_tag=self.head_sub_ctrl)
                    upper_head_ctrl = self.ar.ctrls.create_controller("id_081_HeadUpperHead", ctrl_name=upper_head_ctrl_name, r=self.radius, d=self.curve_degree, head_def=1, guide_source=self.name_guide+"_UpperHead", parent_tag=upper_jaw_ctrl)
                    to_flip_items.extend([upper_jaw_ctrl, upper_head_ctrl])
                    self.ar.ctrls.set_lock_hide([upper_jaw_ctrl, upper_head_ctrl], ['v'], l=False)
                    cmds.select(head_joint)
                if has_jaw:
                    jaw_joint = cmds.joint(name=jaw_joint_name, scaleCompensate=False)
                    self.ar.utils.set_joint_label(jaw_joint, s+self.joint_label_add, 18, self.number_name+"_"+self.ar.data.lang['c025_jaw'])
                    dpar_joints.extend([jaw_joint])
                    self.jaw_ctrl = self.ar.ctrls.create_controller("id_024_HeadJaw", ctrl_name=jaw_ctrl_name, r=(self.radius *0.5), d=self.curve_degree, head_def=3, guide_source=self.name_guide+"_Jaw", parent_tag=self.head_sub_ctrl)
                    to_flip_items.extend([self.jaw_ctrl])
                    self.ar.ctrls.set_lock_hide([self.jaw_ctrl], ['v'], l=False)
                    if has_chin:
                        cmds.select(jaw_joint)
                        chin_joint = cmds.joint(name=chin_joint_name, scaleCompensate=False)
                        chew_joint = cmds.joint(name=chew_joint_name, scaleCompensate=False)
                        end_joint  = cmds.joint(name=end_joint_name, scaleCompensate=False, radius=0.5)
                        self.ar.utils.set_joint_label(chin_joint, s+self.joint_label_add, 18, self.number_name+"_"+self.ar.data.lang['c026_chin'])
                        self.ar.utils.set_joint_label(chew_joint, s+self.joint_label_add, 18, self.number_name+"_"+self.ar.data.lang['c048_chew'])
                        dpar_joints.extend([chin_joint, chew_joint])
                        chin_ctrl = self.ar.ctrls.create_controller("id_025_HeadChin", ctrl_name=chin_ctrl_name, r=(self.radius * 0.13), d=self.curve_degree, head_def=3, guide_source=self.name_guide+"_Chin", parent_tag=self.jaw_ctrl)
                        chew_ctrl = self.ar.ctrls.create_controller("id_026_HeadChew", ctrl_name=chew_ctrl_name, r=(self.radius * 0.08), d=self.curve_degree, head_def=3, guide_source=self.name_guide+"_Chew", parent_tag=chin_ctrl)
                        to_flip_items.extend([chin_ctrl, chew_ctrl])
                        self.ar.ctrls.set_lock_hide([chin_ctrl, chew_ctrl], ['v'], l=False)
                    cmds.select(head_joint)
                if has_lips:
                    left_corner_lip_joint = cmds.joint(name=left_corner_lip_joint_name, scaleCompensate=False)
                    cmds.select(head_joint)
                    right_corner_lip_joint = cmds.joint(name=right_corner_lip_joint_name, scaleCompensate=False)
                    cmds.select(head_joint)
                    if has_upper_head:
                        cmds.select(upper_jaw_joint)
                    upper_lip_joint = cmds.joint(name=upper_lip_joint_name, scaleCompensate=False)
                    if has_chin:
                        cmds.select(chin_joint)
                    lower_lip_joint = cmds.joint(name=lower_lip_joint_name, scaleCompensate=False)
                    cmds.select(clear=True)
                    self.ar.utils.set_joint_label(left_corner_lip_joint, 1, 18, self.number_name+"_"+self.ar.data.lang['c039_lip'])
                    self.ar.utils.set_joint_label(right_corner_lip_joint, 2, 18, self.number_name+"_"+self.ar.data.lang['c039_lip'])
                    self.ar.utils.set_joint_label(upper_lip_joint, s+self.joint_label_add, 18, self.number_name+"_"+self.ar.data.lang['c044_upper']+self.ar.data.lang['c039_lip'])
                    self.ar.utils.set_joint_label(lower_lip_joint, s+self.joint_label_add, 18, self.number_name+"_"+self.ar.data.lang['c045_lower']+self.ar.data.lang['c039_lip'])
                    dpar_joints.extend([left_corner_lip_joint, right_corner_lip_joint, upper_lip_joint, lower_lip_joint])
                    left_corner_lip_ctrl = self.ar.ctrls.create_controller("id_027_HeadLipCorner", ctrl_name=left_corner_lip_ctrl_name, r=(self.radius * 0.1), d=self.curve_degree, head_def=3, guide_source=self.name_guide+"_LCornerLip", parent_tag=self.head_sub_ctrl)
                    right_corner_lip_ctrl = self.ar.ctrls.create_controller("id_027_HeadLipCorner", ctrl_name=right_corner_lip_ctrl_name, r=(self.radius * 0.1), d=self.curve_degree, head_def=3, guide_source=self.name_guide+"_RCornerLip", parent_tag=self.head_sub_ctrl)
                    upper_lip_ctrl = self.ar.ctrls.create_controller("id_072_HeadUpperLip", ctrl_name=upper_lip_ctrl_name, r=(self.radius * 0.1), d=self.curve_degree, head_def=3, guide_source=self.name_guide+"_UpperLip", parent_tag=self.head_sub_ctrl)
                    lower_lip_ctrl = self.ar.ctrls.create_controller("id_073_HeadLowerLip", ctrl_name=lower_lip_ctrl_name, r=(self.radius * 0.1), d=self.curve_degree, head_def=3, guide_source=self.name_guide+"_LowerLip", parent_tag=self.head_sub_ctrl)
                    to_flip_items.extend([left_corner_lip_ctrl, right_corner_lip_ctrl, upper_lip_ctrl, lower_lip_ctrl])
                    self.ar.ctrls.set_lock_hide([upper_lip_ctrl, lower_lip_ctrl], ['v'], l=False)
                dpar_joints.extend(neck_joints)
                for dpar_joint in dpar_joints:
                    cmds.addAttr(dpar_joint, longName='dpAR_joint', attributeType='float', keyable=False)
                # joint labelling:
                for n in range(0, self.n_joints):
                    self.ar.utils.set_joint_label(neck_joints[n], s+self.joint_label_add, 18, self.number_name+"_"+self.ar.data.lang['c023_neck']+"_"+str(n).zfill(2))
                self.ar.utils.set_joint_label(head_joint, s+self.joint_label_add, 18, self.number_name+"_"+self.ar.data.lang['c024_head'])
                
                # facial controls
                facial_ctrls = []
                if cmds.getAttr(self.guide_base+".facial"):
                    if cmds.getAttr(self.guide_base+".facialBrow"):
                        left_brow_ctrl, left_brow_ctrl_grp = self.create_facial_ctrl(side, self.ar.data.lang["p002_left"], self.ar.data.lang["c060_brow"], "id_046_FacialBrow", self.ar.data.facial_brow_targets, (0, 0, 0), False, False, True, True, True, True, False, "red", True, False)
                        right_brow_ctrl, right_brow_ctrl_grp = self.create_facial_ctrl(side, self.ar.data.lang["p003_right"], self.ar.data.lang["c060_brow"], "id_046_FacialBrow", self.ar.data.facial_brow_targets, (0, 0, 0), False, False, True, True, True, True, False, "blue", True, False)
                        facial_ctrls.extend([left_brow_ctrl, right_brow_ctrl])
                    if cmds.getAttr(self.guide_base+".facialEyelid"):
                        if self.facial_connect_type == self.ar.data.facial_connect_types[0]: #blendshapes
                            left_eyelid_ctrl, left_eyelid_ctrl_grp = self.create_facial_ctrl(side, self.ar.data.lang["p002_left"], self.ar.data.lang["c042_eyelid"], "id_047_FacialEyelid", self.ar.data.facial_eyelid_targets, (0, 0, 90), True, False, True, False, True, True, False, "red", True, False)
                            right_eyelid_ctrl, right_eyelid_ctrl_grp = self.create_facial_ctrl(side, self.ar.data.lang["p003_right"], self.ar.data.lang["c042_eyelid"], "id_047_FacialEyelid", self.ar.data.facial_eyelid_targets, (0, 0, 90), True, False, True, False, True, True, False, "blue", True, False)
                            facial_ctrls.extend([left_eyelid_ctrl, right_eyelid_ctrl])
                    if cmds.getAttr(self.guide_base+".facialMouth"):
                        left_mouth_ctrl, left_mouth_ctrl_grp = self.create_facial_ctrl(side, self.ar.data.lang["p002_left"], self.ar.data.lang["c061_mouth"], "id_048_FacialMouth", self.ar.data.facial_mouth_targets, (0, 0, -90), False, False, True, True, True, True, False, "red", True, True)
                        right_mouth_ctrl, right_mouth_ctrl_grp = self.create_facial_ctrl(side, self.ar.data.lang["p003_right"], self.ar.data.lang["c061_mouth"], "id_048_FacialMouth", self.ar.data.facial_mouth_targets, (0, 0, -90), False, False, True, True, True, True, False, "blue", True, True)
                        facial_ctrls.extend([left_mouth_ctrl, right_mouth_ctrl])
                    if cmds.getAttr(self.guide_base+".facialLips"):
                        lips_ctrl, lips_ctrl_grp = self.create_facial_ctrl(side, None, self.ar.data.lang["c062_lips"], "id_049_FacialLips", self.ar.data.facial_lips_targets, (0, 0, 0), False, False, False, True, True, True, False, "yellow", True, True)
                        facial_ctrls.append(lips_ctrl)
                    if cmds.getAttr(self.guide_base+".facialSneer"):
                        sneer_ctrl, sneer_ctrl_grp = self.create_facial_ctrl(side, None, self.ar.data.lang["c063_sneer"], "id_050_FacialSneer", self.ar.data.facial_sneer_targets, (0, 0, 0), False, False, False, True, True, True, False, "cyan", True, True, True, True)
                        facial_ctrls.append(sneer_ctrl)
                    if cmds.getAttr(self.guide_base+".facialGrimace"):
                        grimace_ctrl, grimace_ctrl_grp = self.create_facial_ctrl(side, None, self.ar.data.lang["c064_grimace"], "id_051_FacialGrimace", self.ar.data.facial_grimace_targets, (0, 0, 0), False, False, False, True, True, True, False, "cyan", True, True, True, True, True)
                        facial_ctrls.append(grimace_ctrl)
                    if cmds.getAttr(self.guide_base+".facialFace"):
                        face_ctrl, face_ctrl_grp = self.create_facial_ctrl(side, None, self.ar.data.lang["c065_face"], "id_052_FacialFace", self.ar.data.facial_face_targets, (0, 0, 0), True, True, True, True, True, True, True, "cyan", False, False)
                        facial_ctrls.append(face_ctrl)

                # colorize controllers
                if has_upper_head:
                    self.upper_ctrls.append(upper_head_ctrl)
                    self.upper_jaw_ctrls.append(upper_jaw_ctrl)
                else:
                    self.upper_ctrls.append(head_ctrl)
                    self.upper_jaw_ctrls.append(head_ctrl)
                if has_lips:
                    self.ctrls.append([upper_lip_ctrl, lower_lip_ctrl])
                    self.left_ctrls.append([left_corner_lip_ctrl])
                    self.right_ctrls.append([right_corner_lip_ctrl])
                self.inner_ctrls.append([self.head_sub_ctrl])
                self.ar.ctrls.set_sub_ctrl_display(head_ctrl, self.head_sub_ctrl, 1)

                # optimize control CV shapes:
                temp_head_cluster = cmds.cluster(head_ctrl, self.head_sub_ctrl)[1]
                cmds.setAttr(temp_head_cluster+".translateY", -0.5)
                cmds.delete([head_ctrl, self.head_sub_ctrl], constructionHistory=True)
                if has_jaw:
                    temp_jaw_cluster = cmds.cluster(self.jaw_ctrl)[1]
                    cmds.setAttr(temp_jaw_cluster+".translateY", -1*self.radius)
                    cmds.setAttr(temp_jaw_cluster+".translateZ", self.radius)
                    cmds.delete([self.jaw_ctrl], constructionHistory=True)
                if has_chin:
                    temp_chin_cluster = cmds.cluster(chin_ctrl)[1]
                    cmds.setAttr(temp_chin_cluster+".translateY", -0.75*self.radius)
                    cmds.setAttr(temp_chin_cluster+".translateZ", 1.45*self.radius)
                    cmds.setAttr(temp_chin_cluster+".rotateX", 22)
                    temp_chew_cluster = cmds.cluster(chew_ctrl)[1]
                    cmds.setAttr(temp_chew_cluster+".translateY", -0.75*self.radius)
                    cmds.setAttr(temp_chew_cluster+".translateZ", 1.47*self.radius)
                    cmds.setAttr(temp_chew_cluster+".rotateX", 22)
                    cmds.delete([chin_ctrl, chew_ctrl], constructionHistory=True)
                
                #Setup Axis Order
                if style == 2: #quadruped
                    for n in range(0, self.n_joints):
                        cmds.setAttr(neck_ctrls[n]+".rotateOrder", 1)
                    cmds.setAttr(head_ctrl+".rotateOrder", 1)
                    cmds.setAttr(self.head_sub_ctrl+".rotateOrder", 1)
                    if has_jaw:
                        cmds.setAttr(self.jaw_ctrl+".rotateOrder", 1)
                    if has_upper_head:
                        cmds.setAttr(upper_jaw_ctrl+".rotateOrder", 1)
                        cmds.setAttr(upper_head_ctrl+".rotateOrder", 1)
                else:
                    for n in range(0, self.n_joints):
                        cmds.setAttr(neck_ctrls[n]+".rotateOrder", 3)
                    cmds.setAttr(head_ctrl+".rotateOrder", 3)
                    cmds.setAttr(self.head_sub_ctrl+".rotateOrder", 3)
                    if has_upper_head:
                        cmds.setAttr(upper_jaw_ctrl+".rotateOrder", 3)
                        cmds.setAttr(upper_head_ctrl+".rotateOrder", 3)
                        if has_jaw:
                            cmds.setAttr(self.jaw_ctrl+".rotateOrder", 3)

                # creating the originedFrom attributes (in order to permit integrated parents in the future):
                for n in range(0, self.n_joints):
                    if n == 0:
                        self.ar.utils.set_origined_from_attr(neck_ctrls[0], self.base+";"+neck_locs[0]+";"+self.guide_radius)
                    else:
                        self.ar.utils.set_origined_from_attr(neck_ctrls[n], neck_locs[n])
                self.ar.utils.set_origined_from_attr(self.head_sub_ctrl, self.guide_head_loc)
                if has_upper_head:
                    self.ar.utils.set_origined_from_attr(upper_jaw_ctrl, self.guide_upper_jaw_loc)
                    self.ar.utils.set_origined_from_attr(upper_head_ctrl, self.guide_upper_head_loc)
                if has_lips:
                    self.ar.utils.set_origined_from_attr(upper_lip_ctrl, self.guide_upper_lip_loc)
                    self.ar.utils.set_origined_from_attr(lower_lip_ctrl, self.guide_lower_lip_loc)
                    self.ar.utils.set_origined_from_attr(left_corner_lip_ctrl, self.guide_left_corner_lip_loc)
                    self.ar.utils.set_origined_from_attr(right_corner_lip_ctrl, self.guide_right_corner_lip_loc)
                if has_jaw:
                    self.ar.utils.set_origined_from_attr(self.jaw_ctrl, self.guide_jaw_loc)
                if has_chin:
                    self.ar.utils.set_origined_from_attr(chin_ctrl, self.guide_chin_loc)
                    self.ar.utils.set_origined_from_attr(chew_ctrl, self.guide_chew_loc+";"+self.guide_end_loc)
                # facial origined from
                if cmds.getAttr(self.guide_base+".facial"):
                    if cmds.getAttr(self.guide_base+".facialBrow"):
                        if cmds.getAttr(self.guide_base+".facialEyelid"):
                            cmds.setAttr(upper_head_ctrl+".originedFrom", self.guide_upper_head_loc+";"+self.guide_brow_loc+";"+self.guide_eyelid_loc, type="string")
                        else:
                            cmds.setAttr(upper_head_ctrl+".originedFrom", self.guide_upper_head_loc+";"+self.guide_brow_loc, type="string")
                    elif cmds.getAttr(self.guide_base+".facialEyelid"):
                        cmds.setAttr(upper_head_ctrl+".originedFrom", self.guide_upper_head_loc+";"+self.guide_eyelid_loc, type="string")
                    if cmds.getAttr(self.guide_base+".facialMouth"):
                        if cmds.getAttr(self.guide_base+".facialLips"):
                            cmds.setAttr(upper_jaw_ctrl+".originedFrom", self.guide_upper_jaw_loc+";"+self.guide_mouth_loc+";"+self.guide_lips_loc, type="string")
                        else:
                            cmds.setAttr(upper_jaw_ctrl+".originedFrom", self.guide_upper_jaw_loc+";"+self.guide_mouth_loc, type="string")
                    elif cmds.getAttr(self.guide_base+".facialLips"):
                        cmds.setAttr(upper_jaw_ctrl+".originedFrom", self.guide_upper_jaw_loc+";"+self.guide_lips_loc, type="string")
                    if cmds.getAttr(self.guide_base+".facialSneer"):
                        cmds.setAttr(upper_lip_ctrl+".originedFrom", self.guide_upper_lip_loc+";"+self.guide_sneer_loc, type="string")
                    if cmds.getAttr(self.guide_base+".facialGrimace"):
                        cmds.setAttr(lower_lip_ctrl+".originedFrom", self.guide_lower_lip_loc+";"+self.guide_grimace_loc, type="string")
                    if cmds.getAttr(self.guide_base+".facialFace"):
                        cmds.setAttr(self.head_sub_ctrl+".originedFrom", self.guide_head_loc+";"+self.guide_face_loc, type="string")
                
                # temporary parentConstraints:
                for n in range(0, self.n_joints):
                    cmds.matchTransform(neck_ctrls[n], neck_locs[n], position=True, rotation=True)
                cmds.matchTransform(head_ctrl, self.guide_head_loc, position=True, rotation=True)
                cmds.matchTransform(self.head_sub_ctrl, self.guide_head_loc, position=True, rotation=True)
                if has_upper_head:
                    cmds.matchTransform(upper_jaw_ctrl, self.guide_upper_jaw_loc, position=True, rotation=True)
                    cmds.matchTransform(upper_head_ctrl, self.guide_upper_head_loc, position=True, rotation=True)
                if has_jaw:
                    cmds.matchTransform(self.jaw_ctrl, self.guide_jaw_loc, position=True, rotation=True)
                if has_chin:
                    cmds.matchTransform(chin_ctrl, self.guide_chin_loc, position=True, rotation=True)
                    cmds.matchTransform(chew_ctrl, self.guide_chew_loc, position=True, rotation=True)
                if has_lips:
                    cmds.matchTransform(left_corner_lip_ctrl, self.guide_left_corner_lip_loc, position=True, rotation=True)
                    cmds.matchTransform(right_corner_lip_ctrl, self.guide_right_corner_lip_loc, position=True, rotation=True)
                    cmds.matchTransform(upper_lip_ctrl, self.guide_upper_lip_loc, position=True, rotation=True)
                    cmds.matchTransform(lower_lip_ctrl, self.guide_lower_lip_loc, position=True, rotation=True)

                # edit the mirror shape to a good direction of controls:
                # fixing flip mirror:
                if s == 1:
                    if self.flip:
                        for item in to_flip_items:
                            cmds.setAttr(item+".scaleX", -1)
                            cmds.setAttr(item+".scaleY", -1)
                            cmds.setAttr(item+".scaleZ", -1)

                # create_zero_out controls:
                neck_ctrl_zeros = self.ar.utils.create_zero_out(neck_ctrls)
                head_zero = self.ar.utils.create_zero_out([head_ctrl])[0]
                head_sub_zero = self.ar.utils.create_zero_out([self.head_sub_ctrl])[0]
                # arrange controllers hierarchy
                cmds.parent(head_sub_zero, head_ctrl, absolute=True) #head_sub_ctrl
                if has_jaw:
                    jaw_zero = self.ar.utils.create_zero_out([self.jaw_ctrl])[0]
                    if has_chin:
                        chin_zero = self.ar.utils.create_zero_out([chin_ctrl])[0]
                        chew_zero = self.ar.utils.create_zero_out([chew_ctrl])[0]
                        cmds.parent(chin_zero, self.jaw_ctrl, absolute=True) #chin
                        cmds.parent(chew_zero, chin_ctrl, absolute=True) #chewCtrl
                    if has_lips:
                        upper_lip_zero = self.ar.utils.create_zero_out([upper_lip_ctrl])[0]
                        lower_lip_zero = self.ar.utils.create_zero_out([lower_lip_ctrl])[0]
                        left_corner_zero = self.ar.utils.create_zero_out([left_corner_lip_ctrl])[0]
                        right_corner_zero = self.ar.utils.create_zero_out([right_corner_lip_ctrl])[0]
                        left_lip_grp = cmds.group(left_corner_lip_ctrl, name=left_corner_lip_ctrl+"_Grp")
                        right_lip_grp = cmds.group(right_corner_lip_ctrl, name=right_corner_lip_ctrl+"_Grp")
                        if not self.flip:
                            cmds.setAttr(right_corner_zero+".scaleX", -1)
                        if has_chin:
                            cmds.parent(lower_lip_zero, chin_ctrl, absolute=True) #lowerLipCtrl
                        else:
                            cmds.parent(lower_lip_zero, self.jaw_ctrl, absolute=True) #lowerLipCtrl
                        if has_upper_head:
                            cmds.parent(upper_lip_zero, upper_jaw_ctrl, absolute=True) #upperLipCtrl
                        else:
                            cmds.parent(upper_lip_zero, self.head_sub_ctrl, absolute=True) #upperLipCtrl
                if has_upper_head:
                    upper_jaw_zero = self.ar.utils.create_zero_out([upper_jaw_ctrl])[0]
                    upper_head_zero = self.ar.utils.create_zero_out([upper_head_ctrl])[0]
                    cmds.parent(upper_head_zero, upper_jaw_ctrl, absolute=True) #upperHeadCtrl
                    cmds.parent(upper_jaw_zero, self.head_sub_ctrl, absolute=True) #upperJawCtrl

                # make joints be ride by controls:
                for n in range(0, self.n_joints):
                    cmds.parentConstraint(neck_ctrls[n], neck_joints[n], maintainOffset=False, name=neck_joints[n]+"_PaC")
                    cmds.scaleConstraint(neck_ctrls[n], neck_joints[n], maintainOffset=False, name=neck_joints[n]+"_ScC")
                cmds.parentConstraint(self.head_sub_ctrl, head_joint, maintainOffset=False, name=head_joint+"_PaC")
                cmds.scaleConstraint(self.head_sub_ctrl, head_joint, maintainOffset=True, name=head_joint+"_ScC")
                if has_upper_head:
                    cmds.parentConstraint(upper_jaw_ctrl, upper_jaw_joint, maintainOffset=False, name=upper_jaw_joint+"_PaC")
                    cmds.parentConstraint(upper_head_ctrl, upper_head_joint, maintainOffset=False, name=upper_head_joint+"_PaC")
                    cmds.scaleConstraint(upper_jaw_ctrl, upper_jaw_joint, maintainOffset=True, name=upper_jaw_joint+"_ScC")
                    cmds.scaleConstraint(upper_head_ctrl, upper_head_joint, maintainOffset=True, name=upper_head_joint+"_ScC")
                if has_jaw:
                    cmds.parentConstraint(self.jaw_ctrl, jaw_joint, maintainOffset=False, name=jaw_joint+"_PaC")
                    cmds.scaleConstraint(self.jaw_ctrl, jaw_joint, maintainOffset=True, name=jaw_joint+"_ScC")
                if has_chin:
                    cmds.parentConstraint(chin_ctrl, chin_joint, maintainOffset=False, name=chin_joint+"_PaC")
                    cmds.parentConstraint(chew_ctrl, chew_joint, maintainOffset=False, name=chew_joint+"_PaC")
                    cmds.scaleConstraint(chin_ctrl, chin_joint, maintainOffset=True, name=chin_joint+"_ScC")
                    cmds.scaleConstraint(chew_ctrl, chew_joint, maintainOffset=True, name=chew_joint+"_ScC")
                    cmds.matchTransform(end_joint, self.guide_end_loc, position=True, rotation=True)
                if has_lips:
                    cmds.parentConstraint(left_corner_lip_ctrl, left_corner_lip_joint, maintainOffset=False, name=left_corner_lip_joint+"_PaC")
                    cmds.parentConstraint(right_corner_lip_ctrl, right_corner_lip_joint, maintainOffset=False, name=right_corner_lip_joint+"_PaC")
                    cmds.parentConstraint(upper_lip_ctrl, upper_lip_joint, maintainOffset=False, name=upper_lip_joint+"_PaC")
                    cmds.parentConstraint(lower_lip_ctrl, lower_lip_joint, maintainOffset=False, name=lower_lip_joint+"_PaC")
                    cmds.scaleConstraint(left_corner_lip_ctrl, left_corner_lip_joint, maintainOffset=True, name=left_corner_lip_joint+"_ScC")
                    cmds.scaleConstraint(right_corner_lip_ctrl, right_corner_lip_joint, maintainOffset=True, name=right_corner_lip_joint+"_ScC")
                    cmds.scaleConstraint(upper_lip_ctrl, upper_lip_joint, maintainOffset=True, name=upper_lip_joint+"_ScC")
                    cmds.scaleConstraint(lower_lip_ctrl, lower_lip_joint, maintainOffset=True, name=lower_lip_joint+"_ScC")
                    # hide unnecessary zero out bone display:
                    self.ar.utils.create_zero_out_joints([left_corner_lip_joint, right_corner_lip_joint])

                # head follow/isolate create interations between neck and head:
                head_orient_grp = cmds.group(empty=True, name=head_ctrl+"_Orient_Grp")
                head_orient_zero = self.ar.utils.create_zero_out([head_orient_grp])[0]
                cmds.parent(head_orient_zero, neck_ctrls[-1])
                world_ref = cmds.group(empty=True, name=side+self.number_name+"_WorldRef_Grp")
                self.world_refs.append(world_ref)
                cmds.matchTransform(world_ref, neck_ctrls[0], position=True, rotation=True)
                cmds.matchTransform(head_orient_zero, head_zero, position=True, rotation=True)
                cmds.parent(head_zero, head_orient_grp, absolute=True)
                head_rotate_pac = cmds.parentConstraint(neck_ctrls[-1], world_ref, head_orient_grp, maintainOffset=True, skipTranslate=["x", "y", "z"], name=head_orient_grp+"_PaC")[0]
                cmds.setAttr(head_rotate_pac+".interpType", 2) #shortest

                # connect reverseNode:
                cmds.addAttr(head_ctrl, longName=self.ar.data.lang['c032_follow'], attributeType='float', minValue=0, maxValue=1, keyable=True)
                cmds.connectAttr(head_ctrl+'.'+self.ar.data.lang['c032_follow'], head_rotate_pac+"."+neck_ctrls[-1]+"W0", force=True)
                head_rev = cmds.createNode('reverse', name=side+self.number_name+"_"+self.ar.data.lang['c032_follow'].capitalize()+"_Rev")
                cmds.connectAttr(head_ctrl+'.'+self.ar.data.lang['c032_follow'], head_rev+".inputX", force=True)
                cmds.connectAttr(head_rev+'.outputX', head_rotate_pac+"."+world_ref+"W1", force=True)
                self.to_ids.extend([head_rev])
                
                # setup neck autoRotate:
                for n in range(0, self.n_joints):
                    neck_pivot = cmds.xform(neck_ctrls[n], query=True, worldSpace=True, translation=True)
                    neck_orient_grp = cmds.group(neck_ctrls[n], name=neck_ctrls[n]+"_Orient_Grp")
                    self.ar.utils.add_attr_to_items([neck_orient_grp], self.ar.utils.ignore_transform_io_attr)
                    cmds.xform(neck_orient_grp, pivots=(neck_pivot[0], neck_pivot[1], neck_pivot[2]), worldSpace=True)
                    cmds.addAttr(neck_ctrls[n], longName=self.ar.data.lang['c047_autoRotate'], attributeType='float', minValue=0, maxValue=1, defaultValue=self.get_neck_auto_rotate(n), keyable=True)
                    neck_ar_md_name = self.ar.data.lang['c047_autoRotate'][0].capitalize()+self.ar.data.lang['c047_autoRotate'][1:]
                    neck_ar_md = cmds.createNode('multiplyDivide', name=neck_ctrls[n]+"_"+neck_ar_md_name+"_MD")
                    self.to_ids.append(neck_ar_md)
                    cmds.connectAttr(head_ctrl+".rotateX", neck_ar_md+".input1X", force=True)
                    cmds.connectAttr(head_ctrl+".rotateY", neck_ar_md+".input1Y", force=True)
                    cmds.connectAttr(head_ctrl+".rotateZ", neck_ar_md+".input1Z", force=True)
                    cmds.connectAttr(neck_ctrls[n]+"."+self.ar.data.lang['c047_autoRotate'], neck_ar_md+".input2X", force=True)
                    cmds.connectAttr(neck_ctrls[n]+"."+self.ar.data.lang['c047_autoRotate'], neck_ar_md+".input2Y", force=True)
                    cmds.connectAttr(neck_ctrls[n]+"."+self.ar.data.lang['c047_autoRotate'], neck_ar_md+".input2Z", force=True)
                    cmds.connectAttr(neck_ar_md+".outputX", neck_orient_grp+".rotateX", force=True)
                    if style == 2: #quadruped
                        cmds.connectAttr(neck_ar_md+".outputZ", neck_orient_grp+".rotateY", force=True)
                        quadruped_rot_yz_fix_md = cmds.createNode('multiplyDivide', name=neck_ctrls[n]+"_"+neck_ar_md_name+"_YZ_Fix_MD")
                        self.to_ids.append(quadruped_rot_yz_fix_md)
                        cmds.connectAttr(neck_ar_md+".outputY", quadruped_rot_yz_fix_md+".input1X", force=True)
                        cmds.setAttr(quadruped_rot_yz_fix_md+".input2X", -1)
                        cmds.connectAttr(quadruped_rot_yz_fix_md+".outputX", neck_orient_grp+".rotateZ", force=True)
                    else:
                        cmds.connectAttr(neck_ar_md+".outputY", neck_orient_grp+".rotateY", force=True)
                        cmds.connectAttr(neck_ar_md+".outputZ", neck_orient_grp+".rotateZ", force=True)
                
                if has_jaw:
                    # jaw follow sub head or root ctrl (using world_ref)
                    jaw_pac = cmds.parentConstraint(self.head_sub_ctrl, world_ref, jaw_zero, maintainOffset=True, name=jaw_zero+"_PaC")[0]
                    cmds.setAttr(jaw_pac+".interpType", 2) #Shortest, no flip cause problem with scrubing
                    cmds.addAttr(self.jaw_ctrl, longName=self.ar.data.lang['c032_follow'], attributeType="float", minValue=0, maxValue=1, defaultValue=1, keyable=True)
                    cmds.connectAttr(self.jaw_ctrl+"."+self.ar.data.lang['c032_follow'], jaw_pac+"."+self.head_sub_ctrl+"W0", force=True)
                    jaw_follow_rev = cmds.createNode("reverse", name=self.jaw_ctrl+"_Rev")
                    cmds.connectAttr(self.jaw_ctrl+"."+self.ar.data.lang['c032_follow'], jaw_follow_rev+".inputX", force=True)
                    cmds.connectAttr(jaw_follow_rev+".outputX", jaw_pac+"."+world_ref+"W1", force=True)
                    cmds.scaleConstraint(self.head_sub_ctrl, jaw_zero, maintainOffset=True, name=jaw_zero+"_ScC")[0]
                    self.to_ids.extend([jaw_follow_rev])
                
                    # setup jaw move:
                    # jaw open:
                    self.setup_jaw_move(self.jaw_ctrl, "c108_open", True, "Y", "c049_intensity", create_output=True)
                    self.setup_jaw_move(self.jaw_ctrl, "c108_open", True, "Z", "c049_intensity")
                    # jaw close:
                    self.setup_jaw_move(self.jaw_ctrl, "c109_close", False, "Y", "c049_intensity", create_output=True)
                    self.setup_jaw_move(self.jaw_ctrl, "c109_close", False, "Z", "c049_intensity")
                    if has_lips:
                        # upper lid close:
                        self.setup_jaw_move(upper_lip_ctrl, "c109_close", False, "Y", "c039_lip")
                        self.setup_jaw_move(upper_lip_ctrl, "c109_close", False, "Z", "c039_lip")
                        # lower lid close:
                        self.setup_jaw_move(lower_lip_ctrl, "c109_close", False, "Y", "c039_lip", invert_rot=True)
                        self.setup_jaw_move(lower_lip_ctrl, "c109_close", False, "Z", "c039_lip")
                
                    # set jaw move and lips calibrate default values:
                    cmds.setAttr(self.jaw_ctrl+"."+self.ar.data.lang['c108_open'].lower()+self.ar.data.lang['c110_start'].capitalize()+"Rotation", 5)
                    cmds.setAttr(self.jaw_ctrl+"."+self.ar.data.lang['c108_open'].lower()+self.ar.data.lang['c111_calibrate']+"Y", -2)
                    cmds.setAttr(self.jaw_ctrl+"."+self.ar.data.lang['c109_close'].lower()+self.ar.data.lang['c111_calibrate']+"Z", 0)
                    cmds.setAttr(self.jaw_ctrl+"."+self.ar.data.lang['c108_open'].lower()+self.ar.data.lang['c111_calibrate']+self.ar.data.lang['c112_output'], 30)
                    cmds.setAttr(self.jaw_ctrl+"."+self.ar.data.lang['c109_close'].lower()+self.ar.data.lang['c111_calibrate']+self.ar.data.lang['c112_output'], -10)
                    if has_lips:
                        cmds.setAttr(upper_lip_ctrl+"."+self.ar.data.lang['c109_close'].lower()+self.ar.data.lang['c111_calibrate']+"Z", 2)
                        cmds.setAttr(lower_lip_ctrl+"."+self.ar.data.lang['c109_close'].lower()+self.ar.data.lang['c111_calibrate']+"Y", 0)
                        cmds.setAttr(lower_lip_ctrl+"."+self.ar.data.lang['c109_close'].lower()+self.ar.data.lang['c111_calibrate']+"Z", 2)
                
                # upper lip follows lower lip:
                if has_lips:
                    secound_driver = self.head_sub_ctrl
                    if has_upper_head:
                        secound_driver = upper_jaw_ctrl
                    cmds.addAttr(upper_lip_ctrl, longName=self.ar.data.lang['c032_follow'], attributeType='float', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                    upper_lip_pac = cmds.parentConstraint(secound_driver, lower_lip_ctrl, upper_lip_zero, maintainOffset=True, name=upper_lip_zero+"_PaC")[0]
                    upper_lip_rev = cmds.createNode("reverse", name=upper_lip_zero+"_Follow_Rev")
                    cmds.connectAttr(upper_lip_ctrl+"."+self.ar.data.lang['c032_follow'], upper_lip_rev+".inputX", force=True)
                    cmds.connectAttr(upper_lip_ctrl+"."+self.ar.data.lang['c032_follow'], upper_lip_pac+"."+lower_lip_ctrl+"W1", force=True)
                    cmds.connectAttr(upper_lip_rev+".outputX", upper_lip_pac+"."+secound_driver+"W0", force=True)

                    # left side lip:
                    left_lip_pac = cmds.parentConstraint(self.jaw_ctrl, secound_driver, left_lip_grp, maintainOffset=True, name=left_lip_grp+"_PaC")[0]
                    cmds.setAttr(left_lip_pac+".interpType", 2)
                    cmds.addAttr(left_corner_lip_ctrl, longName=self.ar.data.lang['c032_follow'], attributeType='float', minValue=0, maxValue=1, defaultValue=0.5, keyable=True)
                    cmds.connectAttr(left_corner_lip_ctrl+'.'+self.ar.data.lang['c032_follow'], left_lip_pac+"."+self.jaw_ctrl+"W0", force=True)
                    left_lip_rev = cmds.createNode('reverse', name=side+self.number_name+"_"+self.ar.data.lang['p002_left']+"_"+self.ar.data.lang['c039_lip']+"_Rev")
                    cmds.connectAttr(left_corner_lip_ctrl+'.'+self.ar.data.lang['c032_follow'], left_lip_rev+".inputX", force=True)
                    cmds.connectAttr(left_lip_rev+'.outputX', left_lip_pac+"."+secound_driver+"W1", force=True)
                    cmds.scaleConstraint(secound_driver, left_lip_grp, maintainOffset=True, name=left_lip_grp+"_ScC")[0]
                    # right side lip:
                    right_lip_pac = cmds.parentConstraint(self.jaw_ctrl, secound_driver, right_lip_grp, maintainOffset=True, name=right_lip_grp+"_PaC")[0]
                    cmds.setAttr(right_lip_pac+".interpType", 2)
                    cmds.addAttr(right_corner_lip_ctrl, longName=self.ar.data.lang['c032_follow'], attributeType='float', minValue=0, maxValue=1, defaultValue=0.5, keyable=True)
                    cmds.connectAttr(right_corner_lip_ctrl+'.'+self.ar.data.lang['c032_follow'], right_lip_pac+"."+self.jaw_ctrl+"W0", force=True)
                    right_lip_rev = cmds.createNode('reverse', name=side+self.number_name+"_"+self.ar.data.lang['p003_right']+"_"+self.ar.data.lang['c039_lip']+"_Rev")
                    cmds.connectAttr(right_corner_lip_ctrl+'.'+self.ar.data.lang['c032_follow'], right_lip_rev+".inputX", force=True)
                    cmds.connectAttr(right_lip_rev+'.outputX', right_lip_pac+"."+secound_driver+"W1", force=True)
                    cmds.scaleConstraint(secound_driver, right_lip_grp, maintainOffset=True, name=right_lip_grp+"_ScC")[0]
                    
                    self.to_ids.extend([upper_lip_rev, left_lip_rev, right_lip_rev])

                # articulation joint:
                if self.articulation:
                    # neckBase
                    neck_base_jzt = self.ar.utils.create_zero_out_joints([neck_joints[0]])[0]
                    if self.corrective:
                        # corrective controls group
                        self.corrective_ctrls_grp = cmds.group(name=side+self.number_name+"_Corrective_Grp", empty=True)
                        self.corrective_ctrl_grps.append(self.corrective_ctrls_grp)
                        neck_head_calibrate_presets, inverts = self.get_calibrate_presets(s)
                        
                        # neck corrective
                        for n in range(0, self.n_joints):
                            if n == 0:
                                father_joint = neck_base_jzt
                            else:
                                father_joint = neck_joints[n-1]
                            corrective_nets = [None]
                            corrective_nets.append(self.setup_corrective_net(neck_ctrls[n], father_joint, neck_joints[n], neck_ctrl_base_name+"_"+str(n)+"_YawRight", 2, 2, -80))
                            corrective_nets.append(self.setup_corrective_net(neck_ctrls[n], father_joint, neck_joints[n], neck_ctrl_base_name+"_"+str(n)+"_YawLeft", 2, 2, 80))
                            corrective_nets.append(self.setup_corrective_net(neck_ctrls[n], father_joint, neck_joints[n], neck_ctrl_base_name+"_"+str(n)+"_PitchUp", 0, 0, 80))
                            corrective_nets.append(self.setup_corrective_net(neck_ctrls[n], father_joint, neck_joints[n], neck_ctrl_base_name+"_"+str(n)+"_PitchDown", 0, 0, -80))
                            
                            articulation_joints = self.ar.utils.create_articulation_joint(father_joint, neck_joints[n], 4, [(0.5*self.radius, 0, 0), (-0.5*self.radius, 0, 0), (0, 0, 0.5*self.radius), (0, 0, -0.5*self.radius)])
                            self.setup_corrective_controllers(articulation_joints, s, neck_ctrl_base_name+"_"+str(n), corrective_nets, neck_head_calibrate_presets, inverts, [False, True, True, False, False])
                            if s == 1:
                                if self.flip:
                                    cmds.setAttr(articulation_joints[0]+".scaleX", -1)
                                    cmds.setAttr(articulation_joints[0]+".scaleY", -1)
                                    cmds.setAttr(articulation_joints[0]+".scaleZ", -1)
                            self.ar.utils.set_joint_label(articulation_joints[0], s+self.joint_label_add, 18, self.number_name+"_"+self.ar.data.lang['c023_neck']+"_"+str(n)+"_Jar")

                        # head corrective
                        head_corrective_nets = [None]
                        head_corrective_nets.append(self.setup_corrective_net(self.head_sub_ctrl, neck_joints[-1], head_joint, side+self.number_name+"_"+self.ar.data.lang['c024_head']+"_YawRight", 2, 2, -80))
                        head_corrective_nets.append(self.setup_corrective_net(self.head_sub_ctrl, neck_joints[-1], head_joint, side+self.number_name+"_"+self.ar.data.lang['c024_head']+"_YawLeft", 2, 2, 80))
                        head_corrective_nets.append(self.setup_corrective_net(self.head_sub_ctrl, neck_joints[-1], head_joint, side+self.number_name+"_"+self.ar.data.lang['c024_head']+"_PitchUp", 0, 0, 80))
                        head_corrective_nets.append(self.setup_corrective_net(self.head_sub_ctrl, neck_joints[-1], head_joint, side+self.number_name+"_"+self.ar.data.lang['c024_head']+"_PitchDown", 0, 0, -80))
                        head_calibrate_presets, inverts = self.get_calibrate_presets(s)
                        articulation_joints = self.ar.utils.create_articulation_joint(neck_joints[-1], head_joint, 4, [(0.5*self.radius, 0, 0), (-0.5*self.radius, 0, 0), (0, 0, 0.5*self.radius), (0, 0, -0.5*self.radius)])
                        self.setup_corrective_controllers(articulation_joints, s, side+self.number_name+"_"+self.ar.data.lang['c024_head'], head_corrective_nets, head_calibrate_presets, inverts, [False, True, True, False, False])
                        if s == 1:
                            if self.flip:
                                cmds.setAttr(articulation_joints[0]+".scaleX", -1)
                                cmds.setAttr(articulation_joints[0]+".scaleY", -1)
                                cmds.setAttr(articulation_joints[0]+".scaleZ", -1)
                    else:
                        articulation_joints = self.ar.utils.create_articulation_joint(neck_base_jzt, neck_joints[0])
                        self.ar.utils.set_joint_label(articulation_joints[0], s+self.joint_label_add, 18, self.number_name+"_00_"+self.ar.data.lang['c023_neck']+self.ar.data.lang['c106_base']+"_Jar")
                        cmds.rename(articulation_joints[0], side+self.number_name+"_00_"+self.ar.data.lang['c023_neck']+self.ar.data.lang['c106_base']+"_Jar")
                        articulation_joints = self.ar.utils.create_articulation_joint(neck_joints[-1], head_joint)
                    
                    neck_joints.insert(0, neck_base_jzt)
                    cmds.parentConstraint(neck_ctrl_zeros[0], neck_base_jzt, maintainOffset=True, name=neck_base_jzt+"_PaC")
                    cmds.scaleConstraint(neck_ctrl_zeros[0], neck_base_jzt, maintainOffset=True, name=neck_base_jzt+"_ScC")
                    self.ar.utils.set_joint_label(articulation_joints[0], s+self.joint_label_add, 18, self.number_name+"_01_"+self.ar.data.lang['c024_head']+self.ar.data.lang['c106_base']+"_Jar")
                    cmds.rename(articulation_joints[0], side+self.number_name+"_01_"+self.ar.data.lang['c024_head']+self.ar.data.lang['c106_base']+"_Jar")
                
                # facial controls hierarchy
                if cmds.getAttr(self.guide_base+".facial"):
                    if cmds.getAttr(self.guide_base+".facialBrow"):
                        cmds.parent(left_brow_ctrl_grp, right_brow_ctrl_grp, upper_head_ctrl)
                        cmds.matchTransform(left_brow_ctrl_grp, self.guide_brow_loc, position=True, rotation=True)
                        cmds.matchTransform(right_brow_ctrl_grp, self.guide_brow_loc, position=True, rotation=True)
                        cmds.setAttr(right_brow_ctrl_grp+".translateX", (-1*cmds.getAttr(right_brow_ctrl_grp+".translateX")))
                        cmds.setAttr(right_brow_ctrl_grp+".rotateY", 180)
                    if cmds.getAttr(self.guide_base+".facialEyelid"):
                        if self.facial_connect_type == self.ar.data.facial_connect_types[0]: #blendshapes
                            cmds.parent(left_eyelid_ctrl_grp, right_eyelid_ctrl_grp, upper_head_ctrl)
                            cmds.matchTransform(left_eyelid_ctrl_grp, self.guide_eyelid_loc, position=True, rotation=True)
                            cmds.matchTransform(right_eyelid_ctrl_grp, self.guide_eyelid_loc, position=True, rotation=True)
                            cmds.setAttr(right_eyelid_ctrl_grp+".translateX", (-1*cmds.getAttr(right_eyelid_ctrl_grp+".translateX")))
                    if cmds.getAttr(self.guide_base+".facialMouth"):
                        cmds.parent(left_mouth_ctrl_grp, right_mouth_ctrl_grp, upper_jaw_ctrl)
                        cmds.matchTransform(left_mouth_ctrl_grp, self.guide_mouth_loc, position=True, rotation=True)
                        cmds.matchTransform(right_mouth_ctrl_grp, self.guide_mouth_loc, position=True, rotation=True)
                        cmds.setAttr(right_mouth_ctrl_grp+".translateX", (-1*cmds.getAttr(right_mouth_ctrl_grp+".translateX")))
                        cmds.setAttr(right_mouth_ctrl_grp+".rotateY", 180)
                    if cmds.getAttr(self.guide_base+".facialLips"):
                        cmds.parent(lips_ctrl_grp, upper_jaw_ctrl)
                        cmds.matchTransform(lips_ctrl_grp, self.guide_lips_loc, position=True, rotation=True)
                    if cmds.getAttr(self.guide_base+".facialSneer"):
                        cmds.parent(sneer_ctrl_grp, upper_jaw_ctrl)
                        cmds.matchTransform(sneer_ctrl_grp, self.guide_sneer_loc, position=True, rotation=True)
                    if cmds.getAttr(self.guide_base+".facialGrimace"):
                        cmds.parent(grimace_ctrl_grp, chin_ctrl)
                        cmds.matchTransform(grimace_ctrl_grp, self.guide_grimace_loc, position=True, rotation=True)
                        cmds.setAttr(grimace_ctrl_grp+".rotateX", 180)
                    if cmds.getAttr(self.guide_base+".facialFace"):
                        cmds.parent(face_ctrl_grp, self.head_sub_ctrl)
                        cmds.matchTransform(face_ctrl_grp, self.guide_face_loc, position=True, rotation=True)
                
                # calibration attributes:
                neck_calibrations = [self.ar.data.lang['c047_autoRotate']]
                self.ar.ctrls.set_string_attr_from_items(neck_ctrls[0], neck_calibrations)
                if has_jaw:
                    jaw_calibrations = [
                                        self.ar.data.lang['c108_open'].lower()+self.ar.data.lang['c111_calibrate']+"Y",
                                        self.ar.data.lang['c108_open'].lower()+self.ar.data.lang['c111_calibrate']+"Z",
                                        self.ar.data.lang['c109_close'].lower()+self.ar.data.lang['c111_calibrate']+"Y",
                                        self.ar.data.lang['c109_close'].lower()+self.ar.data.lang['c111_calibrate']+"Z",
                                        self.ar.data.lang['c108_open'].lower()+self.ar.data.lang['c111_calibrate']+self.ar.data.lang['c112_output'],
                                        self.ar.data.lang['c109_close'].lower()+self.ar.data.lang['c111_calibrate']+self.ar.data.lang['c112_output']
                    ]
                    self.ar.ctrls.set_string_attr_from_items(self.jaw_ctrl, jaw_calibrations)
                if has_lips:
                    lip_calibrations = [
                                        self.ar.data.lang['c109_close'].lower()+self.ar.data.lang['c111_calibrate']+"Y",
                                        self.ar.data.lang['c109_close'].lower()+self.ar.data.lang['c111_calibrate']+"Z"
                    ]
                    self.ar.ctrls.set_string_attr_from_items(upper_lip_ctrl, lip_calibrations)
                    self.ar.ctrls.set_string_attr_from_items(lower_lip_ctrl, lip_calibrations)
                
                # create a masterModuleGrp to be checked if this rig exists:
                to_hook_items = [neck_ctrl_zeros[0]]
                if has_jaw:
                    to_hook_items.append(jaw_zero)
                if has_lips:
                    to_hook_items.extend([left_corner_zero, right_corner_zero])
                self.create_hook_setup(side, to_hook_items, [neck_joints[0]], [world_ref])
                if self.corrective:
                    cmds.parent(self.corrective_ctrls_grp, self.ctrl_hook_grp)
                
                # head deformer
                if cmds.getAttr(self.guide_base+".deformer") and has_upper_head:
                    head_def_ctrls = [upper_jaw_ctrl, upper_head_ctrl]
                    if has_jaw:
                        head_def_ctrls.append(self.jaw_ctrl)
                        if has_chin:
                            head_def_ctrls.extend([chin_ctrl, chew_ctrl])
                        if has_lips:
                            head_def_ctrls.extend([left_corner_lip_ctrl, right_corner_lip_ctrl, upper_lip_ctrl, lower_lip_ctrl])
                    # collect nodes to be deformedBy this Head module:
                    deformed_by_items = head_def_ctrls + self.get_deformed_by_items(s) + facial_ctrls

                    hd_net = self.ar.config.get_instance("HeadDeformer", [self.ar.data.tools_folder]).create_head_def(side+self.number_name+"_"+self.ar.data.lang['c024_head'], [self.deformer_cube], self.head_sub_ctrl, deformed_by_items, self.guide_net, ui=False)

                    self.add_node_to_guide_net([hd_net], ["hdNet"])
                    cmds.connectAttr(self.head_sub_ctrl+".message", cmds.listConnections(hd_net+".linkedNode", source=True, destination=False)[0]+".parentTag", force=True)
                elif cmds.objExists(self.name_guide+"_DeformerCube_MD"):
                    cmds.delete(self.name_guide+"_DeformerCube_MD")

                # delete duplicated group for side (mirror):
                cmds.delete(side+self.number_name+'_'+self.mirror_grp)

                self.ar.utils.add_attr_to_items([head_orient_grp, world_ref], self.ar.utils.ignore_transform_io_attr)
                if has_lips:
                    self.ar.utils.add_attr_to_items([left_lip_grp, right_lip_grp], self.ar.utils.ignore_transform_io_attr)
                if self.corrective_ctrl_grps:
                    self.ar.utils.add_attr_to_items(self.corrective_ctrl_grps, self.ar.utils.ignore_transform_io_attr)
                self.ar.custom_attr.add_attr(0, [self.static_hook_grp], descendents=True) #dpID
                
            # connect to facial controllers to blendShapes or facial joints
            if cmds.getAttr(self.guide_base+".facial"):
                if self.facial_connect_type == self.ar.data.facial_connect_types[0]: #blendshapes
                    self.ar.config.get_instance("FacialConnection", [self.ar.data.tools_folder]).connect_to_blendshape()
                else:
                    self.ar.config.get_instance("FacialConnection", [self.ar.data.tools_folder]).connect_to_joints()

            # finalize this rig:
            self.serialize_guide()
            self.composing_info()
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and module_instance namespace:
        self.delete_guide()
        self.rename_unit_conversion()
        self.ar.custom_attr.add_attr(0, self.to_ids) #dpID
    

    def create_face_min_max_sn(self, facial_ctrl):
        """ Creates a scriptNode to set the min and max values to the given Face_Ctrl.
        """
        min_max_code = '''from maya import cmds
class MinMaxValues(object):
    def __init__(self, headNet, *args):
        self.face_ctrl = cmds.listConnections(headNet+".faceCtrl")[0]
        cmds.scriptJob(attributeChange=(self.face_ctrl+".minValue", self.setMinMaxValues), killWithScene=False, compressUndo=True)
        cmds.scriptJob(attributeChange=(self.face_ctrl+".maxValue", self.setMinMaxValues), killWithScene=False, compressUndo=True)

    def setMinMaxValues(self, *args):
        extraAttrList = list(set(cmds.listAttr(self.face_ctrl, userDefined=True, keyable=True)) - set(["minValue", "maxValue"]))
        if extraAttrList:
            minimumValue = cmds.getAttr(self.face_ctrl+".minValue")
            maximumValue = cmds.getAttr(self.face_ctrl+".maxValue")
            if minimumValue > maximumValue:
                cmds.setAttr(self.face_ctrl+".minValue", maximumValue)
                minimumValue = maximumValue
            for extraAttr in extraAttrList:
                cmds.addAttr(self.face_ctrl+"."+extraAttr, edit=True, minValue=minimumValue, maxValue=maximumValue)
                if cmds.getAttr(self.face_ctrl+"."+extraAttr) < minimumValue:
                    cmds.setAttr(self.face_ctrl+"."+extraAttr, minimumValue)
                if cmds.getAttr(self.face_ctrl+"."+extraAttr) > maximumValue:
                    cmds.setAttr(self.face_ctrl+"."+extraAttr, maximumValue)

# fire scriptNode
for net in cmds.ls(type="network"):
    if cmds.objExists(net+".dpNetwork") and cmds.getAttr(net+".dpNetwork") == 1:
        if cmds.objExists(net+".dpGuideNet") and cmds.getAttr(net+".dpGuideNet") == 1:
            if cmds.objExists(net+".dpID") and cmds.getAttr(net+".dpID") == "'''+cmds.getAttr(self.guide_net+".dpID")+'''":
                MinMaxValues(net)
        '''
        cmds.lockNode(self.guide_net, lock=False)
        cmds.addAttr(self.guide_net, longName="faceCtrl", attributeType="message")
        cmds.addAttr(self.guide_net, longName="minMaxScriptNode", attributeType="message")
        cmds.addAttr(facial_ctrl, longName="guideNet", attributeType="message")
        cmds.connectAttr(facial_ctrl+".message", self.guide_net+".faceCtrl", force=True)
        cmds.connectAttr(self.guide_net+".message", facial_ctrl+".guideNet", force=True)
        sn = cmds.scriptNode(name=self.guide_net.replace("Net", 'MinMax_SN'), sourceType='python', scriptType=2, beforeScript=min_max_code)
        self.ar.custom_attr.add_attr(0, [sn]) #dpID
        cmds.addAttr(sn, longName="guideNet", attributeType="message")
        cmds.connectAttr(sn+".message", self.guide_net+".minMaxScriptNode", force=True)
        cmds.connectAttr(self.guide_net+".message", sn+".guideNet", force=True)
        cmds.scriptNode(sn, executeBefore=True)
        cmds.lockNode(self.guide_net, lock=True)

    
    def create_facial_ctrl(self, side, side_name, ctrl_name, cv_ctrl, attributes, rot_vector=(0, 0, 0), lock_x=False, lock_y=False, lock_z=False, limit_x=True, limit_y=True, limit_z=True, direct_connection=False, color='yellow', head_def_influence=False, jaw_def_influence=False, add_translate_y=False, limit_min_y=False, invert_z=False):
        """ Important method to receive called parameters and create the specific asked control.
            Convention:
                transfs = ["tx", "tx", "ty", "ty", "tz", "tz]
                axisDirectionList = [-1, 1, -1, 1, -1, 1] # neg, pos, neg, pos, neg, pos
            Returns the created Facial control and its create_zero_out group.
        """
        # declaring variables:
        facial_ctrl = None
        facial_ctrl_grp = None
        calibration_attrs = ["scaleFactor"]
        transfs = ["tx", "tx", "ty", "ty", "tz", "tz"]
        # naming:
        ctrl_name = side+self.number_name+"_"+ctrl_name
        if side_name:
            ctrl_name = side_name+"_"+ctrl_name
        facial_ctrl_name = ctrl_name+"_Ctrl"
        # skip if already there is this ctrl object:
        if cmds.objExists(facial_ctrl_name):
            return None, None
        else:
            # create control calling controllers function:
            facial_ctrl = self.ar.ctrls.create_controller(cv_ctrl, facial_ctrl_name, r=1, d=0, rot=rot_vector, parent_tag=self.head_sub_ctrl)
            # add head or jaw influence attribute
            if head_def_influence:
                self.ar.ctrls.add_def_influence_attrs(facial_ctrl, 1)                
            if jaw_def_influence:
                self.ar.ctrls.add_def_influence_attrs(facial_ctrl, 2)
            # ctrl create_zero_out grp and color:
            facial_ctrl_grp = self.ar.utils.create_zero_out([facial_ctrl])[0]
            cmds.addAttr(facial_ctrl_grp, longName="facialReceiver", attributeType="bool", defaultValue=1)
            self.facial_ctrl_grps.append(facial_ctrl_grp)
            self.ar.ctrls.color_shape([facial_ctrl], color)
            # lock or limit XYZ axis:
            self.lock_attr_limit(facial_ctrl, ctrl_name, [lock_x, lock_y, lock_z], [limit_x, limit_y, limit_z], limit_min_y)
            self.ar.ctrls.set_lock_hide([facial_ctrl], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v', 'ro'])
            cmds.addAttr(facial_ctrl, longName="scaleFactor", attributeType="float", defaultValue=(self.facial_factor*self.radius), minValue=0.001)
            cmds.connectAttr(facial_ctrl+".scaleFactor", facial_ctrl_grp+".scaleX", force=True)
            cmds.connectAttr(facial_ctrl+".scaleFactor", facial_ctrl_grp+".scaleY", force=True)
            if invert_z: # grimace hack to invert front and back values from Z axis
                inv_z_md = cmds.createNode("multiplyDivide", name=ctrl_name+"_InvZ_MD")
                self.to_ids.append(inv_z_md)
                cmds.setAttr(inv_z_md+".input2Z", -1)
                cmds.connectAttr(facial_ctrl+".scaleFactor", inv_z_md+".input1Z", force=True)
                cmds.connectAttr(inv_z_md+".outputZ", facial_ctrl_grp+".scaleZ", force=True)
            else:
                cmds.connectAttr(facial_ctrl+".scaleFactor", facial_ctrl_grp+".scaleZ", force=True)
            # start working with custom attributes
            facial_ctrl_attributes = []
            if attributes:
                for a, attr in enumerate(attributes):
                    if not attr == None:
                        ctrlAttr = attr
                        if side_name:
                            ctrlAttr = side_name+"_"+attr
                        facial_ctrl_attributes.append(ctrlAttr)
                        clp = cmds.createNode("clamp", name=ctrl_name+"_"+attr+"_Clp")
                        # TODO: to be decommented by 2026-12-24
                        #self.to_ids.append(clp)
                        if direct_connection:
                            if not "minValue" in cmds.listAttr(facial_ctrl):
                                for c, clamp_attr in enumerate(["minValue", "maxValue"]):
                                   cmds.addAttr(facial_ctrl, longName=clamp_attr, attributeType="float", defaultValue=c, keyable=False)
                                   cmds.setAttr(facial_ctrl+"."+clamp_attr, channelBox=True)
                                   calibration_attrs.append(clamp_attr)
                            cmds.addAttr(facial_ctrl, longName=attr, attributeType="float", minValue=0, maxValue=1, defaultValue=0)
                            cmds.setAttr(facial_ctrl+"."+attr, keyable=True)
                            cmds.connectAttr(facial_ctrl+"."+attr, clp+".input.inputR", force=True)
                            cmds.connectAttr(facial_ctrl+".minValue", clp+".minR", force=True)
                            cmds.connectAttr(facial_ctrl+".maxValue", clp+".maxR", force=True)
                        else:
                            if not "intensity" in cmds.listAttr(facial_ctrl):
                                cmds.addAttr(facial_ctrl, longName="intensity", attributeType="float", defaultValue=1)
                                cmds.setAttr(facial_ctrl+".intensity", keyable=True)
                            cmds.addAttr(facial_ctrl, longName=ctrlAttr, attributeType="float", defaultValue=0)
                            calibrate_md = cmds.createNode("multiplyDivide", name=ctrl_name+"_"+attr+"_Calibrate_MD")
                            inv_md = cmds.createNode("multiplyDivide", name=ctrl_name+"_"+attr+"_Invert_MD")
                            intensity_md = cmds.createNode("multiplyDivide", name=ctrl_name+"_"+attr+"_Intensity_MD")
                            self.to_ids.extend([calibrate_md, inv_md, intensity_md])
                            if a == 0 or a == 2 or a == 4: #negative
                                cmds.setAttr(clp+".minR", -1000)
                                cmds.setAttr(inv_md+".input2X", -1)
                            else: #positive
                                cmds.setAttr(clp+".maxR", 1000)
                            # connect nodes:
                            cmds.connectAttr(facial_ctrl+"."+transfs[a], calibrate_md+".input1X", force=True)
                            if a == 0 or a == 1: # -x or +x
                                cmds.connectAttr(facial_ctrl+"."+self.calibrate_name+"TX", calibrate_md+".input2X", force=True)
                                if not self.calibrate_name+"TX" in calibration_attrs:
                                    calibration_attrs.append(self.calibrate_name+"TX")
                            elif a == 2 or a == 3: # -y or +y
                                cmds.connectAttr(facial_ctrl+"."+self.calibrate_name+"TY", calibrate_md+".input2X", force=True)
                                if not self.calibrate_name+"TY" in calibration_attrs:
                                    calibration_attrs.append(self.calibrate_name+"TY")
                            else: # -z or +z
                                cmds.connectAttr(facial_ctrl+"."+self.calibrate_name+"TZ", calibrate_md+".input2X", force=True)
                                if not self.calibrate_name+"TZ" in calibration_attrs:
                                    calibration_attrs.append(self.calibrate_name+"TZ")
                            if add_translate_y: #useful for Sneer and Grimace
                                integrate_ty_pma = cmds.createNode("plusMinusAverage", name=ctrl_name+"_"+attr+"_TY_PMA")
                                self.to_ids.append(integrate_ty_pma)
                                cmds.connectAttr(calibrate_md+".outputX", integrate_ty_pma+".input1D[0]", force=True)
                                if not "Front" in attr:
                                    cmds.connectAttr(facial_ctrl+".translateY", integrate_ty_pma+".input1D[1]", force=True)
                                cmds.connectAttr(integrate_ty_pma+".output1D", clp+".input.inputR", force=True)
                                if "R_" in attr: #hack to set operation as substract in PMA node for Right side
                                    cmds.setAttr(integrate_ty_pma+".operation", 2)
                                cmds.setAttr(facial_ctrl+"."+self.calibrate_name+"TY", lock=True)
                            else:
                                cmds.connectAttr(calibrate_md+".outputX", clp+".input.inputR", force=True)
                            cmds.connectAttr(clp+".outputR", inv_md+".input1X", force=True)
                            cmds.connectAttr(inv_md+".outputX", intensity_md+".input1X", force=True)
                            cmds.connectAttr(facial_ctrl+".intensity", intensity_md+".input2X", force=True)
                            cmds.connectAttr(intensity_md+".outputX", facial_ctrl+"."+ctrlAttr, force=True)
                            cmds.setAttr(facial_ctrl+"."+ctrlAttr, lock=True)
                if direct_connection:
                    self.create_face_min_max_sn(facial_ctrl)
            if facial_ctrl_attributes:
                self.ar.ctrls.set_string_attr_from_items(facial_ctrl, facial_ctrl_attributes, "facialList")
            if calibration_attrs:
                self.ar.ctrls.set_string_attr_from_items(facial_ctrl, calibration_attrs)
        return facial_ctrl, facial_ctrl_grp
    
    
    def lock_attr_limit(self, facial_ctrl, ctrl_name, locks, limits, limit_min_y):
        """ Lock or limit attributes for XYZ.
        """
        for i, axis in enumerate(self.ar.data.axes):
            if locks[i]:
                cmds.setAttr(facial_ctrl+".translate"+axis, lock=True, keyable=False)
            else:
                # add calibrate attributes:
                cmds.addAttr(facial_ctrl, longName=self.calibrate_name+"T"+axis, attributeType="float", defaultValue=1, minValue=0.001)
                if limits[i]:
                    if i == 0: #X
                        cmds.transformLimits(facial_ctrl, enableTranslationX=(1, 1))
                        self.limit_translate(facial_ctrl, ctrl_name, axis)
                    elif i == 1: #Y
                        cmds.transformLimits(facial_ctrl, enableTranslationY=(1, 1))
                        self.limit_translate(facial_ctrl, ctrl_name, axis, limit_min_y)
                    else: #Z
                        cmds.transformLimits(facial_ctrl, enableTranslationZ=(1, 1))
                        self.limit_translate(facial_ctrl, ctrl_name, axis)

    
    def limit_translate(self, facial_ctrl, ctrl_name, axis, limit_min_y=False):
        """ Create a hyperbolic setup to limit min and max value for translation of the control.
            Resuming it's just divide 1 by the calibrate value.
        """
        hyperbole_t_limit_md = cmds.createNode("multiplyDivide", name=ctrl_name+"_LimitT"+axis+"_MD")
        self.to_ids.append(hyperbole_t_limit_md)
        cmds.setAttr(hyperbole_t_limit_md+".input1X", 1)
        cmds.setAttr(hyperbole_t_limit_md+".operation", 2)
        cmds.connectAttr(facial_ctrl+"."+self.calibrate_name+"T"+axis, hyperbole_t_limit_md+".input2X", force=True)
        cmds.connectAttr(hyperbole_t_limit_md+".outputX", facial_ctrl+".maxTransLimit.maxTrans"+axis+"Limit", force=True)
        if limit_min_y:
            cmds.transformLimits(facial_ctrl, translationY=(0, 1))
        else:
            hyperbole_int_md = cmds.createNode("multiplyDivide", name=ctrl_name+"_LimitT"+axis+"_Inv_MD")
            self.to_ids.append(hyperbole_int_md)
            cmds.setAttr(hyperbole_int_md+".input2X", -1)
            cmds.connectAttr(hyperbole_t_limit_md+".outputX", hyperbole_int_md+".input1X", force=True)
            cmds.connectAttr(hyperbole_int_md+".outputX", facial_ctrl+".minTransLimit.minTrans"+axis+"Limit", force=True)
    

    def change_facial_connect_type(self, *args):
        """ Get and return the user selected type of controls.
            Change interface to be more clear.
        """
        if self.ar.data.ui_state:
            selected_type = cmds.radioCollection('edit_guide_facial_type_rc', query=True, select=True)
            self.facial_connect_type = cmds.radioButton(selected_type, query=True, annotation=True)
            if self.facial_connect_type == self.ar.data.facial_connect_types[0]: #blendshapes
                cmds.setAttr(self.guide_base+".connectUserType", 0)
            elif self.facial_connect_type == self.ar.data.facial_connect_types[1]: #joints
                cmds.setAttr(self.guide_base+".connectUserType", 1)
    
    
    def get_deformed_by_items(self, s):
        """ Returns the defomedBy list for this Head module based in the integrated hook dictionary.
        """
        guides, results = [], []
        hook = self.ar.utils.get_hook()
        for item in hook.keys():
            if self.name_guide in hook[item]['fatherGuide']:
                if not item in guides:
                    guides.append(item.split(":")[0])
                    if hook[item]['children']:
                        for child in hook[item]['children']:
                            if not child in guides:
                                guides.append(child.split(":")[0])
        if guides:
            all_transforms = cmds.ls(selection=False, type="transform")
            for node in all_transforms:
                if "guide_source" in cmds.listAttr(node):
                    guide_source = cmds.getAttr(node+".guide_source")
                    if guide_source.split(":")[0] in guides:
                        if not node in results:
                            if self.mirror_axis != 'off':
                                if node.startswith(self.sides[s]):
                                    results.append(node)
                            else:
                                results.append(node)
        return results


    def composing_info(self):
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.composed = {
                            "worldRefList"         : self.world_refs,
                            "upperCtrlList"        : self.upper_ctrls,
                            "controllers"          : self.ctrls,
                            "InnerCtrls"           : self.inner_ctrls,
                            "lCtrls"               : self.left_ctrls,
                            "rCtrls"               : self.right_ctrls,
                            "correctiveCtrlGrpList": self.corrective_ctrl_grps,
                            "upperJawCtrlList"     : self.upper_jaw_ctrls,
                            "facialCtrlGrpList"    : self.facial_ctrl_grps
                        }
