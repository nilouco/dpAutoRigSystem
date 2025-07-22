# importing libraries:
from maya import cmds
from maya import mel
from functools import partial

# global variables to this module:
CLASS_NAME = "MotionCapture"
TITLE = "m239_motionCapture"
DESCRIPTION = "m240_motionCaptureDesc"
ICON = "/Icons/dp_motionCapture.png"

DP_MOTIONCAPTURE_VERSION = 1.0


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
        # call main function:
        if self.ui:
            self.dpMotionCaptureUI(self)

    
    def dpMotionCaptureUI(self, *args):
        """ Create a window in order to load the original model and targets to be mirrored.
        """
        # creating MotionCaptureUI Window:
        self.utils.closeUI('dpMotionCaptureWindow')
        mocap_winWidth  = 320
        mocap_winHeight = 460
        dpMotionCaptureWin = cmds.window('dpMotionCaptureWindow', title="dpAutoRigSystem - "+self.lang["m239_motionCapture"]+" "+str(DP_MOTIONCAPTURE_VERSION), widthHeight=(mocap_winWidth, mocap_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)
        # creating layout:
        mocapMainLayout = cmds.formLayout('mocapMainLayout')
        mocapTabLayout = cmds.tabLayout('mocapTabLayout', innerMarginWidth=5, innerMarginHeight=5, parent=mocapMainLayout)
        cmds.formLayout('mocapMainLayout', edit=True, attachForm=((mocapTabLayout, 'top', 5), (mocapTabLayout, 'left', 0), (mocapTabLayout, 'bottom', 0), (mocapTabLayout, 'right', 0)))

        humanIkFL = cmds.formLayout('humanIkFL', numberOfDivisions=100, parent=mocapTabLayout)
        motionCaptureMainLayout = cmds.columnLayout('motionCaptureMainLayout', columnOffset=("both", 10), rowSpacing=10, parent=humanIkFL)
        cmds.separator(height=5, style="none", horizontal=True, parent=motionCaptureMainLayout)
        
        humanIkModeFL = cmds.frameLayout('humanIkModeFL', label="Ik/Fk "+self.lang['v003_mode'], collapsable=True, collapse=False, parent=motionCaptureMainLayout)
        
        # radio buttons:
        ikFkModeRCL = cmds.rowColumnLayout('ikFkModeRCL', numberOfColumns=3, columnWidth=[(1, 100), (2, 100), (3, 100)], columnAlign=[(1, 'center'), (2, 'center'), (3, 'center')], columnAttach=[(1, 'both', 5), (2, 'both', 2), (3, 'both', 5)], parent=humanIkModeFL)
        
        spineModeCL = cmds.columnLayout('spineModeCL', adjustableColumn=True, width=80, parent=ikFkModeRCL)
        self.spineModeRBC = cmds.radioCollection('self.spineModeRBC', parent=spineModeCL)
        spineIk = cmds.radioButton("spineIk", label=self.lang['m011_spine']+" Ik", annotation="spineIk")
        cmds.radioButton("spineFk", label=self.lang['m011_spine']+" FK", annotation="spineFk")
        cmds.radioCollection(self.spineModeRBC, edit=True, select=spineIk)
        
        armModeCL = cmds.columnLayout('armModeCL', adjustableColumn=True, width=80, parent=ikFkModeRCL)
        self.armModeRBC = cmds.radioCollection('self.armModeRBC', parent=armModeCL)
        cmds.radioButton("armIk", label=self.lang['m028_arm']+" Ik", annotation="armIk")
        armFk = cmds.radioButton("armFk", label=self.lang['m028_arm']+" FK", annotation="armFk")
        cmds.radioCollection(self.armModeRBC, edit=True, select=armFk)

        legModeCL = cmds.columnLayout('legModeCL', adjustableColumn=True, width=80, parent=ikFkModeRCL)
        self.legModeRBC = cmds.radioCollection('self.legModeRBC', parent=legModeCL)
        legIk = cmds.radioButton("legIk", label=self.lang['m030_leg']+" Ik", annotation="legIk")
        cmds.radioButton("legFk", label=self.lang['m030_leg']+" FK", annotation="legFk")
        cmds.radioCollection(self.legModeRBC, edit=True, select=legIk)

        cmds.separator(height=5, style="single", horizontal=True, parent=motionCaptureMainLayout)
        cmds.text(label="Settings", parent=motionCaptureMainLayout)

        cmds.button(label="1 - Set FK mode", annotation="WIP", width=220, command=partial(self.setCtrlMode, 1), parent=motionCaptureMainLayout)
        cmds.button(label="2 - Mute autoRotate (clavicle, neck)", annotation="WIP", width=220, command=self.muteAutoRotate, parent=motionCaptureMainLayout)
        cmds.button(label="3 - Set T-Pose", annotation="WIP", width=220, command=self.setTPose, parent=motionCaptureMainLayout)
        cmds.button(label="4 - Create Character Definition", annotation="WIP", width=220, command=self.hikCreateCharacterDefinition, parent=motionCaptureMainLayout)
        cmds.button(label="5 - Assign joints to definition", annotation="WIP", width=220, command=self.hikAssignJointsToDefinition, parent=motionCaptureMainLayout)
        cmds.button(label="6 - Create custom rig control", annotation="WIP", width=220, command=self.hikCreateCustomRigCtrl, parent=motionCaptureMainLayout)
        cmds.button(label="7 - Set controllers", annotation="WIP", width=220, command=self.hikMapBipedControllersByUI, parent=motionCaptureMainLayout)
        cmds.button(label="8 - Set defined ikFk mode", annotation="WIP", width=220, command=self.setIkFkBipedControllersByUI, parent=motionCaptureMainLayout)
        
        cmds.separator(height=5, style="in", horizontal=True, parent=motionCaptureMainLayout)
        cmds.separator(height=5, style="in", horizontal=True, parent=motionCaptureMainLayout)

        cmds.button(label="BACK 1: remove mocap", annotation="WIP", width=220, command=self.hikRemoveMocap, parent=motionCaptureMainLayout)
        cmds.button(label="BACK 2: redo autoRotate", annotation="WIP", width=220, command=self.redoAutoRotate, parent=motionCaptureMainLayout)
        cmds.button(label="BACK 3: reset default pose", annotation="WIP", width=220, command=self.resetDefaultPose, parent=motionCaptureMainLayout)
        cmds.button(label="BACK 4: set Ik mode", annotation="WIP", width=220, command=partial(self.setCtrlMode, 0), parent=motionCaptureMainLayout)
        
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
                                      "joint"   : self.lang['m011_spine']+"_01_Jnt",
                                      "control" : self.lang['m011_spine']+"_"+self.lang['c027_hips']+"A_Fk_Ctrl",
                                      "ikCtrl"  : self.lang['m011_spine']+"_"+self.lang['c027_hips']+"B_Ctrl"},
                "Spine1"           : {"id"      : 23,
                                      "joint"   : self.lang['m011_spine']+"_02_Jnt",
                                      "control" : self.lang['m011_spine']+"_"+self.lang['c029_middle']+"1_Fk_Ctrl",
                                      "ikCtrl"  : self.lang['m011_spine']+"_"+self.lang['c029_middle']+"1_Ctrl"},
                "Spine2"           : {"id"      : 24,
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
                "LeftHandIndex1"   : {"id"      : 54,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_00_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_00_Ctrl"},
                "LeftHandIndex2"   : {"id"      : 55,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_01_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_01_Ctrl"},
                "LeftHandIndex3"   : {"id"      : 56,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_02_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_02_Ctrl"},
                "LeftHandIndex4"   : {"id"      : 57,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_03_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_03_Ctrl"},
                "LeftHandMiddle1"  : {"id"      : 58,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_00_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_00_Ctrl"},
                "LeftHandMiddle2"  : {"id"      : 59,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_01_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_01_Ctrl"},
                "LeftHandMiddle3"  : {"id"      : 60,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_02_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_02_Ctrl"},
                "LeftHandMiddle4"  : {"id"      : 61,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_03_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_03_Ctrl"},
                "LeftHandRing1"    : {"id"      : 62,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_00_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_00_Ctrl"},
                "LeftHandRing2"    : {"id"      : 63,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_01_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_01_Ctrl"},
                "LeftHandRing3"    : {"id"      : 64,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_02_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_02_Ctrl"},
                "LeftHandRing4"    : {"id"      : 65,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_03_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_03_Ctrl"},
                "LeftHandPinky1"   : {"id"      : 66,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_00_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_00_Ctrl"},
                "LeftHandPinky2"   : {"id"      : 67,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_01_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_01_Ctrl"},
                "LeftHandPinky3"   : {"id"      : 68,
                                      "joint"   : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_02_Jnt",
                                      "control" : self.lang['p002_left']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_02_Ctrl"},
                "LeftHandPinky4"   : {"id"      : 69,
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
                "RightHandIndex1"  : {"id"      : 78,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_00_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_00_Ctrl"},
                "RightHandIndex2"  : {"id"      : 79,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_01_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_01_Ctrl"},
                "RightHandIndex3"  : {"id"      : 80,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_02_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_02_Ctrl"},
                "RightHandIndex4"  : {"id"      : 81,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_03_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m032_index']+"_03_Ctrl"},
                "RightHandMiddle1" : {"id"      : 82,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_00_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_00_Ctrl"},
                "RightHandMiddle2" : {"id"      : 83,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_01_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_01_Ctrl"},
                "RightHandMiddle3" : {"id"      : 84,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_02_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_02_Ctrl"},
                "RightHandMiddle4" : {"id"      : 85,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_03_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m033_middle']+"_03_Ctrl"},
                "RightHandRing1"   : {"id"      : 86,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_00_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_00_Ctrl"},
                "RightHandRing2"   : {"id"      : 87,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_01_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_01_Ctrl"},
                "RightHandRing3"   : {"id"      : 88,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_02_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_02_Ctrl"},
                "RightHandRing4"   : {"id"      : 89,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_03_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m034_ring']+"_03_Ctrl"},
                "RightHandPinky1"  : {"id"      : 90,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_00_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_00_Ctrl"},
                "RightHandPinky2"  : {"id"      : 91,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_01_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_01_Ctrl"},
                "RightHandPinky3"  : {"id"      : 92,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_02_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_02_Ctrl"},
                "RightHandPinky4"  : {"id"      : 93,
                                      "joint"   : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_03_Jnt",
                                      "control" : self.lang['p003_right']+"_"+self.lang['m007_finger']+"_"+self.lang['m035_pinky']+"_03_Ctrl"},
                "Neck"             : {"id"      : 20,
                                      "joint"   : self.lang['c024_head']+"_"+self.lang['c023_neck']+"_00_Jnt",
                                      "control" : self.lang['c024_head']+"_"+self.lang['c023_neck']+"_00_Ctrl"},
                "Head"             : {"id"      : 15,
                                      "joint"   : self.lang['c024_head']+"_00_"+self.lang['c024_head']+"_Jnt",
                                      "joint1"  : self.lang['c024_head']+"_01_"+self.lang['c024_head']+"_Jnt",
                                      "joint2"  : self.lang['c024_head']+"_02_"+self.lang['c024_head']+"_Jnt",
                                      "control" : self.lang['c024_head']+"_"+self.lang['c024_head']+"_Ctrl"},
        }


    def setIkFk(self, optCtrl, mode, *args):
        """ Set ik or fk.
        """
        userDefAttrList = cmds.listAttr(optCtrl, userDefined=True)
        if userDefAttrList:
            for attr in userDefAttrList:
                if attr.endswith("Fk"):
                    cmds.setAttr(optCtrl+"."+attr, mode)


    def setCtrlMode(self, mode=1, *args):
        """ Set dpAR rig to IK or Fk mode.
            Default: mode = 1 = Fk.
        """
        optCtrl = self.utils.getNodeByMessage("optionCtrl")
        if optCtrl:
            self.setIkFk(optCtrl, mode)
            return optCtrl
        else:
            print("There isn't an Option_Ctrl to setup Ik or Fk mode in the rig, sorry.")


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


    def setTPose(self, *args):
        """ Set the biped arms as TPose.
        """
        # clavicle
        beforeCtrlList = self.ctrls.getControlNodeById("id_030_LimbClavicle")
        if beforeCtrlList:
            clavList, dpIDList = [], []
            for beforeCtrl in beforeCtrlList:
                if self.lang['c000_arm_before'] in beforeCtrl: #arm
                    clavList.append(beforeCtrl)
                    if "dpID" in cmds.listAttr(beforeCtrl):
                        dpIDList.append(int(cmds.getAttr(beforeCtrl+".dpID").split(".")[1]))
            lClav = clavList[1]
            rClav = clavList[0]
            if (dpIDList and dpIDList[0] < dpIDList[1]) or clavList[0].startswith(self.lang['p002_left']): #listed left side first
                lClav = clavList[0]
                rClav = clavList[1]
            cmds.xform(lClav, rotation=(90, 0, 90), worldSpace=True) #left
            for axis in self.dpUIinst.axisList:
                cmds.setAttr(rClav+".rotate"+axis, cmds.getAttr(lClav+".rotate"+axis)) #right
        # arm
        fkCtrlList = self.ctrls.getControlNodeById("id_031_LimbFk")
        if fkCtrlList:
            armList, dpIDArmList = [], []
            for i in range(0, 4):
                for fkCtrl in fkCtrlList:
                    if i == 0:
                        if self.lang['c001_arm_main'] in fkCtrl:
                            if not fkCtrl in armList:
                                armList.append(fkCtrl)
                                if "dpID" in cmds.listAttr(fkCtrl):
                                    dpIDArmList.append(int(cmds.getAttr(fkCtrl+".dpID").split(".")[1]))
                    elif i == 1:
                        if self.lang['c002_arm_corner'] in fkCtrl:
                            if not fkCtrl in armList:
                                armList.append(fkCtrl)
                                if "dpID" in cmds.listAttr(fkCtrl):
                                    dpIDArmList.append(int(cmds.getAttr(fkCtrl+".dpID").split(".")[1]))
                    elif i == 2:
                        if self.lang['c004_arm_extrem'] in fkCtrl:
                            if not fkCtrl in armList:
                                armList.append(fkCtrl)
                                if "dpID" in cmds.listAttr(fkCtrl):
                                    dpIDArmList.append(int(cmds.getAttr(fkCtrl+".dpID").split(".")[1]))
            if (dpIDArmList and dpIDArmList[0] < dpIDArmList[2]) or armList[0].startswith(self.lang['p002_left']):
                cmds.xform(armList[0], rotation=(90, 90, 0), worldSpace=True) #left
                cmds.xform(armList[2], rotation=(90, 90, 0), worldSpace=True) #left
                cmds.xform(armList[4], rotation=(90, 90, 0), worldSpace=True) #left
                cmds.xform(armList[1], rotation=(-90, 90, 0), worldSpace=True) #right
                cmds.xform(armList[3], rotation=(-90, 90, 0), worldSpace=True) #right
                cmds.xform(armList[5], rotation=(-90, 90, 0), worldSpace=True) #right
            else:
                cmds.xform(armList[0], rotation=(-90, 90, 0), worldSpace=True) #right
                cmds.xform(armList[2], rotation=(-90, 90, 0), worldSpace=True) #right
                cmds.xform(armList[4], rotation=(-90, 90, 0), worldSpace=True) #right
                cmds.xform(armList[1], rotation=(90, 90, 0), worldSpace=True) #left
                cmds.xform(armList[3], rotation=(90, 90, 0), worldSpace=True) #left
                cmds.xform(armList[5], rotation=(90, 90, 0), worldSpace=True) #left
        # ik
        optCtrl = self.utils.getNodeByMessage("optionCtrl")
        if optCtrl:
            if "ikFkSnap" in cmds.listAttr(optCtrl):
                cmds.setAttr(optCtrl+".ikFkSnap", 1)
                self.setIkFk(optCtrl, 0)
                cmds.setAttr(optCtrl+".ikFkSnap", 0)
                self.setIkFk(optCtrl, 1)
            else:
                print("Need to set the TPose for the ik controllers.")


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
                            print("There's no object to set joint definition:", str(self.hikDic[hikKey]["joint"]))
                if oldRefNodeList:
                    cmds.delete(oldRefNodeList[0])
            else:
                print("There's no dpAR in the scene to continue the HumanIk biped retargeting, sorry.")
        else:
            print("There's no HIKCharacterNode in the scene to use. Create one to continue, please.")


    def hikMapBipedControllers(self, ikList=None, *args):
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
                            mel.eval('hikCustomRigAssignEffector '+str(self.hikDic[hikKey]["id"])+';')
                cmds.select(clear=True)
            else:
                print("There's no dpAR in the scene to continue the HumanIk biped retargeting, sorry.")
        else:
            print("There's no HIKCharacterNode in the scene to use. Create one to continue, please.")


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


    def hikRemoveMocap(self, *args):
        """ Remove HumanIk mocap integration from dpAR.
        """
        mel.eval('hikDeleteCustomRig( hikGetCurrentCharacter() );')
        mel.eval('hikDeleteDefinition();')
    
    
    def redoAutoRotate(self, *args):
        """ Reaply the clavicle and neck autoRotate behavior unmuting it.
        """
        ctrlList = self.getAutoRotateCtrlList()
        if ctrlList:
            for ctrl in ctrlList:
                self.lockAutoRotateAttr(ctrl, False)
                zeroGrp = cmds.listRelatives(ctrl, parent=True, type="transform")[0]
                for axis in self.dpUIinst.axisList:
                    cmds.mute(zeroGrp+".rotate"+axis, disable=True)


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
