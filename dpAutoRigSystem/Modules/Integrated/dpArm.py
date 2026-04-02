# importing libraries:
from maya import cmds
from maya import mel
from ..Base import dpBaseLibrary
from importlib import reload

# global variables to this module:    
CLASS_NAME = "Arm"
TITLE = "m028_arm"
DESCRIPTION = "m029_armDesc"
ICON = "/Icons/dp_arm.png"
WIKI = "03-‐-Guides#-arm"

DP_ARM_VERSION = 2.02


class Arm(dpBaseLibrary.BaseLibrary):
    def __init__(self,  *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        kwargs["WIKI"] = WIKI
        dpBaseLibrary.BaseLibrary.__init__(self, *args, **kwargs)
        if self.ar.dev:
            reload(dpBaseLibrary)
        

    def build_template(self, *args):
        """ This function will create all guides needed to compose an arm.
        """
        # check modules integrity:
        guideDir = 'Modules.Standard'
        standardDir = 'Modules/Standard'
        checkModuleList = ['dpLimb', 'dpFinger']
        checkResultList = self.ar.check_missing_modules(standardDir, checkModuleList)
        
        if len(checkResultList) == 0:
            self.ar.collapseEditSelModFL = True
            # defining naming:
            doingName = self.ar.data.lang['m094_doing']
            # part names:
            armName = self.ar.data.lang['c037_arm']
            fingerIndexName = self.ar.data.lang['m007_finger']+"_"+self.ar.data.lang['m032_index']
            fingerMiddleName = self.ar.data.lang['m007_finger']+"_"+self.ar.data.lang['m033_middle']
            fingerRingName = self.ar.data.lang['m007_finger']+"_"+self.ar.data.lang['m034_ring']
            fingerPinkyName = self.ar.data.lang['m007_finger']+"_"+self.ar.data.lang['m035_pinky']
            fingerThumbName = self.ar.data.lang['m007_finger']+"_"+self.ar.data.lang['m036_thumb']
            armGuideName = self.ar.data.lang['c037_arm']+" "+self.ar.data.lang['i205_guide']
        
            # Starting progress window
            maxProcess = 6 # number of modules to create
            self.ar.utils.setProgress(doingName, armGuideName, maxProcess, addOne=False, addNumber=False)
            self.ar.utils.setProgress(doingName+armName)
            
            # getting module instances:
            limb = self.ar.config.get_instance("dpLimb", [guideDir])
            finger = self.ar.config.get_instance("dpFinger", [guideDir])
            
            # creating arm:
            arm_guide = limb.build_raw_guide()
            # change name to arm:
            limb.editGuideModuleName(armName.capitalize())
            # edit arm limb guide:
            cmds.setAttr(arm_guide+".translateX", 2.5)
            cmds.setAttr(arm_guide+".translateY", 16)
            cmds.setAttr(arm_guide+".displayAnnotation", 0)
            cmds.setAttr(limb.cvExtremLoc+".translateZ", 7)
            cmds.setAttr(limb.radiusCtrl+".translateX", 1.5)
            limb.changeStyle(self.ar.data.lang['m026_biped'])
            cmds.refresh()

            # edit finger guides:
            finger_names = [fingerThumbName, fingerIndexName, fingerMiddleName, fingerRingName, fingerPinkyName]
            fingerTZList = [0.72, 0.6, 0.2, -0.2, -0.6]
            for n, finger_name in enumerate(finger_names):
                self.ar.utils.setProgress(doingName+self.ar.data.lang['m007_finger'])
                finger_guide = finger.build_raw_guide()
                finger.editGuideModuleName(finger_name)
                cmds.setAttr(finger_guide+".translateX", 11)
                cmds.setAttr(finger_guide+".translateY", 16)
                cmds.setAttr(finger_guide+".translateZ", fingerTZList[n])
                cmds.setAttr(finger_guide+".displayAnnotation", 0)
                cmds.setAttr(finger_guide+".shapeSize", 0.3)
                cmds.setAttr(finger.radiusCtrl+".translateX", 0.3)
                cmds.setAttr(finger.annotation+".visibility", 0)
                if n == 0:
                    # correct not commun values for thumb guide:
                    cmds.setAttr(finger_guide+".translateX", 10.1)
                    cmds.setAttr(finger_guide+".rotateX", 60)
                    finger.changeJointNumber(2)
                    cmds.setAttr(finger_guide+".nJoints", 2)
                # parent finger guide to the arm wrist guide:
                cmds.parent(finger_guide, limb.cvExtremLoc, absolute=True)
                cmds.refresh()
            
            # Close progress window
            self.ar.utils.setProgress(endIt=True)

            # select the armGuide_Base:
            self.ar.collapseEditSelModFL = False
            cmds.select(arm_guide)
            print(self.ar.data.lang['m091_createdArm'])
        else:
            # error checking modules in the folder:
            mel.eval('error \"'+ self.ar.data.lang['e001_guideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
