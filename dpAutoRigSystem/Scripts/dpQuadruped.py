# importing libraries:
import maya.cmds as cmds
import maya.mel as mel

# global variables to this module:    
CLASS_NAME = "Quadruped"
TITLE = "m037_quadruped"
DESCRIPTION = "m038_quadrupedDesc"
ICON = "/Icons/dp_quadruped.png"


def Quadruped(self):
    """ This function will create all guides needed to compose a quadruped.
    """
    # check modules integrity:
    guideDir = 'Modules'
    checkModuleList = ['dpLimb', 'dpFoot', 'dpSpine', 'dpHead', 'dpFkLine']
    checkResultList = self.startGuideModules(guideDir, "check", checkModuleList)
    
    if len(checkResultList) == 0:
        # woking with SPINE system:
        # create spine module instance:
        spineInstance = self.initGuide('dpSpine', guideDir)
        # editing spine base guide informations:
        self.guide.Spine.editUserName(spineInstance, checkText=self.langDic[self.langName]['m011_spine'].lower())
        cmds.setAttr(spineInstance.moduleGrp+".translateY", 10)
        cmds.setAttr(spineInstance.moduleGrp+".translateZ", -5)
        cmds.setAttr(spineInstance.moduleGrp+".rotateX", 0)
        cmds.setAttr(spineInstance.moduleGrp+".rotateY", 0)
        cmds.setAttr(spineInstance.moduleGrp+".rotateZ", 90)
        cmds.setAttr(spineInstance.cvLocator+".translateZ", 6)
        cmds.setAttr(spineInstance.annotation+".translateX", 6)
        cmds.setAttr(spineInstance.annotation+".translateY", 0)
        
        # woking with HEAD system:
        # create head module instance:
        headInstance = self.initGuide('dpHead', guideDir)
        # editing head base guide informations:
        self.guide.Head.editUserName(headInstance, checkText=self.langDic[self.langName]['m017_head'].lower())
        cmds.setAttr(headInstance.moduleGrp+".translateY", 11)
        cmds.setAttr(headInstance.moduleGrp+".translateZ", 7)
        cmds.setAttr(headInstance.moduleGrp+".rotateX", 0)
        cmds.setAttr(headInstance.moduleGrp+".rotateY", 8)
        cmds.setAttr(headInstance.moduleGrp+".rotateZ", 90)
        cmds.setAttr(headInstance.cvHeadLoc+".translateX", 2)
        cmds.setAttr(headInstance.cvHeadLoc+".translateZ", 3)
        cmds.setAttr(headInstance.cvJawLoc+".translateZ", 2)
        cmds.setAttr(headInstance.cvJawLoc+".rotateY", -15)
        cmds.setAttr(headInstance.annotation+".translateX", 4)
        cmds.setAttr(headInstance.annotation+".translateY", 0)
        
        # parent head guide to spine guide:
        cmds.parent(headInstance.moduleGrp, spineInstance.cvLocator, absolute=True)
        
        # working with BACK LEG (B) system:
        # create back leg module instance:
        backLegLimbInstance = self.initGuide('dpLimb', guideDir)
        # change limb guide to back leg type:
        self.guide.Limb.changeType(backLegLimbInstance, self.langDic[self.langName]['m030_leg'])
        # change limb guide to back leg style (quadruped):
        self.guide.Limb.changeStyle(backLegLimbInstance, self.langDic[self.langName]['m037_quadruped'])
        # set for not use bend ribbons as default:
        self.guide.Limb.setBendFalse(backLegLimbInstance)
        # change name to back leg:
        self.guide.Limb.editUserName(backLegLimbInstance, checkText=self.langDic[self.langName]['m030_leg'].lower()+'B')
        cmds.setAttr(backLegLimbInstance.annotation+".translateY", -4)
        
        # editing back leg base guide informations:
        backLegBaseGuide = backLegLimbInstance.moduleGrp
        cmds.setAttr(backLegBaseGuide+".type", 1)
        cmds.setAttr(backLegBaseGuide+".translateX", 3)
        cmds.setAttr(backLegBaseGuide+".translateY", 9.5)
        cmds.setAttr(backLegBaseGuide+".translateZ", -6.5)
        cmds.setAttr(backLegBaseGuide+".rotateX", 0)
        
        # edit before, main and corners:
        cmds.setAttr(backLegLimbInstance.cvBeforeLoc+".translateX", 2)
        cmds.setAttr(backLegLimbInstance.cvBeforeLoc+".translateY", 2)
        cmds.setAttr(backLegLimbInstance.cvBeforeLoc+".translateZ", -1)
        cmds.setAttr(backLegLimbInstance.cvBeforeLoc+".rotateY", 65)
        cmds.setAttr(backLegLimbInstance.cvBeforeLoc+".rotateZ", -136)
        cmds.setAttr(backLegLimbInstance.cvMainLoc+".rotateY", 12)
        cmds.setAttr(backLegLimbInstance.cvCornerALoc+".translateX", 0.7)
        cmds.setAttr(backLegLimbInstance.cvCornerALoc+".translateZ", -0.7)
        cmds.setAttr(backLegLimbInstance.cvCornerBLoc+".translateX", -0.5)
        cmds.setAttr(backLegLimbInstance.cvCornerBLoc+".translateZ", 2)
        
        # edit location of back leg ankle guide:
        cmds.setAttr(backLegLimbInstance.cvExtremLoc+".translateZ", 8)
        # parent back leg guide to spine base guide:
        cmds.parent(backLegBaseGuide, spineInstance.moduleGrp, absolute=True)
        # setting X mirror:
        self.guide.Limb.changeMirror(backLegLimbInstance, "X")
        
        # create BACK FOOT (B) module instance:
        backFootInstance = self.initGuide('dpFoot', guideDir)
        self.guide.Foot.editUserName(backFootInstance, checkText=self.langDic[self.langName]['m024_foot'].lower()+'B')
        cmds.setAttr(backFootInstance.annotation+".translateY", -3)
        cmds.setAttr(backFootInstance.moduleGrp+".translateX", 3)
        cmds.setAttr(backFootInstance.moduleGrp+".translateZ", -6.5)
        cmds.setAttr(backFootInstance.cvFootLoc+".translateZ", 1.5)
        cmds.setAttr(backFootInstance.cvRFALoc+".translateX", 0)
        cmds.setAttr(backFootInstance.cvRFBLoc+".translateX", 0)
        cmds.setAttr(backFootInstance.cvRFDLoc+".translateX", -1.5)
        cmds.setAttr(backFootInstance.cvRFELoc+".translateZ", 1)
        
        # parent back foot guide to back leg ankle guide:
        cmds.parent(backFootInstance.moduleGrp, backLegLimbInstance.cvExtremLoc, absolute=True)
        
        # working with FRONT LEG (A) system:
        # create front leg module instance:
        frontLegLimbInstance = self.initGuide('dpLimb', guideDir)
        # change limb guide to front leg type:
        self.guide.Limb.changeType(frontLegLimbInstance, self.langDic[self.langName]['m030_leg'])
        # change limb guide to front leg style (quadruped spring):
        self.guide.Limb.changeStyle(frontLegLimbInstance, self.langDic[self.langName]['m043_quadSpring'])
        # set for not use bend ribbons as default:
        self.guide.Limb.setBendFalse(frontLegLimbInstance)
        # change name to front leg:
        self.guide.Limb.editUserName(frontLegLimbInstance, checkText=self.langDic[self.langName]['m030_leg'].lower()+'A')
        cmds.setAttr(frontLegLimbInstance.annotation+".translateY", -4)
        
        # editing front leg base guide informations:
        frontLegBaseGuide = frontLegLimbInstance.moduleGrp
        cmds.setAttr(frontLegBaseGuide+".type", 1)
        cmds.setAttr(frontLegBaseGuide+".translateX", 2.5)
        cmds.setAttr(frontLegBaseGuide+".translateY", 8)
        cmds.setAttr(frontLegBaseGuide+".translateZ", 5.5)
        cmds.setAttr(frontLegBaseGuide+".rotateX", 0)
        
        # edit before, main and corners:
        cmds.setAttr(frontLegLimbInstance.cvBeforeLoc+".translateX", -1.4)
        cmds.setAttr(frontLegLimbInstance.cvBeforeLoc+".translateY", 1.7)
        cmds.setAttr(frontLegLimbInstance.cvBeforeLoc+".translateZ", -2.5)
        cmds.setAttr(frontLegLimbInstance.cvBeforeLoc+".rotateY", 40)
        cmds.setAttr(frontLegLimbInstance.cvBeforeLoc+".rotateZ", -50)
        cmds.setAttr(frontLegLimbInstance.cvMainLoc+".rotateY", -15)
        cmds.setAttr(frontLegLimbInstance.cvCornerALoc+".translateX", -0.5)
        cmds.setAttr(frontLegLimbInstance.cvCornerALoc+".translateZ", -1.3)
        cmds.setAttr(frontLegLimbInstance.cvCornerBLoc+".translateX", 0.2)
        cmds.setAttr(frontLegLimbInstance.cvCornerBLoc+".translateZ", 1.2)
        
        # edit location of front leg ankle guide:
        cmds.setAttr(frontLegLimbInstance.cvExtremLoc+".translateZ", 6.5)
        # parent front leg guide to spine chest guide:
        cmds.parent(frontLegBaseGuide, spineInstance.cvLocator, absolute=True)
        # setting X mirror:
        self.guide.Limb.changeMirror(frontLegLimbInstance, "X")
        
        # create FRONT FOOT (A) module instance:
        frontFootInstance = self.initGuide('dpFoot', guideDir)
        self.guide.Foot.editUserName(frontFootInstance, checkText=self.langDic[self.langName]['m024_foot'].lower()+'A')
        cmds.setAttr(frontFootInstance.annotation+".translateY", -3)
        cmds.setAttr(frontFootInstance.moduleGrp+".translateX", 2.5)
        cmds.setAttr(frontFootInstance.moduleGrp+".translateZ", 5.5)
        cmds.setAttr(frontFootInstance.cvFootLoc+".translateZ", 1.5)
        cmds.setAttr(frontFootInstance.cvRFALoc+".translateX", 0)
        cmds.setAttr(frontFootInstance.cvRFBLoc+".translateX", 0)
        cmds.setAttr(frontFootInstance.cvRFDLoc+".translateX", -1.5)
        cmds.setAttr(frontFootInstance.cvRFELoc+".translateZ", 1)
        
        # parent fron foot guide to front leg ankle guide:
        cmds.parent(frontFootInstance.moduleGrp, frontLegLimbInstance.cvExtremLoc, absolute=True)
        
        # woking with TAIL system:
        # create FkLine module instance:
        tailInstance = self.initGuide('dpFkLine', guideDir)
        # editing tail base guide informations:
        self.guide.FkLine.editUserName(tailInstance, checkText=self.langDic[self.langName]['m039_tail'].lower())
        cmds.setAttr(tailInstance.moduleGrp+".translateY", 9.8)
        cmds.setAttr(tailInstance.moduleGrp+".translateZ", -7.6)
        cmds.setAttr(tailInstance.moduleGrp+".rotateX", 180)
        cmds.setAttr(tailInstance.moduleGrp+".rotateY", 20)
        cmds.setAttr(tailInstance.moduleGrp+".rotateZ", 90)
        cmds.setAttr(tailInstance.annotation+".translateX", 4)
        cmds.setAttr(tailInstance.annotation+".translateY", 0)
        cmds.setAttr(tailInstance.radiusCtrl+".translateX", 1)
        # change the number of joints to the tail module:
        self.guide.FkLine.changeJointNumber(tailInstance, 3)
        
        # parent tail guide to spine guide:
        cmds.parent(tailInstance.moduleGrp, spineInstance.moduleGrp, absolute=True)
        
        # woking with EAR system:
        # create FkLine module instance:
        earInstance = self.initGuide('dpFkLine', guideDir)
        # editing ear base guide informations:
        self.guide.FkLine.editUserName(earInstance, checkText=self.langDic[self.langName]['m040_ear'].lower())
        cmds.setAttr(earInstance.moduleGrp+".translateX", 0.8)
        cmds.setAttr(earInstance.moduleGrp+".translateY", 14.5)
        cmds.setAttr(earInstance.moduleGrp+".translateZ", 10)
        cmds.setAttr(earInstance.moduleGrp+".rotateX", 90)
        cmds.setAttr(earInstance.moduleGrp+".rotateY", 20)
        cmds.setAttr(earInstance.moduleGrp+".rotateZ", 127)
        cmds.setAttr(earInstance.annotation+".translateX", 4)
        cmds.setAttr(earInstance.annotation+".translateY", 0)
        cmds.setAttr(earInstance.annotation+".translateZ", 1.4)
        cmds.setAttr(earInstance.radiusCtrl+".translateX", 1)
        # change the number of joints to the ear module:
        self.guide.FkLine.changeJointNumber(earInstance, 2)
        
        # parent ear guide to spine guide:
        cmds.parent(earInstance.moduleGrp, headInstance.cvHeadLoc, absolute=True)
        cmds.setAttr(earInstance.moduleGrp+".scaleX", 0.5)
        cmds.setAttr(earInstance.moduleGrp+".scaleY", 0.5)
        cmds.setAttr(earInstance.moduleGrp+".scaleZ", 0.5)
        # setting X mirror:
        self.guide.FkLine.changeMirror(earInstance, "X")
        
        # select spineGuide_base:
        cmds.select(spineInstance.moduleGrp)
    else:
        # error checking modules in the folder:
        mel.eval('error \"'+ self.langDic[self.langName]['e001_guideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
