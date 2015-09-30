# importing libraries:
import maya.cmds as cmds
import maya.mel as mel

# global variables to this module:    
CLASS_NAME = "Arm"
TITLE = "m028_arm"
DESCRIPTION = "m029_armDesc"
ICON = "/Icons/dp_arm.png"


def Arm(self):
    """ This function will create all guides needed to compose an arm.
    """
    # check modules integrity:
    guideDir = 'Modules'
    checkModuleList = ['dpLimb', 'dpFinger']
    checkResultList = self.startGuideModules(guideDir, "check", checkModuleList)
    
    if len(checkResultList) == 0:
        # creating module instances:
        armLimbInstance = self.initGuide('dpLimb', guideDir)
        # change name to arm:
        self.guide.Limb.editUserName(armLimbInstance, checkText=self.langDic[self.langName]['m028_arm'].capitalize())
        # create finger instances:
        indexFingerInstance  = self.initGuide('dpFinger', guideDir)
        self.guide.Finger.editUserName(indexFingerInstance, checkText=self.langDic[self.langName]['m032_index'])
        middleFingerInstance = self.initGuide('dpFinger', guideDir)
        self.guide.Finger.editUserName(middleFingerInstance, checkText=self.langDic[self.langName]['m033_middle'])
        ringFingerInstance   = self.initGuide('dpFinger', guideDir)
        self.guide.Finger.editUserName(ringFingerInstance, checkText=self.langDic[self.langName]['m034_ring'])
        pinkFingerInstance   = self.initGuide('dpFinger', guideDir)
        self.guide.Finger.editUserName(pinkFingerInstance, checkText=self.langDic[self.langName]['m035_pink'])
        thumbFingerInstance  = self.initGuide('dpFinger', guideDir)
        self.guide.Finger.editUserName(thumbFingerInstance, checkText=self.langDic[self.langName]['m036_thumb'])
        
        # edit arm limb guide:
        armBaseGuide = armLimbInstance.moduleGrp
        cmds.setAttr(armBaseGuide+".translateX", 2.5)
        cmds.setAttr(armBaseGuide+".translateY", 16)
        cmds.setAttr(armBaseGuide+".displayAnnotation", 0)
        cmds.setAttr(armLimbInstance.cvExtremLoc+".translateZ", 7)
        cmds.setAttr(armLimbInstance.radiusCtrl+".translateX", 1.5)
        
        # edit finger guides:
        fingerInstanceList = [indexFingerInstance, middleFingerInstance, ringFingerInstance, pinkFingerInstance, thumbFingerInstance]
        fingerTZList       = [0.6, 0.2, -0.2, -0.6, 0.72]
        for n, fingerInstance in enumerate(fingerInstanceList):
            cmds.setAttr(fingerInstance.moduleGrp+".translateX", 11)
            cmds.setAttr(fingerInstance.moduleGrp+".translateY", 16)
            cmds.setAttr(fingerInstance.moduleGrp+".translateZ", fingerTZList[n])
            cmds.setAttr(fingerInstance.moduleGrp+".displayAnnotation", 0)
            cmds.setAttr(fingerInstance.radiusCtrl+".translateX", 0.3)
            cmds.setAttr(fingerInstance.annotation+".visibility", 0)
            
            if n == len(fingerInstanceList)-1:
                # correct not commun values for thumb guide:
                cmds.setAttr(thumbFingerInstance.moduleGrp+".translateX", 10.1)
                cmds.setAttr(thumbFingerInstance.moduleGrp+".rotateX", 60)
                self.guide.Finger.changeJointNumber(thumbFingerInstance, 2)
                cmds.setAttr(thumbFingerInstance.moduleGrp+".nJoints", 2)
            
            # parent finger guide to the arm wrist guide:
            cmds.parent(fingerInstance.moduleGrp, armLimbInstance.cvExtremLoc, absolute=True)
        
        # select the armGuide_Base:
        cmds.select(armBaseGuide)
        
    else:
        # error checking modules in the folder:
        mel.eval('error \"'+ self.langDic[self.langName]['e001_GuideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
