# importing libraries:
import maya.cmds as cmds
import maya.mel as mel
from ..Modules.dpBaseClass import RigType

# global variables to this module:    
CLASS_NAME = "Quadruped"
TITLE = "m037_quadruped"
DESCRIPTION = "m038_quadrupedDesc"
ICON = "/Icons/dp_quadruped.png"


def Quadruped(dpAutoRigInst):
    """ This function will create all guides needed to compose a quadruped.
    """
    # check modules integrity:
    guideDir = 'Modules'
    checkModuleList = ['dpLimb', 'dpFoot', 'dpSpine', 'dpHead', 'dpFkLine']
    checkResultList = dpAutoRigInst.startGuideModules(guideDir, "check", None, checkModuleList=checkModuleList)
    
    if len(checkResultList) == 0:
        # woking with SPINE system:
        # create spine module instance:
        spineInstance = dpAutoRigInst.initGuide('dpSpine', guideDir, RigType.quadruped)
        # editing spine base guide informations:
        dpAutoRigInst.guide.Spine.editUserName(spineInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m011_spine'])
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
        headInstance = dpAutoRigInst.initGuide('dpHead', guideDir, RigType.quadruped)
        # editing head base guide informations:
        dpAutoRigInst.guide.Head.editUserName(headInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_head'])
        cmds.setAttr(headInstance.moduleGrp+".translateY", 11)
        cmds.setAttr(headInstance.moduleGrp+".translateZ", 7)
        cmds.setAttr(headInstance.moduleGrp+".rotateX", 0)
        cmds.setAttr(headInstance.moduleGrp+".rotateY", 8)
        cmds.setAttr(headInstance.moduleGrp+".rotateZ", 90)
        cmds.setAttr(headInstance.cvNeckLoc+".rotateY", 25)
        cmds.setAttr(headInstance.cvHeadLoc+".translateZ", 3.5)
        cmds.setAttr(headInstance.cvHeadLoc+".rotateY", -33)
        cmds.setAttr(headInstance.cvJawLoc+".translateZ", 1.6)
        cmds.setAttr(headInstance.cvJawLoc+".rotateY", -5.5)
        cmds.setAttr(headInstance.cvLLipLoc+".translateY", -0.5)
        cmds.setAttr(headInstance.cvLLipLoc+".translateZ", 0.6)
        cmds.setAttr(headInstance.annotation+".translateX", 4)
        cmds.setAttr(headInstance.annotation+".translateY", 0)
        
        # parent head guide to spine guide:
        cmds.parent(headInstance.moduleGrp, spineInstance.cvLocator, absolute=True)
        
        # woking with EyeLookAt system:
        # create eyeLookAt module instance:
        eyeLookAtInstance = dpAutoRigInst.initGuide('dpEyeLookAt', guideDir, RigType.quadruped)
        # setting X mirror:
        dpAutoRigInst.guide.EyeLookAt.changeMirror(eyeLookAtInstance, "X")
        # editing eyeLookAt base guide informations:
        dpAutoRigInst.guide.EyeLookAt.editUserName(eyeLookAtInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_eye'])
        cmds.setAttr(eyeLookAtInstance.moduleGrp+".translateX", 0.5)
        cmds.setAttr(eyeLookAtInstance.moduleGrp+".translateY", 13.5)
        cmds.setAttr(eyeLookAtInstance.moduleGrp+".translateZ", 11)
        cmds.setAttr(eyeLookAtInstance.annotation+".translateY", 3.5)
        cmds.setAttr(eyeLookAtInstance.radiusCtrl+".translateX", 0.5)
        
        # parent head guide to spine guide:
        cmds.parent(eyeLookAtInstance.moduleGrp, headInstance.cvHeadLoc, absolute=True)
        
        # working with BACK LEG (B) system:
        # create back leg module instance:
        backLegLimbInstance = dpAutoRigInst.initGuide('dpLimb', guideDir, RigType.quadruped)
        # change limb guide to back leg type:
        dpAutoRigInst.guide.Limb.changeType(backLegLimbInstance, dpAutoRigInst.langDic[dpAutoRigInst.langName]['m030_leg'])
        # change limb guide to back leg style (quadruped):
        dpAutoRigInst.guide.Limb.changeStyle(backLegLimbInstance, dpAutoRigInst.langDic[dpAutoRigInst.langName]['m037_quadruped'])
        # set for not use bend ribbons as default:
        dpAutoRigInst.guide.Limb.setBendFalse(backLegLimbInstance)
        # change name to back leg:
        dpAutoRigInst.guide.Limb.editUserName(backLegLimbInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m030_leg'].capitalize()+'B')
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
        cmds.setAttr(backLegLimbInstance.cvMainLoc+".rotateY", 25)
        cmds.setAttr(backLegLimbInstance.cvCornerLoc+".translateX", 0.7)
        cmds.setAttr(backLegLimbInstance.cvCornerLoc+".translateZ", -0.7)
        
        # edit location of back leg ankle guide:
        cmds.setAttr(backLegLimbInstance.cvExtremLoc+".translateZ", 8)

        # edit location of double back leg joint:
        cmds.setAttr(backLegLimbInstance.cvCornerBLoc+".translateX", -2)

        # parent back leg guide to spine base guide:
        cmds.parent(backLegBaseGuide, spineInstance.moduleGrp, absolute=True)
        # setting X mirror:
        dpAutoRigInst.guide.Limb.changeMirror(backLegLimbInstance, "X")
        
        # create BACK FOOT (B) module instance:
        backFootInstance = dpAutoRigInst.initGuide('dpFoot', guideDir, RigType.quadruped)
        dpAutoRigInst.guide.Foot.editUserName(backFootInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_foot']+'B')
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
        frontLegLimbInstance = dpAutoRigInst.initGuide('dpLimb', guideDir, RigType.quadruped)
        # change limb guide to front leg type:
        dpAutoRigInst.guide.Limb.changeType(frontLegLimbInstance, dpAutoRigInst.langDic[dpAutoRigInst.langName]['m030_leg'])
        # change limb guide to front leg style (quadruped spring):
        dpAutoRigInst.guide.Limb.changeStyle(frontLegLimbInstance, dpAutoRigInst.langDic[dpAutoRigInst.langName]['m043_quadSpring'])
        # set for not use bend ribbons as default:
        dpAutoRigInst.guide.Limb.setBendFalse(frontLegLimbInstance)
        # change name to front leg:
        dpAutoRigInst.guide.Limb.editUserName(frontLegLimbInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m030_leg'].capitalize()+'A')
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
        cmds.setAttr(frontLegLimbInstance.cvMainLoc+".rotateY", 18)
        cmds.setAttr(frontLegLimbInstance.cvCornerLoc+".translateX", -0.5)
        cmds.setAttr(frontLegLimbInstance.cvCornerLoc+".translateZ", -1.3)
        
        # edit location of front leg ankle guide:
        cmds.setAttr(frontLegLimbInstance.cvExtremLoc+".translateZ", 6.5)

        # edit location of double front leg joint:
        cmds.setAttr(frontLegLimbInstance.cvCornerBLoc+".translateX", 0.5)

        # parent front leg guide to spine chest guide:
        cmds.parent(frontLegBaseGuide, spineInstance.cvLocator, absolute=True)
        # setting X mirror:
        dpAutoRigInst.guide.Limb.changeMirror(frontLegLimbInstance, "X")
        
        # create FRONT FOOT (A) module instance:
        frontFootInstance = dpAutoRigInst.initGuide('dpFoot', guideDir, RigType.quadruped)
        dpAutoRigInst.guide.Foot.editUserName(frontFootInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_foot']+'A')
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
        tailInstance = dpAutoRigInst.initGuide('dpFkLine', guideDir, RigType.quadruped)
        # editing tail base guide informations:
        dpAutoRigInst.guide.FkLine.editUserName(tailInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m039_tail'])
        cmds.setAttr(tailInstance.moduleGrp+".translateY", 9.8)
        cmds.setAttr(tailInstance.moduleGrp+".translateZ", -7.6)
        cmds.setAttr(tailInstance.moduleGrp+".rotateX", 180)
        cmds.setAttr(tailInstance.moduleGrp+".rotateY", 20)
        cmds.setAttr(tailInstance.moduleGrp+".rotateZ", 90)
        cmds.setAttr(tailInstance.annotation+".translateX", 4)
        cmds.setAttr(tailInstance.annotation+".translateY", 0)
        cmds.setAttr(tailInstance.radiusCtrl+".translateX", 1)
        # change the number of joints to the tail module:
        dpAutoRigInst.guide.FkLine.changeJointNumber(tailInstance, 3)
        
        # parent tail guide to spine guide:
        cmds.parent(tailInstance.moduleGrp, spineInstance.moduleGrp, absolute=True)
        
        # woking with EAR system:
        # create FkLine module instance:
        earInstance = dpAutoRigInst.initGuide('dpFkLine', guideDir, RigType.quadruped)
        # editing ear base guide informations:
        dpAutoRigInst.guide.FkLine.editUserName(earInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m040_ear'])
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
        dpAutoRigInst.guide.FkLine.changeJointNumber(earInstance, 2)
        
        # parent ear guide to spine guide:
        cmds.parent(earInstance.moduleGrp, headInstance.cvHeadLoc, absolute=True)
        cmds.setAttr(earInstance.moduleGrp+".scaleX", 0.5)
        cmds.setAttr(earInstance.moduleGrp+".scaleY", 0.5)
        cmds.setAttr(earInstance.moduleGrp+".scaleZ", 0.5)
        # setting X mirror:
        dpAutoRigInst.guide.FkLine.changeMirror(earInstance, "X")
        cmds.setAttr(earInstance.moduleGrp+".flip", 1)
        
        # select spineGuide_Base:
        cmds.select(spineInstance.moduleGrp)
    else:
        # error checking modules in the folder:
        mel.eval('error \"'+ dpAutoRigInst.langDic[dpAutoRigInst.langName]['e001_GuideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
