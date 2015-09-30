# importing libraries:
import maya.cmds as cmds
import maya.mel as mel

# global variables to this module:    
CLASS_NAME = "Biped"
TITLE = "m026_biped"
DESCRIPTION = "m027_bipedDesc"
ICON = "/Icons/dp_biped.png"


def Biped(self):
    """ This function will create all guides needed to compose a biped.
    """
    # check modules integrity:
    guideDir = 'Modules'
    checkModuleList = ['dpLimb', 'dpFoot', 'dpFinger', 'dpSpine', 'dpHead']
    checkResultList = self.startGuideModules(guideDir, "check", checkModuleList)
    
    if len(checkResultList) == 0:
        # woking with SPINE system:
        # create spine module instance:
        spineInstance = self.initGuide('dpSpine', guideDir)
        # editing spine base guide informations:
        self.guide.Spine.editUserName(spineInstance, checkText=self.langDic[self.langName]['m011_spine'])
        cmds.setAttr(spineInstance.moduleGrp+".translateY", 11)
        cmds.setAttr(spineInstance.annotation+".translateY", -6)
        cmds.setAttr(spineInstance.radiusCtrl+".translateX", 2.5)
        
        # woking with HEAD system:
        # create head module instance:
        headInstance = self.initGuide('dpHead', guideDir)
        # editing head base guide informations:
        self.guide.Head.editUserName(headInstance, checkText=self.langDic[self.langName]['c_head'])
        cmds.setAttr(headInstance.moduleGrp+".translateY", 17)
        cmds.setAttr(headInstance.annotation+".translateY", 3.5)
        
        # parent head guide to spine guide:
        cmds.parent(headInstance.moduleGrp, spineInstance.cvLocator, absolute=True)
        
        # woking with EyeLookAt system:
        # create eyeLookAt module instance:
        eyeLookAtInstance = self.initGuide('dpEyeLookAt', guideDir)
        # setting X mirror:
        self.guide.EyeLookAt.changeMirror(eyeLookAtInstance, "X")
        # editing eyeLookAt base guide informations:
        self.guide.EyeLookAt.editUserName(eyeLookAtInstance, checkText=self.langDic[self.langName]['c_eye'])
        cmds.setAttr(eyeLookAtInstance.moduleGrp+".translateX", 0.5)
        cmds.setAttr(eyeLookAtInstance.moduleGrp+".translateY", 21)
        cmds.setAttr(eyeLookAtInstance.moduleGrp+".translateZ", 1.5)
        cmds.setAttr(eyeLookAtInstance.annotation+".translateY", 3.5)
        cmds.setAttr(eyeLookAtInstance.radiusCtrl+".translateX", 0.5)
        
        # parent head guide to spine guide:
        cmds.parent(eyeLookAtInstance.moduleGrp, headInstance.cvHeadLoc, absolute=True)
        
        # working with LEG system:
        # create leg module instance:
        legLimbInstance = self.initGuide('dpLimb', guideDir)
        # setting X mirror:
        self.guide.Limb.changeMirror(legLimbInstance, "X")
        # change limb guide to leg type:
        self.guide.Limb.changeType(legLimbInstance, self.langDic[self.langName]['m030_leg'])
        # change limb style to biped:
        self.guide.Limb.changeStyle(legLimbInstance, self.langDic[self.langName]['m026_biped'])
        # change name to leg:
        self.guide.Limb.editUserName(legLimbInstance, checkText=self.langDic[self.langName]['m030_leg'].capitalize())
        cmds.setAttr(legLimbInstance.annotation+".translateY", -4)
        
        # editing leg base guide informations:
        legBaseGuide = legLimbInstance.moduleGrp
        cmds.setAttr(legBaseGuide+".type", 1)
        cmds.setAttr(legBaseGuide+".translateX", 1.5)
        cmds.setAttr(legBaseGuide+".translateY", 10)
        cmds.setAttr(legBaseGuide+".rotateX", 0)
        cmds.setAttr(legLimbInstance.radiusCtrl+".translateX", 1.5)
        
        # edit location of leg ankle guide:
        cmds.setAttr(legLimbInstance.cvExtremLoc+".translateZ", 8.5)
        
        # parent leg guide to spine base guide:
        cmds.parent(legBaseGuide, spineInstance.moduleGrp, absolute=True)
        
        # create foot module instance:
        footInstance = self.initGuide('dpFoot', guideDir)
        self.guide.Foot.editUserName(footInstance, checkText=self.langDic[self.langName]['c_foot'])
        cmds.setAttr(footInstance.annotation+".translateY", -3)
        cmds.setAttr(footInstance.moduleGrp+".translateX", 1.5)
        cmds.setAttr(footInstance.cvFootLoc+".translateZ", 1.5)
        
        # parent foot guide to leg ankle guide:
        cmds.parent(footInstance.moduleGrp, legLimbInstance.cvExtremLoc, absolute=True)
        
        # working with ARM system:
        # creating module instances:
        armLimbInstance = self.initGuide('dpLimb', guideDir)
        # setting X mirror:
        self.guide.Limb.changeMirror(armLimbInstance, "X")
        # change limb style to biped:
        self.guide.Limb.changeStyle(armLimbInstance, self.langDic[self.langName]['m026_biped'])
        # change name to arm:
        self.guide.Limb.editUserName(armLimbInstance, checkText=self.langDic[self.langName]['c_arm'].capitalize())
        cmds.setAttr(armLimbInstance.annotation+".translateX", 3)
        cmds.setAttr(armLimbInstance.annotation+".translateY", 0)
        cmds.setAttr(armLimbInstance.annotation+".translateZ", 2)
        # edit arm limb guide:
        armBaseGuide = armLimbInstance.moduleGrp
        cmds.setAttr(armBaseGuide+".translateX", 2.5)
        cmds.setAttr(armBaseGuide+".translateY", 16)
        cmds.setAttr(armBaseGuide+".displayAnnotation", 0)
        cmds.setAttr(armLimbInstance.cvExtremLoc+".translateZ", 7)
        cmds.setAttr(armLimbInstance.radiusCtrl+".translateX", 1.5)
        # parent arm guide to spine chest guide:
        cmds.parent(armLimbInstance.moduleGrp, spineInstance.cvLocator, absolute=True)
        
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
        
        # woking with EAR system:
        # create FkLine module instance:
        earInstance = self.initGuide('dpFkLine', guideDir)
        # editing ear base guide informations:
        self.guide.FkLine.editUserName(earInstance, checkText=self.langDic[self.langName]['m040_ear'])
        cmds.setAttr(earInstance.moduleGrp+".translateX", 1)
        cmds.setAttr(earInstance.moduleGrp+".translateY", 21)
        cmds.setAttr(earInstance.moduleGrp+".rotateY", 110)
        cmds.setAttr(earInstance.radiusCtrl+".translateX", 0.5)
        
        # parent ear guide to spine guide:
        cmds.parent(earInstance.moduleGrp, headInstance.cvHeadLoc, absolute=True)
        # setting X mirror:
        self.guide.FkLine.changeMirror(earInstance, "X")
        cmds.setAttr(earInstance.moduleGrp+".flip", 1)

        # select spineGuide_Base:
        cmds.select(spineInstance.moduleGrp)
    else:
        # error checking modules in the folder:
        mel.eval('error \"'+ self.langDic[self.langName]['e001_GuideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
