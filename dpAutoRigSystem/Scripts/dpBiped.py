# importing libraries:
import maya.cmds as cmds
import maya.mel as mel

# global variables to this module:    
CLASS_NAME = "Biped"
TITLE = "m026_biped"
DESCRIPTION = "m027_bipedDesc"
ICON = "/Icons/dp_biped.png"



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
    checkModuleList = ['dpLimb', 'dpFoot', 'dpFinger', 'dpSpine', 'dpHead', 'dpFkLine', 'dpEye']
    checkResultList = dpUIinst.startGuideModules(guideDir, "check", None, checkModuleList=checkModuleList)
    
    if len(checkResultList) == 0:
        # defining naming:
        doingName = dpUIinst.langDic[dpUIinst.langName]['m094_doing']
        bipedStyleName = dpUIinst.langDic[dpUIinst.langName]['m026_biped']
        # part names:
        spineName = dpUIinst.langDic[dpUIinst.langName]['m011_spine']
        headName = dpUIinst.langDic[dpUIinst.langName]['c024_head']
        eyeName = dpUIinst.langDic[dpUIinst.langName]['c036_eye']
        legName = dpUIinst.langDic[dpUIinst.langName]['m030_leg'].capitalize()
        footName = dpUIinst.langDic[dpUIinst.langName]['c038_foot']
        armName = dpUIinst.langDic[dpUIinst.langName]['c037_arm'].capitalize()
        fingerIndexName = dpUIinst.langDic[dpUIinst.langName]['m007_finger']+"_"+dpUIinst.langDic[dpUIinst.langName]['m032_index']
        fingerMiddleName = dpUIinst.langDic[dpUIinst.langName]['m007_finger']+"_"+dpUIinst.langDic[dpUIinst.langName]['m033_middle']
        fingerRingName = dpUIinst.langDic[dpUIinst.langName]['m007_finger']+"_"+dpUIinst.langDic[dpUIinst.langName]['m034_ring']
        fingerPinkyName = dpUIinst.langDic[dpUIinst.langName]['m007_finger']+"_"+dpUIinst.langDic[dpUIinst.langName]['m035_pinky']
        fingerThumbName = dpUIinst.langDic[dpUIinst.langName]['m007_finger']+"_"+dpUIinst.langDic[dpUIinst.langName]['m036_thumb']
        earName = dpUIinst.langDic[dpUIinst.langName]['m040_ear']
        upperTeethName = dpUIinst.langDic[dpUIinst.langName]['m075_upperTeeth']
        upperTeethMiddleName = dpUIinst.langDic[dpUIinst.langName]['m075_upperTeeth']+dpUIinst.langDic[dpUIinst.langName]['c029_middle'].capitalize()
        upperTeethSideName = dpUIinst.langDic[dpUIinst.langName]['m075_upperTeeth']+dpUIinst.langDic[dpUIinst.langName]['c016_RevFoot_G'].capitalize()
        lowerTeethName = dpUIinst.langDic[dpUIinst.langName]['m076_lowerTeeth']
        lowerTeethMiddleName = dpUIinst.langDic[dpUIinst.langName]['m076_lowerTeeth']+dpUIinst.langDic[dpUIinst.langName]['c029_middle'].capitalize()
        lowerTeethSideName = dpUIinst.langDic[dpUIinst.langName]['m076_lowerTeeth']+dpUIinst.langDic[dpUIinst.langName]['c016_RevFoot_G'].capitalize()
        noseName = dpUIinst.langDic[dpUIinst.langName]['m078_nose']
        nostrilName = dpUIinst.langDic[dpUIinst.langName]['m079_nostril']
        tongueName = dpUIinst.langDic[dpUIinst.langName]['m077_tongue']
        toeName = dpUIinst.langDic[dpUIinst.langName]['c013_RevFoot_D'].capitalize()
        breathName = dpUIinst.langDic[dpUIinst.langName]['c095_breath']
        bellyName = dpUIinst.langDic[dpUIinst.langName]['c096_belly']
        simple   = dpUIinst.langDic[dpUIinst.langName]['i175_simple']
        complete = dpUIinst.langDic[dpUIinst.langName]['i176_complete']
        cancel   = dpUIinst.langDic[dpUIinst.langName]['i132_cancel']
        userMessage = dpUIinst.langDic[dpUIinst.langName]['i177_chooseMessage']
        
        
        # getting Simple or Complete module guides to create:
        userDetail = getUserDetail(simple, complete, cancel, userMessage)
        if not userDetail == cancel:
            # number of modules to create:
            if userDetail == simple:
                maxProcess = 7
            else:
                maxProcess = 18
        
            # Starting progress window
            progressAmount = 0
            cmds.progressWindow(title='Biped Guides', progress=progressAmount, status=doingName+': 0%', isInterruptable=False)

            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+spineName))
            
            
            # woking with SPINE system:
            # create spine module instance:
            spineInstance = dpUIinst.initGuide('dpSpine', guideDir)
            # editing spine base guide informations:
            spineInstance.editUserName(spineName)
            spineInstance.changeStyle(bipedStyleName)
            cmds.setAttr(spineInstance.moduleGrp+".translateY", 11)
            cmds.setAttr(spineInstance.annotation+".translateY", -6)
            cmds.setAttr(spineInstance.radiusCtrl+".translateX", 2.5)
            
            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+headName))
            
            # woking with HEAD system:
            # create head module instance:
            headInstance = dpUIinst.initGuide('dpHead', guideDir)
            # editing head base guide informations:
            headInstance.editUserName(headName)
            cmds.setAttr(headInstance.moduleGrp+".translateY", 17)
            cmds.setAttr(headInstance.annotation+".translateY", 3.5)
            
            # parent head guide to spine guide:
            cmds.parent(headInstance.moduleGrp, spineInstance.cvLocator, absolute=True)
            
            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+eyeName))
            
            # woking with Eye system:
            # create eye module instance:
            eyeInstance = dpUIinst.initGuide('dpEye', guideDir)
            # setting X mirror:
            eyeInstance.changeMirror("X")
            # editing eyeLookAt base guide informations:
            eyeInstance.editUserName(eyeName)
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
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+legName))
            
            # working with LEG system:
            # create leg module instance:
            legLimbInstance = dpUIinst.initGuide('dpLimb', guideDir)
            # setting X mirror:
            legLimbInstance.changeMirror("X")
            # change limb guide to leg type:
            legLimbInstance.changeType(legName)
            # change limb style to biped:
            legLimbInstance.changeStyle(bipedStyleName)
            # change name to leg:
            legLimbInstance.editUserName(legName)
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
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+footName))
            
            # create foot module instance:
            footInstance = dpUIinst.initGuide('dpFoot', guideDir)
            footInstance.editUserName(footName)
            cmds.setAttr(footInstance.annotation+".translateY", -3)
            cmds.setAttr(footInstance.moduleGrp+".translateX", 1.5)
            cmds.setAttr(footInstance.cvFootLoc+".translateZ", 1.5)
            
            # parent foot guide to leg ankle guide:
            cmds.parent(footInstance.moduleGrp, legLimbInstance.cvExtremLoc, absolute=True)
            
            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+armName))
            
            # working with ARM system:
            # creating module instances:
            armLimbInstance = dpUIinst.initGuide('dpLimb', guideDir)
            # setting X mirror:
            armLimbInstance.changeMirror("X")
            # change limb style to biped:
            armLimbInstance.changeStyle(bipedStyleName)
            # change name to arm:
            armLimbInstance.editUserName(armName)
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
            
            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+fingerIndexName))
            
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
            
            
            # complete part:
            if userDetail == complete:
            
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+earName))
                
                # woking with EAR system:
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
                cmds.parent(earInstance.moduleGrp, headInstance.cvHeadLoc, absolute=True)
                # setting X mirror:
                earInstance.changeMirror("X")
                cmds.setAttr(earInstance.moduleGrp+".flip", 1)

                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+upperTeethName))
                
                # woking with Teeth system:
                # create FkLine module instance:
                upperTeethInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing upperTeeth base guide informations:
                upperTeethInstance.editUserName(upperTeethName)
                cmds.setAttr(upperTeethInstance.moduleGrp+".translateY", 20.3)
                cmds.setAttr(upperTeethInstance.moduleGrp+".translateZ", 2.2)
                cmds.setAttr(upperTeethInstance.radiusCtrl+".translateX", 0.5)
                cmds.setAttr(upperTeethInstance.cvEndJoint+".translateZ", 0.1)
                cmds.setAttr(upperTeethInstance.moduleGrp+".shapeSize", 0.5)
                # parent upperTeeth guide to head guide:
                cmds.parent(upperTeethInstance.moduleGrp, headInstance.cvHeadLoc, absolute=True)
                # create FkLine module instance:
                upperTeethMiddleInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing upperTeethMiddle base guide informations:
                upperTeethMiddleInstance.editUserName(upperTeethMiddleName)
                cmds.setAttr(upperTeethMiddleInstance.moduleGrp+".translateY", 20.1)
                cmds.setAttr(upperTeethMiddleInstance.moduleGrp+".translateZ", 2.2)
                cmds.setAttr(upperTeethMiddleInstance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(upperTeethMiddleInstance.cvEndJoint+".translateZ", 0.1)
                cmds.setAttr(upperTeethMiddleInstance.moduleGrp+".shapeSize", 0.3)
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
                lowerTeethSideInstance.changeMirror("X")
                cmds.setAttr(lowerTeethSideInstance.moduleGrp+".flip", 1)
                lowerTeethSideInstance.displayAnnotation(0)
                # parent lowerTeethSide guide to lowerTeeth guide:
                cmds.parent(lowerTeethSideInstance.moduleGrp, lowerTeethInstance.cvJointLoc, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+noseName))
                
                # woking with Nose and Nostril systems:
                # create FkLine module instance:
                noseInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing upperTeeth base guide informations:
                noseInstance.editUserName(noseName)
                cmds.setAttr(noseInstance.moduleGrp+".translateY", 20.9)
                cmds.setAttr(noseInstance.moduleGrp+".translateZ", 2)
                cmds.setAttr(noseInstance.radiusCtrl+".translateX", 0.3)
                noseInstance.changeJointNumber(2)
                cmds.setAttr(noseInstance.moduleGrp+".nJoints", 2)
                cmds.setAttr(noseInstance.cvJointLoc+".translateY", -0.15)
                cmds.setAttr(noseInstance.cvJointLoc+".translateZ", 0.3)
                cmds.setAttr(noseInstance.cvEndJoint+".translateZ", 0.1)
                cmds.setAttr(noseInstance.moduleGrp+".shapeSize", 0.5)
                # parent nose guide to head guide:
                cmds.parent(noseInstance.moduleGrp, headInstance.cvHeadLoc, absolute=True)
                # create FkLine module instance:
                nostrilInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing nostril base guide informations:
                nostrilInstance.editUserName(nostrilName)
                cmds.setAttr(nostrilInstance.moduleGrp+".translateX", 0.33)
                cmds.setAttr(nostrilInstance.moduleGrp+".translateY", 20.65)
                cmds.setAttr(nostrilInstance.moduleGrp+".translateZ", 2.15)
                cmds.setAttr(nostrilInstance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(nostrilInstance.cvEndJoint+".translateZ", 0.1)
                cmds.setAttr(nostrilInstance.moduleGrp+".shapeSize", 0.3)
                # setting X mirror:
                nostrilInstance.changeMirror("X")
                cmds.setAttr(nostrilInstance.moduleGrp+".flip", 1)
                # parent nostril guide to nose guide:
                cmds.parent(nostrilInstance.moduleGrp, noseInstance.moduleGrp, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+tongueName))
                
                # woking with Tongue system:
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
                # parent tongue guide to head guide:
                cmds.parent(tongueInstance.moduleGrp, headInstance.cvChinLoc, absolute=True)
            
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+toeName+'_1'))
                
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
                cmds.parent(toe1Instance.moduleGrp, footInstance.cvRFELoc, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+toeName+'_2'))
                
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
                cmds.parent(toe2Instance.moduleGrp, footInstance.cvRFELoc, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+toeName+'_3'))
                
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
                cmds.parent(toe3Instance.moduleGrp, footInstance.cvRFELoc, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+toeName+'_4'))
                
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
                cmds.parent(toe4Instance.moduleGrp, footInstance.cvRFELoc, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+toeName+'_5'))
                
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
                cmds.parent(toe5Instance.moduleGrp, footInstance.cvRFELoc, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+breathName))
                
                # woking with Breath system:
                # create FkLine module instance:
                breathInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing breath base guide informations:
                breathInstance.editUserName(breathName)
                cmds.setAttr(breathInstance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(breathInstance.moduleGrp+".translateY", 14.5)
                cmds.setAttr(breathInstance.moduleGrp+".translateZ", 0.3)
                cmds.setAttr(breathInstance.radiusCtrl+".translateX", 0.35)
                cmds.setAttr(breathInstance.cvEndJoint+".translateZ", 0.2)
                breathInstance.displayAnnotation(0)
                # parent breath guide to chest guide:
                cmds.parent(breathInstance.moduleGrp, spineInstance.cvLocator, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+bellyName))
                
                # woking with Belly system:
                # create FkLine module instance:
                bellyInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing belly base guide informations:
                bellyInstance.editUserName(bellyName)
                cmds.setAttr(bellyInstance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(bellyInstance.moduleGrp+".translateY", 11.75)
                cmds.setAttr(bellyInstance.moduleGrp+".translateZ", 0.75)
                cmds.setAttr(bellyInstance.radiusCtrl+".translateX", 0.35)
                cmds.setAttr(bellyInstance.cvEndJoint+".translateZ", 0.2)
                bellyInstance.displayAnnotation(0)
                # parent belly guide to chest guide:
                cmds.parent(bellyInstance.moduleGrp, spineInstance.moduleGrp, absolute=True)
            
            # Close progress window
            cmds.progressWindow(endProgress=True)
            
            # select spineGuide_Base:
            cmds.select(spineInstance.moduleGrp)
            print dpUIinst.langDic[dpUIinst.langName]['m089_createdBiped']+"\n",
    else:
        # error checking modules in the folder:
        mel.eval('error \"'+ dpUIinst.langDic[dpUIinst.langName]['e001_GuideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
