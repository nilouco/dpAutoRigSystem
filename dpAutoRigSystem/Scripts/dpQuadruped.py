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
    checkModuleList = ['dpLimb', 'dpFoot', 'dpSpine', 'dpHead', 'dpFkLine', 'dpEye']
    checkResultList = dpAutoRigInst.startGuideModules(guideDir, "check", None, checkModuleList=checkModuleList)
    
    if len(checkResultList) == 0:
        # Starting progress window
        progressAmount = 0
        cmds.progressWindow(title='Quadruped Guides', progress=progressAmount, status=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': 0%', isInterruptable=False)
        maxProcess = 13 # number of modules to create

        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m011_spine']))
        
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
        dpAutoRigInst.guide.Spine.changeStyle(spineInstance, dpAutoRigInst.langDic[dpAutoRigInst.langName]['m026_biped'])
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_neck']))
        
        # woking with NeckBase system:
        # create fkLine module instance:
        neckBaseInstance = dpAutoRigInst.initGuide('dpFkLine', guideDir, RigType.quadruped)
        # editing fkLine base guide informations:
        dpAutoRigInst.guide.FkLine.editUserName(neckBaseInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_neck']+"Base")
        cmds.setAttr(neckBaseInstance.moduleGrp+".translateY", 9.5)
        cmds.setAttr(neckBaseInstance.moduleGrp+".translateZ", 5.5)
        cmds.setAttr(neckBaseInstance.moduleGrp+".rotateX", -45)
        cmds.setAttr(neckBaseInstance.radiusCtrl+".translateX", 2.8)
        
        # parent neckBase guide to spine guide:
        cmds.parent(neckBaseInstance.moduleGrp, spineInstance.cvLocator, absolute=True)
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m017_head']))
        
        # woking with HEAD system:
        # create head module instance:
        headInstance = dpAutoRigInst.initGuide('dpHead', guideDir, RigType.quadruped)
        # editing head base guide informations:
        dpAutoRigInst.guide.Head.editUserName(headInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_head'])
        cmds.setAttr(headInstance.moduleGrp+".translateY", 11)
        cmds.setAttr(headInstance.moduleGrp+".translateZ", 7)
        cmds.setAttr(headInstance.moduleGrp+".rotateX", 0)
        cmds.setAttr(headInstance.moduleGrp+".rotateY", 45)
        cmds.setAttr(headInstance.moduleGrp+".rotateZ", 90)
        cmds.setAttr(headInstance.cvNeckLoc+".rotateX", 0)
        cmds.setAttr(headInstance.cvNeckLoc+".rotateZ", -90)
        cmds.setAttr(headInstance.cvHeadLoc+".translateY", 0)
        cmds.setAttr(headInstance.cvHeadLoc+".translateZ", 2.5)
        cmds.setAttr(headInstance.cvHeadLoc+".rotateX", 45)
        cmds.setAttr(headInstance.cvJawLoc+".translateY", -1.0)
        cmds.setAttr(headInstance.cvJawLoc+".translateZ", 2.0)
        cmds.setAttr(headInstance.cvJawLoc+".rotateY", 0)
        cmds.setAttr(headInstance.cvLLipLoc+".translateX", 0.6)
        cmds.setAttr(headInstance.cvLLipLoc+".translateY", -0.15)
        cmds.setAttr(headInstance.cvLLipLoc+".translateZ", 1.6)
        cmds.setAttr(headInstance.annotation+".translateX", 4)
        cmds.setAttr(headInstance.annotation+".translateY", 0)
        
        # parent head guide to neckBase guide:
        cmds.parent(headInstance.moduleGrp, neckBaseInstance.cvJointLoc, absolute=True)
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m063_eye']))
        
        # woking with Eye system:
        # create eyeLookAt module instance:
        eyeInstance = dpAutoRigInst.initGuide('dpEye', guideDir, RigType.quadruped)
        # setting X mirror:
        dpAutoRigInst.guide.Eye.changeMirror(eyeInstance, "X")
        # editing eyeLookAt base guide informations:
        dpAutoRigInst.guide.Eye.editUserName(eyeInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_eye'])
        cmds.setAttr(eyeInstance.moduleGrp+".translateX", 0.5)
        cmds.setAttr(eyeInstance.moduleGrp+".translateY", 13.5)
        cmds.setAttr(eyeInstance.moduleGrp+".translateZ", 11)
        cmds.setAttr(eyeInstance.annotation+".translateY", 3.5)
        cmds.setAttr(eyeInstance.radiusCtrl+".translateX", 0.5)
        cmds.setAttr(eyeInstance.cvEndJoint+".translateZ", 7)
        cmds.setAttr(eyeInstance.moduleGrp+".flip", 1)
        
        # parent head guide to spine guide:
        cmds.parent(eyeInstance.moduleGrp, headInstance.cvHeadLoc, absolute=True)
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m030_leg']))
        
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
        dpAutoRigInst.guide.Limb.editUserName(backLegLimbInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m030_leg'].capitalize()+dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_back'])
        cmds.setAttr(backLegLimbInstance.annotation+".translateY", -4)
        
        # editing back leg base guide informations:
        backLegBaseGuide = backLegLimbInstance.moduleGrp
        cmds.setAttr(backLegBaseGuide+".type", 1)
        cmds.setAttr(backLegBaseGuide+".translateX", 3)
        cmds.setAttr(backLegBaseGuide+".translateY", 9.5)
        cmds.setAttr(backLegBaseGuide+".translateZ", -6.5)
        cmds.setAttr(backLegBaseGuide+".rotateX", 0)
        
        # edit before, main and corners:
        cmds.setAttr(backLegLimbInstance.cvBeforeLoc+".translateX", 1)
        cmds.setAttr(backLegLimbInstance.cvBeforeLoc+".translateY", 0,5)
        cmds.setAttr(backLegLimbInstance.cvBeforeLoc+".translateZ", -2.5)
        cmds.setAttr(backLegLimbInstance.cvBeforeLoc+".rotateX", 20)
        cmds.setAttr(backLegLimbInstance.cvBeforeLoc+".rotateY", 10)
        cmds.setAttr(backLegLimbInstance.cvBeforeLoc+".rotateZ", -105)
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
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m024_foot']))
        
        # create BACK FOOT (B) module instance:
        backFootInstance = dpAutoRigInst.initGuide('dpFoot', guideDir, RigType.quadruped)
        dpAutoRigInst.guide.Foot.editUserName(backFootInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_foot']+dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_back'])
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
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m030_leg']))
        
        # working with FRONT LEG (A) system:
        # create front leg module instance:
        frontLegLimbInstance = dpAutoRigInst.initGuide('dpLimb', guideDir, RigType.quadruped)
        # change limb guide to front leg type:
        dpAutoRigInst.guide.Limb.changeType(frontLegLimbInstance, dpAutoRigInst.langDic[dpAutoRigInst.langName]['m030_leg'])
        # change limb guide to front leg style (biped):
        dpAutoRigInst.guide.Limb.changeStyle(frontLegLimbInstance, dpAutoRigInst.langDic[dpAutoRigInst.langName]['m026_biped'])
        # set for not use bend ribbons as default:
        dpAutoRigInst.guide.Limb.setBendFalse(frontLegLimbInstance)
        # change name to front leg:
        dpAutoRigInst.guide.Limb.editUserName(frontLegLimbInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m030_leg'].capitalize()+dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_front'])
        cmds.setAttr(frontLegLimbInstance.annotation+".translateY", -4)
        
        # editing front leg base guide informations:
        frontLegBaseGuide = frontLegLimbInstance.moduleGrp
        cmds.setAttr(frontLegBaseGuide+".type", 1)
        cmds.setAttr(frontLegBaseGuide+".translateX", 2.5)
        cmds.setAttr(frontLegBaseGuide+".translateY", 8)
        cmds.setAttr(frontLegBaseGuide+".translateZ", 5.5)
        cmds.setAttr(frontLegBaseGuide+".rotateX", 0)
        
        # edit before, main and corners:
        cmds.setAttr(frontLegLimbInstance.cvBeforeLoc+".translateX", -0.75)
        cmds.setAttr(frontLegLimbInstance.cvBeforeLoc+".translateY", 0.5)
        cmds.setAttr(frontLegLimbInstance.cvBeforeLoc+".translateZ", -2.5)
        cmds.setAttr(frontLegLimbInstance.cvBeforeLoc+".rotateX", -15)
        cmds.setAttr(frontLegLimbInstance.cvBeforeLoc+".rotateY", 15)
        cmds.setAttr(frontLegLimbInstance.cvBeforeLoc+".rotateZ", -90)
        cmds.setAttr(frontLegLimbInstance.cvMainLoc+".rotateY", -27)
        cmds.setAttr(frontLegLimbInstance.cvCornerLoc+".translateX", -2.0)
        cmds.setAttr(frontLegLimbInstance.cvCornerLoc+".translateZ", -0.6)
        
        # edit location of front leg ankle guide:
        cmds.setAttr(frontLegLimbInstance.cvExtremLoc+".translateZ", 6.5)

        # edit location of double front leg joint:
        cmds.setAttr(frontLegLimbInstance.cvCornerBLoc+".translateX", 0.5)

        # parent front leg guide to spine chest guide:
        cmds.parent(frontLegBaseGuide, spineInstance.cvLocator, absolute=True)
        # setting X mirror:
        dpAutoRigInst.guide.Limb.changeMirror(frontLegLimbInstance, "X")
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m024_foot']))
        
        # create FRONT FOOT (A) module instance:
        frontFootInstance = dpAutoRigInst.initGuide('dpFoot', guideDir, RigType.quadruped)
        dpAutoRigInst.guide.Foot.editUserName(frontFootInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_foot']+dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_front'])
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
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m039_tail']))
        
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
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m040_ear']))
        
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
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m075_upperTeeth']))
        
        # woking with Teeth system:
        # create FkLine module instance:
        upperTeethInstance = dpAutoRigInst.initGuide('dpFkLine', guideDir)
        # editing upperTeeth base guide informations:
        dpAutoRigInst.guide.FkLine.editUserName(upperTeethInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m075_upperTeeth'])
        cmds.setAttr(upperTeethInstance.moduleGrp+".translateY", 12.5)
        cmds.setAttr(upperTeethInstance.moduleGrp+".translateZ", 12.7)
        cmds.setAttr(upperTeethInstance.radiusCtrl+".translateX", 0.5)
        cmds.setAttr(upperTeethInstance.cvEndJoint+".translateZ", 0.1)
        cmds.setAttr(upperTeethInstance.moduleGrp+".shapeSize", 0.5)
        # create FkLine module instance:
        upperTeethMiddleInstance = dpAutoRigInst.initGuide('dpFkLine', guideDir)
        # editing upperTeethMiddle base guide informations:
        dpAutoRigInst.guide.FkLine.editUserName(upperTeethMiddleInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m075_upperTeeth']+dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_middle'])
        cmds.setAttr(upperTeethMiddleInstance.moduleGrp+".translateY", 12.3)
        cmds.setAttr(upperTeethMiddleInstance.moduleGrp+".translateZ", 12.7)
        cmds.setAttr(upperTeethMiddleInstance.radiusCtrl+".translateX", 0.2)
        cmds.setAttr(upperTeethMiddleInstance.cvEndJoint+".translateZ", 0.1)
        cmds.setAttr(upperTeethMiddleInstance.moduleGrp+".shapeSize", 0.3)
        # parent upperTeethMiddle guide to upperTeeth guide:
        cmds.parent(upperTeethMiddleInstance.moduleGrp, upperTeethInstance.cvJointLoc, absolute=True)
        # create FkLine module instance:
        upperTeethSideInstance = dpAutoRigInst.initGuide('dpFkLine', guideDir)
        # editing upperTeethSide base guide informations:
        dpAutoRigInst.guide.FkLine.editUserName(upperTeethSideInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m075_upperTeeth']+dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_RevFoot_G'].capitalize())
        cmds.setAttr(upperTeethSideInstance.moduleGrp+".translateX", 0.2)
        cmds.setAttr(upperTeethSideInstance.moduleGrp+".translateY", 12.3)
        cmds.setAttr(upperTeethSideInstance.moduleGrp+".translateZ", 12.3)
        cmds.setAttr(upperTeethSideInstance.radiusCtrl+".translateX", 0.2)
        cmds.setAttr(upperTeethSideInstance.cvEndJoint+".translateZ", 0.1)
        cmds.setAttr(upperTeethSideInstance.moduleGrp+".shapeSize", 0.3)
        dpAutoRigInst.guide.FkLine.changeMirror(upperTeethSideInstance, "X")
        cmds.setAttr(upperTeethSideInstance.moduleGrp+".flip", 1)
        # parent upperTeethSide guide to upperTeeth guide:
        cmds.parent(upperTeethSideInstance.moduleGrp, upperTeethInstance.cvJointLoc, absolute=True)
        # create FkLine module instance:
        lowerTeethInstance = dpAutoRigInst.initGuide('dpFkLine', guideDir)
        # editing lowerTeeth base guide informations:
        dpAutoRigInst.guide.FkLine.editUserName(lowerTeethInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m076_lowerTeeth'])
        cmds.setAttr(lowerTeethInstance.moduleGrp+".translateY", 11.7)
        cmds.setAttr(lowerTeethInstance.moduleGrp+".translateZ", 12.7)
        cmds.setAttr(lowerTeethInstance.radiusCtrl+".translateX", 0.5)
        cmds.setAttr(lowerTeethInstance.cvEndJoint+".translateZ", 0.1)
        cmds.setAttr(lowerTeethInstance.moduleGrp+".shapeSize", 0.5)
        # parent lowerTeeth guide to head guide:
        cmds.parent(lowerTeethInstance.moduleGrp, headInstance.cvChinLoc, absolute=True)
        # create FkLine module instance:
        lowerTeethMiddleInstance = dpAutoRigInst.initGuide('dpFkLine', guideDir)
        # editing lowerTeethMiddle base guide informations:
        dpAutoRigInst.guide.FkLine.editUserName(lowerTeethMiddleInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m076_lowerTeeth']+dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_middle'])
        cmds.setAttr(lowerTeethMiddleInstance.moduleGrp+".translateY", 11.9)
        cmds.setAttr(lowerTeethMiddleInstance.moduleGrp+".translateZ", 12.7)
        cmds.setAttr(lowerTeethMiddleInstance.radiusCtrl+".translateX", 0.2)
        cmds.setAttr(lowerTeethMiddleInstance.cvEndJoint+".translateZ", 0.1)
        cmds.setAttr(lowerTeethMiddleInstance.moduleGrp+".shapeSize", 0.3)
        # parent lowerTeeth guide to lowerTeeth guide:
        cmds.parent(lowerTeethMiddleInstance.moduleGrp, lowerTeethInstance.cvJointLoc, absolute=True)
        # create FkLine module instance:
        lowerTeethSideInstance = dpAutoRigInst.initGuide('dpFkLine', guideDir)
        # editing lowerTeethSide base guide informations:
        dpAutoRigInst.guide.FkLine.editUserName(lowerTeethSideInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m076_lowerTeeth']+dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_RevFoot_G'].capitalize())
        cmds.setAttr(lowerTeethSideInstance.moduleGrp+".translateX", 0.2)
        cmds.setAttr(lowerTeethSideInstance.moduleGrp+".translateY", 11.9)
        cmds.setAttr(lowerTeethSideInstance.moduleGrp+".translateZ", 12.3)
        cmds.setAttr(lowerTeethSideInstance.radiusCtrl+".translateX", 0.2)
        cmds.setAttr(lowerTeethSideInstance.cvEndJoint+".translateZ", 0.1)
        cmds.setAttr(lowerTeethSideInstance.moduleGrp+".shapeSize", 0.3)
        dpAutoRigInst.guide.FkLine.changeMirror(lowerTeethSideInstance, "X")
        cmds.setAttr(lowerTeethSideInstance.moduleGrp+".flip", 1)
        # parent lowerTeethSide guide to lowerTeeth guide:
        cmds.parent(lowerTeethSideInstance.moduleGrp, lowerTeethInstance.cvJointLoc, absolute=True)
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m077_tongue']))
        
        # woking with Tongue system:
        # create FkLine module instance:
        tongueInstance = dpAutoRigInst.initGuide('dpFkLine', guideDir)
        # editing tongue base guide informations:
        dpAutoRigInst.guide.FkLine.editUserName(tongueInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m077_tongue'])
        cmds.setAttr(tongueInstance.moduleGrp+".translateY", 12)
        cmds.setAttr(tongueInstance.moduleGrp+".translateZ", 12)
        cmds.setAttr(tongueInstance.radiusCtrl+".translateX", 0.35)
        dpAutoRigInst.guide.FkLine.changeJointNumber(tongueInstance, 2)
        cmds.setAttr(tongueInstance.moduleGrp+".nJoints", 2)
        cmds.setAttr(tongueInstance.cvJointLoc+".translateZ", 0.3)
        dpAutoRigInst.guide.FkLine.changeJointNumber(tongueInstance, 3)
        cmds.setAttr(tongueInstance.moduleGrp+".nJoints", 3)
        cmds.setAttr(tongueInstance.cvJointLoc+".translateZ", 0.3)
        cmds.setAttr(tongueInstance.cvEndJoint+".translateZ", 0.2)
        cmds.setAttr(tongueInstance.moduleGrp+".shapeSize", 0.4)
        # parent tongue guide to head guide:
        cmds.parent(tongueInstance.moduleGrp, headInstance.cvChinLoc, absolute=True)
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m078_nose']))
        
        # woking with Nose and Nostril systems:
        # create FkLine module instance:
        noseInstance = dpAutoRigInst.initGuide('dpFkLine', guideDir)
        # editing upperTeeth base guide informations:
        dpAutoRigInst.guide.FkLine.editUserName(noseInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m078_nose'])
        cmds.setAttr(noseInstance.moduleGrp+".translateY", 13)
        cmds.setAttr(noseInstance.moduleGrp+".translateZ", 11.5)
        cmds.setAttr(noseInstance.radiusCtrl+".translateX", 0.3)
        dpAutoRigInst.guide.FkLine.changeJointNumber(noseInstance, 2)
        cmds.setAttr(noseInstance.moduleGrp+".nJoints", 2)
        cmds.setAttr(noseInstance.cvJointLoc+".translateY", -0.2)
        cmds.setAttr(noseInstance.cvJointLoc+".translateZ", 0.7)
        cmds.setAttr(noseInstance.cvEndJoint+".translateZ", 0.1)
        cmds.setAttr(noseInstance.moduleGrp+".shapeSize", 0.5)
        storedNose2Guide = noseInstance.cvJointLoc
        # adding a new nose point segment to quadrupeds:
        dpAutoRigInst.guide.FkLine.changeJointNumber(noseInstance, 3)
        cmds.setAttr(noseInstance.moduleGrp+".nJoints", 3)
        cmds.setAttr(noseInstance.cvJointLoc+".translateZ", 0.7)
        cmds.setAttr(noseInstance.cvEndJoint+".translateZ", 0.1)
        # parent nose guide to head guide:
        cmds.parent(noseInstance.moduleGrp, headInstance.cvHeadLoc, absolute=True)
        # parent upperTeeth guide to Nose1 guide:
        cmds.parent(upperTeethInstance.moduleGrp, noseInstance.moduleGrp, absolute=True)
        # create FkLine module instance:
        nostrilInstance = dpAutoRigInst.initGuide('dpFkLine', guideDir)
        # editing nostril base guide informations:
        dpAutoRigInst.guide.FkLine.editUserName(nostrilInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m079_nostril'])
        cmds.setAttr(nostrilInstance.moduleGrp+".translateX", 0.33)
        cmds.setAttr(nostrilInstance.moduleGrp+".translateY", 12.7)
        cmds.setAttr(nostrilInstance.moduleGrp+".translateZ", 12.8)
        cmds.setAttr(nostrilInstance.radiusCtrl+".translateX", 0.2)
        cmds.setAttr(nostrilInstance.cvEndJoint+".translateZ", 0.1)
        cmds.setAttr(nostrilInstance.moduleGrp+".shapeSize", 0.3)
        # setting X mirror:
        dpAutoRigInst.guide.FkLine.changeMirror(nostrilInstance, "X")
        cmds.setAttr(nostrilInstance.moduleGrp+".flip", 1)
        # parent nostril guide to nose guide:
        cmds.parent(nostrilInstance.moduleGrp, storedNose2Guide, absolute=True)
        
        
        # Close progress window
        cmds.progressWindow(endProgress=True)
        
        # select spineGuide_Base:
        cmds.select(spineInstance.moduleGrp)
        print dpAutoRigInst.langDic[dpAutoRigInst.langName]['m090_createdQuadruped']
    else:
        # error checking modules in the folder:
        mel.eval('error \"'+ dpAutoRigInst.langDic[dpAutoRigInst.langName]['e001_GuideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
