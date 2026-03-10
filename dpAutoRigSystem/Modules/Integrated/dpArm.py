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
        checkResultList = self.ar.startGuideModules(standardDir, "check", None, checkModuleList=checkModuleList)
        
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
            
            # creating module instances:
            armLimbInstance = self.ar.initGuide('dpLimb', guideDir)
            # change name to arm:
            armLimbInstance.editGuideModuleName(armName.capitalize())
            # create finger instances:
            thumbFingerInstance  = self.ar.initGuide('dpFinger', guideDir)
            thumbFingerInstance.editGuideModuleName(fingerThumbName)
            indexFingerInstance  = self.ar.initGuide('dpFinger', guideDir)
            indexFingerInstance.editGuideModuleName(fingerIndexName)
            middleFingerInstance = self.ar.initGuide('dpFinger', guideDir)
            middleFingerInstance.editGuideModuleName(fingerMiddleName)
            ringFingerInstance   = self.ar.initGuide('dpFinger', guideDir)
            ringFingerInstance.editGuideModuleName(fingerRingName)
            pinkyFingerInstance  = self.ar.initGuide('dpFinger', guideDir)
            pinkyFingerInstance.editGuideModuleName(fingerPinkyName)
            
            # edit arm limb guide:
            armBaseGuide = armLimbInstance.moduleGrp
            cmds.setAttr(armBaseGuide+".translateX", 2.5)
            cmds.setAttr(armBaseGuide+".translateY", 16)
            cmds.setAttr(armBaseGuide+".displayAnnotation", 0)
            cmds.setAttr(armLimbInstance.cvExtremLoc+".translateZ", 7)
            cmds.setAttr(armLimbInstance.radiusCtrl+".translateX", 1.5)
            armLimbInstance.changeStyle(self.ar.data.lang['m026_biped'])
            cmds.refresh()
            
            # edit finger guides:
            fingerInstanceList = [thumbFingerInstance, indexFingerInstance, middleFingerInstance, ringFingerInstance, pinkyFingerInstance]
            fingerTZList       = [0.72, 0.6, 0.2, -0.2, -0.6]
            for n, fingerInstance in enumerate(fingerInstanceList):
                self.ar.utils.setProgress(doingName+self.ar.data.lang['m007_finger'])
                cmds.setAttr(fingerInstance.moduleGrp+".translateX", 11)
                cmds.setAttr(fingerInstance.moduleGrp+".translateY", 16)
                cmds.setAttr(fingerInstance.moduleGrp+".translateZ", fingerTZList[n])
                cmds.setAttr(fingerInstance.moduleGrp+".displayAnnotation", 0)
                cmds.setAttr(fingerInstance.radiusCtrl+".translateX", 0.3)
                cmds.setAttr(fingerInstance.annotation+".visibility", 0)
                cmds.setAttr(fingerInstance.moduleGrp+".shapeSize", 0.3)
                if n == 0:
                    # correct not commun values for thumb guide:
                    cmds.setAttr(thumbFingerInstance.moduleGrp+".translateX", 10.1)
                    cmds.setAttr(thumbFingerInstance.moduleGrp+".rotateX", 60)
                    thumbFingerInstance.changeJointNumber(2)
                    cmds.setAttr(thumbFingerInstance.moduleGrp+".nJoints", 2)
                # parent finger guide to the arm wrist guide:
                cmds.parent(fingerInstance.moduleGrp, armLimbInstance.cvExtremLoc, absolute=True)
                cmds.refresh()
            
            # Close progress window
            self.ar.utils.setProgress(endIt=True)

            # select the armGuide_Base:
            self.ar.collapseEditSelModFL = False
            cmds.select(armBaseGuide)
            print(self.ar.data.lang['m091_createdArm'])
        else:
            # error checking modules in the folder:
            mel.eval('error \"'+ self.ar.data.lang['e001_guideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
