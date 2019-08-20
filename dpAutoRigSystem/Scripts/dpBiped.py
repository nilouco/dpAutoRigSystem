# importing libraries:
import maya.cmds as cmds
import maya.mel as mel

# global variables to this module:    
CLASS_NAME = "Biped"
TITLE = "m026_biped"
DESCRIPTION = "m027_bipedDesc"
ICON = "/Icons/dp_biped.png"


def Biped(dpAutoRigInst):
    """ This function will create all guides needed to compose a biped.
    """
    # check modules integrity:
    guideDir = 'Modules'
    checkModuleList = ['dpLimb', 'dpFoot', 'dpFinger', 'dpSpine', 'dpHead', 'dpFkLine', 'dpEye']
    checkResultList = dpAutoRigInst.startGuideModules(guideDir, "check", None, checkModuleList=checkModuleList)
    
    if len(checkResultList) == 0:
        # Starting progress window
        progressAmount = 0
        cmds.progressWindow(title='Biped Guides', progress=progressAmount, status=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': 0%', isInterruptable=False)
        maxProcess = 12 # number of modules to create

        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m011_spine']))
        
        # woking with SPINE system:
        # create spine module instance:
        spineInstance = dpAutoRigInst.initGuide('dpSpine', guideDir)
        # editing spine base guide informations:
        dpAutoRigInst.guide.Spine.editUserName(spineInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m011_spine'])
        dpAutoRigInst.guide.Spine.changeStyle(spineInstance, dpAutoRigInst.langDic[dpAutoRigInst.langName]['m026_biped'])
        cmds.setAttr(spineInstance.moduleGrp+".translateY", 11)
        cmds.setAttr(spineInstance.annotation+".translateY", -6)
        cmds.setAttr(spineInstance.radiusCtrl+".translateX", 2.5)
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m017_head']))
        
        # woking with HEAD system:
        # create head module instance:
        headInstance = dpAutoRigInst.initGuide('dpHead', guideDir)
        # editing head base guide informations:
        dpAutoRigInst.guide.Head.editUserName(headInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_head'])
        cmds.setAttr(headInstance.moduleGrp+".translateY", 17)
        cmds.setAttr(headInstance.annotation+".translateY", 3.5)
        
        # parent head guide to spine guide:
        cmds.parent(headInstance.moduleGrp, spineInstance.cvLocator, absolute=True)
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m063_eye']))
        
        # woking with Eye system:
        # create eye module instance:
        eyeInstance = dpAutoRigInst.initGuide('dpEye', guideDir)
        # setting X mirror:
        dpAutoRigInst.guide.Eye.changeMirror(eyeInstance, "X")
        # editing eyeLookAt base guide informations:
        dpAutoRigInst.guide.Eye.editUserName(eyeInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_eye'])
        cmds.setAttr(eyeInstance.moduleGrp+".translateX", 0.5)
        cmds.setAttr(eyeInstance.moduleGrp+".translateY", 21)
        cmds.setAttr(eyeInstance.moduleGrp+".translateZ", 1.5)
        cmds.setAttr(eyeInstance.annotation+".translateY", 3.5)
        cmds.setAttr(eyeInstance.radiusCtrl+".translateX", 0.5)
        cmds.setAttr(eyeInstance.cvEndJoint+".translateZ", 7)
        cmds.setAttr(eyeInstance.moduleGrp+".flip", 1)
        
        # parent eye guide to spine guide:
        cmds.parent(eyeInstance.moduleGrp, headInstance.cvHeadLoc, absolute=True)
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m030_leg']))
        
        # working with LEG system:
        # create leg module instance:
        legLimbInstance = dpAutoRigInst.initGuide('dpLimb', guideDir)
        # setting X mirror:
        dpAutoRigInst.guide.Limb.changeMirror(legLimbInstance, "X")
        # change limb guide to leg type:
        dpAutoRigInst.guide.Limb.changeType(legLimbInstance, dpAutoRigInst.langDic[dpAutoRigInst.langName]['m030_leg'])
        # change limb style to biped:
        dpAutoRigInst.guide.Limb.changeStyle(legLimbInstance, dpAutoRigInst.langDic[dpAutoRigInst.langName]['m026_biped'])
        # change name to leg:
        dpAutoRigInst.guide.Limb.editUserName(legLimbInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m030_leg'].capitalize())
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
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m024_foot']))
        
        # create foot module instance:
        footInstance = dpAutoRigInst.initGuide('dpFoot', guideDir)
        dpAutoRigInst.guide.Foot.editUserName(footInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_foot'])
        cmds.setAttr(footInstance.annotation+".translateY", -3)
        cmds.setAttr(footInstance.moduleGrp+".translateX", 1.5)
        cmds.setAttr(footInstance.cvFootLoc+".translateZ", 1.5)
        
        # parent foot guide to leg ankle guide:
        cmds.parent(footInstance.moduleGrp, legLimbInstance.cvExtremLoc, absolute=True)
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m028_arm']))
        
        # working with ARM system:
        # creating module instances:
        armLimbInstance = dpAutoRigInst.initGuide('dpLimb', guideDir)
        # setting X mirror:
        dpAutoRigInst.guide.Limb.changeMirror(armLimbInstance, "X")
        # change limb style to biped:
        dpAutoRigInst.guide.Limb.changeStyle(armLimbInstance, dpAutoRigInst.langDic[dpAutoRigInst.langName]['m026_biped'])
        # change name to arm:
        dpAutoRigInst.guide.Limb.editUserName(armLimbInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_arm'].capitalize())
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
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m007_finger']))
        
        # create finger instances:
        indexFingerInstance  = dpAutoRigInst.initGuide('dpFinger', guideDir)
        dpAutoRigInst.guide.Finger.editUserName(indexFingerInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m007_finger']+"_"+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m032_index'])
        middleFingerInstance = dpAutoRigInst.initGuide('dpFinger', guideDir)
        dpAutoRigInst.guide.Finger.editUserName(middleFingerInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m007_finger']+"_"+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m033_middle'])
        ringFingerInstance   = dpAutoRigInst.initGuide('dpFinger', guideDir)
        dpAutoRigInst.guide.Finger.editUserName(ringFingerInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m007_finger']+"_"+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m034_ring'])
        pinkyFingerInstance   = dpAutoRigInst.initGuide('dpFinger', guideDir)
        dpAutoRigInst.guide.Finger.editUserName(pinkyFingerInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m007_finger']+"_"+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m035_pinky'])
        thumbFingerInstance  = dpAutoRigInst.initGuide('dpFinger', guideDir)
        dpAutoRigInst.guide.Finger.editUserName(thumbFingerInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m007_finger']+"_"+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m036_thumb'])
        
        # edit finger guides:
        fingerInstanceList = [indexFingerInstance, middleFingerInstance, ringFingerInstance, pinkyFingerInstance, thumbFingerInstance]
        fingerTZList       = [0.6, 0.2, -0.2, -0.6, 0.72]
        for n, fingerInstance in enumerate(fingerInstanceList):
            cmds.setAttr(fingerInstance.moduleGrp+".translateX", 11)
            cmds.setAttr(fingerInstance.moduleGrp+".translateY", 16)
            cmds.setAttr(fingerInstance.moduleGrp+".translateZ", fingerTZList[n])
            cmds.setAttr(fingerInstance.moduleGrp+".displayAnnotation", 0)
            cmds.setAttr(fingerInstance.radiusCtrl+".translateX", 0.3)
            cmds.setAttr(fingerInstance.annotation+".visibility", 0)
            cmds.setAttr(fingerInstance.moduleGrp+".shapeSize", 0.3)
            
            if n == len(fingerInstanceList)-1:
                # correct not commun values for thumb guide:
                cmds.setAttr(thumbFingerInstance.moduleGrp+".translateX", 10.1)
                cmds.setAttr(thumbFingerInstance.moduleGrp+".rotateX", 60)
                dpAutoRigInst.guide.Finger.changeJointNumber(thumbFingerInstance, 2)
                cmds.setAttr(thumbFingerInstance.moduleGrp+".nJoints", 2)
            
            # parent finger guide to the arm wrist guide:
            cmds.parent(fingerInstance.moduleGrp, armLimbInstance.cvExtremLoc, absolute=True)
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m040_ear']))
        
        # woking with EAR system:
        # create FkLine module instance:
        earInstance = dpAutoRigInst.initGuide('dpFkLine', guideDir)
        # editing ear base guide informations:
        dpAutoRigInst.guide.FkLine.editUserName(earInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m040_ear'])
        cmds.setAttr(earInstance.moduleGrp+".translateX", 1)
        cmds.setAttr(earInstance.moduleGrp+".translateY", 21)
        cmds.setAttr(earInstance.moduleGrp+".rotateY", 110)
        cmds.setAttr(earInstance.radiusCtrl+".translateX", 0.5)
        cmds.setAttr(earInstance.cvEndJoint+".translateZ", 0.4)
        # parent ear guide to head guide:
        cmds.parent(earInstance.moduleGrp, headInstance.cvHeadLoc, absolute=True)
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
        cmds.setAttr(upperTeethInstance.moduleGrp+".translateY", 20.3)
        cmds.setAttr(upperTeethInstance.moduleGrp+".translateZ", 2.2)
        cmds.setAttr(upperTeethInstance.radiusCtrl+".translateX", 0.5)
        cmds.setAttr(upperTeethInstance.cvEndJoint+".translateZ", 0.1)
        cmds.setAttr(upperTeethInstance.moduleGrp+".shapeSize", 0.5)
        # parent upperTeeth guide to head guide:
        cmds.parent(upperTeethInstance.moduleGrp, headInstance.cvHeadLoc, absolute=True)
        # create FkLine module instance:
        upperTeethMiddleInstance = dpAutoRigInst.initGuide('dpFkLine', guideDir)
        # editing upperTeethMiddle base guide informations:
        dpAutoRigInst.guide.FkLine.editUserName(upperTeethMiddleInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m075_upperTeeth']+dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_middle'])
        cmds.setAttr(upperTeethMiddleInstance.moduleGrp+".translateY", 20.1)
        cmds.setAttr(upperTeethMiddleInstance.moduleGrp+".translateZ", 2.2)
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
        cmds.setAttr(upperTeethSideInstance.moduleGrp+".translateY", 20.1)
        cmds.setAttr(upperTeethSideInstance.moduleGrp+".translateZ", 2)
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
        cmds.setAttr(lowerTeethInstance.moduleGrp+".translateY", 19.5)
        cmds.setAttr(lowerTeethInstance.moduleGrp+".translateZ", 2.2)
        cmds.setAttr(lowerTeethInstance.radiusCtrl+".translateX", 0.5)
        cmds.setAttr(lowerTeethInstance.cvEndJoint+".translateZ", 0.1)
        cmds.setAttr(lowerTeethInstance.moduleGrp+".shapeSize", 0.5)
        # parent lowerTeeth guide to head guide:
        cmds.parent(lowerTeethInstance.moduleGrp, headInstance.cvChinLoc, absolute=True)
        # create FkLine module instance:
        lowerTeethMiddleInstance = dpAutoRigInst.initGuide('dpFkLine', guideDir)
        # editing lowerTeethMiddle base guide informations:
        dpAutoRigInst.guide.FkLine.editUserName(lowerTeethMiddleInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m076_lowerTeeth']+dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_middle'])
        cmds.setAttr(lowerTeethMiddleInstance.moduleGrp+".translateY", 19.7)
        cmds.setAttr(lowerTeethMiddleInstance.moduleGrp+".translateZ", 2.2)
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
        cmds.setAttr(lowerTeethSideInstance.moduleGrp+".translateY", 19.7)
        cmds.setAttr(lowerTeethSideInstance.moduleGrp+".translateZ", 2)
        cmds.setAttr(lowerTeethSideInstance.radiusCtrl+".translateX", 0.2)
        cmds.setAttr(lowerTeethSideInstance.cvEndJoint+".translateZ", 0.1)
        cmds.setAttr(lowerTeethSideInstance.moduleGrp+".shapeSize", 0.3)
        dpAutoRigInst.guide.FkLine.changeMirror(lowerTeethSideInstance, "X")
        cmds.setAttr(lowerTeethSideInstance.moduleGrp+".flip", 1)
        # parent lowerTeethSide guide to lowerTeeth guide:
        cmds.parent(lowerTeethSideInstance.moduleGrp, lowerTeethInstance.cvJointLoc, absolute=True)
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m078_nose']))
        
        # woking with Nose and Nostril systems:
        # create FkLine module instance:
        noseInstance = dpAutoRigInst.initGuide('dpFkLine', guideDir)
        # editing upperTeeth base guide informations:
        dpAutoRigInst.guide.FkLine.editUserName(noseInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m078_nose'])
        cmds.setAttr(noseInstance.moduleGrp+".translateY", 20.9)
        cmds.setAttr(noseInstance.moduleGrp+".translateZ", 2)
        cmds.setAttr(noseInstance.radiusCtrl+".translateX", 0.3)
        dpAutoRigInst.guide.FkLine.changeJointNumber(noseInstance, 2)
        cmds.setAttr(noseInstance.moduleGrp+".nJoints", 2)
        cmds.setAttr(noseInstance.cvJointLoc+".translateY", -0.15)
        cmds.setAttr(noseInstance.cvJointLoc+".translateZ", 0.3)
        cmds.setAttr(noseInstance.cvEndJoint+".translateZ", 0.1)
        cmds.setAttr(noseInstance.moduleGrp+".shapeSize", 0.5)
        # parent nose guide to head guide:
        cmds.parent(noseInstance.moduleGrp, headInstance.cvHeadLoc, absolute=True)
        # create FkLine module instance:
        nostrilInstance = dpAutoRigInst.initGuide('dpFkLine', guideDir)
        # editing nostril base guide informations:
        dpAutoRigInst.guide.FkLine.editUserName(nostrilInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m079_nostril'])
        cmds.setAttr(nostrilInstance.moduleGrp+".translateX", 0.33)
        cmds.setAttr(nostrilInstance.moduleGrp+".translateY", 20.65)
        cmds.setAttr(nostrilInstance.moduleGrp+".translateZ", 2.15)
        cmds.setAttr(nostrilInstance.radiusCtrl+".translateX", 0.2)
        cmds.setAttr(nostrilInstance.cvEndJoint+".translateZ", 0.1)
        cmds.setAttr(nostrilInstance.moduleGrp+".shapeSize", 0.3)
        # setting X mirror:
        dpAutoRigInst.guide.FkLine.changeMirror(nostrilInstance, "X")
        cmds.setAttr(nostrilInstance.moduleGrp+".flip", 1)
        # parent nostril guide to nose guide:
        cmds.parent(nostrilInstance.moduleGrp, noseInstance.moduleGrp, absolute=True)
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m077_tongue']))
        
        # woking with Tongue system:
        # create FkLine module instance:
        tongueInstance = dpAutoRigInst.initGuide('dpFkLine', guideDir)
        # editing tongue base guide informations:
        dpAutoRigInst.guide.FkLine.editUserName(tongueInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m077_tongue'])
        cmds.setAttr(tongueInstance.moduleGrp+".translateY", 19.85)
        cmds.setAttr(tongueInstance.moduleGrp+".translateZ", 1.45)
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
        
        # Close progress window
        cmds.progressWindow(endProgress=True)
        
        # select spineGuide_Base:
        cmds.select(spineInstance.moduleGrp)
        print dpAutoRigInst.langDic[dpAutoRigInst.langName]['m089_createdBiped']
    else:
        # error checking modules in the folder:
        mel.eval('error \"'+ dpAutoRigInst.langDic[dpAutoRigInst.langName]['e001_GuideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
