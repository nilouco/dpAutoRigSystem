# importing libraries:
from maya import cmds
from maya import mel
from ..Modules.Library import dpIkFkSnap

# global variables to this module:
CLASS_NAME = "MotionCapture"
TITLE = "m239_motionCapture"
DESCRIPTION = "m240_motionCaptureDesc"
ICON = "/Icons/dp_motionCapture.png"

DP_MOTIONCAPTURE_VERSION = 1.01


class MotionCapture(object):
    def __init__(self, dpUIinst, ui=True, *args, **kwargs):
        # defining variables:
        self.dpUIinst = dpUIinst
        self.utils = dpUIinst.utils
        self.ctrls = dpUIinst.ctrls
        self.lang = self.dpUIinst.lang
        self.ui = ui
        self.autoRotateAttrList = [self.lang['c047_autoRotate'], self.lang['c032_follow']]
        self.hikCharacterAttr = "Character"
        self.hikNode = self.hikGetLatestNode()
        self.hikDic = None
        if self.dpUIinst.dev:
            from importlib import reload
            reload(dpIkFkSnap)
        # call main function:
        if self.ui:
            self.dpMotionCaptureUI(self)

    
    def dpMotionCaptureUI(self, *args):
        """ Create a window in order to load the original model and targets to be mirrored.
        """
        # creating MotionCaptureUI Window:
        self.utils.closeUI('dpMotionCaptureWindow')
        mocap_winWidth  = 280
        mocap_winHeight = 390
        dpMotionCaptureWin = cmds.window('dpMotionCaptureWindow', title=self.lang["m239_motionCapture"]+" "+str(DP_MOTIONCAPTURE_VERSION), widthHeight=(mocap_winWidth, mocap_winHeight), menuBar=False, sizeable=False, minimizeButton=True, maximizeButton=False, menuBarVisible=False, titleBar=True)
        # creating layout:
        mocapMainLayout = cmds.formLayout('mocapMainLayout')
        mocapTabLayout = cmds.tabLayout('mocapTabLayout', innerMarginWidth=5, innerMarginHeight=5, parent=mocapMainLayout)
        cmds.formLayout('mocapMainLayout', edit=True, attachForm=((mocapTabLayout, 'top', 5), (mocapTabLayout, 'left', 0), (mocapTabLayout, 'bottom', 0), (mocapTabLayout, 'right', 0)))
        humanIkFL = cmds.formLayout('humanIkFL', numberOfDivisions=100, parent=mocapTabLayout)
        motionCaptureMainLayout = cmds.columnLayout('motionCaptureMainLayout', columnOffset=("both", 10), rowSpacing=10, parent=humanIkFL)
        cmds.separator(height=5, style="none", horizontal=True, parent=motionCaptureMainLayout)
        humanIkModeFL = cmds.frameLayout('humanIkModeFL', label="Ik/Fk "+self.lang['v003_mode'], collapsable=True, collapse=False, parent=motionCaptureMainLayout)
        # radio buttons:
        ikFkModeRCL = cmds.rowColumnLayout('ikFkModeRCL', numberOfColumns=3, columnWidth=[(1, 90), (2, 80), (3, 70)], columnAlign=[(1, 'center'), (2, 'center'), (3, 'center')], columnAttach=[(1, 'both', 5), (2, 'both', 5), (3, 'both', 5)], parent=humanIkModeFL)
        # spine
        spineModeCL = cmds.columnLayout('spineModeCL', adjustableColumn=True, width=80, parent=ikFkModeRCL)
        self.spineModeRBC = cmds.radioCollection('self.spineModeRBC', parent=spineModeCL)
        spineChoose = cmds.radioButton("spineIk", label=self.lang['m011_spine']+" Ik", annotation="spineIk")
        cmds.radioButton("spineFk", label=self.lang['m011_spine']+" FK", annotation="spineFk")
        cmds.radioCollection(self.spineModeRBC, edit=True, select=spineChoose)
        # arm
        armModeCL = cmds.columnLayout('armModeCL', adjustableColumn=True, width=80, parent=ikFkModeRCL)
        self.armModeRBC = cmds.radioCollection('self.armModeRBC', parent=armModeCL)
        cmds.radioButton("armIk", label=self.lang['m028_arm']+" Ik", annotation="armIk")
        armChoose = cmds.radioButton("armFk", label=self.lang['m028_arm']+" FK", annotation="armFk")
        cmds.radioCollection(self.armModeRBC, edit=True, select=armChoose)
        # leg
        legModeCL = cmds.columnLayout('legModeCL', adjustableColumn=True, width=80, parent=ikFkModeRCL)
        self.legModeRBC = cmds.radioCollection('self.legModeRBC', parent=legModeCL)
        cmds.radioButton("legIk", label=self.lang['m030_leg']+" Ik", annotation="legIk")
        legChoose = cmds.radioButton("legFk", label=self.lang['m030_leg']+" FK", annotation="legFk")
        cmds.radioCollection(self.legModeRBC, edit=True, select=legChoose)
        cmds.separator(parent=motionCaptureMainLayout)
        # processes buttons
        cmds.text(label=self.lang['i292_processes'], parent=motionCaptureMainLayout)
        cmds.button(label=self.lang['m241_prepareTPose'], annotation="prepareTPose", width=240, command=self.prepareTPose, parent=motionCaptureMainLayout)
        cmds.button(label=self.lang['m242_retargeting']+" HumanIk", annotation="retargetHumanIk", width=240, command=self.hikRetarget, parent=motionCaptureMainLayout)
        # animation buttons
        cmds.separator(style='in', height=10, width=240, parent=motionCaptureMainLayout)
        cmds.text(label=self.lang['i185_animation'], parent=motionCaptureMainLayout)
        cmds.button(label=self.lang['i360_snapIkFromBakedFk'], annotation="Snap Ik timeline", width=240, command=self.hikSnapIkTimeline, parent=motionCaptureMainLayout)
        # clear buttons
        cmds.separator(style='in', height=10, width=240, parent=motionCaptureMainLayout)
        cmds.text(label=self.lang['v096_cleanup'], parent=motionCaptureMainLayout)
        cmds.button(label=self.lang['i046_remove']+" HumanIk", annotation="removeHumanIk", width=240, command=self.hikRemoveMocap, parent=motionCaptureMainLayout)
        cmds.tabLayout(mocapTabLayout, edit=True, tabLabel=((humanIkFL, 'HumanIk')))
        # call Window:
        cmds.showWindow(dpMotionCaptureWin)
    

    def hikGetDefaultMapDic(self, *args):
        """ Returns the default hik controllers mapping dictionary accordly with the language.
        """
        return {
                "Reference"        : {"id"      : 0,
                                      "joint"   : "Root_Ctrl",
                                      "control" : "Root_Ctrl"},
                "Hips"             : {"id"      : 1,
                                      "joint"   : self.lang['m011_spine']+"_00_"+self.lang['c106_base']+"_Jnt",
                                      "control" : self.lang['m011_spine']+"_"+self.lang['c027_hips']+"A_Ctrl"},
                "LeftUpLeg"        : {"id"      : 2,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_"+self.lang['c006_leg_main']+"_Jxt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_"+self.lang['c006_leg_main']+"_Fk_Ctrl",
                                      "ikCtrl"  : ""},
                "LeftLeg"          : {"id"      : 3,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_"+self.lang['c007_leg_corner']+"_Jxt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_"+self.lang['c007_leg_corner']+"_Fk_Ctrl",
                                      "ikCtrl"  : ""},
                "LeftFoot"         : {"id"      : 4,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c038_foot']+"_"+self.lang['c009_leg_extrem']+"_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_"+self.lang['c009_leg_extrem']+"_Fk_Ctrl",
                                      "ikCtrl"  : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_"+self.lang['c009_leg_extrem']+"_Ik_Ctrl"},
                "LeftToeBase"      : {"id"      : 16,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c038_foot']+"_"+self.lang['c029_middle']+"_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c038_foot']+"_"+self.lang['c029_middle']+"_Ctrl"},
                "RightUpLeg"       : {"id"      : 5,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_"+self.lang['c006_leg_main']+"_Jxt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_"+self.lang['c006_leg_main']+"_Fk_Ctrl",
                                      "ikCtrl"  : ""},
                "RightLeg"         : {"id"      : 6,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_"+self.lang['c007_leg_corner']+"_Jxt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_"+self.lang['c007_leg_corner']+"_Fk_Ctrl",
                                      "ikCtrl"  : ""},
                "RightFoot"        : {"id"      : 7,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c038_foot']+"_"+self.lang['c009_leg_extrem']+"_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_"+self.lang['c009_leg_extrem']+"_Fk_Ctrl",
                                      "ikCtrl"  : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_"+self.lang['c009_leg_extrem']+"_Ik_Ctrl"},
                "RightToeBase"     : {"id"      : 17,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c038_foot']+"_"+self.lang['c029_middle']+"_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c038_foot']+"_"+self.lang['c029_middle']+"_Ctrl"},
                "Spine"            : {"id"      : 8,
                                      "joint"   : self.lang['m011_spine']+"_02_Jnt",
                                      "control" : self.lang['m011_spine']+"_"+self.lang['c029_middle']+"1_Fk_Ctrl",
                                      "ikCtrl"  : self.lang['m011_spine']+"_"+self.lang['c029_middle']+"1_Ctrl"},
                "Spine1"           : {"id"      : 23,
                                      "joint"   : self.lang['m011_spine']+"_04_"+self.lang['c120_tip']+"_Jnt",
                                      "control" : self.lang['m011_spine']+"_"+self.lang['c028_chest']+"A_Fk_Ctrl",
                                      "ikCtrl"  : self.lang['m011_spine']+"_"+self.lang['c028_chest']+"B_Ctrl"},
                "LeftShoulder"     : {"id"      : 18,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_00_"+self.lang['c000_arm_before']+"_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_"+self.lang['c000_arm_before']+"_Ctrl"},
                "LeftArm"          : {"id"      : 9,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_"+self.lang['c001_arm_main']+"_Jxt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_"+self.lang['c001_arm_main']+"_Fk_Ctrl",
                                      "ikCtrl"  : ""},
                "LeftForeArm"      : {"id"      : 10,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_"+self.lang['c002_arm_corner']+"_Jxt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_"+self.lang['c002_arm_corner']+"_Fk_Ctrl",
                                      "ikCtrl"  : ""},
                "LeftHand"         : {"id"      : 11,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_13_"+self.lang['c004_arm_extrem']+"_Jnt",
                                      "joint1"  : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_10_"+self.lang['c004_arm_extrem']+"_Jnt",
                                      "joint2"  : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_09_"+self.lang['c004_arm_extrem']+"_Jnt",
                                      "joint3"  : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_17_"+self.lang['c004_arm_extrem']+"_Jnt",
                                      "joint4"  : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_14_"+self.lang['c004_arm_extrem']+"_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_"+self.lang['c004_arm_extrem']+"_Fk_Ctrl",
                                      "ikCtrl"  : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_"+self.lang['c004_arm_extrem']+"_Ik_Ctrl"},
                "LeftHandThumb1"   : {"id"      : 50,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m036_thumb']+"_00_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m036_thumb']+"_00_Ctrl"},
                "LeftHandThumb2"   : {"id"      : 51,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m036_thumb']+"_01_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m036_thumb']+"_01_Ctrl"},
                "LeftHandThumb3"   : {"id"      : 52,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m036_thumb']+"_02_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m036_thumb']+"_02_Ctrl"},
                "LeftInHandIndex"  : {"id"      : 147,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_00_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_00_Ctrl"},
                "LeftHandIndex1"   : {"id"      : 54,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_01_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_01_Ctrl"},
                "LeftHandIndex2"   : {"id"      : 55,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_02_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_02_Ctrl"},
                "LeftHandIndex3"   : {"id"      : 56,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_03_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_03_Ctrl"},
                "LeftInHandMiddle" : {"id"      : 148,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_00_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_00_Ctrl"},
                "LeftHandMiddle1"  : {"id"      : 58,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_01_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_01_Ctrl"},
                "LeftHandMiddle2"  : {"id"      : 59,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_02_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_02_Ctrl"},
                "LeftHandMiddle3"  : {"id"      : 60,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_03_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_03_Ctrl"},
                "LeftInHandRing"   : {"id"      : 149,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_00_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_00_Ctrl"},
                "LeftHandRing1"    : {"id"      : 62,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_01_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_01_Ctrl"},
                "LeftHandRing2"    : {"id"      : 63,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_02_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_02_Ctrl"},
                "LeftHandRing3"    : {"id"      : 64,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_03_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_03_Ctrl"},
                "LeftInHandPinky"  : {"id"      : 150,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_00_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_00_Ctrl"},
                "LeftHandPinky1"   : {"id"      : 66,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_01_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_01_Ctrl"},
                "LeftHandPinky2"   : {"id"      : 67,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_02_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_02_Ctrl"},
                "LeftHandPinky3"   : {"id"      : 68,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_03_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_03_Ctrl"},
                "RightShoulder"    : {"id"      : 19,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_00_"+self.lang['c000_arm_before']+"_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_"+self.lang['c000_arm_before']+"_Ctrl"},
                "RightArm"         : {"id"      : 12,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_"+self.lang['c001_arm_main']+"_Jxt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_"+self.lang['c001_arm_main']+"_Fk_Ctrl",
                                      "ikCtrl"  : ""},
                "RightForeArm"     : {"id"      : 13,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_"+self.lang['c002_arm_corner']+"_Jxt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_"+self.lang['c002_arm_corner']+"_Fk_Ctrl",
                                      "ikCtrl"  : ""},
                "RightHand"        : {"id"      : 14,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_13_"+self.lang['c004_arm_extrem']+"_Jnt",
                                      "joint1"  : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_10_"+self.lang['c004_arm_extrem']+"_Jnt",
                                      "joint2"  : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_09_"+self.lang['c004_arm_extrem']+"_Jnt",
                                      "joint3"  : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_17_"+self.lang['c004_arm_extrem']+"_Jnt",
                                      "joint4"  : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_14_"+self.lang['c004_arm_extrem']+"_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_"+self.lang['c004_arm_extrem']+"_Fk_Ctrl",
                                      "ikCtrl"  : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_"+self.lang['c004_arm_extrem']+"_Ik_Ctrl"},
                "RightHandThumb1"  : {"id"      : 74,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m036_thumb']+"_00_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m036_thumb']+"_00_Ctrl"},
                "RightHandThumb2"  : {"id"      : 75,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m036_thumb']+"_01_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m036_thumb']+"_01_Ctrl"},
                "RightHandThumb3"  : {"id"      : 76,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m036_thumb']+"_02_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m036_thumb']+"_02_Ctrl"},
                "RightInHandIndex" : {"id"      : 153,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_00_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_00_Ctrl"},
                "RightHandIndex1"  : {"id"      : 78,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_01_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_01_Ctrl"},
                "RightHandIndex2"  : {"id"      : 79,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_02_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_02_Ctrl"},
                "RightHandIndex3"  : {"id"      : 80,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_03_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_03_Ctrl"},
                "RightInHandMiddle": {"id"      : 154,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_00_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_00_Ctrl"},
                "RightHandMiddle1" : {"id"      : 82,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_01_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_01_Ctrl"},
                "RightHandMiddle2" : {"id"      : 83,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_02_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_02_Ctrl"},
                "RightHandMiddle3" : {"id"      : 84,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_03_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_03_Ctrl"},
                "RightInHandRing"  : {"id"      : 155,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_00_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_00_Ctrl"},
                "RightHandRing1"   : {"id"      : 86,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_01_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_01_Ctrl"},
                "RightHandRing2"   : {"id"      : 87,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_02_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_02_Ctrl"},
                "RightHandRing3"   : {"id"      : 88,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_03_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_03_Ctrl"},
                "RightInHandPinky" : {"id"      : 156,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_00_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_00_Ctrl"},
                "RightHandPinky1"  : {"id"      : 90,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_01_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_01_Ctrl"},
                "RightHandPinky2"  : {"id"      : 91,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_02_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_02_Ctrl"},
                "RightHandPinky3"  : {"id"      : 92,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_03_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_03_Ctrl"},
                "Neck"             : {"id"      : 20,
                                      "joint"   : self.lang['c024_head']+"_"+self.lang['c023_neck']+"_00_Jnt",
                                      "control" : self.lang['c024_head']+"_"+self.lang['c023_neck']+"_00_Ctrl"},
                "Neck1"            : {"id"      : 32,
                                      "joint"   : self.lang['c024_head']+"_"+self.lang['c023_neck']+"_01_Jnt",
                                      "control" : self.lang['c024_head']+"_"+self.lang['c023_neck']+"_01_Ctrl"},
                "Head"             : {"id"      : 15,
                                      "joint"   : self.lang['c024_head']+"_00_"+self.lang['c024_head']+"_Jnt",
                                      "joint1"  : self.lang['c024_head']+"_01_"+self.lang['c024_head']+"_Jnt",
                                      "joint2"  : self.lang['c024_head']+"_02_"+self.lang['c024_head']+"_Jnt",
                                      "control" : self.lang['c024_head']+"_"+self.lang['c024_head']+"_Ctrl"},
                "LeafLeftArmRoll1" : {"id"      : 176,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_02"+"_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_Up_00"+"_Ctrl"},
                "LeafLeftArmRoll2" : {"id"      : 184,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_03"+"_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_Up_01"+"_Ctrl"},
                "LeafLeftArmRoll3" : {"id"      : 192,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_04"+"_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_Up_02"+"_Ctrl"},
                "LeafLeftArmRoll4" : {"id"      : 200,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_05"+"_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_Up_03"+"_Ctrl"},
                "LeafLeftArmRoll5" : {"id"      : 208,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_06"+"_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_Up_04"+"_Ctrl"},
                "LeafLeftForeArmRoll1" : {"id"  : 177,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_08"+"_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_Down_00"+"_Ctrl"},
                "LeafLeftForeArmRoll2" : {"id"  : 185,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_09"+"_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_Down_01"+"_Ctrl"},
                "LeafLeftForeArmRoll3" : {"id"  : 193,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_10"+"_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_Down_02"+"_Ctrl"},
                "LeafLeftForeArmRoll4" : {"id"  : 201,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_11"+"_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_Down_03"+"_Ctrl"},
                "LeafLeftForeArmRoll5" : {"id"  : 209,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_12"+"_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c037_arm']+"_Down_04"+"_Ctrl"},
                "LeafRightArmRoll1": {"id"      : 178,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_02"+"_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_Up_00"+"_Ctrl"},
                "LeafRightArmRoll2": {"id"      : 186,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_03"+"_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_Up_01"+"_Ctrl"},
                "LeafRightArmRoll3": {"id"      : 194,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_04"+"_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_Up_02"+"_Ctrl"},
                "LeafRightArmRoll4": {"id"      : 202,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_05"+"_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_Up_03"+"_Ctrl"},
                "LeafRightArmRoll5": {"id"      : 210,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_06"+"_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_Up_04"+"_Ctrl"},
                "LeafRightForeArmRoll1" : {"id" : 179,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_08"+"_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_Down_00"+"_Ctrl"},
                "LeafRightForeArmRoll2" : {"id" : 187,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_09"+"_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_Down_01"+"_Ctrl"},
                "LeafRightForeArmRoll3" : {"id" : 195,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_10"+"_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_Down_02"+"_Ctrl"},
                "LeafRightForeArmRoll4" : {"id" : 203,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_11"+"_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_Down_03"+"_Ctrl"},
                "LeafRightForeArmRoll5" : {"id" : 211,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_12"+"_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c037_arm']+"_Down_04"+"_Ctrl"},
                "LeafLeftUpLegRoll1" : {"id"    : 172,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_02"+"_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_Up_00"+"_Ctrl"},
                "LeafLeftUpLegRoll2" : {"id"    : 180,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_03"+"_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_Up_01"+"_Ctrl"},
                "LeafLeftUpLegRoll3" : {"id"    : 188,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_04"+"_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_Up_02"+"_Ctrl"},
                "LeafLeftUpLegRoll4" : {"id"    : 196,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_05"+"_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_Up_03"+"_Ctrl"},
                "LeafLeftUpLegRoll5" : {"id"    : 204,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_06"+"_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_Up_04"+"_Ctrl"},
                "LeafLeftLegRoll1" : {"id"      : 173,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_08"+"_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_Down_00"+"_Ctrl"},
                "LeafLeftLegRoll2" : {"id"      : 181,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_09"+"_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_Down_01"+"_Ctrl"},
                "LeafLeftLegRoll3" : {"id"      : 189,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_10"+"_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_Down_02"+"_Ctrl"},
                "LeafLeftLegRoll4" : {"id"      : 197,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_11"+"_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_Down_03"+"_Ctrl"},
                "LeafLeftLegRoll5" : {"id"      : 205,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_12"+"_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['c006_leg_main']+"_Down_04"+"_Ctrl"},
                "LeafRightUpLegRoll1": {"id"    : 174,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_02"+"_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_Up_00"+"_Ctrl"},
                "LeafRightUpLegRoll2": {"id"    : 182,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_03"+"_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_Up_01"+"_Ctrl"},
                "LeafRightUpLegRoll3": {"id"    : 190,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_04"+"_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_Up_02"+"_Ctrl"},
                "LeafRightUpLegRoll4": {"id"    : 198,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_05"+"_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_Up_03"+"_Ctrl"},
                "LeafRightUpLegRoll5": {"id"    : 206,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_06"+"_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_Up_04"+"_Ctrl"},
                "LeafRightLegRoll1" : {"id"     : 175,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_08"+"_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_Down_00"+"_Ctrl"},
                "LeafRightLegRoll2" : {"id"     : 183,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_09"+"_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_Down_01"+"_Ctrl"},
                "LeafRightLegRoll3" : {"id"     : 191,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_10"+"_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_Down_02"+"_Ctrl"},
                "LeafRightLegRoll4" : {"id"     : 199,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_11"+"_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_Down_03"+"_Ctrl"},
                "LeafRightLegRoll5" : {"id"     : 207,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_12"+"_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['c006_leg_main']+"_Down_04"+"_Ctrl"},
        }


    def prepareTPose(self, *args):
        """ Prepare the biped character rig to T-Pose in order to receive the mocap retargeting.
        """
        print(self.lang['c110_start']+" "+self.lang['m241_prepareTPose'])
        self.setCtrlMode(1) #FK
        self.muteAutoRotate()
        self.setTPose()


    def hikRetarget(self, *args):
        """ Run the HumanIk retargeting processes.
        """
        self.utils.setProgress(self.lang['m242_retargeting']+" HumanIk", self.lang['m239_motionCapture'], addOne=False, addNumber=False, max=8)
        self.hikCreateCharacterDefinition()
        self.utils.setProgress(self.lang['m242_retargeting']+" HumanIk")
        self.hikAssignJointsToDefinition()
        self.utils.setProgress(self.lang['m242_retargeting']+" HumanIk")
        self.hikCreateCustomRigCtrl()
        self.utils.setProgress(self.lang['m242_retargeting']+" HumanIk")
        self.hikMapBipedControllersByUI()
        self.utils.setProgress(self.lang['m242_retargeting']+" HumanIk")
        self.setIkFkBipedControllersByUI()
        self.utils.setProgress(self.lang['m242_retargeting']+" HumanIk")
        self.hikMapCustomElements()
        self.utils.setProgress(self.lang['m242_retargeting']+" HumanIk")
        self.hikMapCustomChest()
        self.utils.setProgress(self.lang['m242_retargeting']+" HumanIk")
        self.hikCreateJob()
        mel.eval('hikCustomRigToolWidget -e -sl -1;') #unselect
        cmds.select(clear=True)
        self.utils.setProgress(endIt=True)


    def hikRemoveMocap(self, *args):
        """ Remove the HumanIk mocap nodes and reset the dpAR rig to default pose.
        """
        self.hikDeleteNodes()
        self.unmuteAutoRotate()
        self.resetDefaultPose()
        print(self.lang['i046_remove']+" HumanIk")
        self.utils.setProgress(endIt=True)


    def setIkFk(self, optCtrl, mode, *args):
        """ Set ik or fk.
        """
        userDefAttrList = cmds.listAttr(optCtrl, userDefined=True)
        if userDefAttrList:
            for attr in userDefAttrList:
                if attr.endswith("Fk"):
                    cmds.setAttr(optCtrl+"."+attr, mode)


    def runIkFkSnap(self, key=True, *args):
        """ Execute the ikFkSnap script nodes.
            It's very usefull to transfer baked fk animation to ik controllers.
        """
        netList = self.utils.getNetworkNodeByAttr("dpIkFkSnapNet")
        if netList:
            for net in netList:
                # declare needed variables:
                worldRef = cmds.listConnections(net+".worldRef")[0]
                fkCtrlList = cmds.listConnections(net+".fkCtrlList")
                ikCornerCtrl = cmds.listConnections(net+".ikPoleVectorCtrl")[0]
                ikExtremCtrl = cmds.listConnections(net+".ikExtremCtrl")[0]
                ikExtremSubCtrl = cmds.listConnections(net+".ikExtremSubCtrl")[0]
                ikJointList = cmds.listConnections(net+".ikJointList")
                # make an ikFkSnap instance without create another network node.
                ikFkSnapInst = dpIkFkSnap.IkFkSnapClass(self.dpUIinst, net, worldRef, fkCtrlList, [ikCornerCtrl, ikExtremCtrl, ikExtremSubCtrl], ikJointList, [self.dpUIinst.lang['c018_revFoot_roll'], self.dpUIinst.lang['c019_revFoot_spin'], self.dpUIinst.lang['c020_revFoot_turn']], self.dpUIinst.lang['c040_uniformScale'], creation=False)
                # snap from Fk to Ik (that means move ik to fk position)                
                ikFkSnapInst.snapFkToIk()
                del ikFkSnapInst
                if key:
                    cmds.setKeyframe([ikExtremCtrl, ikCornerCtrl], attribute=["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"])


    def setCtrlMode(self, mode=1, *args):
        """ Set dpAR rig to IK or Fk mode.
            Default: mode = 1 = Fk.
        """
        optCtrl = self.utils.getNodeByMessage("optionCtrl")
        if optCtrl:
            self.setIkFk(optCtrl, mode)
            print(self.lang['m248_setIkFkMode']+" "+str(mode))
            return optCtrl
        else:
            mel.eval('warning \"'+self.lang['m243_noOptCtrlToIkFk']+'\";')


    def getAutoRotateCtrlList(self, *args):
        """ Get and return the clavicle and neck controllers.
        """
        ctrlList = self.ctrls.getControlNodeById("id_030_LimbClavicle")
        ctrlList.extend(self.ctrls.getControlNodeById("id_022_HeadNeck"))
        return ctrlList


    def lockAutoRotateAttr(self, ctrl, value, *args):
        """ Lock or unlock the autoRotate attribute for the given controller.
        """
        for followAttr in self.autoRotateAttrList:
            if followAttr in cmds.listAttr(ctrl):
                cmds.setAttr(ctrl+"."+followAttr, lock=value)


    def muteAutoRotate(self, *args):
        """ Mute clavicle and neck autoRotate behavior.
        """
        ctrlList = self.getAutoRotateCtrlList()
        if ctrlList:
            for ctrl in ctrlList:
                self.lockAutoRotateAttr(ctrl, True)
                zeroGrp = cmds.listRelatives(ctrl, parent=True, type="transform")[0]
                for axis in self.dpUIinst.axisList:
                    cmds.mute(zeroGrp+".rotate"+axis, force=True)
        print(self.lang['m249_muteAutoRotate']+" "+", ".join(ctrlList))


    def getOrderedByTimeID(self, itemList, *args):
        """ Return ordered list of the given item list by the time in the dpID.
        """
        orderedList, idList = [], []
        for item in itemList:
            if "dpID" in cmds.listAttr(item):
                idList.append(int(cmds.getAttr(item+".dpID").split(".")[1])) #time
        if idList:
            tmpList, orderedList = zip(*sorted(zip(idList, itemList)))
        return orderedList


    def setTPose(self, *args):
        """ Set the biped arms as TPose and align leg and feet as vertical to front direction.
        """
        # clavicle/hips
        beforeCtrlList = self.ctrls.getControlNodeById("id_030_LimbClavicle")
        if beforeCtrlList:
            clavList, hipList = [], []
            for beforeCtrl in beforeCtrlList:
                if self.lang['c000_arm_before'] in beforeCtrl: #arm
                    clavList.append(beforeCtrl)
                else: #leg
                    hipList.append(beforeCtrl)
            clavList = self.getOrderedByTimeID(clavList)
            hipList = self.getOrderedByTimeID(hipList)
            cmds.xform(clavList[0], rotation=(90, 0, 90), worldSpace=True) #left clavicle
            cmds.xform(hipList[0], rotation=(90, 0, 0), worldSpace=True) #left hips
            for axis in self.dpUIinst.axisList:
                cmds.setAttr(clavList[1]+".rotate"+axis, cmds.getAttr(clavList[0]+".rotate"+axis)) #right clavicle
                cmds.setAttr(hipList[1]+".rotate"+axis, cmds.getAttr(hipList[0]+".rotate"+axis)) #right hips
        # arm/leg
        fkCtrlList = self.ctrls.getControlNodeById("id_031_LimbFk")
        if fkCtrlList:
            armList, legList = [], []
            for fkCtrl in fkCtrlList:
                if self.lang['c001_arm_main'] in fkCtrl:
                    if not fkCtrl in armList:
                        armList.append(fkCtrl)
                if self.lang['c006_leg_main'] in fkCtrl:
                    if not fkCtrl in legList:
                        legList.append(fkCtrl)
                if self.lang['c002_arm_corner'] in fkCtrl:
                    if not fkCtrl in armList:
                        armList.append(fkCtrl)
                if self.lang['c007_leg_corner'] in fkCtrl:
                    if not fkCtrl in legList:
                        legList.append(fkCtrl)
                if self.lang['c004_arm_extrem'] in fkCtrl:
                    if not fkCtrl in armList:
                        armList.append(fkCtrl)
                if self.lang['c009_leg_extrem'] in fkCtrl:
                    if not fkCtrl in legList:
                        legList.append(fkCtrl)
            armList = self.getOrderedByTimeID(armList)
            legList = self.getOrderedByTimeID(legList)
            # arm
            cmds.xform(armList[0], rotation=(90, 90, 0), worldSpace=True) #left shoulder
            cmds.xform(armList[1], rotation=(90, 90, 0), worldSpace=True) #left elbow
            cmds.xform(armList[2], rotation=(90, 90, 0), worldSpace=True) #left wrist
            cmds.xform(armList[3], rotation=(-90, 90, 0), worldSpace=True) #right shoulder
            cmds.xform(armList[4], rotation=(-90, 90, 0), worldSpace=True) #right elbow
            cmds.xform(armList[5], rotation=(-90, 90, 0), worldSpace=True) #right wrist
            # leg
            cmds.xform(legList[0], rotation=(90, 0, 90), worldSpace=True) #left leg
            cmds.xform(legList[1], rotation=(90, 0, 90), worldSpace=True) #left knee
            cmds.xform(legList[2], rotation=(0, -90, 90), worldSpace=True) #left ankle
            cmds.xform(legList[3], rotation=(-90, 0, 90), worldSpace=True) #right leg
            cmds.xform(legList[4], rotation=(-90, 0, 90), worldSpace=True) #right knee
            cmds.xform(legList[5], rotation=(0, 90, 90), worldSpace=True) #right ankle
        # fingers
        fingerCtrlList = self.ctrls.getControlNodeById("id_015_FingerMain") or []
        fingerCtrlList.extend(self.ctrls.getControlNodeById("id_016_FingerFk"))
        if fingerCtrlList:
            fingerCtrlList = [f for f in fingerCtrlList if not "_00_" in f and not self.lang['m036_thumb'] in f]
            for fingerCtrl in fingerCtrlList:
                zeroGrp = fingerCtrl.replace("_Ctrl", "_SDK_Zero_0_Grp")
                if cmds.objExists(zeroGrp):
                    cmds.setAttr(fingerCtrl+".rotateY", (-1)*cmds.getAttr(zeroGrp+".rotateY"))
        # ik
        optCtrl = self.utils.getNodeByMessage("optionCtrl")
        if optCtrl:
            if "ikFkSnap" in cmds.listAttr(optCtrl):
                self.runIkFkSnap(False)
            else:
                mel.eval('warning \"'+self.lang['m244_setTPoseIssue']+' ikFkSnap'+'\";')
        beforeCtrlList.extend(fkCtrlList)
        print(self.lang['m250_trySetTPose']+" "+", ".join(beforeCtrlList))


    def hikGetLatestNode(self, *args):
        """ Return the latest listed HIKCharacterNode.
        """
        hikList = cmds.ls(type="HIKCharacterNode")
        if hikList:
            #hikList.sort()
            return hikList[-1]


    def hikCreateCharacterDefinition(self, *args):
        """ Create humanIk character definition node.
            Returns its latest HIKCharacterNode.
        """
        hikOldList = cmds.ls(type="HIKCharacterNode")
        mel.eval("HIKCharacterControlsTool;")
        mel.eval("hikCreateDefinition;")
        self.hikNode = list(set(cmds.ls(type="HIKCharacterNode"))-set(hikOldList))[0]
        self.dpID = self.dpUIinst.customAttr.addAttr(0, [self.hikNode])[0] #dpID
        print(self.lang['m251_createdCharDefinition']+" "+self.hikNode)
        return self.hikNode
    

    def hikAssignJointsToDefinition(self, *args):
        """ Map dpAR biped joints to HumanIk character definition.
        """
        if self.hikNode:
            if self.utils.getAllGrp():
                oldRefNodeList = cmds.listConnections(self.hikNode+".Reference", source=True, destination=False)
                if not self.hikDic:
                    self.hikDic = self.hikGetDefaultMapDic()
                for hikKey in self.hikDic.keys():
                    for r in ["", "1", "2", "3", "4"]: #workaround to accept many ribbons renaming
                        if "joint"+r in self.hikDic[hikKey].keys():
                            if cmds.objExists(self.hikDic[hikKey]["joint"+r]):
                                cmds.connectAttr(self.hikDic[hikKey]["joint"+r]+".message", self.hikNode+"."+hikKey, force=True)
                                if not self.hikCharacterAttr in cmds.listAttr(self.hikDic[hikKey]["joint"+r]):
                                    cmds.addAttr(self.hikDic[hikKey]["joint"+r], longName=self.hikCharacterAttr, attributeType="message")
                                for attr in self.dpUIinst.transformAttrList:
                                    cmds.setAttr(self.hikDic[hikKey]["joint"+r]+"."+attr, lock=False)
                                break
                        else:
                            mel.eval('warning \"'+self.lang['m245_jointDefinitionIssue']+str(self.hikDic[hikKey]["joint"])+'\";')
                print(self.lang['m252_assignJointDefinition'])
                if oldRefNodeList:
                    cmds.delete(oldRefNodeList[0])
            else:
                mel.eval('warning \"'+self.lang['m246_missingDpARToRetarget']+'\";')
        else:
            mel.eval('warning \"'+self.lang['m247_missingHIKCharNode']+'\";')


    def hikMapBipedControllers(self, ikList=None, *args):
        """ Map the HumanIk biped controllers to the definition.
        """
        if self.hikNode:
            if self.utils.getAllGrp():
                if not self.hikDic:
                    self.hikDic = self.hikGetDefaultMapDic()
                for hikKey in self.hikDic.keys():
                    if not self.hikDic[hikKey]["id"] == 0: #reference
                        #ik or fk
                        ctrl = "control"
                        if ikList and hikKey in ikList:
                            ctrl = "ikCtrl"
                        if cmds.objExists(self.hikDic[hikKey][ctrl]):
                            cmds.select(self.hikDic[hikKey][ctrl])
                            mel.eval('hikControlRigSelectionChangedCallback;')
                            mel.eval('hikCustomRigAssignEffector '+str(self.hikDic[hikKey]["id"])+';')
                print(self.lang['m253_assignCtrlDefinition'])
                cmds.select(clear=True)
            else:
                mel.eval('warning \"'+self.lang['m246_missingDpARToRetarget']+'\";')
        else:
            mel.eval('warning \"'+self.lang['m247_missingHIKCharNode']+'\";')


    def hikMapBipedControllersByUI(self, *args):
        """ Ready the UI to set user defined definition to controllers as ik or fk.
            By default:
                spineMode = "spineIk"
                armMode   = "armFk"
                legMode   = "legIk"
        """
        ikList = []
        if cmds.radioCollection(self.spineModeRBC, query=True, select=True) == "spineIk":
            ikList.extend(["Spine", "Spine1", "Spine2"])
        if cmds.radioCollection(self.armModeRBC, query=True, select=True) == "armIk":
            ikList.extend(["LeftArm", "LeftForeArm", "LeftHand", "RightArm", "RightForeArm", "RightHand"])
        if cmds.radioCollection(self.legModeRBC, query=True, select=True) == "legIk":
            ikList.extend(["LeftUpLeg", "LeftLeg", "LeftFoot", "RightUpLeg", "RightLeg", "RightFoot"])
        self.hikMapBipedControllers(ikList)


    def hikCreateCustomRigCtrl(self, *args):
        """ Call humanIk to create a customRig node.
        """
        mel.eval('hikCreateCustomRig( hikGetCurrentCharacter() );')


    def hikDeleteNodes(self, *args):
        """ Remove HumanIk mocap integration from dpAR.
        """
        mel.eval('hikDeleteCustomRig( hikGetCurrentCharacter() );')
        mel.eval('hikDeleteDefinition();')
    
    
    def unmuteAutoRotate(self, *args):
        """ Reaply the clavicle and neck autoRotate behavior unmuting it.
        """
        ctrlList = self.getAutoRotateCtrlList()
        if ctrlList:
            for ctrl in ctrlList:
                self.lockAutoRotateAttr(ctrl, False)
                zeroGrp = cmds.listRelatives(ctrl, parent=True, type="transform")[0]
                for axis in self.dpUIinst.axisList:
                    cmds.mute(zeroGrp+".rotate"+axis, disable=True)
            print(self.lang['i046_remove']+" "+self.lang['m249_muteAutoRotate']+" "+", ".join(ctrlList))


    def resetDefaultPose(self, *args):
        """ Back rig to default pose calling the ResetPose validator.
        """
        if self.dpUIinst.checkOutInstanceList:
            for checkOutInst in self.dpUIinst.checkOutInstanceList:
                if "ResetPose" in str(checkOutInst):
                    checkOutInst.verbose = False
                    checkOutInst.runAction(False) #fix
                    checkOutInst.endProgress()


    def setIkFkBipedControllersByUI(self, *args):
        """ Set the ikFk attributes in the optionCtrl as the choose UI.
        """
        optCtrl = self.setCtrlMode() #fk
        if optCtrl:
            if cmds.radioCollection(self.spineModeRBC, query=True, select=True) == "spineIk":
                cmds.setAttr(optCtrl+"."+self.lang['m011_spine'].lower()+"Fk", 0)
            if cmds.radioCollection(self.armModeRBC, query=True, select=True) == "armIk":
                cmds.setAttr(optCtrl+"."+self.lang['p002_left'].lower()+self.lang['c037_arm']+"Fk", 0)
                cmds.setAttr(optCtrl+"."+self.lang['p003_right'].lower()+self.lang['c037_arm']+"Fk", 0)
            if cmds.radioCollection(self.legModeRBC, query=True, select=True) == "legIk":
                cmds.setAttr(optCtrl+"."+self.lang['p002_left'].lower()+self.lang['c006_leg_main']+"Fk", 0)
                cmds.setAttr(optCtrl+"."+self.lang['p003_right'].lower()+self.lang['c006_leg_main']+"Fk", 0)


    def hikSetCustomMap(self, id, t=None, r=None, *args):
        """ Set custom map to translate and/or rotate for the given HumanIk item ID.
        """
        mel.eval('hikCustomRigToolWidget -e -sl '+str(id)+';')
        mel.eval('hikControlRigSelectionChangedCallback;')
        mel.eval('hikUpdateCustomRigUI')
        if not t == None:
            mel.eval('hikCustomRigAddRemoveMapping( "T", '+str(t)+' );')
        if not r == None:
            mel.eval('hikCustomRigAddRemoveMapping( "R", '+str(r)+' );')
        mel.eval('hikUpdateCustomRigUI')


    def hikMapCustomElements(self, *args):
        """ Set cutom HumanIk controllers properly mapping.
        """
        fingerList = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
        for hikKey in self.hikDic.keys():
            for finger in fingerList:
                if finger in hikKey:
                    if cmds.objExists(self.hikDic[hikKey]["control"]):
                        self.hikSetCustomMap(self.hikDic[hikKey]["id"], r=1) #Finger add rotate
                        self.hikSetCustomMap(self.hikDic[hikKey]["id"], t=0) #Finger remove translate
            if "Roll" in hikKey:
                if cmds.objExists(self.hikDic[hikKey]["control"]):
                    self.hikSetCustomMap(self.hikDic[hikKey]["id"], r=1) #Ribbon add rotate
        self.hikSetCustomMap(15, t=0) #Head remove translate, let it rotate only
        self.hikSetCustomMap(8,  r=1) #Spine add rotate
        self.hikSetCustomMap(20, r=1) #Neck add rotate
        self.hikSetCustomMap(32, r=1) #Neck1 add rotate
    
    
    def hikMapCustomChest(self, *args):
        """ Set HumanIk Chest controller.
        """
        cmds.select(self.lang['m011_spine']+"_"+self.lang['c028_chest']+"A_Fk_Ctrl")
        if cmds.radioCollection(self.spineModeRBC, query=True, select=True) == "spineIk":
            cmds.select(self.lang['m011_spine']+"_"+self.lang['c028_chest']+"B_Ctrl")
        mel.eval('hikControlRigSelectionChangedCallback; hikCustomRigAssignEffector 1000;')
        cmds.select(clear=True)
    

    def hikCreateJob(self, *args):
        """ Create a scriptJob to check if the HumanIkCharacterNode will be deleted to unmute autoRotate feature.
        """
        hikCleanerCode = '''
from maya import cmds
DP_MOTIONCAPTURE_VERSION = '''+str(DP_MOTIONCAPTURE_VERSION)+'''

class HumanIKCleaner(object):
    def __init__(self, hikNode, sn, ctrlList, attrList, *args):
        self.hikNode = hikNode
        self.myself = sn
        self.ctrlList = ctrlList
        self.attrList = attrList
        cmds.scriptJob(nodeDeleted=(self.hikNode, self.jobDeletedMocap), killWithScene=False, compressUndo=True)

    def jobDeletedMocap(self, *args):
        """ Restore autoRotate feature in dpAR.
        """
        print("'''+self.lang['i046_remove']+''' HumanIk")
        self.unmuteAutoRotate()
        if cmds.objExists(self.myself):
            cmds.delete(self.myself)
            print("Deleted "+self.myself)

    def unmuteAutoRotate(self, *args):
        """ Reaply the clavicle and neck autoRotate behavior unmuting it.
        """
        if self.ctrlList:
            for ctrl in self.ctrlList:
                self.lockAutoRotateAttr(ctrl, False)
                zeroGrp = cmds.listRelatives(ctrl, parent=True, type="transform")[0]
                for axis in ["X", "Y", "Z"]:
                    cmds.mute(zeroGrp+".rotate"+axis, disable=True)
            print("'''+self.lang['i046_remove']+''' '''+self.lang['m249_muteAutoRotate']+''' "+", ".join(self.ctrlList))

    def lockAutoRotateAttr(self, ctrl, value, *args):
        """ Lock or unlock the autoRotate attribute for the given controller.
        """
        for followAttr in self.attrList:
            if followAttr in cmds.listAttr(ctrl):
                cmds.setAttr(ctrl+"."+followAttr, lock=value)
    
# fire scriptNode
for hik in cmds.ls(type="HIKCharacterNode"):
    if cmds.objExists(hik+".dpID") and cmds.getAttr(hik+".dpID") == "'''+self.dpID+'''":
        HumanIKCleaner(hik, "'''+self.hikNode+'_Cleaner_SN'+'''", '''+str(self.getAutoRotateCtrlList())+''', '''+str(self.autoRotateAttrList)+''')
'''
        sn = cmds.scriptNode(name=self.hikNode+'_Cleaner_SN', sourceType='python', scriptType=2, beforeScript=hikCleanerCode)
        self.dpUIinst.customAttr.addAttr(0, [sn]) #dpID
        cmds.scriptNode(sn, executeBefore=True)


    def hikSnapIkTimeline(self, start=None, end=None, *args):
        """ Run to all timeline and snap ik from baked fk.
        """
        optCtrl = self.utils.getNodeByMessage("optionCtrl")
        if optCtrl:
            if "ikFkSnap" in cmds.listAttr(optCtrl):
                startFrame = start
                endFrame = end
                if start == None:
                    startFrame = int(cmds.playbackOptions(query=True, minTime=True))
                if end == None:
                    endFrame = int(cmds.playbackOptions(query=True, maxTime=True))
                self.utils.setProgress("HumanIk - Snap ikFk", self.lang['m239_motionCapture'], addOne=False, addNumber=False, max=(endFrame-startFrame))
                initialTime = cmds.currentTime(query=True)
                for t in range(startFrame, endFrame+1):
                    self.utils.setProgress("Timeline")
                    cmds.currentTime(t)
                    self.runIkFkSnap()
                cmds.currentTime(initialTime)
                self.utils.setProgress(endIt=True)
