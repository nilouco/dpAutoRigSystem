# importing libraries:
from maya import cmds
from maya import mel

# global variables to this module:    
CLASS_NAME = "Biped"
TITLE = "m026_biped"
DESCRIPTION = "m027_bipedDesc"
ICON = "/Icons/dp_biped.png"

DP_BIPED_VERSION = 2.1


def getUserDetail(opt1, opt2, cancel, userMessage):
    """ Ask user the detail level we'll create the guides by a confirm dialog box window.
        Options:
            Simple
            Complete
        Returns the user choose option or None if canceled.
    """
    result = cmds.confirmDialog(title=CLASS_NAME, message=userMessage, button=[opt1, opt2, cancel], defaultButton=opt2, cancelButton=cancel, dismissString=cancel)
    return result


def Biped(dpUIinst):
    """ This function will create all guides needed to compose a biped.
    """
    # check modules integrity:
    guideDir = 'Modules'
    checkModuleList = ['dpLimb', 'dpFoot', 'dpFinger', 'dpSpine', 'dpHead', 'dpFkLine', 'dpEye', 'dpNose', 'dpSingle']
    checkResultList = dpUIinst.startGuideModules(guideDir, "check", None, checkModuleList=checkModuleList)
    
    if len(checkResultList) == 0:
        # defining naming:
        doingName = dpUIinst.lang['m094_doing']
        bipedStyleName = dpUIinst.lang['m026_biped']
        # part names:
        spineName = dpUIinst.lang['m011_spine']
        headName = dpUIinst.lang['c024_head']
        eyeName = dpUIinst.lang['c036_eye']
        legName = dpUIinst.lang['m030_leg'].capitalize()
        footName = dpUIinst.lang['c038_foot']
        armName = dpUIinst.lang['c037_arm'].capitalize()
        fingerIndexName = dpUIinst.lang['m007_finger']+"_"+dpUIinst.lang['m032_index']
        fingerMiddleName = dpUIinst.lang['m007_finger']+"_"+dpUIinst.lang['m033_middle']
        fingerRingName = dpUIinst.lang['m007_finger']+"_"+dpUIinst.lang['m034_ring']
        fingerPinkyName = dpUIinst.lang['m007_finger']+"_"+dpUIinst.lang['m035_pinky']
        fingerThumbName = dpUIinst.lang['m007_finger']+"_"+dpUIinst.lang['m036_thumb']
        earName = dpUIinst.lang['m040_ear']
        upperTeethName = dpUIinst.lang['m075_upperTeeth']
        upperTeethMiddleName = dpUIinst.lang['m075_upperTeeth']+dpUIinst.lang['c029_middle'].capitalize()
        upperTeethSideName = dpUIinst.lang['m075_upperTeeth']+dpUIinst.lang['c016_revFoot_G'].capitalize()
        lowerTeethName = dpUIinst.lang['m076_lowerTeeth']
        lowerTeethMiddleName = dpUIinst.lang['m076_lowerTeeth']+dpUIinst.lang['c029_middle'].capitalize()
        lowerTeethSideName = dpUIinst.lang['m076_lowerTeeth']+dpUIinst.lang['c016_revFoot_G'].capitalize()
        noseName = dpUIinst.lang['m078_nose']
        tongueName = dpUIinst.lang['m077_tongue']
        toeName = dpUIinst.lang['c013_revFoot_D'].capitalize()
        breathName = dpUIinst.lang['c095_breath']
        bellyName = dpUIinst.lang['c096_belly']
        simple   = dpUIinst.lang['i175_simple']
        complete = dpUIinst.lang['i176_complete']
        cancel   = dpUIinst.lang['i132_cancel']
        userMessage = dpUIinst.lang['i177_chooseMessage']
        bipedGuideName = dpUIinst.lang['m026_biped']+" "+dpUIinst.lang['i205_guide']
        
        
        # getting Simple or Complete module guides to create:
        userDetail = getUserDetail(simple, complete, cancel, userMessage)
        if not userDetail == cancel:
            # number of modules to create:
            if userDetail == simple:
                maxProcess = 7
            else:
                maxProcess = 18
        
            # Starting progress window
            dpUIinst.utils.setProgress(doingName, bipedGuideName, maxProcess, addOne=False, addNumber=False)

            # working with SPINE system:
            dpUIinst.utils.setProgress(doingName+spineName)
            # create spine module instance:
            spineInstance = dpUIinst.initGuide('dpSpine', guideDir)
            # editing spine base guide informations:
            spineInstance.editUserName(spineName)
            spineInstance.changeStyle(bipedStyleName)
            cmds.setAttr(spineInstance.moduleGrp+".translateY", 11)
            cmds.setAttr(spineInstance.annotation+".translateY", -6)
            cmds.setAttr(spineInstance.radiusCtrl+".translateX", 2.5)
            cmds.refresh()
            
            # working with HEAD system:
            dpUIinst.utils.setProgress(doingName+headName)
            # create head module instance:
            headInstance = dpUIinst.initGuide('dpHead', guideDir)
            # editing head base guide informations:
            headInstance.editUserName(headName)
            headInstance.changeJointNumber(2)
            cmds.setAttr(headInstance.moduleGrp+".translateY", 17)
            cmds.setAttr(headInstance.annotation+".translateY", 3.5)
            # parent head guide to spine guide:
            cmds.parent(headInstance.moduleGrp, spineInstance.cvLocator, absolute=True)
            cmds.refresh()
            
            # working with Eye system:
            dpUIinst.utils.setProgress(doingName+eyeName)
            # create eye module instance:
            eyeInstance = dpUIinst.initGuide('dpEye', guideDir)
            # editing eyeLookAt base guide informations:
            eyeInstance.editUserName(eyeName)
            # setting X mirror:
            eyeInstance.changeMirror("X")
            cmds.setAttr(eyeInstance.moduleGrp+".translateX", 0.5)
            cmds.setAttr(eyeInstance.moduleGrp+".translateY", 21)
            cmds.setAttr(eyeInstance.moduleGrp+".translateZ", 1.5)
            cmds.setAttr(eyeInstance.annotation+".translateY", 3.5)
            cmds.setAttr(eyeInstance.radiusCtrl+".translateX", 0.5)
            cmds.setAttr(eyeInstance.cvEndJoint+".translateZ", 7)
            cmds.setAttr(eyeInstance.moduleGrp+".flip", 1)
            # parent eye guide to spine guide:
            cmds.parent(eyeInstance.moduleGrp, headInstance.cvUpperHeadLoc, absolute=True)
            cmds.refresh()
            
            # working with LEG system:
            dpUIinst.utils.setProgress(doingName+legName)
            # create leg module instance:
            legLimbInstance = dpUIinst.initGuide('dpLimb', guideDir)
            # change name to leg:
            legLimbInstance.editUserName(legName)
            # setting X mirror:
            legLimbInstance.changeMirror("X")
            # change limb guide to leg type:
            legLimbInstance.changeType(legName)
            # change limb style to biped:
            legLimbInstance.changeStyle(bipedStyleName)
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
            cmds.refresh()
            
            # working with FOOT system:
            dpUIinst.utils.setProgress(doingName+footName)
            # create foot module instance:
            footInstance = dpUIinst.initGuide('dpFoot', guideDir)
            footInstance.editUserName(footName)
            cmds.setAttr(footInstance.annotation+".translateY", -3)
            cmds.setAttr(footInstance.moduleGrp+".translateX", 1.5)
            cmds.setAttr(footInstance.cvFootLoc+".translateZ", 1.5)
            # parent foot guide to leg ankle guide:
            cmds.parent(footInstance.moduleGrp, legLimbInstance.cvExtremLoc, absolute=True)
            cmds.refresh()
            
            # working with ARM system:
            dpUIinst.utils.setProgress(doingName+armName)
            # creating module instances:
            armLimbInstance = dpUIinst.initGuide('dpLimb', guideDir)
            # change name to arm:
            armLimbInstance.editUserName(armName)
            # setting X mirror:
            armLimbInstance.changeMirror("X")
            # change limb style to biped:
            armLimbInstance.changeStyle(bipedStyleName)
            cmds.setAttr(armLimbInstance.annotation+".translateX", 3)
            cmds.setAttr(armLimbInstance.annotation+".translateY", 0)
            cmds.setAttr(armLimbInstance.annotation+".translateZ", 2)
            # edit arm limb guide:
            armBaseGuide = armLimbInstance.moduleGrp
            cmds.setAttr(armBaseGuide+".translateX", 2.5)
            cmds.setAttr(armBaseGuide+".translateY", 16)
            cmds.setAttr(armLimbInstance.cvExtremLoc+".translateZ", 7)
            cmds.setAttr(armLimbInstance.radiusCtrl+".translateX", 1.5)
            # parent arm guide to spine chest guide:
            cmds.parent(armLimbInstance.moduleGrp, spineInstance.cvLocator, absolute=True)
            cmds.refresh()
            
            # working with FINGERS system:
            dpUIinst.utils.setProgress(doingName+dpUIinst.lang['m007_finger'])
            # create finger instances:
            thumbFingerInstance = dpUIinst.initGuide('dpFinger', guideDir)
            thumbFingerInstance.editUserName(fingerThumbName)
            indexFingerInstance = dpUIinst.initGuide('dpFinger', guideDir)
            indexFingerInstance.editUserName(fingerIndexName)
            middleFingerInstance = dpUIinst.initGuide('dpFinger', guideDir)
            middleFingerInstance.editUserName(fingerMiddleName)
            ringFingerInstance = dpUIinst.initGuide('dpFinger', guideDir)
            ringFingerInstance.editUserName(fingerRingName)
            pinkyFingerInstance = dpUIinst.initGuide('dpFinger', guideDir)
            pinkyFingerInstance.editUserName(fingerPinkyName)
            # edit finger guides:
            fingerInstanceList = [thumbFingerInstance, indexFingerInstance, middleFingerInstance, ringFingerInstance, pinkyFingerInstance]
            fingerTZList       = [0.72, 0.6, 0.2, -0.2, -0.6]
            for n, fingerInstance in enumerate(fingerInstanceList):
                cmds.setAttr(fingerInstance.moduleGrp+".translateX", 11)
                cmds.setAttr(fingerInstance.moduleGrp+".translateY", 16)
                cmds.setAttr(fingerInstance.moduleGrp+".translateZ", fingerTZList[n])
                cmds.setAttr(fingerInstance.radiusCtrl+".translateX", 0.3)
                cmds.setAttr(fingerInstance.annotation+".visibility", 0)
                cmds.setAttr(fingerInstance.moduleGrp+".shapeSize", 0.3)
                fingerInstance.displayAnnotation(0)
                if n == 0:
                    # correct not commun values for thumb guide:
                    cmds.setAttr(thumbFingerInstance.moduleGrp+".translateX", 10.1)
                    cmds.setAttr(thumbFingerInstance.moduleGrp+".rotateX", 60)
                    thumbFingerInstance.changeJointNumber(2)
                    cmds.setAttr(thumbFingerInstance.moduleGrp+".nJoints", 2)
                # parent finger guide to the arm wrist guide:
                cmds.parent(fingerInstance.moduleGrp, armLimbInstance.cvExtremLoc, absolute=True)
                cmds.refresh()
            
            #
            # complete part:
            #
            if userDetail == complete:
            
                # set guides attributes to complete system
                headInstance.changeDeformer(1)
                headInstance.changeFacial(1)
                correctiveGuideInstanceList = [armLimbInstance, legLimbInstance] + fingerInstanceList
                for instance in correctiveGuideInstanceList:
                    instance.setCorrective(1)

                # working with EAR system:
                dpUIinst.utils.setProgress(doingName+earName)
                # create FkLine module instance:
                earInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing ear base guide informations:
                earInstance.editUserName(earName)
                cmds.setAttr(earInstance.moduleGrp+".translateX", 1)
                cmds.setAttr(earInstance.moduleGrp+".translateY", 21)
                cmds.setAttr(earInstance.moduleGrp+".rotateY", 110)
                cmds.setAttr(earInstance.radiusCtrl+".translateX", 0.5)
                earInstance.changeJointNumber(2)
                cmds.setAttr(earInstance.cvJointLoc+".translateZ", 0.25)
                cmds.setAttr(earInstance.cvEndJoint+".translateZ", 0.3)
                # parent ear guide to head guide:
                cmds.parent(earInstance.moduleGrp, headInstance.cvUpperHeadLoc, absolute=True)
                # setting X mirror:
                earInstance.changeMirror("X")
                cmds.setAttr(earInstance.moduleGrp+".flip", 1)
                cmds.setAttr(earInstance.moduleGrp+".deformedBy", 1)
                cmds.refresh()

                # working with Teeth system:
                dpUIinst.utils.setProgress(doingName+upperTeethName)
                # create FkLine module instance:
                upperTeethInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing upperTeeth base guide informations:
                upperTeethInstance.editUserName(upperTeethName)
                cmds.setAttr(upperTeethInstance.moduleGrp+".translateY", 20.3)
                cmds.setAttr(upperTeethInstance.moduleGrp+".translateZ", 2.2)
                cmds.setAttr(upperTeethInstance.radiusCtrl+".translateX", 0.5)
                cmds.setAttr(upperTeethInstance.cvEndJoint+".translateZ", 0.1)
                cmds.setAttr(upperTeethInstance.moduleGrp+".shapeSize", 0.5)
                cmds.setAttr(upperTeethInstance.moduleGrp+".deformedBy", 3)
                # parent upperTeeth guide to head guide:
                cmds.parent(upperTeethInstance.moduleGrp, headInstance.cvUpperJawLoc, absolute=True)
                # create FkLine module instance:
                upperTeethMiddleInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing upperTeethMiddle base guide informations:
                upperTeethMiddleInstance.editUserName(upperTeethMiddleName)
                cmds.setAttr(upperTeethMiddleInstance.moduleGrp+".translateY", 20.1)
                cmds.setAttr(upperTeethMiddleInstance.moduleGrp+".translateZ", 2.2)
                cmds.setAttr(upperTeethMiddleInstance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(upperTeethMiddleInstance.cvEndJoint+".translateZ", 0.1)
                cmds.setAttr(upperTeethMiddleInstance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(upperTeethMiddleInstance.moduleGrp+".deformedBy", 3)
                upperTeethMiddleInstance.displayAnnotation(0)
                # parent upperTeethMiddle guide to upperTeeth guide:
                cmds.parent(upperTeethMiddleInstance.moduleGrp, upperTeethInstance.cvJointLoc, absolute=True)
                # create FkLine module instance:
                upperTeethSideInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing upperTeethSide base guide informations:
                upperTeethSideInstance.editUserName(upperTeethSideName)
                cmds.setAttr(upperTeethSideInstance.moduleGrp+".translateX", 0.2)
                cmds.setAttr(upperTeethSideInstance.moduleGrp+".translateY", 20.1)
                cmds.setAttr(upperTeethSideInstance.moduleGrp+".translateZ", 2)
                cmds.setAttr(upperTeethSideInstance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(upperTeethSideInstance.cvEndJoint+".translateZ", 0.1)
                cmds.setAttr(upperTeethSideInstance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(upperTeethSideInstance.moduleGrp+".deformedBy", 3)
                upperTeethSideInstance.changeMirror("X")
                cmds.setAttr(upperTeethSideInstance.moduleGrp+".flip", 1)
                upperTeethSideInstance.displayAnnotation(0)
                # parent upperTeethSide guide to upperTeeth guide:
                cmds.parent(upperTeethSideInstance.moduleGrp, upperTeethInstance.cvJointLoc, absolute=True)
                # create FkLine module instance:
                lowerTeethInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing lowerTeeth base guide informations:
                lowerTeethInstance.editUserName(lowerTeethName)
                cmds.setAttr(lowerTeethInstance.moduleGrp+".translateY", 19.5)
                cmds.setAttr(lowerTeethInstance.moduleGrp+".translateZ", 2.2)
                cmds.setAttr(lowerTeethInstance.radiusCtrl+".translateX", 0.5)
                cmds.setAttr(lowerTeethInstance.cvEndJoint+".translateZ", 0.1)
                cmds.setAttr(lowerTeethInstance.moduleGrp+".shapeSize", 0.5)
                cmds.setAttr(lowerTeethInstance.moduleGrp+".deformedBy", 3)
                # parent lowerTeeth guide to head guide:
                cmds.parent(lowerTeethInstance.moduleGrp, headInstance.cvChinLoc, absolute=True)
                # create FkLine module instance:
                lowerTeethMiddleInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing lowerTeethMiddle base guide informations:
                lowerTeethMiddleInstance.editUserName(lowerTeethMiddleName)
                cmds.setAttr(lowerTeethMiddleInstance.moduleGrp+".translateY", 19.7)
                cmds.setAttr(lowerTeethMiddleInstance.moduleGrp+".translateZ", 2.2)
                cmds.setAttr(lowerTeethMiddleInstance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(lowerTeethMiddleInstance.cvEndJoint+".translateZ", 0.1)
                cmds.setAttr(lowerTeethMiddleInstance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(lowerTeethMiddleInstance.moduleGrp+".deformedBy", 3)
                lowerTeethMiddleInstance.displayAnnotation(0)
                # parent lowerTeeth guide to lowerTeeth guide:
                cmds.parent(lowerTeethMiddleInstance.moduleGrp, lowerTeethInstance.cvJointLoc, absolute=True)
                # create FkLine module instance:
                lowerTeethSideInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing lowerTeethSide base guide informations:
                lowerTeethSideInstance.editUserName(lowerTeethSideName)
                cmds.setAttr(lowerTeethSideInstance.moduleGrp+".translateX", 0.2)
                cmds.setAttr(lowerTeethSideInstance.moduleGrp+".translateY", 19.7)
                cmds.setAttr(lowerTeethSideInstance.moduleGrp+".translateZ", 2)
                cmds.setAttr(lowerTeethSideInstance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(lowerTeethSideInstance.cvEndJoint+".translateZ", 0.1)
                cmds.setAttr(lowerTeethSideInstance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(lowerTeethSideInstance.moduleGrp+".deformedBy", 3)
                lowerTeethSideInstance.changeMirror("X")
                cmds.setAttr(lowerTeethSideInstance.moduleGrp+".flip", 1)
                lowerTeethSideInstance.displayAnnotation(0)
                # parent lowerTeethSide guide to lowerTeeth guide:
                cmds.parent(lowerTeethSideInstance.moduleGrp, lowerTeethInstance.cvJointLoc, absolute=True)
                cmds.refresh()
                
                # working with Nose systems:
                dpUIinst.utils.setProgress(doingName+noseName)
                # create FkLine module instance:
                noseInstance = dpUIinst.initGuide('dpNose', guideDir)
                # editing upperTeeth base guide informations:
                noseInstance.editUserName(noseName)
                cmds.setAttr(noseInstance.moduleGrp+".translateY", 21.2)
                cmds.setAttr(noseInstance.moduleGrp+".translateZ", 2)
                cmds.setAttr(noseInstance.radiusCtrl+".translateX", 0.3)
                noseInstance.changeJointNumber(2)
                # parent nose guide to head guide:
                cmds.parent(noseInstance.moduleGrp, headInstance.cvUpperJawLoc, absolute=True)
                cmds.refresh()
                
                # working with Tongue system:
                dpUIinst.utils.setProgress(doingName+tongueName)
                # create FkLine module instance:
                tongueInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing tongue base guide informations:
                tongueInstance.editUserName(tongueName)
                cmds.setAttr(tongueInstance.moduleGrp+".translateY", 19.85)
                cmds.setAttr(tongueInstance.moduleGrp+".translateZ", 1.45)
                cmds.setAttr(tongueInstance.radiusCtrl+".translateX", 0.35)
                tongueInstance.changeJointNumber(2)
                cmds.setAttr(tongueInstance.moduleGrp+".nJoints", 2)
                cmds.setAttr(tongueInstance.cvJointLoc+".translateZ", 0.3)
                tongueInstance.changeJointNumber(3)
                cmds.setAttr(tongueInstance.moduleGrp+".nJoints", 3)
                cmds.setAttr(tongueInstance.cvJointLoc+".translateZ", 0.3)
                cmds.setAttr(tongueInstance.cvEndJoint+".translateZ", 0.2)
                cmds.setAttr(tongueInstance.moduleGrp+".shapeSize", 0.4)
                cmds.setAttr(tongueInstance.moduleGrp+".deformedBy", 3)
                # parent tongue guide to head guide:
                cmds.parent(tongueInstance.moduleGrp, headInstance.cvChinLoc, absolute=True)
                cmds.refresh()
                
                # working with Toes system:
                dpUIinst.utils.setProgress(doingName+toeName)
                # create toe1 module instance:
                toe1Instance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe1Instance.editUserName(toeName+"_1")
                # editing toe base guide informations:
                cmds.setAttr(toe1Instance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(toe1Instance.moduleGrp+".translateX", 1)
                cmds.setAttr(toe1Instance.moduleGrp+".translateY", 0.5)
                cmds.setAttr(toe1Instance.moduleGrp+".translateZ", 2.7)
                toe1Instance.changeJointNumber(2)
                cmds.setAttr(toe1Instance.cvJointLoc+".translateZ", 0.25)
                toe1Instance.changeJointNumber(3)
                cmds.setAttr(toe1Instance.cvJointLoc+".translateZ", 0.25)
                cmds.setAttr(toe1Instance.cvEndJoint+".translateZ", 0.2)
                cmds.setAttr(toe1Instance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(toe1Instance.moduleGrp+".flip", 1)
                toe1Instance.displayAnnotation(0)
                # parent toe1 guide to foot middle guide:
                cmds.parent(toe1Instance.moduleGrp, footInstance.cvRFFLoc, absolute=True)
                cmds.refresh()
                
                dpUIinst.utils.setProgress(doingName+toeName)
                # create toe2 module instance:
                toe2Instance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe2Instance.editUserName(toeName+"_2")
                # editing toe base guide informations:
                cmds.setAttr(toe2Instance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(toe2Instance.moduleGrp+".translateX", 1.35)
                cmds.setAttr(toe2Instance.moduleGrp+".translateY", 0.5)
                cmds.setAttr(toe2Instance.moduleGrp+".translateZ", 2.7)
                toe2Instance.changeJointNumber(2)
                cmds.setAttr(toe2Instance.cvJointLoc+".translateZ", 0.25)
                toe2Instance.changeJointNumber(3)
                cmds.setAttr(toe2Instance.cvJointLoc+".translateZ", 0.25)
                cmds.setAttr(toe2Instance.cvEndJoint+".translateZ", 0.2)
                cmds.setAttr(toe2Instance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(toe2Instance.moduleGrp+".flip", 1)
                toe2Instance.displayAnnotation(0)
                # parent toe2 guide to foot middle guide:
                cmds.parent(toe2Instance.moduleGrp, footInstance.cvRFFLoc, absolute=True)
                cmds.refresh()
                
                dpUIinst.utils.setProgress(doingName+toeName)
                # create toe3 module instance:
                toe3Instance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe3Instance.editUserName(toeName+"_3")
                # editing toe base guide informations:
                cmds.setAttr(toe3Instance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(toe3Instance.moduleGrp+".translateX", 1.65)
                cmds.setAttr(toe3Instance.moduleGrp+".translateY", 0.5)
                cmds.setAttr(toe3Instance.moduleGrp+".translateZ", 2.7)
                toe3Instance.changeJointNumber(2)
                cmds.setAttr(toe3Instance.cvJointLoc+".translateZ", 0.25)
                toe3Instance.changeJointNumber(3)
                cmds.setAttr(toe3Instance.cvJointLoc+".translateZ", 0.25)
                cmds.setAttr(toe3Instance.cvEndJoint+".translateZ", 0.2)
                cmds.setAttr(toe3Instance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(toe3Instance.moduleGrp+".flip", 1)
                toe3Instance.displayAnnotation(0)
                # parent toe3 guide to foot middle guide:
                cmds.parent(toe3Instance.moduleGrp, footInstance.cvRFFLoc, absolute=True)
                cmds.refresh()

                dpUIinst.utils.setProgress(doingName+toeName)
                # create toe4 module instance:
                toe4Instance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe4Instance.editUserName(toeName+"_4")
                # editing toe base guide informations:
                cmds.setAttr(toe4Instance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(toe4Instance.moduleGrp+".translateX", 1.95)
                cmds.setAttr(toe4Instance.moduleGrp+".translateY", 0.5)
                cmds.setAttr(toe4Instance.moduleGrp+".translateZ", 2.7)
                toe4Instance.changeJointNumber(2)
                cmds.setAttr(toe4Instance.cvJointLoc+".translateZ", 0.25)
                toe4Instance.changeJointNumber(3)
                cmds.setAttr(toe4Instance.cvJointLoc+".translateZ", 0.25)
                cmds.setAttr(toe4Instance.cvEndJoint+".translateZ", 0.2)
                cmds.setAttr(toe4Instance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(toe4Instance.moduleGrp+".flip", 1)
                toe4Instance.displayAnnotation(0)
                # parent toe4 guide to foot middle guide:
                cmds.parent(toe4Instance.moduleGrp, footInstance.cvRFFLoc, absolute=True)
                cmds.refresh()
                
                dpUIinst.utils.setProgress(doingName+toeName)
                # create toe5 module instance:
                toe5Instance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe5Instance.editUserName(toeName+"_5")
                # editing toe base guide informations:
                cmds.setAttr(toe5Instance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(toe5Instance.moduleGrp+".translateX", 2.25)
                cmds.setAttr(toe5Instance.moduleGrp+".translateY", 0.5)
                cmds.setAttr(toe5Instance.moduleGrp+".translateZ", 2.7)
                toe5Instance.changeJointNumber(2)
                cmds.setAttr(toe5Instance.cvJointLoc+".translateZ", 0.25)
                toe5Instance.changeJointNumber(3)
                cmds.setAttr(toe5Instance.cvJointLoc+".translateZ", 0.25)
                cmds.setAttr(toe5Instance.cvEndJoint+".translateZ", 0.2)
                cmds.setAttr(toe5Instance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(toe5Instance.moduleGrp+".flip", 1)
                toe5Instance.displayAnnotation(0)
                # parent toe5 guide to foot middle guide:
                cmds.parent(toe5Instance.moduleGrp, footInstance.cvRFFLoc, absolute=True)
                cmds.refresh()
                
                # working with Breath system:
                dpUIinst.utils.setProgress(doingName+breathName)
                # create FkLine module instance:
                breathInstance = dpUIinst.initGuide('dpSingle', guideDir)
                # editing breath base guide informations:
                breathInstance.editUserName(breathName)
                cmds.setAttr(breathInstance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(breathInstance.moduleGrp+".translateY", 14.5)
                cmds.setAttr(breathInstance.moduleGrp+".translateZ", 0.3)
                cmds.setAttr(breathInstance.radiusCtrl+".translateX", 0.35)
                cmds.setAttr(breathInstance.cvEndJoint+".translateZ", 0.2)
                cmds.setAttr(breathInstance.moduleGrp+".indirectSkin", 1)
                breathInstance.displayAnnotation(0)
                # parent breath guide to chest guide:
                cmds.parent(breathInstance.moduleGrp, spineInstance.cvLocator, absolute=True)
                cmds.refresh()

                # working with Belly system:
                dpUIinst.utils.setProgress(doingName+bellyName)
                # create FkLine module instance:
                bellyInstance = dpUIinst.initGuide('dpSingle', guideDir)
                # editing belly base guide informations:
                bellyInstance.editUserName(bellyName)
                cmds.setAttr(bellyInstance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(bellyInstance.moduleGrp+".translateY", 11.75)
                cmds.setAttr(bellyInstance.moduleGrp+".translateZ", 0.75)
                cmds.setAttr(bellyInstance.radiusCtrl+".translateX", 0.35)
                cmds.setAttr(bellyInstance.cvEndJoint+".translateZ", 0.2)
                cmds.setAttr(bellyInstance.moduleGrp+".indirectSkin", 1)
                bellyInstance.displayAnnotation(0)
                # parent belly guide to chest guide:
                cmds.parent(bellyInstance.moduleGrp, spineInstance.moduleGrp, absolute=True)
            
            # Close progress window
            dpUIinst.utils.setProgress(endIt=True)
            
            # select spineGuide_Base:
            cmds.select(spineInstance.moduleGrp)
            print(dpUIinst.lang['m089_createdBiped'])
    else:
        # error checking modules in the folder:
        mel.eval('error \"'+ dpUIinst.lang['e001_guideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
