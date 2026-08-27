#import libraries
from maya import cmds
from functools import partial


class MotionCaptureUI(object):
    def __init__(self, ar):
        self.ar = ar
    
    
    def create_ui(self, app):
        """ This is the main method to load the Motion Capture UI.
        """
        self.app = app
        # creating MotionCaptureUI Window:
        self.ar.utils.close_ui('dpMotionCaptureWindow')
        width  = 280
        height = 470
        cmds.window('dpMotionCaptureWindow', title=self.ar.data.lang["m239_motionCapture"]+" "+str(self.ar.data.version), widthHeight=(width, height), menuBar=False, sizeable=False, minimizeButton=True, maximizeButton=False, menuBarVisible=False, titleBar=True)
        # creating layout:
        cmds.formLayout('mocap_main_fl')
        cmds.tabLayout('mocap_tl', innerMarginWidth=5, innerMarginHeight=5, parent='mocap_main_fl')
        cmds.formLayout('mocap_main_fl', edit=True, attachForm=(('mocap_tl', 'top', 5), ('mocap_tl', 'left', 0), ('mocap_tl', 'bottom', 0), ('mocap_tl', 'right', 0)))
        cmds.formLayout('mocap_hik_fl', numberOfDivisions=100, parent='mocap_tl')
        cmds.columnLayout('mocap_cl', columnOffset=("both", 10), rowSpacing=10, parent='mocap_hik_fl')
        cmds.separator(height=5, style="none", horizontal=True, parent='mocap_cl')
        cmds.checkBox('mocap_map_ribbon_cb', label=self.ar.data.lang['i361_mapRibbon'], value=False, parent='mocap_cl')
        cmds.frameLayout('mocap_hik_mode_fl', label="Ik/Fk "+self.ar.data.lang['v003_mode'], collapsable=True, collapse=False, parent='mocap_cl')
        # radio buttons:
        cmds.rowColumnLayout('mocap_ikfk_mode_rcl', numberOfColumns=3, columnWidth=[(1, 90), (2, 80), (3, 70)], columnAlign=[(1, 'center'), (2, 'center'), (3, 'center')], columnAttach=[(1, 'both', 5), (2, 'both', 5), (3, 'both', 5)], parent='mocap_hik_mode_fl')
        # spine
        cmds.columnLayout('mocap_spine_mode_cl', adjustableColumn=True, width=80, parent='mocap_ikfk_mode_rcl')
        cmds.radioCollection('mocap_spine_mode_rc', parent='mocap_spine_mode_cl')
        cmds.radioButton('mocap_spine_ik_rb', label=self.ar.data.lang['m011_spine']+" Ik", annotation="spineIk")
        cmds.radioButton('mocap_spine_fk_rb', label=self.ar.data.lang['m011_spine']+" FK", annotation="spineFk")
        cmds.radioCollection('mocap_spine_mode_rc', edit=True, select='mocap_spine_ik_rb')
        # arm
        cmds.columnLayout('mocap_arm_mode_cl', adjustableColumn=True, width=80, parent='mocap_ikfk_mode_rcl')
        cmds.radioCollection('mocap_arm_mode_rc', parent='mocap_arm_mode_cl')
        cmds.radioButton("mocap_arm_ik_rb", label=self.ar.data.lang['m028_arm']+" Ik", annotation="armIk")
        cmds.radioButton("mocap_arm_fk_rb", label=self.ar.data.lang['m028_arm']+" FK", annotation="armFk")
        cmds.radioCollection('mocap_arm_mode_rc', edit=True, select="mocap_arm_fk_rb")
        # leg
        cmds.columnLayout('mocap_leg_mode_cl', adjustableColumn=True, width=80, parent='mocap_ikfk_mode_rcl')
        cmds.radioCollection('mocap_leg_mode_rc', parent='mocap_leg_mode_cl')
        cmds.radioButton("mocap_leg_ik_rb", label=self.ar.data.lang['m030_leg']+" Ik", annotation="legIk")
        cmds.radioButton("mocap_leg_fk_rb", label=self.ar.data.lang['m030_leg']+" FK", annotation="legFk")
        cmds.radioCollection('mocap_leg_mode_rc', edit=True, select="mocap_leg_fk_rb")
        cmds.separator(parent='mocap_cl')
        # processes buttons
        cmds.text('mocap_processes_txt', label=self.ar.data.lang['i292_processes'], parent='mocap_cl')
        cmds.button('mocap_prepare_tpose_btn', label=self.ar.data.lang['m241_prepareTPose'], annotation="prepare_t_pose", width=240, command=self.app.prepare_t_pose, parent='mocap_cl')
        cmds.button('mocap_retargeting_btn', label=self.ar.data.lang['m242_retargeting']+" HumanIk", annotation="retargetHumanIk", width=240, command=self.app.hik_retarget, parent='mocap_cl')
        cmds.button('mocap_reset_pose_btn', label=self.ar.data.lang['v032_resetPose'], annotation="resetPose", width=240, command=self.app.reset_default_pose, parent='mocap_cl')
        # animation buttons
        cmds.separator(style='in', height=10, width=240, parent='mocap_cl')
        cmds.text('mocap_animation_txt', label=self.ar.data.lang['i185_animation'], parent='mocap_cl')
        cmds.button('mocap_snap_ik_from_baked_fk_btn', label=self.ar.data.lang['i360_snapIkFromBakedFk'], annotation="Snap Ik timeline", width=240, command=self.app.hik_snap_ik_timeline, parent='mocap_cl')
        # clear buttons
        cmds.separator(style='in', height=10, width=240, parent='mocap_cl')
        cmds.text('mocap_cleanup_txt', label=self.ar.data.lang['v096_cleanup'], parent='mocap_cl')
        cmds.button('mocap_remove_hik_btn', label=self.ar.data.lang['i046_remove']+" HumanIk", annotation="removeHumanIk", width=240, command=self.app.hik_remove_mocap, parent='mocap_cl')
        cmds.tabLayout('mocap_tl', edit=True, tabLabel=(('mocap_hik_fl', 'HumanIk')))
        # call Window:
        cmds.showWindow('dpMotionCaptureWindow')


    def get_ik_modes_from_ui(self):
        """ Ready the UI to set user defined definition to controllers as ik or fk.
            By default:
                spineMode = "spineIk"
                armMode   = "armFk"
                legMode   = "legIk"
        """
        iks = []
        if cmds.radioCollection('mocap_spine_mode_rc', query=True, select=True) == "spineIk":
            iks.extend(["Spine", "Spine1", "Spine2"])
        if cmds.radioCollection('mocap_arm_mode_rc', query=True, select=True) == "armIk":
            iks.extend(["LeftArm", "LeftForeArm", "LeftHand", "RightArm", "RightForeArm", "RightHand"])
        if cmds.radioCollection('mocap_leg_mode_rc', query=True, select=True) == "legIk":
            iks.extend(["LeftUpLeg", "LeftLeg", "LeftFoot", "RightUpLeg", "RightLeg", "RightFoot"])
        return iks
