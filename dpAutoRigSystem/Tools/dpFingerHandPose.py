# importing libraries:
from maya import cmds
from ..Modules.Base import dpBaseLibrary
from importlib import reload

# global variables to this module:    
CLASS_NAME = "FingerHandPose"
TITLE = "m256_fingerHandPose"
DESCRIPTION = "m257_fingerHandPoseDesc"
ICON = "/Icons/dp_fingerHandPose.png"
WIKI = "06-‐-Tools#-finger-hand-pose"

DP_FINGERHANDPOSE_VERSION = 1.01


class FingerHandPose(dpBaseLibrary.BaseLibrary):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        kwargs["WIKI"] = WIKI
        dpBaseLibrary.BaseLibrary.__init__(self, *args, **kwargs)
        if self.ar.dev:
            reload(dpBaseLibrary)
        self.drivenKeyTypeList = ["animCurveUA", "animCurveUL", "animCurveUT", "animCurveUU"]
        self.oldDrivenKeyList = cmds.ls(selection=False, type=self.drivenKeyTypeList)
        self.sideList = ["", self.ar.data.lang['p002_left']+"_", self.ar.data.lang['p003_right']+"_"]
        self.armName = self.ar.data.lang['c037_arm']
        self.wristName = self.ar.data.lang['c004_arm_extrem']
        self.fingerIndexName = self.ar.data.lang['m007_finger']+"_"+self.ar.data.lang['m032_index']
        self.fingerMiddleName = self.ar.data.lang['m007_finger']+"_"+self.ar.data.lang['m033_middle']
        self.fingerRingName = self.ar.data.lang['m007_finger']+"_"+self.ar.data.lang['m034_ring']
        self.fingerPinkyName = self.ar.data.lang['m007_finger']+"_"+self.ar.data.lang['m035_pinky']
        self.fingerList = [self.fingerIndexName, self.fingerMiddleName, self.fingerRingName, self.fingerPinkyName]
        self.curlName = self.ar.data.lang['c128_curl']
        self.sideName = self.ar.data.lang['c121_side'].lower()
        self.scratchName = self.ar.data.lang['c129_scratch']
        self.spreadName = self.ar.data.lang['c130_spread']
        self.relaxName = self.ar.data.lang['c131_relax']
        self.handAttrList = [self.curlName, self.sideName, self.scratchName, self.spreadName, self.relaxName]
        
        
    def build_tool(self, *args):
        self.toIDList = []
        handCtrlList = []
        
        # find nodes
        allGrp = self.ar.utils.getAllGrp()
        if allGrp:
            if cmds.getAttr(allGrp+".dpFingerCount"): #it has fingers
                for side in self.sideList:
                    handCtrl = side+self.armName+"_"+self.wristName+"_ToParent_Ctrl"
                    if cmds.objExists(handCtrl): #there's an arm
                        handCtrlList.append(handCtrl)
                        for attr in self.handAttrList:
                            if not attr in cmds.listAttr(handCtrl):
                                cmds.addAttr(handCtrl, longName=attr, attributeType="double", minValue=-1, maxValue=1, defaultValue=0, keyable=True)
                        for f, finger in enumerate(self.fingerList):
                            for n in range(1, 4):
                                if cmds.objExists(side+finger+"_"+str(n).zfill(2)+"_Ctrl"):
                                    fingerGrp = side+finger+"_%02d_Pose_Grp"%(n)
                                    if not cmds.objExists(fingerGrp):
                                        fingerGrp = cmds.group(side+finger+"_"+str(n).zfill(2)+"_Ctrl", name=side+finger+"_%02d_Pose_Grp"%(n))
                                        cmds.xform(fingerGrp, rotatePivot=cmds.xform(side+finger+"_"+str(n).zfill(2)+"_Ctrl", query=True, rotatePivot=True, worldSpace=True), worldSpace=True)
                                        self.toIDList.append(fingerGrp)
                                    # Curl
                                    cmds.setDrivenKeyframe(fingerGrp+".rotateY", currentDriver=handCtrl+"."+self.curlName, driverValue=-1, value=-90)
                                    cmds.setDrivenKeyframe(fingerGrp+".rotateY", currentDriver=handCtrl+"."+self.curlName, driverValue=0, value=0)
                                    cmds.setDrivenKeyframe(fingerGrp+".rotateY", currentDriver=handCtrl+"."+self.curlName, driverValue=1, value=90)
                                    # Side
                                    cmds.setDrivenKeyframe(fingerGrp+".rotateX", currentDriver=handCtrl+"."+self.sideName, driverValue=-1, value=-45)
                                    cmds.setDrivenKeyframe(fingerGrp+".rotateX", currentDriver=handCtrl+"."+self.sideName, driverValue=0, value=0)
                                    cmds.setDrivenKeyframe(fingerGrp+".rotateX", currentDriver=handCtrl+"."+self.sideName, driverValue=1, value=45)
                                    # Relax
                                    cmds.setDrivenKeyframe(fingerGrp+".rotateY", currentDriver=handCtrl+"."+self.relaxName, driverValue=-1, value=(-1*n-f)*(f+1)-10)
                                    cmds.setDrivenKeyframe(fingerGrp+".rotateY", currentDriver=handCtrl+"."+self.relaxName, driverValue=0, value=0)
                                    cmds.setDrivenKeyframe(fingerGrp+".rotateY", currentDriver=handCtrl+"."+self.relaxName, driverValue=1, value=40*(1/(n*(f+1))))
                            # Scratch
                            if cmds.objExists(side+finger+"_01_Pose_Grp"):
                                cmds.setDrivenKeyframe(side+finger+"_01_Pose_Grp.rotateY", currentDriver=handCtrl+"."+self.scratchName, driverValue=-1, value=60)
                                cmds.setDrivenKeyframe(side+finger+"_01_Pose_Grp.rotateY", currentDriver=handCtrl+"."+self.scratchName, driverValue=0, value=0)
                                cmds.setDrivenKeyframe(side+finger+"_01_Pose_Grp.rotateY", currentDriver=handCtrl+"."+self.scratchName, driverValue=1, value=-60)
                            if cmds.objExists(side+finger+"_02_Pose_Grp"):
                                cmds.setDrivenKeyframe(side+finger+"_02_Pose_Grp.rotateY", currentDriver=handCtrl+"."+self.scratchName, driverValue=-1, value=-60)
                                cmds.setDrivenKeyframe(side+finger+"_02_Pose_Grp.rotateY", currentDriver=handCtrl+"."+self.scratchName, driverValue=0, value=0)
                                cmds.setDrivenKeyframe(side+finger+"_02_Pose_Grp.rotateY", currentDriver=handCtrl+"."+self.scratchName, driverValue=1, value=60)
                            if cmds.objExists(side+finger+"_03_Pose_Grp"):
                                cmds.setDrivenKeyframe(side+finger+"_03_Pose_Grp.rotateY", currentDriver=handCtrl+"."+self.scratchName, driverValue=-1, value=-60)
                                cmds.setDrivenKeyframe(side+finger+"_03_Pose_Grp.rotateY", currentDriver=handCtrl+"."+self.scratchName, driverValue=0, value=0)
                                cmds.setDrivenKeyframe(side+finger+"_03_Pose_Grp.rotateY", currentDriver=handCtrl+"."+self.scratchName, driverValue=1, value=60)
                        # Spread
                        if cmds.objExists(side+self.fingerIndexName+"_01_Pose_Grp"):
                            cmds.setDrivenKeyframe(side+self.fingerIndexName+"_01_Pose_Grp.rotateX", currentDriver=handCtrl+"."+self.spreadName, driverValue=-1, value=-45)
                            cmds.setDrivenKeyframe(side+self.fingerIndexName+"_01_Pose_Grp.rotateX", currentDriver=handCtrl+"."+self.spreadName, driverValue=0, value=0)
                            cmds.setDrivenKeyframe(side+self.fingerIndexName+"_01_Pose_Grp.rotateX", currentDriver=handCtrl+"."+self.spreadName, driverValue=1, value=10)
                        if cmds.objExists(side+self.fingerMiddleName+"_01_Pose_Grp"):
                            cmds.setDrivenKeyframe(side+self.fingerMiddleName+"_01_Pose_Grp.rotateX", currentDriver=handCtrl+"."+self.spreadName, driverValue=-1, value=-20)
                            cmds.setDrivenKeyframe(side+self.fingerMiddleName+"_01_Pose_Grp.rotateX", currentDriver=handCtrl+"."+self.spreadName, driverValue=0, value=0)
                            cmds.setDrivenKeyframe(side+self.fingerMiddleName+"_01_Pose_Grp.rotateX", currentDriver=handCtrl+"."+self.spreadName, driverValue=1, value=5)
                        if cmds.objExists(side+self.fingerRingName+"_01_Pose_Grp"):
                            cmds.setDrivenKeyframe(side+self.fingerRingName+"_01_Pose_Grp.rotateX", currentDriver=handCtrl+"."+self.spreadName, driverValue=-1, value=5)
                            cmds.setDrivenKeyframe(side+self.fingerRingName+"_01_Pose_Grp.rotateX", currentDriver=handCtrl+"."+self.spreadName, driverValue=0, value=0)
                            cmds.setDrivenKeyframe(side+self.fingerRingName+"_01_Pose_Grp.rotateX", currentDriver=handCtrl+"."+self.spreadName, driverValue=1, value=-5)
                        if cmds.objExists(side+self.fingerPinkyName+"_01_Pose_Grp"):
                            cmds.setDrivenKeyframe(side+self.fingerPinkyName+"_01_Pose_Grp.rotateX", currentDriver=handCtrl+"."+self.spreadName, driverValue=-1, value=45)
                            cmds.setDrivenKeyframe(side+self.fingerPinkyName+"_01_Pose_Grp.rotateX", currentDriver=handCtrl+"."+self.spreadName, driverValue=0, value=0)
                            cmds.setDrivenKeyframe(side+self.fingerPinkyName+"_01_Pose_Grp.rotateX", currentDriver=handCtrl+"."+self.spreadName, driverValue=1, value=-10)
            currentDrivenKeyList = cmds.ls(selection=False, type=self.drivenKeyTypeList)
            newDrivenKeyList = currentDrivenKeyList
            if self.oldDrivenKeyList:
                newDrivenKeyList = list(set(currentDrivenKeyList) - set(self.oldDrivenKeyList))
            self.toIDList.extend(newDrivenKeyList)
            self.ar.customAttr.addAttr(0, self.toIDList) #dpID
            if self.ui: #verbose
                cmds.select(handCtrlList)
                self.ar.logger.infoWin(TITLE, 'i363_addedFingerHandPose', None, 'center', 200, 120)
