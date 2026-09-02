# importing libraries:
from maya import cmds
from ..base import base
from importlib import reload

# global variables to this module:    
CLASS_NAME = "FingerHandPose"
TITLE = "m256_fingerHandPose"
DESCRIPTION = "m257_fingerHandPoseDesc"
WIKI = "06-‐-Tools#-finger-hand-pose"



class FingerHandPose(base.BaseLibrary):
    def __init__(self, ar):
        base.BaseLibrary.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(base)
        self.old_drivenkeys = cmds.ls(selection=False, type=self.ar.data.drivenkey_types)
        self.sides = ["", self.ar.data.lang['p002_left']+"_", self.ar.data.lang['p003_right']+"_"]
        self.arm_name = self.ar.data.lang['c037_arm']
        self.wrist_name = self.ar.data.lang['c004_arm_extrem']
        self.finger_index_name = self.ar.data.lang['m007_finger']+"_"+self.ar.data.lang['m032_index']
        self.finger_middle_name = self.ar.data.lang['m007_finger']+"_"+self.ar.data.lang['m033_middle']
        self.finger_ring_name = self.ar.data.lang['m007_finger']+"_"+self.ar.data.lang['m034_ring']
        self.finger_pinky_name = self.ar.data.lang['m007_finger']+"_"+self.ar.data.lang['m035_pinky']
        self.fingers = [self.finger_index_name, self.finger_middle_name, self.finger_ring_name, self.finger_pinky_name]
        self.curl_name = self.ar.data.lang['c128_curl']
        self.side_name = self.ar.data.lang['c121_side'].lower()
        self.scratch_name = self.ar.data.lang['c129_scratch']
        self.spread_name = self.ar.data.lang['c130_spread']
        self.relax_name = self.ar.data.lang['c131_relax']
        self.hand_attributes = [self.curl_name, self.side_name, self.scratch_name, self.spread_name, self.relax_name]
        
        
    def build_tool(self, *args):
        self.run_finger_hand_pose()


    def run_finger_hand_pose(self):
        self.to_ids = []
        hand_ctrls = []
        # find nodes
        all_grp = self.ar.utils.get_all_grp()
        if all_grp:
            if cmds.getAttr(all_grp+".dpFingerCount"): #it has fingers
                for side in self.sides:
                    hand_ctrl = side+self.arm_name+"_"+self.wrist_name+"_ToParent_Ctrl"
                    if cmds.objExists(hand_ctrl): #there's an arm
                        hand_ctrls.append(hand_ctrl)
                        for attr in self.hand_attributes:
                            if not attr in cmds.listAttr(hand_ctrl):
                                cmds.addAttr(hand_ctrl, longName=attr, attributeType="double", minValue=-1, maxValue=1, defaultValue=0, keyable=True)
                        for f, finger in enumerate(self.fingers):
                            for n in range(1, 4):
                                if cmds.objExists(side+finger+"_"+str(n).zfill(2)+"_Ctrl"):
                                    finger_grp = side+finger+"_%02d_Pose_Grp"%(n)
                                    if not cmds.objExists(finger_grp):
                                        finger_grp = cmds.group(side+finger+"_"+str(n).zfill(2)+"_Ctrl", name=side+finger+"_%02d_Pose_Grp"%(n))
                                        cmds.xform(finger_grp, rotatePivot=cmds.xform(side+finger+"_"+str(n).zfill(2)+"_Ctrl", query=True, rotatePivot=True, worldSpace=True), worldSpace=True)
                                        self.to_ids.append(finger_grp)
                                    # Curl
                                    cmds.setDrivenKeyframe(finger_grp+".rotateY", currentDriver=hand_ctrl+"."+self.curl_name, driverValue=-1, value=-90)
                                    cmds.setDrivenKeyframe(finger_grp+".rotateY", currentDriver=hand_ctrl+"."+self.curl_name, driverValue=0, value=0)
                                    cmds.setDrivenKeyframe(finger_grp+".rotateY", currentDriver=hand_ctrl+"."+self.curl_name, driverValue=1, value=90)
                                    # Side
                                    cmds.setDrivenKeyframe(finger_grp+".rotateX", currentDriver=hand_ctrl+"."+self.side_name, driverValue=-1, value=-45)
                                    cmds.setDrivenKeyframe(finger_grp+".rotateX", currentDriver=hand_ctrl+"."+self.side_name, driverValue=0, value=0)
                                    cmds.setDrivenKeyframe(finger_grp+".rotateX", currentDriver=hand_ctrl+"."+self.side_name, driverValue=1, value=45)
                                    # Relax
                                    cmds.setDrivenKeyframe(finger_grp+".rotateY", currentDriver=hand_ctrl+"."+self.relax_name, driverValue=-1, value=(-1*n-f)*(f+1)-10)
                                    cmds.setDrivenKeyframe(finger_grp+".rotateY", currentDriver=hand_ctrl+"."+self.relax_name, driverValue=0, value=0)
                                    cmds.setDrivenKeyframe(finger_grp+".rotateY", currentDriver=hand_ctrl+"."+self.relax_name, driverValue=1, value=40*(1/(n*(f+1))))
                            # Scratch
                            if cmds.objExists(side+finger+"_01_Pose_Grp"):
                                cmds.setDrivenKeyframe(side+finger+"_01_Pose_Grp.rotateY", currentDriver=hand_ctrl+"."+self.scratch_name, driverValue=-1, value=60)
                                cmds.setDrivenKeyframe(side+finger+"_01_Pose_Grp.rotateY", currentDriver=hand_ctrl+"."+self.scratch_name, driverValue=0, value=0)
                                cmds.setDrivenKeyframe(side+finger+"_01_Pose_Grp.rotateY", currentDriver=hand_ctrl+"."+self.scratch_name, driverValue=1, value=-60)
                            if cmds.objExists(side+finger+"_02_Pose_Grp"):
                                cmds.setDrivenKeyframe(side+finger+"_02_Pose_Grp.rotateY", currentDriver=hand_ctrl+"."+self.scratch_name, driverValue=-1, value=-60)
                                cmds.setDrivenKeyframe(side+finger+"_02_Pose_Grp.rotateY", currentDriver=hand_ctrl+"."+self.scratch_name, driverValue=0, value=0)
                                cmds.setDrivenKeyframe(side+finger+"_02_Pose_Grp.rotateY", currentDriver=hand_ctrl+"."+self.scratch_name, driverValue=1, value=60)
                            if cmds.objExists(side+finger+"_03_Pose_Grp"):
                                cmds.setDrivenKeyframe(side+finger+"_03_Pose_Grp.rotateY", currentDriver=hand_ctrl+"."+self.scratch_name, driverValue=-1, value=-60)
                                cmds.setDrivenKeyframe(side+finger+"_03_Pose_Grp.rotateY", currentDriver=hand_ctrl+"."+self.scratch_name, driverValue=0, value=0)
                                cmds.setDrivenKeyframe(side+finger+"_03_Pose_Grp.rotateY", currentDriver=hand_ctrl+"."+self.scratch_name, driverValue=1, value=60)
                        # Spread
                        if cmds.objExists(side+self.finger_index_name+"_01_Pose_Grp"):
                            cmds.setDrivenKeyframe(side+self.finger_index_name+"_01_Pose_Grp.rotateX", currentDriver=hand_ctrl+"."+self.spread_name, driverValue=-1, value=-45)
                            cmds.setDrivenKeyframe(side+self.finger_index_name+"_01_Pose_Grp.rotateX", currentDriver=hand_ctrl+"."+self.spread_name, driverValue=0, value=0)
                            cmds.setDrivenKeyframe(side+self.finger_index_name+"_01_Pose_Grp.rotateX", currentDriver=hand_ctrl+"."+self.spread_name, driverValue=1, value=10)
                        if cmds.objExists(side+self.finger_middle_name+"_01_Pose_Grp"):
                            cmds.setDrivenKeyframe(side+self.finger_middle_name+"_01_Pose_Grp.rotateX", currentDriver=hand_ctrl+"."+self.spread_name, driverValue=-1, value=-20)
                            cmds.setDrivenKeyframe(side+self.finger_middle_name+"_01_Pose_Grp.rotateX", currentDriver=hand_ctrl+"."+self.spread_name, driverValue=0, value=0)
                            cmds.setDrivenKeyframe(side+self.finger_middle_name+"_01_Pose_Grp.rotateX", currentDriver=hand_ctrl+"."+self.spread_name, driverValue=1, value=5)
                        if cmds.objExists(side+self.finger_ring_name+"_01_Pose_Grp"):
                            cmds.setDrivenKeyframe(side+self.finger_ring_name+"_01_Pose_Grp.rotateX", currentDriver=hand_ctrl+"."+self.spread_name, driverValue=-1, value=5)
                            cmds.setDrivenKeyframe(side+self.finger_ring_name+"_01_Pose_Grp.rotateX", currentDriver=hand_ctrl+"."+self.spread_name, driverValue=0, value=0)
                            cmds.setDrivenKeyframe(side+self.finger_ring_name+"_01_Pose_Grp.rotateX", currentDriver=hand_ctrl+"."+self.spread_name, driverValue=1, value=-5)
                        if cmds.objExists(side+self.finger_pinky_name+"_01_Pose_Grp"):
                            cmds.setDrivenKeyframe(side+self.finger_pinky_name+"_01_Pose_Grp.rotateX", currentDriver=hand_ctrl+"."+self.spread_name, driverValue=-1, value=45)
                            cmds.setDrivenKeyframe(side+self.finger_pinky_name+"_01_Pose_Grp.rotateX", currentDriver=hand_ctrl+"."+self.spread_name, driverValue=0, value=0)
                            cmds.setDrivenKeyframe(side+self.finger_pinky_name+"_01_Pose_Grp.rotateX", currentDriver=hand_ctrl+"."+self.spread_name, driverValue=1, value=-10)
                if hand_ctrls:
                    current_drivenkeys = cmds.ls(selection=False, type=self.ar.data.drivenkey_types)
                    new_drivenkeys = current_drivenkeys
                    if self.old_drivenkeys:
                        new_drivenkeys = list(set(current_drivenkeys) - set(self.old_drivenkeys))
                    self.to_ids.extend(new_drivenkeys)
                    self.ar.custom_attr.add_attr(0, self.to_ids) #dpID
                    if self.ar.data.ui_state: #verbose
                        cmds.select(hand_ctrls)
                        if not self.ar.data.rebuilding:
                            self.ar.logger.infoWin(TITLE, 'i363_addedFingerHandPose', None, 'center', 200, 120)
