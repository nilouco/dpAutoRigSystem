from importlib import reload

from maya import cmds, mel

from ..base import base
from ..util import ik_fk_snap

# global variables to this module:
CLASS_NAME = 'MotionCapture'
TITLE = 'm239_motionCapture'
DESCRIPTION = 'm240_motionCaptureDesc'
WIKI = '06-‐-Tools#-motion-capture'



class MotionCapture(base.BaseLibrary):
    def __init__(self, ar):
        base.BaseLibrary.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(base)
            reload(ik_fk_snap)
        self.auto_rotate_attrs = [self.ar.data.lang['c047_autoRotate'], self.ar.data.lang['c032_follow']]
        self.hik_character_attr = 'Character'
        

    def build_tool(self, *args):
        self.hik_node = self.hik_get_latest_node()
        self.hik_data = None
        # call main function:
        if self.ar.data.ui_state:
            self.ar.motion_capture_ui.create_ui(self)
    

    def hik_get_default_map_data(self):
        """ Returns the default hik controllers mapping dictionary accordly with the language.
        """
        return {
                "Reference"        : {"id"      : 0,
                                      "joint"   : "Root_Ctrl",
                                      "control" : "Root_Ctrl"},
                "Hips"             : {"id"      : 1,
                                      "joint"   : f"{self.ar.data.lang['m011_spine']}_00_{self.ar.data.lang['c106_base']}_Jnt",
                                      "control" : f"{self.ar.data.lang['m011_spine']}_{self.ar.data.lang['c027_hips']}A_Ctrl"},
                "LeftUpLeg"        : {"id"      : 2,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_{self.ar.data.lang['c006_leg_main']}_Jxt",
                                      "joint1"  : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_{self.ar.data.lang['c006_leg_main']}_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_{self.ar.data.lang['c006_leg_main']}_Fk_Ctrl",
                                      "ikCtrl"  : ""},
                "LeftLeg"          : {"id"      : 3,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_{self.ar.data.lang['c007_leg_corner']}_Jxt",
                                      "joint1"  : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_{self.ar.data.lang['c007_leg_corner']}_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_{self.ar.data.lang['c007_leg_corner']}_Fk_Ctrl",
                                      "ikCtrl"  : ""},
                "LeftFoot"         : {"id"      : 4,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c038_foot']}_{self.ar.data.lang['c009_leg_extrem']}_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_{self.ar.data.lang['c009_leg_extrem']}_Fk_Ctrl",
                                      "ikCtrl"  : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_{self.ar.data.lang['c009_leg_extrem']}_Ik_Ctrl"},
                "LeftToeBase"      : {"id"      : 16,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c038_foot']}_{self.ar.data.lang['c029_middle']}_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c038_foot']}_{self.ar.data.lang['c029_middle']}_Ctrl"},
                "RightUpLeg"       : {"id"      : 5,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_{self.ar.data.lang['c006_leg_main']}_Jxt",
                                      "joint1"  : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_{self.ar.data.lang['c006_leg_main']}_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_{self.ar.data.lang['c006_leg_main']}_Fk_Ctrl",
                                      "ikCtrl"  : ""},
                "RightLeg"         : {"id"      : 6,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_{self.ar.data.lang['c007_leg_corner']}_Jxt",
                                      "joint1"  : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_{self.ar.data.lang['c007_leg_corner']}_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_{self.ar.data.lang['c007_leg_corner']}_Fk_Ctrl",
                                      "ikCtrl"  : ""},
                "RightFoot"        : {"id"      : 7,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c038_foot']}_{self.ar.data.lang['c009_leg_extrem']}_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_{self.ar.data.lang['c009_leg_extrem']}_Fk_Ctrl",
                                      "ikCtrl"  : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_{self.ar.data.lang['c009_leg_extrem']}_Ik_Ctrl"},
                "RightToeBase"     : {"id"      : 17,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c038_foot']}_{self.ar.data.lang['c029_middle']}_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c038_foot']}_{self.ar.data.lang['c029_middle']}_Ctrl"},
                "Spine"            : {"id"      : 8,
                                      "joint"   : f"{self.ar.data.lang['m011_spine']}_02_Jnt",
                                      "control" : f"{self.ar.data.lang['m011_spine']}_{self.ar.data.lang['c029_middle']}1_Fk_Ctrl",
                                      "ikCtrl"  : f"{self.ar.data.lang['m011_spine']}_{self.ar.data.lang['c029_middle']}1_Ctrl"},
                "Spine1"           : {"id"      : 23,
                                      "joint"   : f"{self.ar.data.lang['m011_spine']}_04_{self.ar.data.lang['c120_tip']}_Jnt",
                                      "control" : f"{self.ar.data.lang['m011_spine']}_{self.ar.data.lang['c028_chest']}A_Fk_Ctrl",
                                      "ikCtrl"  : f"{self.ar.data.lang['m011_spine']}_{self.ar.data.lang['c028_chest']}B_Ctrl"},
                "LeftShoulder"     : {"id"      : 18,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_00_{self.ar.data.lang['c000_arm_before']}_Jnt",
                                      "joint1"  : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_{self.ar.data.lang['c000_arm_before']}_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_{self.ar.data.lang['c000_arm_before']}_Ctrl"},
                "LeftArm"          : {"id"      : 9,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_{self.ar.data.lang['c001_arm_main']}_Jxt",
                                      "joint1"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_{self.ar.data.lang['c001_arm_main']}_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_{self.ar.data.lang['c001_arm_main']}_Fk_Ctrl",
                                      "ikCtrl"  : ""},
                "LeftForeArm"      : {"id"      : 10,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_{self.ar.data.lang['c002_arm_corner']}_Jxt",
                                      "joint1"  : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_{self.ar.data.lang['c002_arm_corner']}_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_{self.ar.data.lang['c002_arm_corner']}_Fk_Ctrl",
                                      "ikCtrl"  : ""},
                "LeftHand"         : {"id"      : 11,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_13_{self.ar.data.lang['c004_arm_extrem']}_Jnt",
                                      "joint1"  : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_10_{self.ar.data.lang['c004_arm_extrem']}_Jnt",
                                      "joint2"  : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_09_{self.ar.data.lang['c004_arm_extrem']}_Jnt",
                                      "joint3"  : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_17_{self.ar.data.lang['c004_arm_extrem']}_Jnt",
                                      "joint4"  : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_14_{self.ar.data.lang['c004_arm_extrem']}_Jnt",
                                      "joint5"  : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_{self.ar.data.lang['c004_arm_extrem']}_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_{self.ar.data.lang['c004_arm_extrem']}_Fk_Ctrl",
                                      "ikCtrl"  : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_{self.ar.data.lang['c004_arm_extrem']}_Ik_Ctrl"},
                "LeftHandThumb1"   : {"id"      : 50,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m036_thumb']}_00_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m036_thumb']}_00_Ctrl"},
                "LeftHandThumb2"   : {"id"      : 51,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m036_thumb']}_01_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m036_thumb']}_01_Ctrl"},
                "LeftHandThumb3"   : {"id"      : 52,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m036_thumb']}_02_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m036_thumb']}_02_Ctrl"},
                "LeftInHandIndex"  : {"id"      : 147,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m032_index']}_00_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m032_index']}_00_Ctrl"},
                "LeftHandIndex1"   : {"id"      : 54,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m032_index']}_01_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m032_index']}_01_Ctrl"},
                "LeftHandIndex2"   : {"id"      : 55,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m032_index']}_02_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m032_index']}_02_Ctrl"},
                "LeftHandIndex3"   : {"id"      : 56,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m032_index']}_03_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m032_index']}_03_Ctrl"},
                "LeftInHandMiddle" : {"id"      : 148,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m033_middle']}_00_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m033_middle']}_00_Ctrl"},
                "LeftHandMiddle1"  : {"id"      : 58,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m033_middle']}_01_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m033_middle']}_01_Ctrl"},
                "LeftHandMiddle2"  : {"id"      : 59,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m033_middle']}_02_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m033_middle']}_02_Ctrl"},
                "LeftHandMiddle3"  : {"id"      : 60,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m033_middle']}_03_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m033_middle']}_03_Ctrl"},
                "LeftInHandRing"   : {"id"      : 149,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m034_ring']}_00_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m034_ring']}_00_Ctrl"},
                "LeftHandRing1"    : {"id"      : 62,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m034_ring']}_01_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m034_ring']}_01_Ctrl"},
                "LeftHandRing2"    : {"id"      : 63,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m034_ring']}_02_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m034_ring']}_02_Ctrl"},
                "LeftHandRing3"    : {"id"      : 64,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m034_ring']}_03_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m034_ring']}_03_Ctrl"},
                "LeftInHandPinky"  : {"id"      : 150,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m035_pinky']}_00_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m035_pinky']}_00_Ctrl"},
                "LeftHandPinky1"   : {"id"      : 66,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m035_pinky']}_01_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m035_pinky']}_01_Ctrl"},
                "LeftHandPinky2"   : {"id"      : 67,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m035_pinky']}_02_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m035_pinky']}_02_Ctrl"},
                "LeftHandPinky3"   : {"id"      : 68,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m035_pinky']}_03_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m035_pinky']}_03_Ctrl"},
                "RightShoulder"    : {"id"      : 19,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_00_{self.ar.data.lang['c000_arm_before']}_Jnt",
                                      "joint1"  : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_{self.ar.data.lang['c000_arm_before']}_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_{self.ar.data.lang['c000_arm_before']}_Ctrl"},
                "RightArm"         : {"id"      : 12,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_{self.ar.data.lang['c001_arm_main']}_Jxt",
                                      "joint1"  : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_{self.ar.data.lang['c001_arm_main']}_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_{self.ar.data.lang['c001_arm_main']}_Fk_Ctrl",
                                      "ikCtrl"  : ""},
                "RightForeArm"     : {"id"      : 13,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_{self.ar.data.lang['c002_arm_corner']}_Jxt",
                                      "joint1"  : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_{self.ar.data.lang['c002_arm_corner']}_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_{self.ar.data.lang['c002_arm_corner']}_Fk_Ctrl",
                                      "ikCtrl"  : ""},
                "RightHand"        : {"id"      : 14,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_13_{self.ar.data.lang['c004_arm_extrem']}_Jnt",
                                      "joint1"  : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_10_{self.ar.data.lang['c004_arm_extrem']}_Jnt",
                                      "joint2"  : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_09_{self.ar.data.lang['c004_arm_extrem']}_Jnt",
                                      "joint3"  : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_17_{self.ar.data.lang['c004_arm_extrem']}_Jnt",
                                      "joint4"  : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_14_{self.ar.data.lang['c004_arm_extrem']}_Jnt",
                                      "joint5"  : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_{self.ar.data.lang['c004_arm_extrem']}_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_{self.ar.data.lang['c004_arm_extrem']}_Fk_Ctrl",
                                      "ikCtrl"  : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_{self.ar.data.lang['c004_arm_extrem']}_Ik_Ctrl"},
                "RightHandThumb1"  : {"id"      : 74,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m036_thumb']}_00_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m036_thumb']}_00_Ctrl"},
                "RightHandThumb2"  : {"id"      : 75,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m036_thumb']}_01_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m036_thumb']}_01_Ctrl"},
                "RightHandThumb3"  : {"id"      : 76,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m036_thumb']}_02_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m036_thumb']}_02_Ctrl"},
                "RightInHandIndex" : {"id"      : 153,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m032_index']}_00_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m032_index']}_00_Ctrl"},
                "RightHandIndex1"  : {"id"      : 78,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m032_index']}_01_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m032_index']}_01_Ctrl"},
                "RightHandIndex2"  : {"id"      : 79,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m032_index']}_02_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m032_index']}_02_Ctrl"},
                "RightHandIndex3"  : {"id"      : 80,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m032_index']}_03_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m032_index']}_03_Ctrl"},
                "RightInHandMiddle": {"id"      : 154,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m033_middle']}_00_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m033_middle']}_00_Ctrl"},
                "RightHandMiddle1" : {"id"      : 82,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m033_middle']}_01_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m033_middle']}_01_Ctrl"},
                "RightHandMiddle2" : {"id"      : 83,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m033_middle']}_02_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m033_middle']}_02_Ctrl"},
                "RightHandMiddle3" : {"id"      : 84,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m033_middle']}_03_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m033_middle']}_03_Ctrl"},
                "RightInHandRing"  : {"id"      : 155,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m034_ring']}_00_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m034_ring']}_00_Ctrl"},
                "RightHandRing1"   : {"id"      : 86,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m034_ring']}_01_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m034_ring']}_01_Ctrl"},
                "RightHandRing2"   : {"id"      : 87,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m034_ring']}_02_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m034_ring']}_02_Ctrl"},
                "RightHandRing3"   : {"id"      : 88,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m034_ring']}_03_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m034_ring']}_03_Ctrl"},
                "RightInHandPinky" : {"id"      : 156,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m035_pinky']}_00_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m035_pinky']}_00_Ctrl"},
                "RightHandPinky1"  : {"id"      : 90,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m035_pinky']}_01_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m035_pinky']}_01_Ctrl"},
                "RightHandPinky2"  : {"id"      : 91,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m035_pinky']}_02_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m035_pinky']}_02_Ctrl"},
                "RightHandPinky3"  : {"id"      : 92,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m035_pinky']}_03_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['m007_finger']}_{self.ar.data.lang['m035_pinky']}_03_Ctrl"},
                "Neck"             : {"id"      : 20,
                                      "joint"   : f"{self.ar.data.lang['c024_head']}_{self.ar.data.lang['c023_neck']}_00_Jnt",
                                      "control" : f"{self.ar.data.lang['c024_head']}_{self.ar.data.lang['c023_neck']}_00_Ctrl"},
                "Neck1"            : {"id"      : 32,
                                      "joint"   : f"{self.ar.data.lang['c024_head']}_{self.ar.data.lang['c023_neck']}_01_Jnt",
                                      "control" : f"{self.ar.data.lang['c024_head']}_{self.ar.data.lang['c023_neck']}_01_Ctrl"},
                "Head"             : {"id"      : 15,
                                      "joint"   : f"{self.ar.data.lang['c024_head']}_00_{self.ar.data.lang['c024_head']}_Jnt",
                                      "joint1"  : f"{self.ar.data.lang['c024_head']}_01_{self.ar.data.lang['c024_head']}_Jnt",
                                      "joint2"  : f"{self.ar.data.lang['c024_head']}_02_{self.ar.data.lang['c024_head']}_Jnt",
                                      "control" : f"{self.ar.data.lang['c024_head']}_{self.ar.data.lang['c024_head']}_Ctrl"},
                "LeafLeftArmRoll1" : {"id"      : 176,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_02_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_Up_00_Ctrl"},
                "LeafLeftArmRoll2" : {"id"      : 184,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_03_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_Up_01_Ctrl"},
                "LeafLeftArmRoll3" : {"id"      : 192,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_04_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_Up_02_Ctrl"},
                "LeafLeftArmRoll4" : {"id"      : 200,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_05_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_Up_03_Ctrl"},
                "LeafLeftArmRoll5" : {"id"      : 208,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_06_Jnt",
                                      "needJnt" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_12_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_Up_04_Ctrl"},
                "LeafLeftForeArmRoll1" : {"id"  : 177,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_08_Jnt",
                                      "joint1"  : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_06_Jnt",
                                      "needJnt" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_12_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_Down_00_Ctrl"},
                "LeafLeftForeArmRoll2" : {"id"  : 185,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_09_Jnt",
                                      "joint1"  : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_07_Jnt",
                                      "needJnt" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_12_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_Down_01_Ctrl"},
                "LeafLeftForeArmRoll3" : {"id"  : 193,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_10_Jnt",
                                      "joint1"  : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_08_Jnt",
                                      "needJnt" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_12_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_Down_02_Ctrl"},
                "LeafLeftForeArmRoll4" : {"id"  : 201,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_11_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_Down_03_Ctrl"},
                "LeafLeftForeArmRoll5" : {"id"  : 209,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_12_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c037_arm']}_Down_04_Ctrl"},
                "LeafRightArmRoll1": {"id"      : 178,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_02_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_Up_00_Ctrl"},
                "LeafRightArmRoll2": {"id"      : 186,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_03_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_Up_01_Ctrl"},
                "LeafRightArmRoll3": {"id"      : 194,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_04_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_Up_02_Ctrl"},
                "LeafRightArmRoll4": {"id"      : 202,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_05_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_Up_03_Ctrl"},
                "LeafRightArmRoll5": {"id"      : 210,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_06_Jnt",
                                      "needJnt" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_12_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_Up_04_Ctrl"},
                "LeafRightForeArmRoll1" : {"id" : 179,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_08_Jnt",
                                      "joint1"  : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_06_Jnt",
                                      "needJnt" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_12_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_Down_00_Ctrl"},
                "LeafRightForeArmRoll2" : {"id" : 187,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_09_Jnt",
                                      "joint1"  : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_07_Jnt",
                                      "needJnt" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_12_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_Down_01_Ctrl"},
                "LeafRightForeArmRoll3" : {"id" : 195,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_10_Jnt",
                                      "joint1"  : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_08_Jnt",
                                      "needJnt" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_12_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_Down_02_Ctrl"},
                "LeafRightForeArmRoll4" : {"id" : 203,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_11_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_Down_03_Ctrl"},
                "LeafRightForeArmRoll5" : {"id" : 211,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_12_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c037_arm']}_Down_04_Ctrl"},
                "LeafLeftUpLegRoll1" : {"id"    : 172,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_02_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_Up_00_Ctrl"},
                "LeafLeftUpLegRoll2" : {"id"    : 180,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_03_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_Up_01_Ctrl"},
                "LeafLeftUpLegRoll3" : {"id"    : 188,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_04_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_Up_02_Ctrl"},
                "LeafLeftUpLegRoll4" : {"id"    : 196,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_05_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_Up_03_Ctrl"},
                "LeafLeftUpLegRoll5" : {"id"    : 204,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_06_Jnt",
                                      "needJnt" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_12_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_Up_04_Ctrl"},
                "LeafLeftLegRoll1" : {"id"      : 173,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_08_Jnt",
                                      "joint1"  : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_06_Jnt",
                                      "needJnt" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_12_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_Down_00_Ctrl"},
                "LeafLeftLegRoll2" : {"id"      : 181,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_09_Jnt",
                                      "joint1"  : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_07_Jnt",
                                      "needJnt" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_12_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_Down_01_Ctrl"},
                "LeafLeftLegRoll3" : {"id"      : 189,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_10_Jnt",
                                      "joint1"  : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_08_Jnt",
                                      "needJnt" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_12_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_Down_02_Ctrl"},
                "LeafLeftLegRoll4" : {"id"      : 197,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_11_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_Down_03_Ctrl"},
                "LeafLeftLegRoll5" : {"id"      : 205,
                                      "joint"   : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_12_Jnt",
                                      "control" : f"{self.ar.data.lang['p002_left']}_{self.ar.data.lang['c006_leg_main']}_Down_04_Ctrl"},
                "LeafRightUpLegRoll1": {"id"    : 174,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_02_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_Up_00_Ctrl"},
                "LeafRightUpLegRoll2": {"id"    : 182,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_03_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_Up_01_Ctrl"},
                "LeafRightUpLegRoll3": {"id"    : 190,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_04_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_Up_02_Ctrl"},
                "LeafRightUpLegRoll4": {"id"    : 198,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_05_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_Up_03_Ctrl"},
                "LeafRightUpLegRoll5": {"id"    : 206,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_06_Jnt",
                                      "needJnt" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_12_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_Up_04_Ctrl"},
                "LeafRightLegRoll1" : {"id"     : 175,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_08_Jnt",
                                      "joint1"  : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_06_Jnt",
                                      "needJnt" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_12_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_Down_00_Ctrl"},
                "LeafRightLegRoll2" : {"id"     : 183,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_09_Jnt",
                                      "joint1"  : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_07_Jnt",
                                      "needJnt" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_12_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_Down_01_Ctrl"},
                "LeafRightLegRoll3" : {"id"     : 191,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_10_Jnt",
                                      "joint1"  : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_08_Jnt",
                                      "needJnt" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_12_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_Down_02_Ctrl"},
                "LeafRightLegRoll4" : {"id"     : 199,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_11_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_Down_03_Ctrl"},
                "LeafRightLegRoll5" : {"id"     : 207,
                                      "joint"   : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_12_Jnt",
                                      "control" : f"{self.ar.data.lang['p003_right']}_{self.ar.data.lang['c006_leg_main']}_Down_04_Ctrl"},
        }


    def prepare_t_pose(self, *args):
        """ Prepare the biped character rig to T-Pose in order to receive the mocap retargeting.
        """
        print(f"{self.ar.data.lang['c110_start']} {self.ar.data.lang['m241_prepareTPose']}")
        self.set_ctrl_mode(1) #FK
        self.mute_auto_rotate()
        self.set_t_pose()


    def hik_retarget(self, rib=False, *args):
        """ Run the HumanIk retargeting processes.
        """
        if self.ar.data.ui_state:
            rib = cmds.checkBox('mocap_map_ribbon_cb', query=True, value=True)
        self.ar.ui_manager.set_progress(f"{self.ar.data.lang['m242_retargeting']} HumanIk", self.ar.data.lang['m239_motionCapture'], add_one=False, add_number=False, max=8)
        self.hik_create_character_definition()
        self.ar.ui_manager.set_progress(f"{self.ar.data.lang['m242_retargeting']} HumanIk")
        self.hik_assign_joints_to_definition(rib)
        self.ar.ui_manager.set_progress(f"{self.ar.data.lang['m242_retargeting']} HumanIk")
        self.hik_create_custom_rig_ctrl()
        self.ar.ui_manager.set_progress(f"{self.ar.data.lang['m242_retargeting']} HumanIk")
        self.hik_map_biped_controllers(rib)
        self.ar.ui_manager.set_progress(f"{self.ar.data.lang['m242_retargeting']} HumanIk")
        self.set_ikfk_biped_controllers_by_ui()
        self.ar.ui_manager.set_progress(f"{self.ar.data.lang['m242_retargeting']} HumanIk")
        self.hik_map_custom_elements(rib)
        self.ar.ui_manager.set_progress(f"{self.ar.data.lang['m242_retargeting']} HumanIk")
        self.hik_map_custom_chest()
        self.ar.ui_manager.set_progress(f"{self.ar.data.lang['m242_retargeting']} HumanIk")
        self.hik_create_job()
        mel.eval('hikCustomRigToolWidget -e -sl -1;') #unselect
        cmds.select(clear=True)
        self.ar.ui_manager.set_progress(end_it=True)


    def hik_remove_mocap(self, *args):
        """ Remove the HumanIk mocap nodes and reset the dpAR rig to default pose.
        """
        self.hik_delete_nodes()
        self.unmute_auto_rotate()
        self.reset_default_pose()
        print(f"{self.ar.data.lang['i046_remove']} HumanIk")
        self.ar.ui_manager.set_progress(end_it=True)


    def set_ikfk(self, opt_ctrl, mode):
        """ Set ik or fk.
        """
        userDefAttrList = cmds.listAttr(opt_ctrl, userDefined=True)
        if userDefAttrList:
            for attr in userDefAttrList:
                if attr.endswith('Fk'):
                    cmds.setAttr(f"{opt_ctrl}.{attr}", mode)


    def run_ikfk_snap(self, key=True):
        """ Execute the ikFkSnap script nodes.
            It's very usefull to transfer baked fk animation to ik controllers.
        """
        nets = self.ar.utils.get_network_by_attr('dpIkFkSnapNet')
        if nets:
            for net in nets:
                # declare needed variables:
                world_ref = cmds.listConnections(f"{net}.worldRef")[0]
                fk_ctrls = cmds.listConnections(f"{net}.fkCtrlList")
                ik_corner_ctrl = cmds.listConnections(f"{net}.ikPoleVectorCtrl")[0]
                ik_extreme_ctrl = cmds.listConnections(f"{net}.ikExtremCtrl")[0]
                ik_extreme_sub_ctrl = cmds.listConnections(f"{net}.ikExtremSubCtrl")[0]
                ik_joints = cmds.listConnections(f"{net}.ikJointList")
                # make an ikFkSnap instance without create another network node.
                ikfk_snap_inst = ik_fk_snap.IkFkSnap(self.ar, net, world_ref, fk_ctrls, [ik_corner_ctrl, ik_extreme_ctrl, ik_extreme_sub_ctrl], ik_joints, [self.ar.data.lang['c018_revFoot_roll'], self.ar.data.lang['c019_revFoot_spin'], self.ar.data.lang['c020_revFoot_turn']], self.ar.data.lang['c040_uniformScale'], creation=False)
                # snap from Fk to Ik (that means move ik to fk position)                
                ikfk_snap_inst.snapFkToIk()
                del ikfk_snap_inst
                if key:
                    cmds.setKeyframe([ik_extreme_ctrl, ik_corner_ctrl], attribute=['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ'])


    def set_ctrl_mode(self, mode=1, *args):
        """ Set dpAR rig to IK or Fk mode.
            Default: mode = 1 = Fk.
        """
        opt_ctrl = self.ar.utils.get_node_by_message('optionCtrl')
        if opt_ctrl:
            self.set_ikfk(opt_ctrl, mode)
            print(f"{self.ar.data.lang['m248_setIkFkMode']} {mode}")
            return opt_ctrl
        else:
            mel.eval(f'warning "{self.ar.data.lang['m243_noOptCtrlToIkFk']}";')


    def get_auto_rotate_ctrls(self):
        """ Get and return the clavicle and neck controllers.
        """
        controllers = self.ar.ctrls.get_controller_node_by_id('id_030_LimbClavicle')
        controllers.extend(self.ar.ctrls.get_controller_node_by_id('id_022_HeadNeck'))
        return controllers


    def lock_auto_rotate_attr(self, ctrl, value):
        """ Lock or unlock the autoRotate attribute for the given controller.
        """
        for follow_attr in self.auto_rotate_attrs:
            if follow_attr in cmds.listAttr(ctrl):
                cmds.setAttr(f"{ctrl}.{follow_attr}", lock=value)


    def mute_auto_rotate(self):
        """ Mute clavicle and neck autoRotate behavior.
        """
        controllers = self.get_auto_rotate_ctrls()
        if controllers:
            for ctrl in controllers:
                self.lock_auto_rotate_attr(ctrl, True)
                zero_grp = cmds.listRelatives(ctrl, parent=True, type='transform')[0]
                for axis in self.ar.data.axes:
                    cmds.mute(f"{zero_grp}.rotate{axis}", force=True)
        print(f"{self.ar.data.lang['m249_muteAutoRotate']} {', '.join(controllers)}")


    def get_ordered_by_time_id(self, items):
        """ Return ordered list of the given item list by the time in the dpID.
        """
        odered_items, ids = [], []
        for item in items:
            if self.ar.data.dp_id in cmds.listAttr(item):
                ids.append(int(cmds.getAttr(f"{item}.{self.ar.data.dp_id}").split('.')[1])) #time
        if ids:
            _temps, odered_items = zip(*sorted(zip(ids, items)))
        return odered_items


    def set_t_pose(self):
        """ Set the biped arms as TPose and align leg and feet as vertical to front direction.
        """
        # clavicle/hips
        before_ctrls = self.ar.ctrls.get_controller_node_by_id('id_030_LimbClavicle')
        if before_ctrls:
            clav_items, hip_items = [], []
            for before_ctrl in before_ctrls:
                if self.ar.data.lang['c000_arm_before'] in before_ctrl: #arm
                    clav_items.append(before_ctrl)
                else: #leg
                    hip_items.append(before_ctrl)
            clav_items = self.get_ordered_by_time_id(clav_items)
            hip_items = self.get_ordered_by_time_id(hip_items)
            cmds.xform(clav_items[0], rotation=(90, 0, 90), worldSpace=True) #left clavicle
            cmds.xform(hip_items[0], rotation=(90, 0, 0), worldSpace=True) #left hips
            for axis in self.ar.data.axes:
                cmds.setAttr(f"{clav_items[1]}.rotate{axis}", cmds.getAttr(f"{clav_items[0]}.rotate{axis}")) #right clavicle
                cmds.setAttr(f"{hip_items[1]}.rotate{axis}", cmds.getAttr(f"{hip_items[0]}.rotate{axis}")) #right hips
        # arm/leg
        fk_ctrls = self.ar.ctrls.get_controller_node_by_id('id_031_LimbFk')
        if fk_ctrls:
            arms, legs = [], []
            for fkCtrl in fk_ctrls:
                if self.ar.data.lang['c001_arm_main'] in fkCtrl and not fkCtrl in arms:
                    arms.append(fkCtrl)
                if self.ar.data.lang['c006_leg_main'] in fkCtrl and not fkCtrl in legs:
                    legs.append(fkCtrl)
                if self.ar.data.lang['c002_arm_corner'] in fkCtrl and not fkCtrl in arms:
                    arms.append(fkCtrl)
                if self.ar.data.lang['c007_leg_corner'] in fkCtrl and not fkCtrl in legs:
                    legs.append(fkCtrl)
                if self.ar.data.lang['c004_arm_extrem'] in fkCtrl and not fkCtrl in arms:
                    arms.append(fkCtrl)
                if self.ar.data.lang['c009_leg_extrem'] in fkCtrl and not fkCtrl in legs:
                    legs.append(fkCtrl)
            arms = self.get_ordered_by_time_id(arms)
            legs = self.get_ordered_by_time_id(legs)
            # arm
            cmds.xform(arms[0], rotation=(90, 90, 0), worldSpace=True) #left shoulder
            cmds.xform(arms[1], rotation=(90, 90, 0), worldSpace=True) #left elbow
            cmds.xform(arms[2], rotation=(90, 90, 0), worldSpace=True) #left wrist
            cmds.xform(arms[3], rotation=(-90, 90, 0), worldSpace=True) #right shoulder
            cmds.xform(arms[4], rotation=(-90, 90, 0), worldSpace=True) #right elbow
            cmds.xform(arms[5], rotation=(-90, 90, 0), worldSpace=True) #right wrist
            # leg
            cmds.xform(legs[0], rotation=(90, 0, 90), worldSpace=True) #left leg
            cmds.xform(legs[1], rotation=(90, 0, 90), worldSpace=True) #left knee
            cmds.xform(legs[2], rotation=(0, -90, 90), worldSpace=True) #left ankle
            cmds.xform(legs[3], rotation=(-90, 0, 90), worldSpace=True) #right leg
            cmds.xform(legs[4], rotation=(-90, 0, 90), worldSpace=True) #right knee
            cmds.xform(legs[5], rotation=(0, 90, 90), worldSpace=True) #right ankle
        # fingers
        finger_ctrls = self.ar.ctrls.get_controller_node_by_id('id_015_FingerMain') or []
        finger_ctrls.extend(self.ar.ctrls.get_controller_node_by_id('id_016_FingerFk'))
        if finger_ctrls:
            finger_ctrls = [f for f in finger_ctrls if not '_00_' in f and not self.ar.data.lang['m036_thumb'] in f]
            for finger_ctrl in finger_ctrls:
                zero_grp = finger_ctrl.replace('_Ctrl', '_SDK_Zero_0_Grp')
                if cmds.objExists(zero_grp):
                    cmds.setAttr(f"{finger_ctrl}.rotateY", (-1)*cmds.getAttr(f"{zero_grp}.rotateY"))
        # ik
        opt_ctrl = self.ar.utils.get_node_by_message('optionCtrl')
        if opt_ctrl:
            if 'ikFkSnap' in cmds.listAttr(opt_ctrl):
                self.run_ikfk_snap(False)
            else:
                mel.eval(f'warning "{self.ar.data.lang['m244_setTPoseIssue']} ikFkSnap";')
        before_ctrls.extend(fk_ctrls)
        print(f"{self.ar.data.lang['m250_trySetTPose']} {', '.join(before_ctrls)}")


    def hik_get_latest_node(self):
        """ Return the latest listed HIKCharacterNode.
        """
        hik_items = cmds.ls(type='HIKCharacterNode')
        if hik_items:
            return hik_items[-1]


    def hik_create_character_definition(self):
        """ Create humanIk character definition node.
            Returns its latest HIKCharacterNode.
        """
        hik_old_items = cmds.ls(type='HIKCharacterNode')
        mel.eval('HIKCharacterControlsTool;')
        mel.eval('hikCreateDefinition;')
        self.hik_node = next(iter(set(cmds.ls(type='HIKCharacterNode'))-set(hik_old_items)))
        self.id = self.ar.custom_attr.add_attr(0, [self.hik_node])[0] #dpID
        print(f"{self.ar.data.lang['m251_createdCharDefinition']} {self.hik_node}")
        return self.hik_node
    

    def hik_assign_joints_to_definition(self, rib=False):
        """ Map dpAR biped joints to HumanIk character definition.
        """
        if self.hik_node:
            if self.ar.utils.get_all_grp():
                old_ref_nodes = cmds.listConnections(f"{self.hik_node}.Reference", source=True, destination=False)
                if not self.hik_data:
                    self.hik_data = self.hik_get_default_map_data()
                for hik_item in self.hik_data:
                    if 'Roll' in hik_item and not rib:
                        continue
                    for r in ['', '1', '2', '3', '4', '5']: #workaround to accept many ribbons renaming
                        if f"joint{r}" in self.hik_data[hik_item]:
                            if cmds.objExists(self.hik_data[hik_item][f"joint{r}"]):
                                if r == '' and 'needJnt' in self.hik_data[hik_item] and not cmds.objExists(self.hik_data[hik_item]['needJnt']):
                                    continue
                                cmds.connectAttr(f"{self.hik_data[hik_item][f"joint{r}"]}.message", f"{self.hik_node}.{hik_item}", force=True)
                                if not self.hik_character_attr in cmds.listAttr(self.hik_data[hik_item][f"joint{r}"]):
                                    cmds.addAttr(self.hik_data[hik_item][f"joint{r}"], longName=self.hik_character_attr, attributeType='message')
                                for attr in self.ar.data.transform_attrs:
                                    cmds.setAttr(f"{self.hik_data[hik_item][f"joint{r}"]}.{attr}", lock=False)
                                break
                        else:
                            mel.eval(f'warning "{self.ar.data.lang['m245_jointDefinitionIssue']}{self.hik_data[hik_item]['joint']}";')
                print(self.ar.data.lang['m252_assignJointDefinition'])
                if old_ref_nodes:
                    cmds.delete(old_ref_nodes[0])
            else:
                mel.eval(f'warning "{self.ar.data.lang['m246_missingDpARToRetarget']}";')
        else:
            mel.eval(f'warning "{self.ar.data.lang['m247_missingHIKCharNode']}";')


    def hik_map_biped_controllers(self, rib=False):
        """ Map the HumanIk biped controllers to the definition.
        """
        iks = ['Spine', 'Spine1', 'Spine2']
        if self.ar.data.ui_state:
            iks = self.ar.motion_capture_ui.get_ik_modes_from_ui()
        if self.hik_node:
            if self.ar.utils.get_all_grp():
                if not self.hik_data:
                    self.hik_data = self.hik_get_default_map_data()
                for hik_item in self.hik_data:
                    if 'Roll' in hik_item and not rib:
                        continue
                    if self.hik_data[hik_item]['id'] != 0: #reference
                        #ik or fk
                        ctrl = 'control'
                        if iks and hik_item in iks:
                            ctrl = 'ikCtrl'
                        if cmds.objExists(self.hik_data[hik_item][ctrl]):
                            cmds.select(self.hik_data[hik_item][ctrl])
                            mel.eval('hikControlRigSelectionChangedCallback;')
                            mel.eval(f'hikCustomRigAssignEffector {self.hik_data[hik_item]['id']};')
                            #print(self.hik_data[hik_item]['id'], self.hik_data[hik_item][ctrl])
                print(self.ar.data.lang['m253_assignCtrlDefinition'])
                cmds.select(clear=True)
            else:
                mel.eval(f'warning "{self.ar.data.lang['m246_missingDpARToRetarget']}";')
        else:
            mel.eval(f'warning "{self.ar.data.lang['m247_missingHIKCharNode']}";')


    def hik_create_custom_rig_ctrl(self):
        """ Call humanIk to create a customRig node.
        """
        mel.eval('hikCreateCustomRig( hikGetCurrentCharacter() );')


    def hik_delete_nodes(self):
        """ Remove HumanIk mocap integration from dpAR.
        """
        mel.eval('hikDeleteCustomRig( hikGetCurrentCharacter() );')
        mel.eval('hikDeleteDefinition();')
    
    
    def unmute_auto_rotate(self):
        """ Reaply the clavicle and neck autoRotate behavior unmuting it.
        """
        controllers = self.get_auto_rotate_ctrls()
        if controllers:
            for ctrl in controllers:
                self.lock_auto_rotate_attr(ctrl, False)
                zero_grp = cmds.listRelatives(ctrl, parent=True, type='transform')[0]
                for axis in self.ar.data.axes:
                    cmds.mute(f"{zero_grp}.rotate{axis}", disable=True)
            print(f"{self.ar.data.lang['i046_remove']} {self.ar.data.lang['m249_muteAutoRotate']} {', '.join(controllers)}")


    def reset_default_pose(self, *args):
        """ Back rig to default pose calling the ResetPose validator.
        """
        reset_pose = self.ar.config.get_instance('ResetPose', [self.ar.data.checkout_folder])
        reset_pose.verbose = False
        reset_pose.run_action(False) #fix
        reset_pose.end_progress()
        self.ar.ui_manager.set_progress(end_it=True)


    def set_ikfk_biped_controllers_by_ui(self):
        """ Set the ikFk attributes in the optionCtrl as the choose UI.
        """
        opt_ctrl = self.set_ctrl_mode() #fk
        if opt_ctrl and self.ar.data.ui_state:
            if cmds.radioCollection('mocap_spine_mode_rc', query=True, select=True) == "spineIk":
                cmds.setAttr(f"{opt_ctrl}.{self.ar.data.lang['m011_spine'].lower()}Fk", 0)
            if cmds.radioCollection('mocap_arm_mode_rc', query=True, select=True) == "armIk":
                cmds.setAttr(f"{opt_ctrl}.{self.ar.data.lang['p002_left'].lower()}{self.ar.data.lang['c037_arm']}Fk", 0)
                cmds.setAttr(f"{opt_ctrl}.{self.ar.data.lang['p003_right'].lower()}{self.ar.data.lang['c037_arm']}Fk", 0)
            if cmds.radioCollection('mocap_leg_mode_rc', query=True, select=True) == "legIk":
                cmds.setAttr(f"{opt_ctrl}.{self.ar.data.lang['p002_left'].lower()}{self.ar.data.lang['c006_leg_main']}Fk", 0)
                cmds.setAttr(f"{opt_ctrl}.{self.ar.data.lang['p003_right'].lower()}{self.ar.data.lang['c006_leg_main']}Fk", 0)


    def hik_check_exists(self, id, dataKey='control'):
        """ Return True of False if the object inside the dataKey exists or not.
        """
        for hik_item in self.hik_data:
            if id == self.hik_data[hik_item]['id']:
                return cmds.objExists(self.hik_data[hik_item][dataKey])


    def hik_set_custom_map(self, id, t=None, r=None):
        """ Set custom map to translate and/or rotate for the given HumanIk item ID.
        """
        if self.hik_check_exists(id):
            mel.eval(f'hikCustomRigToolWidget -e -sl {id};')
            mel.eval('hikControlRigSelectionChangedCallback;')
            mel.eval('hikUpdateCustomRigUI')
            if t != None:
                mel.eval(f'hikCustomRigAddRemoveMapping( "T", {t} );')
            if r != None:
                mel.eval(f'hikCustomRigAddRemoveMapping( "R", {r} );')
            mel.eval('hikUpdateCustomRigUI')


    def hik_map_custom_elements(self, rib=False):
        """ Set custom HumanIk controllers properly mapping.
        """
        fingers = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
        for hik_item in self.hik_data:
            for finger in fingers:
                if finger in hik_item:
                    self.hik_set_custom_map(self.hik_data[hik_item]['id'], r=1) #Finger add rotate
                    self.hik_set_custom_map(self.hik_data[hik_item]['id'], t=0) #Finger remove translate
            if 'Roll' in hik_item and rib:
                self.hik_set_custom_map(self.hik_data[hik_item]['id'], r=1) #Ribbon add rotate
        self.hik_set_custom_map(15, t=0) #Head remove translate, let it rotate only
        self.hik_set_custom_map(8,  r=1) #Spine add rotate
        self.hik_set_custom_map(20, r=1) #Neck add rotate
        self.hik_set_custom_map(32, r=1) #Neck1 add rotate
    
    
    def hik_map_custom_chest(self):
        """ Set HumanIk Chest controller.
        """
        cmds.select(f"{self.ar.data.lang['m011_spine']}_{self.ar.data.lang['c028_chest']}A_Fk_Ctrl")
        if self.ar.data.ui_state and cmds.radioCollection('mocap_spine_mode_rc', query=True, select=True) == 'spineIk':
            cmds.select(f"{self.ar.data.lang['m011_spine']}_{self.ar.data.lang['c028_chest']}B_Ctrl")
        mel.eval('hikControlRigSelectionChangedCallback; hikCustomRigAssignEffector 1000;')
        cmds.select(clear=True)
    

    def hik_create_job(self):
        """ Create a scriptJob to check if the HumanIkCharacterNode will be deleted to unmute autoRotate feature.
        """
        hik_cleaner_code = '''
from maya import cmds
DP_MOTIONCAPTURE_VERSION = "'''+str(self.ar.data.version)+'''"

class HumanIKCleaner(object):
    def __init__(self, hikNode, sn, controllers, attributes, *args):
        self.hik_node = hikNode
        self.myself = sn
        self.controllers = controllers
        self.attributes = attributes
        cmds.scriptJob(nodeDeleted=(self.hik_node, self.jobDeletedMocap), killWithScene=False, compressUndo=True)

    def jobDeletedMocap(self, *args):
        """ Restore autoRotate feature in dpAR.
        """
        print("'''+self.ar.data.lang['i046_remove']+''' HumanIk")
        self.unmute_auto_rotate()
        if cmds.objExists(self.myself):
            cmds.delete(self.myself)
            print("Deleted "+self.myself)

    def unmute_auto_rotate(self):
        """ Reaply the clavicle and neck autoRotate behavior unmuting it.
        """
        if self.controllers:
            for ctrl in self.controllers:
                self.lock_auto_rotate_attr(ctrl, False)
                zero_grp = cmds.listRelatives(ctrl, parent=True, type='transform')[0]
                for axis in ['X', 'Y', 'Z']:
                    cmds.mute(zero_grp+".rotate"+axis, disable=True)
            print("'''+self.ar.data.lang['i046_remove']+''' '''+self.ar.data.lang['m249_muteAutoRotate']+''' {', '.join(self.controllers))

    def lock_auto_rotate_attr(self, ctrl, value):
        """ Lock or unlock the autoRotate attribute for the given controller.
        """
        for follow_attr in self.attributes:
            if follow_attr in cmds.listAttr(ctrl):
                cmds.setAttr(ctrl+"."+follow_attr, lock=value)
    
# fire scriptNode
for hik in cmds.ls(type="HIKCharacterNode"):
    if cmds.objExists(hik+".dpID") and cmds.getAttr(hik+".dpID") == "'''+self.id+'''":
        HumanIKCleaner(hik, "'''+self.hik_node+'_Cleaner_SN'+'''", '''+str(self.get_auto_rotate_ctrls())+''', '''+str(self.auto_rotate_attrs)+''')
'''
        sn = cmds.scriptNode(name=f"{self.hik_node}_Cleaner_SN", sourceType='python', scriptType=2, beforeScript=hik_cleaner_code)
        self.ar.custom_attr.add_attr(0, [sn]) #dpID
        cmds.scriptNode(sn, executeBefore=True)


    def hik_snap_ik_timeline(self, start=None, end=None, *args):
        """ Run to all timeline and snap ik from baked fk.
        """
        opt_ctrl = self.ar.utils.get_node_by_message('optionCtrl')
        if opt_ctrl and 'ikFkSnap' in cmds.listAttr(opt_ctrl):
            start_frame = start
            end_frame = end
            if start == None:
                start_frame = int(cmds.playbackOptions(query=True, minTime=True))
            if end == None:
                end_frame = int(cmds.playbackOptions(query=True, maxTime=True))
            self.ar.ui_manager.set_progress('HumanIk - Snap ikFk', self.ar.data.lang['m239_motionCapture'], add_one=False, add_number=False, max=(end_frame-start_frame))
            initial_time = cmds.currentTime(query=True)
            for t in range(start_frame, end_frame+1):
                self.ar.ui_manager.set_progress('Timeline')
                cmds.currentTime(t)
                self.run_ikfk_snap()
            cmds.currentTime(initial_time)
            self.ar.ui_manager.set_progress(end_it=True)
