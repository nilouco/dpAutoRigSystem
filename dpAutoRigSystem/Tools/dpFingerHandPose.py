# importing libraries:
from maya import cmds

# global variables to this module:    
CLASS_NAME = "FingerHandPose"
TITLE = "m256_fingerHandPose"
DESCRIPTION = "m257_fingerHandPoseDesc"
ICON = "/Icons/dp_fingerHandPose.png"
WIKI = "06-‐-Tools#-finger-hand-pose"

DP_FINGERHANDPOSE_VERSION = 1.01


class FingerHandPose(object):
    def __init__(self, ar, ui=True, *args):
        # redeclaring variables
        self.ar = ar
        self.drivenKeyTypeList = ["animCurveUA", "animCurveUL", "animCurveUT", "animCurveUU"]
        oldDrivenKeyList = cmds.ls(selection=False, type=self.drivenKeyTypeList)
        self.toIDList = []
        sideList = ["", self.ar.data.lang['p002_left']+"_", self.ar.data.lang['p003_right']+"_"]
        armName = ar.data.lang['c037_arm']
        wristName = ar.data.lang['c004_arm_extrem']
        fingerIndexName = ar.data.lang['m007_finger']+"_"+ar.data.lang['m032_index']
        fingerMiddleName = ar.data.lang['m007_finger']+"_"+ar.data.lang['m033_middle']
        fingerRingName = ar.data.lang['m007_finger']+"_"+ar.data.lang['m034_ring']
        fingerPinkyName = ar.data.lang['m007_finger']+"_"+ar.data.lang['m035_pinky']
        fingerList = [fingerIndexName, fingerMiddleName, fingerRingName, fingerPinkyName]
        curlName = ar.data.lang['c128_curl']
        sideName = ar.data.lang['c121_side'].lower()
        scratchName = ar.data.lang['c129_scratch']
        spreadName = ar.data.lang['c130_spread']
        relaxName = ar.data.lang['c131_relax']
        handAttrList = [curlName, sideName, scratchName, spreadName, relaxName]
        handCtrlList = []
        
        # find nodes
        allGrp = self.ar.utils.getAllGrp()
        if allGrp:
            if cmds.getAttr(allGrp+".dpFingerCount"): #it has fingers
                for side in sideList:
                    handCtrl = side+armName+"_"+wristName+"_ToParent_Ctrl"
                    if cmds.objExists(handCtrl): #there's an arm
                        handCtrlList.append(handCtrl)
                        for attr in handAttrList:
                            if not attr in cmds.listAttr(handCtrl):
                                cmds.addAttr(handCtrl, longName=attr, attributeType="double", minValue=-1, maxValue=1, defaultValue=0, keyable=True)
                        for f, finger in enumerate(fingerList):
                            for n in range(1, 4):
                                if cmds.objExists(side+finger+"_"+str(n).zfill(2)+"_Ctrl"):
                                    fingerGrp = side+finger+"_%02d_Pose_Grp"%(n)
                                    if not cmds.objExists(fingerGrp):
                                        fingerGrp = cmds.group(side+finger+"_"+str(n).zfill(2)+"_Ctrl", name=side+finger+"_%02d_Pose_Grp"%(n))
                                        cmds.xform(fingerGrp, rotatePivot=cmds.xform(side+finger+"_"+str(n).zfill(2)+"_Ctrl", query=True, rotatePivot=True, worldSpace=True), worldSpace=True)
                                        self.toIDList.append(fingerGrp)
                                    # Curl
                                    cmds.setDrivenKeyframe(fingerGrp+".rotateY", currentDriver=handCtrl+"."+curlName, driverValue=-1, value=-90)
                                    cmds.setDrivenKeyframe(fingerGrp+".rotateY", currentDriver=handCtrl+"."+curlName, driverValue=0, value=0)
                                    cmds.setDrivenKeyframe(fingerGrp+".rotateY", currentDriver=handCtrl+"."+curlName, driverValue=1, value=90)
                                    # Side
                                    cmds.setDrivenKeyframe(fingerGrp+".rotateX", currentDriver=handCtrl+"."+sideName, driverValue=-1, value=-45)
                                    cmds.setDrivenKeyframe(fingerGrp+".rotateX", currentDriver=handCtrl+"."+sideName, driverValue=0, value=0)
                                    cmds.setDrivenKeyframe(fingerGrp+".rotateX", currentDriver=handCtrl+"."+sideName, driverValue=1, value=45)
                                    # Relax
                                    cmds.setDrivenKeyframe(fingerGrp+".rotateY", currentDriver=handCtrl+"."+relaxName, driverValue=-1, value=(-1*n-f)*(f+1)-10)
                                    cmds.setDrivenKeyframe(fingerGrp+".rotateY", currentDriver=handCtrl+"."+relaxName, driverValue=0, value=0)
                                    cmds.setDrivenKeyframe(fingerGrp+".rotateY", currentDriver=handCtrl+"."+relaxName, driverValue=1, value=40*(1/(n*(f+1))))
                            # Scratch
                            if cmds.objExists(side+finger+"_01_Pose_Grp"):
                                cmds.setDrivenKeyframe(side+finger+"_01_Pose_Grp.rotateY", currentDriver=handCtrl+"."+scratchName, driverValue=-1, value=60)
                                cmds.setDrivenKeyframe(side+finger+"_01_Pose_Grp.rotateY", currentDriver=handCtrl+"."+scratchName, driverValue=0, value=0)
                                cmds.setDrivenKeyframe(side+finger+"_01_Pose_Grp.rotateY", currentDriver=handCtrl+"."+scratchName, driverValue=1, value=-60)
                            if cmds.objExists(side+finger+"_02_Pose_Grp"):
                                cmds.setDrivenKeyframe(side+finger+"_02_Pose_Grp.rotateY", currentDriver=handCtrl+"."+scratchName, driverValue=-1, value=-60)
                                cmds.setDrivenKeyframe(side+finger+"_02_Pose_Grp.rotateY", currentDriver=handCtrl+"."+scratchName, driverValue=0, value=0)
                                cmds.setDrivenKeyframe(side+finger+"_02_Pose_Grp.rotateY", currentDriver=handCtrl+"."+scratchName, driverValue=1, value=60)
                            if cmds.objExists(side+finger+"_03_Pose_Grp"):
                                cmds.setDrivenKeyframe(side+finger+"_03_Pose_Grp.rotateY", currentDriver=handCtrl+"."+scratchName, driverValue=-1, value=-60)
                                cmds.setDrivenKeyframe(side+finger+"_03_Pose_Grp.rotateY", currentDriver=handCtrl+"."+scratchName, driverValue=0, value=0)
                                cmds.setDrivenKeyframe(side+finger+"_03_Pose_Grp.rotateY", currentDriver=handCtrl+"."+scratchName, driverValue=1, value=60)
                        # Spread
                        if cmds.objExists(side+fingerIndexName+"_01_Pose_Grp"):
                            cmds.setDrivenKeyframe(side+fingerIndexName+"_01_Pose_Grp.rotateX", currentDriver=handCtrl+"."+spreadName, driverValue=-1, value=-45)
                            cmds.setDrivenKeyframe(side+fingerIndexName+"_01_Pose_Grp.rotateX", currentDriver=handCtrl+"."+spreadName, driverValue=0, value=0)
                            cmds.setDrivenKeyframe(side+fingerIndexName+"_01_Pose_Grp.rotateX", currentDriver=handCtrl+"."+spreadName, driverValue=1, value=10)
                        if cmds.objExists(side+fingerMiddleName+"_01_Pose_Grp"):
                            cmds.setDrivenKeyframe(side+fingerMiddleName+"_01_Pose_Grp.rotateX", currentDriver=handCtrl+"."+spreadName, driverValue=-1, value=-20)
                            cmds.setDrivenKeyframe(side+fingerMiddleName+"_01_Pose_Grp.rotateX", currentDriver=handCtrl+"."+spreadName, driverValue=0, value=0)
                            cmds.setDrivenKeyframe(side+fingerMiddleName+"_01_Pose_Grp.rotateX", currentDriver=handCtrl+"."+spreadName, driverValue=1, value=5)
                        if cmds.objExists(side+fingerRingName+"_01_Pose_Grp"):
                            cmds.setDrivenKeyframe(side+fingerRingName+"_01_Pose_Grp.rotateX", currentDriver=handCtrl+"."+spreadName, driverValue=-1, value=5)
                            cmds.setDrivenKeyframe(side+fingerRingName+"_01_Pose_Grp.rotateX", currentDriver=handCtrl+"."+spreadName, driverValue=0, value=0)
                            cmds.setDrivenKeyframe(side+fingerRingName+"_01_Pose_Grp.rotateX", currentDriver=handCtrl+"."+spreadName, driverValue=1, value=-5)
                        if cmds.objExists(side+fingerPinkyName+"_01_Pose_Grp"):
                            cmds.setDrivenKeyframe(side+fingerPinkyName+"_01_Pose_Grp.rotateX", currentDriver=handCtrl+"."+spreadName, driverValue=-1, value=45)
                            cmds.setDrivenKeyframe(side+fingerPinkyName+"_01_Pose_Grp.rotateX", currentDriver=handCtrl+"."+spreadName, driverValue=0, value=0)
                            cmds.setDrivenKeyframe(side+fingerPinkyName+"_01_Pose_Grp.rotateX", currentDriver=handCtrl+"."+spreadName, driverValue=1, value=-10)
            currentDrivenKeyList = cmds.ls(selection=False, type=self.drivenKeyTypeList)
            newDrivenKeyList = currentDrivenKeyList
            if oldDrivenKeyList:
                newDrivenKeyList = list(set(currentDrivenKeyList) - set(oldDrivenKeyList))
            self.toIDList.extend(newDrivenKeyList)
            self.ar.customAttr.addAttr(0, self.toIDList) #dpID
            if ui: #verbose
                cmds.select(handCtrlList)
                self.ar.logger.infoWin(TITLE, 'i363_addedFingerHandPose', None, 'center', 200, 120)
