# importing libraries:
from maya import cmds
from maya import mel

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
        self.ui = ui
        self.hikCharacterAttr = "Character"
        self.hikNode = self.hikGetLatestNode()
        print("self.hikNode starts =", self.hikNode)
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
        dpMotionCaptureWin = cmds.window('dpMotionCaptureWindow', title="dpAutoRigSystem - "+self.dpUIinst.lang["m239_motionCapture"]+" "+str(DP_MOTIONCAPTURE_VERSION), widthHeight=(mocap_winWidth, mocap_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)
        # creating layout:
        mocapMainLayout = cmds.formLayout('mocapMainLayout')
        mocapTabLayout = cmds.tabLayout('mocapTabLayout', innerMarginWidth=5, innerMarginHeight=5, parent=mocapMainLayout)
        cmds.formLayout('mocapMainLayout', edit=True, attachForm=((mocapTabLayout, 'top', 5), (mocapTabLayout, 'left', 0), (mocapTabLayout, 'bottom', 0), (mocapTabLayout, 'right', 0)))

        humaIkFL = cmds.formLayout('humaIkFL', numberOfDivisions=100, parent=mocapTabLayout)
        motionCaptureMainLayout = cmds.columnLayout('motionCaptureMainLayout', columnOffset=("both", 10), rowSpacing=10, parent=humaIkFL)
        cmds.separator(height=5, style="none", horizontal=True, parent=motionCaptureMainLayout)
        
        
        cmds.separator(height=5, style="single", horizontal=True, parent=motionCaptureMainLayout)
        cmds.text(label="WIP", parent=motionCaptureMainLayout)
        
#        cmds.button(label=self.dpUIinst.lang['m241_createSkeleton'], annotation="WIP", width=220, command=self.hikCreateSkeleton, parent=motionCaptureMainLayout)
        cmds.button(label="Create Character Definition", annotation="WIP", width=220, command=self.hikCreateCharacterDefinition, parent=motionCaptureMainLayout)
        cmds.button(label="Assign joints to definition", annotation="WIP", width=220, command=self.hikAssignJointsToDefinition, parent=motionCaptureMainLayout)
        cmds.button(label="Create custom rig control", annotation="WIP", width=220, command=self.hikCreateCustomRigCtrl, parent=motionCaptureMainLayout)
        cmds.button(label=self.dpUIinst.lang['m242_mapBipedControllers'], annotation="WIP", width=220, command=self.hikMapBipedControllers, parent=motionCaptureMainLayout)
        cmds.button(label="Lock definition = NO???", annotation="WIP", width=220, command=self.hikLockDefinition, parent=motionCaptureMainLayout)
        
        cmds.tabLayout(mocapTabLayout, edit=True, tabLabel=((humaIkFL, 'HumanIk')))
        # call Window:
        cmds.showWindow(dpMotionCaptureWin)
    

    def hikGetDefaultMapDic(self, *args):
        """ Returns the default hik controllers mapping dictionary.
        """
        return {
                "Reference"        : {"id"      : 0,
                                      "joint"   : "Root_Ctrl",
                                      "control" : "Root_Ctrl"},
                "Hips"             : {"id"      : 1,
                                      "joint"   : "Spine_00_Base_Jnt",
                                      "control" : "Spine_HipsA_Ctrl"},
                "LeftUpLeg"        : {"id"      : 2,
                                      "joint"   : "L_Leg_Leg_Jxt",
                                      "control" : "L_Leg_Leg_Fk_Ctrl"},
                "LeftLeg"          : {"id"      : 3,
                                      "joint"   : "L_Leg_Knee_Jxt",
                                      "control" : "L_Leg_Knee_Fk_Ctrl"},
                "LeftFoot"         : {"id"      : 4,
                                      "joint"   : "L_Foot_Ankle_Jnt",
                                      "control" : "L_Leg_Ankle_Fk_Ctrl"},
                "LeftToeBase"      : {"id"      : 16,
                                      "joint"   : "L_Foot_Middle_Jnt",
                                      "control" : "L_Foot_Middle_Ctrl"},
                "RightUpLeg"       : {"id"      : 5,
                                      "joint"   : "R_Leg_Leg_Jxt",
                                      "control" : "R_Leg_Leg_Fk_Ctrl"},
                "RightLeg"         : {"id"      : 6,
                                      "joint"   : "R_Leg_Knee_Jxt",
                                      "control" : "R_Leg_Knee_Fk_Ctrl"},
                "RightFoot"        : {"id"      : 7,
                                      "joint"   : "R_Foot_Ankle_Jnt",
                                      "control" : "R_Leg_Ankle_Fk_Ctrl"},
                "RightToeBase"     : {"id"      : 17,
                                      "joint"   : "R_Foot_Middle_Jnt",
                                      "control" : "R_Foot_Middle_Ctrl"},
                "Spine"            : {"id"      : 8,
                                      "joint"   : "Spine_01_Jnt",
                                      "control" : "Spine_HipsA_Fk_Ctrl"},
                "Spine1"           : {"id"      : 23,
                                      "joint"   : "Spine_02_Jnt",
                                      "control" : "Spine_Middle1_Fk_Ctrl"},
                "Spine2"           : {"id"      : 24,
                                      "joint"   : "Spine_04_Tip_Jnt",
                                      "control" : "Spine_ChestA_Fk_Ctrl"},
                "LeftShoulder"     : {"id"      : 18,
                                      "joint"   : "L_Arm_00_Clavicle_Jnt",
                                      "control" : "L_Arm_Clavicle_Ctrl"},
                "LeftArm"          : {"id"      : 9,
                                      "joint"   : "L_Arm_Shoulder_Jxt",
                                      "control" : "L_Arm_Shoulder_Fk_Ctrl"},
                "LeftForeArm"      : {"id"      : 10,
                                      "joint"   : "L_Arm_Elbow_Jxt",
                                      "control" : "L_Arm_Elbow_Fk_Ctrl"},
                "LeftHand"         : {"id"      : 11,
                                      "joint"   : "L_Arm_13_Wrist_Jnt",
                                      "control" : "L_Arm_Wrist_Fk_Ctrl"},
                "LeftHandThumb1"   : {"id"      : 50,
                                      "joint"   : "L_Finger_Thumb_00_Jnt",
                                      "control" : "L_Finger_Thumb_00_Ctrl"},
                "LeftHandThumb2"   : {"id"      : 51,
                                      "joint"   : "L_Finger_Thumb_01_Jnt",
                                      "control" : "L_Finger_Thumb_01_Ctrl"},
                "LeftHandThumb3"   : {"id"      : 52,
                                      "joint"   : "L_Finger_Thumb_02_Jnt",
                                      "control" : "L_Finger_Thumb_02_Ctrl"},
                #"LeftHandThumb4"   : {"id"      : 53,
                #                      "joint"   : "",
                #                      "control" : ""},
                "LeftHandIndex1"   : {"id"      : 54,
                                      "joint"   : "L_Finger_Index_00_Jnt",
                                      "control" : "L_Finger_Index_00_Ctrl"},
                "LeftHandIndex2"   : {"id"      : 55,
                                      "joint"   : "L_Finger_Index_01_Jnt",
                                      "control" : "L_Finger_Index_01_Ctrl"},
                "LeftHandIndex3"   : {"id"      : 56,
                                      "joint"   : "L_Finger_Index_02_Jnt",
                                      "control" : "L_Finger_Index_02_Ctrl"},
                "LeftHandIndex4"   : {"id"      : 57,
                                      "joint"   : "L_Finger_Index_03_Jnt",
                                      "control" : "L_Finger_Index_03_Ctrl"},
                "LeftHandMiddle1"  : {"id"      : 58,
                                      "joint"   : "L_Finger_Middle_00_Jnt",
                                      "control" : "L_Finger_Middle_00_Ctrl"},
                "LeftHandMiddle2"  : {"id"      : 59,
                                      "joint"   : "L_Finger_Middle_01_Jnt",
                                      "control" : "L_Finger_Middle_01_Ctrl"},
                "LeftHandMiddle3"  : {"id"      : 60,
                                      "joint"   : "L_Finger_Middle_02_Jnt",
                                      "control" : "L_Finger_Middle_02_Ctrl"},
                "LeftHandMiddle4"  : {"id"      : 61,
                                      "joint"   : "L_Finger_Middle_03_Jnt",
                                      "control" : "L_Finger_Middle_03_Ctrl"},
                "LeftHandRing1"    : {"id"      : 62,
                                      "joint"   : "L_Finger_Ring_00_Jnt",
                                      "control" : "L_Finger_Ring_00_Ctrl"},
                "LeftHandRing2"    : {"id"      : 63,
                                      "joint"   : "L_Finger_Ring_01_Jnt",
                                      "control" : "L_Finger_Ring_01_Ctrl"},
                "LeftHandRing3"    : {"id"      : 64,
                                      "joint"   : "L_Finger_Ring_02_Jnt",
                                      "control" : "L_Finger_Ring_02_Ctrl"},
                "LeftHandRing4"    : {"id"      : 65,
                                      "joint"   : "L_Finger_Ring_03_Jnt",
                                      "control" : "L_Finger_Ring_03_Ctrl"},
                "LeftHandPinky1"   : {"id"      : 66,
                                      "joint"   : "L_Finger_Pinky_00_Jnt",
                                      "control" : "L_Finger_Pinky_00_Ctrl"},
                "LeftHandPinky2"   : {"id"      : 66,
                                      "joint"   : "L_Finger_Pinky_01_Jnt",
                                      "control" : "L_Finger_Pinky_01_Ctrl"},
                "LeftHandPinky3"   : {"id"      : 66,
                                      "joint"   : "L_Finger_Pinky_02_Jnt",
                                      "control" : "L_Finger_Pinky_02_Ctrl"},
                "LeftHandPinky4"   : {"id"      : 66,
                                      "joint"   : "L_Finger_Pinky_03_Jnt",
                                      "control" : "L_Finger_Pinky_03_Ctrl"},
                "RightShoulder"    : {"id"      : 19,
                                      "joint"   : "R_Arm_00_Clavicle_Jnt",
                                      "control" : "R_Arm_Clavicle_Ctrl"},
                "RightArm"         : {"id"      : 12,
                                      "joint"   : "R_Arm_Shoulder_Jxt",
                                      "control" : "R_Arm_Shoulder_Fk_Ctrl"},
                "RightForeArm"     : {"id"      : 13,
                                      "joint"   : "R_Arm_Elbow_Jxt",
                                      "control" : "R_Arm_Elbow_Fk_Ctrl"},
                "RightHand"        : {"id"      : 14,
                                      "joint"   : "R_Arm_13_Wrist_Jnt",
                                      "control" : "R_Arm_Wrist_Fk_Ctrl"},
                "RightHandThumb1"  : {"id"      : 74,
                                      "joint"   : "R_Finger_Thumb_00_Jnt",
                                      "control" : "R_Finger_Thumb_00_Ctrl"},
                "RightHandThumb2"  : {"id"      : 75,
                                    "joint"   : "R_Finger_Thumb_01_Jnt",
                                    "control" : "R_Finger_Thumb_01_Ctrl"},
                "RightHandThumb3"  : {"id"      : 76,
                                      "joint"   : "R_Finger_Thumb_02_Jnt",
                                      "control" : "R_Finger_Thumb_02_Ctrl"},
                #"RightHandThumb4"  : {"id"      : 77,
                #                      "joint"   : "",
                #                      "control" : ""},
                "RightHandIndex1"  : {"id"      : 78,
                                      "joint"   : "R_Finger_Index_00_Jnt",
                                      "control" : "R_Finger_Index_00_Ctrl"},
                "RightHandIndex2"  : {"id"      : 79,
                                      "joint"   : "R_Finger_Index_01_Jnt",
                                      "control" : "R_Finger_Index_01_Ctrl"},
                "RightHandIndex3"  : {"id"      : 80,
                                      "joint"   : "R_Finger_Index_02_Jnt",
                                      "control" : "R_Finger_Index_02_Ctrl"},
                "RightHandIndex4"  : {"id"      : 81,
                                      "joint"   : "R_Finger_Index_03_Jnt",
                                      "control" : "R_Finger_Index_03_Ctrl"},
                "RightHandMiddle1" : {"id"      : 82,
                                      "joint"   : "R_Finger_Middle_00_Jnt",
                                      "control" : "R_Finger_Middle_00_Ctrl"},
                "RightHandMiddle2" : {"id"      : 83,
                                      "joint"   : "R_Finger_Middle_01_Jnt",
                                      "control" : "R_Finger_Middle_01_Ctrl"},
                "RightHandMiddle3" : {"id"      : 85,
                                      "joint"   : "R_Finger_Middle_02_Jnt",
                                      "control" : "R_Finger_Middle_02_Ctrl"},
                "RightHandMiddle4" : {"id"      : 85,
                                      "joint"   : "R_Finger_Middle_03_Jnt",
                                      "control" : "R_Finger_Middle_03_Ctrl"},
                "RightHandRing1"   : {"id"      : 86,
                                      "joint"   : "R_Finger_Ring_00_Jnt",
                                      "control" : "R_Finger_Ring_00_Ctrl"},
                "RightHandRing2"   : {"id"      : 87,
                                      "joint"   : "R_Finger_Ring_01_Jnt",
                                      "control" : "R_Finger_Ring_01_Ctrl"},
                "RightHandRing3"   : {"id"      : 88,
                                      "joint"   : "R_Finger_Ring_02_Jnt",
                                      "control" : "R_Finger_Ring_02_Ctrl"},
                "RightHandRing4"   : {"id"      : 89,
                                      "joint"   : "R_Finger_Ring_03_Jnt",
                                      "control" : "R_Finger_Ring_03_Ctrl"},
                "RightHandPinky1"  : {"id"      : 90,
                                      "joint"   : "R_Finger_Pinky_00_Jnt",
                                      "control" : "R_Finger_Pinky_00_Ctrl"},
                "RightHandPinky2"  : {"id"      : 91,
                                      "joint"   : "R_Finger_Pinky_01_Jnt",
                                      "control" : "R_Finger_Pinky_01_Ctrl"},
                "RightHandPinky3"  : {"id"      : 92,
                                      "joint"   : "R_Finger_Pinky_02_Jnt",
                                      "control" : "R_Finger_Pinky_02_Ctrl"},
                "RightHandPinky4"  : {"id"      : 93,
                                      "joint"   : "R_Finger_Pinky_03_Jnt",
                                      "control" : "R_Finger_Pinky_03_Ctrl"},
                "Neck"             : {"id"      : 20,
                                      "joint"   : "Head_Neck_00_Jnt",
                                      "control" : "Head_Neck_00_Ctrl"},
                "Head"             : {"id"      : 15,
                                      "joint"   : "Head_01_Head_Jnt",
                                      "control" : "Head_Head_Ctrl"},
        }




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
        print("self.hikNode =", self.hikNode)
        return self.hikNode
    

    def hikCreateSkeleton(self, *args):
        """ Create humanIk skeleton.
            Returns its latest HIKCharacterNode.
        """
        hikOldList = cmds.ls(type="HIKCharacterNode")
        mel.eval("HIKCharacterControlsTool;")
        mel.eval("hikCreateSkeleton;")
        self.hikNode = list(set(cmds.ls(type="HIKCharacterNode"))-set(hikOldList))[0]
        print("self.hikNode =", self.hikNode)
        return self.hikNode
    
    
    
    
    def hikAssignJointsToDefinition(self, *args):
        """ Map dpAR biped joints to HumanIk character skeleton.
        """
        if self.hikNode:
            if self.utils.getAllGrp():
                oldRefNodeList = cmds.listConnections(self.hikNode+".Reference", source=True, destination=False)
                if not self.hikDic:
                    self.hikDic = self.hikGetDefaultMapDic()
                #TODO get user defined dictionary to mapping
                for hikKey in self.hikDic.keys():
                    if cmds.objExists(self.hikDic[hikKey]["joint"]):
                        cmds.connectAttr(self.hikDic[hikKey]["joint"]+".message", self.hikNode+"."+hikKey, force=True)
                        if not self.hikCharacterAttr in cmds.listAttr(self.hikDic[hikKey]["joint"]):
                            cmds.addAttr(self.hikDic[hikKey]["joint"], longName=self.hikCharacterAttr, attributeType="message")
                        for attr in self.dpUIinst.transformAttrList:
                            cmds.setAttr(self.hikDic[hikKey]["joint"]+"."+attr, lock=False)
                if oldRefNodeList:
                    cmds.delete(oldRefNodeList[0])

                print("here WIP mapping... done")
            else:
                print("There's no dpAR in the scene to continue the HumanIk biped retargeting, sorry.")
        else:
            print("There's no HIKCharacterNode in the scene to use. Create one to continue, please.")


    def hikMapBipedControllers(self, *args):
        if self.hikNode:
            if self.utils.getAllGrp():

                if not self.hikDic:
                    self.hikDic = self.hikGetDefaultMapDic()
                #TODO get user defined dictionary to mapping
                for hikKey in self.hikDic.keys():
                    if not self.hikDic[hikKey]["id"] == 0: #reference
                        if cmds.objExists(self.hikDic[hikKey]["control"]):
                            cmds.select(self.hikDic[hikKey]["control"])
                            print('hikCustomRigAssignEffector '+str(self.hikDic[hikKey]["id"])+';')
                            mel.eval('hikCustomRigAssignEffector '+str(self.hikDic[hikKey]["id"])+';')
                        

            else:
                print("There's no dpAR in the scene to continue the HumanIk biped retargeting, sorry.")
        else:
            print("There's no HIKCharacterNode in the scene to use. Create one to continue, please.")

    def hikLockDefinition(self, *args):
        """ WIP starts
        """
        #WIP
        print("wip here thanks")
        if self.hikNode:
            if cmds.objExists(self.hikNode):
                cmds.select(self.hikNode)
                mel.eval("hikToggleLockDefinition;")


    def hikCreateCustomRigCtrl(self, *args):
        """ WIP: pass hikNode?
        """
        mel.eval('hikCreateCustomRig( hikGetCurrentCharacter() );')
        #TODO returns the hik customRig node
        