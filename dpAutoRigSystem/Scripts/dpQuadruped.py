# importing libraries:
import maya.cmds as cmds
import maya.mel as mel
from ..Modules.dpBaseClass import RigType

# global variables to this module:    
CLASS_NAME = "Quadruped"
TITLE = "m037_quadruped"
DESCRIPTION = "m038_quadrupedDesc"
ICON = "/Icons/dp_quadruped.png"



def getUserDetail(opt1, opt2, cancel, userMessage):
    """ Ask user the detail level we'll create the guides by a confirm dialog box window.
        Options:
            Simple
            Complete
        Returns the user choose option or None if canceled.
    """
    result = cmds.confirmDialog(title=CLASS_NAME, message=userMessage, button=[opt1, opt2, cancel], defaultButton=opt2, cancelButton=cancel, dismissString=cancel)
    return result


def Quadruped(dpUIinst):
    """ This function will create all guides needed to compose a quadruped.
    """
    # check modules integrity:
    guideDir = 'Modules'
    checkModuleList = ['dpLimb', 'dpFoot', 'dpSpine', 'dpHead', 'dpFkLine', 'dpEye']
    checkResultList = dpUIinst.startGuideModules(guideDir, "check", None, checkModuleList=checkModuleList)
    
    if len(checkResultList) == 0:
        # defining naming:
        doingName = dpUIinst.langDic[dpUIinst.langName]['m094_doing']
        bipedStyleName = dpUIinst.langDic[dpUIinst.langName]['m026_biped']
        quadrupedStyleName = dpUIinst.langDic[dpUIinst.langName]['m155_quadrupedExtra']
        # part names:
        spineName = dpUIinst.langDic[dpUIinst.langName]['m011_spine']
        neckName = dpUIinst.langDic[dpUIinst.langName]['c023_neck']
        headName = dpUIinst.langDic[dpUIinst.langName]['c024_head']
        eyeName = dpUIinst.langDic[dpUIinst.langName]['c036_eye']
        legName = dpUIinst.langDic[dpUIinst.langName]['m030_leg'].capitalize()
        footName = dpUIinst.langDic[dpUIinst.langName]['c038_foot']
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
        tailName = dpUIinst.langDic[dpUIinst.langName]['m039_tail']
        toeName = dpUIinst.langDic[dpUIinst.langName]['c013_RevFoot_D'].capitalize()
        frontName = dpUIinst.langDic[dpUIinst.langName]['c056_front']
        backName = dpUIinst.langDic[dpUIinst.langName]['c057_back']
        simple   = dpUIinst.langDic[dpUIinst.langName]['i175_simple']
        complete = dpUIinst.langDic[dpUIinst.langName]['i176_complete']
        cancel   = dpUIinst.langDic[dpUIinst.langName]['i132_cancel']
        userMessage = dpUIinst.langDic[dpUIinst.langName]['i177_chooseMessage']
        
        # getting Simple or Complete module guides to create:
        userDetail = getUserDetail(simple, complete, cancel, userMessage)
        if not userDetail == cancel:
            # number of modules to create:
            if userDetail == simple:
                maxProcess = 8
            else:
                maxProcess = 21
                
            # Starting progress window
            progressAmount = 0
            cmds.progressWindow(title='Quadruped Guides', progress=progressAmount, status=doingName+': 0%', isInterruptable=False)

            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+spineName))
            
            # woking with SPINE system:
            # create spine module instance:
            spineInstance = dpUIinst.initGuide('dpSpine', guideDir, RigType.quadruped)
            # editing spine base guide informations:
            spineInstance.editUserName(spineName)
            cmds.setAttr(spineInstance.moduleGrp+".translateY", 10)
            cmds.setAttr(spineInstance.moduleGrp+".translateZ", -5)
            cmds.setAttr(spineInstance.moduleGrp+".rotateX", 0)
            cmds.setAttr(spineInstance.moduleGrp+".rotateY", 0)
            cmds.setAttr(spineInstance.moduleGrp+".rotateZ", 90)
            cmds.setAttr(spineInstance.cvLocator+".translateZ", 6)
            cmds.setAttr(spineInstance.annotation+".translateX", 6)
            cmds.setAttr(spineInstance.annotation+".translateY", 0)
            spineInstance.changeStyle(bipedStyleName)
            
            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+headName))
            
            # woking with HEAD system:
            # create head module instance:
            headInstance = dpUIinst.initGuide('dpHead', guideDir, RigType.quadruped)
            # editing head base guide informations:
            headInstance.editUserName(headName)
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
            
            # parent head guide to chest guide:
            cmds.parent(headInstance.moduleGrp, spineInstance.cvLocator, absolute=True)
            
            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+eyeName))
            
            # woking with Eye system:
            # create eyeLookAt module instance:
            eyeInstance = dpUIinst.initGuide('dpEye', guideDir, RigType.quadruped)
            # setting X mirror:
            eyeInstance.changeMirror("X")
            # editing eyeLookAt base guide informations:
            eyeInstance.editUserName(eyeName)
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
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+legName))
            
            # working with BACK LEG (B) system:
            # create back leg module instance:
            backLegLimbInstance = dpUIinst.initGuide('dpLimb', guideDir, RigType.quadruped)
            # change limb guide to back leg type:
            backLegLimbInstance.changeType(legName)
            # change limb guide to back leg style (quadruped):
            backLegLimbInstance.changeStyle(quadrupedStyleName)
            # set for not use bend ribbons as default:
            backLegLimbInstance.setBendFalse(backLegLimbInstance)
            # change name to back leg:
            backLegLimbInstance.editUserName(legName+backName)
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
            backLegLimbInstance.changeMirror("X")
            
            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+footName))
            
            # create BACK FOOT (B) module instance:
            backFootInstance = dpUIinst.initGuide('dpFoot', guideDir, RigType.quadruped)
            backFootInstance.editUserName(footName+backName)
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
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+legName))
            
            # working with FRONT LEG (A) system:
            # create front leg module instance:
            frontLegLimbInstance = dpUIinst.initGuide('dpLimb', guideDir, RigType.quadruped)
            # change limb guide to front leg type:
            frontLegLimbInstance.changeType(legName)
            # change limb guide to front leg style (biped):
            frontLegLimbInstance.changeStyle(quadrupedStyleName)
            # set for not use bend ribbons as default:
            frontLegLimbInstance.setBendFalse(frontLegLimbInstance)
            # change name to front leg:
            frontLegLimbInstance.editUserName(legName+frontName)
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
            cmds.setAttr(frontLegLimbInstance.cvCornerBLoc+".translateX", 1.75)
            cmds.setAttr(frontLegLimbInstance.cvCornerBLoc+".translateZ", 2.75)
            cmds.setAttr(frontLegLimbInstance.cvCornerBLoc+".rotateY", 10)

            # parent front leg guide to spine chest guide:
            cmds.parent(frontLegBaseGuide, spineInstance.cvLocator, absolute=True)
            # setting X mirror:
            frontLegLimbInstance.changeMirror("X")
            
            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+footName))
            
            # create FRONT FOOT (A) module instance:
            frontFootInstance = dpUIinst.initGuide('dpFoot', guideDir, RigType.quadruped)
            frontFootInstance.editUserName(footName+frontName)
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
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+tailName))
            
            # woking with TAIL system:
            # create FkLine module instance:
            tailInstance = dpUIinst.initGuide('dpFkLine', guideDir, RigType.quadruped)
            # editing tail base guide informations:
            tailInstance.editUserName(tailName)
            cmds.setAttr(tailInstance.moduleGrp+".translateY", 9.8)
            cmds.setAttr(tailInstance.moduleGrp+".translateZ", -7.6)
            cmds.setAttr(tailInstance.moduleGrp+".rotateX", 180)
            cmds.setAttr(tailInstance.moduleGrp+".rotateY", 20)
            cmds.setAttr(tailInstance.moduleGrp+".rotateZ", 90)
            cmds.setAttr(tailInstance.annotation+".translateX", 4)
            cmds.setAttr(tailInstance.annotation+".translateY", 0)
            cmds.setAttr(tailInstance.radiusCtrl+".translateX", 1)
            # change the number of joints to the tail module:
            tailInstance.changeJointNumber(3)
            
            # parent tail guide to spine guide:
            cmds.parent(tailInstance.moduleGrp, spineInstance.moduleGrp, absolute=True)
            
            
            # complete part:
            if userDetail == complete:
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+earName))
                
                # woking with EAR system:
                # create FkLine module instance:
                earInstance = dpUIinst.initGuide('dpFkLine', guideDir, RigType.quadruped)
                # editing ear base guide informations:
                earInstance.editUserName(earName)
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
                earInstance.changeJointNumber(2)
                
                # parent ear guide to spine guide:
                cmds.parent(earInstance.moduleGrp, headInstance.cvHeadLoc, absolute=True)
                cmds.setAttr(earInstance.moduleGrp+".scaleX", 0.5)
                cmds.setAttr(earInstance.moduleGrp+".scaleY", 0.5)
                cmds.setAttr(earInstance.moduleGrp+".scaleZ", 0.5)
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
                cmds.setAttr(upperTeethInstance.moduleGrp+".translateY", 12.5)
                cmds.setAttr(upperTeethInstance.moduleGrp+".translateZ", 12.7)
                cmds.setAttr(upperTeethInstance.radiusCtrl+".translateX", 0.5)
                cmds.setAttr(upperTeethInstance.cvEndJoint+".translateZ", 0.1)
                cmds.setAttr(upperTeethInstance.moduleGrp+".shapeSize", 0.5)
                # create FkLine module instance:
                upperTeethMiddleInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing upperTeethMiddle base guide informations:
                upperTeethMiddleInstance.editUserName(upperTeethMiddleName)
                cmds.setAttr(upperTeethMiddleInstance.moduleGrp+".translateY", 12.3)
                cmds.setAttr(upperTeethMiddleInstance.moduleGrp+".translateZ", 12.7)
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
                cmds.setAttr(upperTeethSideInstance.moduleGrp+".translateY", 12.3)
                cmds.setAttr(upperTeethSideInstance.moduleGrp+".translateZ", 12.3)
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
                cmds.setAttr(lowerTeethInstance.moduleGrp+".translateY", 11.7)
                cmds.setAttr(lowerTeethInstance.moduleGrp+".translateZ", 12.7)
                cmds.setAttr(lowerTeethInstance.radiusCtrl+".translateX", 0.5)
                cmds.setAttr(lowerTeethInstance.cvEndJoint+".translateZ", 0.1)
                cmds.setAttr(lowerTeethInstance.moduleGrp+".shapeSize", 0.5)
                # parent lowerTeeth guide to head guide:
                cmds.parent(lowerTeethInstance.moduleGrp, headInstance.cvChinLoc, absolute=True)
                # create FkLine module instance:
                lowerTeethMiddleInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing lowerTeethMiddle base guide informations:
                lowerTeethMiddleInstance.editUserName(lowerTeethMiddleName)
                cmds.setAttr(lowerTeethMiddleInstance.moduleGrp+".translateY", 11.9)
                cmds.setAttr(lowerTeethMiddleInstance.moduleGrp+".translateZ", 12.7)
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
                cmds.setAttr(lowerTeethSideInstance.moduleGrp+".translateY", 11.9)
                cmds.setAttr(lowerTeethSideInstance.moduleGrp+".translateZ", 12.3)
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
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+tongueName))
                
                # woking with Tongue system:
                # create FkLine module instance:
                tongueInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing tongue base guide informations:
                tongueInstance.editUserName(tongueName)
                cmds.setAttr(tongueInstance.moduleGrp+".translateY", 12)
                cmds.setAttr(tongueInstance.moduleGrp+".translateZ", 12)
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
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+noseName))
                
                # woking with Nose and Nostril systems:
                # create FkLine module instance:
                noseInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing upperTeeth base guide informations:
                noseInstance.editUserName(noseName)
                cmds.setAttr(noseInstance.moduleGrp+".translateY", 13)
                cmds.setAttr(noseInstance.moduleGrp+".translateZ", 11.5)
                cmds.setAttr(noseInstance.radiusCtrl+".translateX", 0.3)
                noseInstance.changeJointNumber(2)
                cmds.setAttr(noseInstance.moduleGrp+".nJoints", 2)
                cmds.setAttr(noseInstance.cvJointLoc+".translateY", -0.2)
                cmds.setAttr(noseInstance.cvJointLoc+".translateZ", 0.7)
                cmds.setAttr(noseInstance.cvEndJoint+".translateZ", 0.1)
                cmds.setAttr(noseInstance.moduleGrp+".shapeSize", 0.5)
                storedNose2Guide = noseInstance.cvJointLoc
                # adding a new nose point segment to quadrupeds:
                noseInstance.changeJointNumber(3)
                cmds.setAttr(noseInstance.moduleGrp+".nJoints", 3)
                cmds.setAttr(noseInstance.cvJointLoc+".translateZ", 0.7)
                cmds.setAttr(noseInstance.cvEndJoint+".translateZ", 0.1)
                # parent nose guide to head guide:
                cmds.parent(noseInstance.moduleGrp, headInstance.cvHeadLoc, absolute=True)
                # parent upperTeeth guide to Nose1 guide:
                cmds.parent(upperTeethInstance.moduleGrp, noseInstance.moduleGrp, absolute=True)
                # create FkLine module instance:
                nostrilInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing nostril base guide informations:
                nostrilInstance.editUserName(nostrilName)
                cmds.setAttr(nostrilInstance.moduleGrp+".translateX", 0.33)
                cmds.setAttr(nostrilInstance.moduleGrp+".translateY", 12.7)
                cmds.setAttr(nostrilInstance.moduleGrp+".translateZ", 12.8)
                cmds.setAttr(nostrilInstance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(nostrilInstance.cvEndJoint+".translateZ", 0.1)
                cmds.setAttr(nostrilInstance.moduleGrp+".shapeSize", 0.3)
                # setting X mirror:
                nostrilInstance.changeMirror("X")
                cmds.setAttr(nostrilInstance.moduleGrp+".flip", 1)
                # parent nostril guide to nose guide:
                cmds.parent(nostrilInstance.moduleGrp, storedNose2Guide, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+toeName+frontName+'_1'))
                
                # create toe1 module instance:
                toe1FrontInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe1FrontInstance.editUserName(toeName+frontName+"_1")
                # editing toe base guide informations:
                cmds.setAttr(toe1FrontInstance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(toe1FrontInstance.moduleGrp+".translateX", 2)
                cmds.setAttr(toe1FrontInstance.moduleGrp+".translateY", 0.5)
                cmds.setAttr(toe1FrontInstance.moduleGrp+".translateZ", 6.7)
                toe1FrontInstance.changeJointNumber(2)
                cmds.setAttr(toe1FrontInstance.cvJointLoc+".translateZ", 0.25)
                toe1FrontInstance.changeJointNumber(3)
                cmds.setAttr(toe1FrontInstance.cvJointLoc+".translateZ", 0.25)
                cmds.setAttr(toe1FrontInstance.cvEndJoint+".translateZ", 0.2)
                cmds.setAttr(toe1FrontInstance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(toe1FrontInstance.moduleGrp+".flip", 1)
                toe1FrontInstance.displayAnnotation(0)
                
                # parent toe1 guide to foot middle guide:
                cmds.parent(toe1FrontInstance.moduleGrp, frontFootInstance.cvRFELoc, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+toeName+frontName+'_2'))
                
                # create toe2 module instance:
                toe2FrontInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe2FrontInstance.editUserName(toeName+frontName+"_2")
                # editing toe base guide informations:
                cmds.setAttr(toe2FrontInstance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(toe2FrontInstance.moduleGrp+".translateX", 2.35)
                cmds.setAttr(toe2FrontInstance.moduleGrp+".translateY", 0.5)
                cmds.setAttr(toe2FrontInstance.moduleGrp+".translateZ", 6.7)
                toe2FrontInstance.changeJointNumber(2)
                cmds.setAttr(toe2FrontInstance.cvJointLoc+".translateZ", 0.25)
                toe2FrontInstance.changeJointNumber(3)
                cmds.setAttr(toe2FrontInstance.cvJointLoc+".translateZ", 0.25)
                cmds.setAttr(toe2FrontInstance.cvEndJoint+".translateZ", 0.2)
                cmds.setAttr(toe2FrontInstance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(toe2FrontInstance.moduleGrp+".flip", 1)
                toe2FrontInstance.displayAnnotation(0)
                
                # parent toe1 guide to foot middle guide:
                cmds.parent(toe2FrontInstance.moduleGrp, frontFootInstance.cvRFELoc, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+toeName+frontName+'_3'))
                
                # create toe3 module instance:
                toe3FrontInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe3FrontInstance.editUserName(toeName+frontName+"_3")
                # editing toe base guide informations:
                cmds.setAttr(toe3FrontInstance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(toe3FrontInstance.moduleGrp+".translateX", 2.65)
                cmds.setAttr(toe3FrontInstance.moduleGrp+".translateY", 0.5)
                cmds.setAttr(toe3FrontInstance.moduleGrp+".translateZ", 6.7)
                toe3FrontInstance.changeJointNumber(2)
                cmds.setAttr(toe3FrontInstance.cvJointLoc+".translateZ", 0.25)
                toe3FrontInstance.changeJointNumber(3)
                cmds.setAttr(toe3FrontInstance.cvJointLoc+".translateZ", 0.25)
                cmds.setAttr(toe3FrontInstance.cvEndJoint+".translateZ", 0.2)
                cmds.setAttr(toe3FrontInstance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(toe3FrontInstance.moduleGrp+".flip", 1)
                toe3FrontInstance.displayAnnotation(0)
                
                # parent toe1 guide to foot middle guide:
                cmds.parent(toe3FrontInstance.moduleGrp, frontFootInstance.cvRFELoc, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+toeName+frontName+'_4'))
                
                # create toe4 module instance:
                toe4FrontInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe4FrontInstance.editUserName(toeName+frontName+"_4")
                # editing toe base guide informations:
                cmds.setAttr(toe4FrontInstance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(toe4FrontInstance.moduleGrp+".translateX", 2.95)
                cmds.setAttr(toe4FrontInstance.moduleGrp+".translateY", 0.5)
                cmds.setAttr(toe4FrontInstance.moduleGrp+".translateZ", 6.7)
                toe4FrontInstance.changeJointNumber(2)
                cmds.setAttr(toe4FrontInstance.cvJointLoc+".translateZ", 0.25)
                toe4FrontInstance.changeJointNumber(3)
                cmds.setAttr(toe4FrontInstance.cvJointLoc+".translateZ", 0.25)
                cmds.setAttr(toe4FrontInstance.cvEndJoint+".translateZ", 0.2)
                cmds.setAttr(toe4FrontInstance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(toe4FrontInstance.moduleGrp+".flip", 1)
                toe4FrontInstance.displayAnnotation(0)
                
                # parent toe4 guide to foot middle guide:
                cmds.parent(toe4FrontInstance.moduleGrp, frontFootInstance.cvRFELoc, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+toeName+backName+'_1'))
                
                # create toe1 module instance:
                toe1BackInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe1BackInstance.editUserName(toeName+backName+"_1")
                # editing toe base guide informations:
                cmds.setAttr(toe1BackInstance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(toe1BackInstance.moduleGrp+".translateX", 2.5)
                cmds.setAttr(toe1BackInstance.moduleGrp+".translateY", 0.5)
                cmds.setAttr(toe1BackInstance.moduleGrp+".translateZ", -5.33)
                toe1BackInstance.changeJointNumber(2)
                cmds.setAttr(toe1BackInstance.cvJointLoc+".translateZ", 0.25)
                toe1BackInstance.changeJointNumber(3)
                cmds.setAttr(toe1BackInstance.cvJointLoc+".translateZ", 0.25)
                cmds.setAttr(toe1BackInstance.cvEndJoint+".translateZ", 0.2)
                cmds.setAttr(toe1BackInstance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(toe1BackInstance.moduleGrp+".flip", 1)
                toe1BackInstance.displayAnnotation(0)
                
                # parent toe1 guide to foot middle guide:
                cmds.parent(toe1BackInstance.moduleGrp, backFootInstance.cvRFELoc, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+toeName+backName+'_2'))
                
                # create toe2 module instance:
                toe2BackInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe2BackInstance.editUserName(toeName+backName+"_2")
                # editing toe base guide informations:
                cmds.setAttr(toe2BackInstance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(toe2BackInstance.moduleGrp+".translateX", 2.85)
                cmds.setAttr(toe2BackInstance.moduleGrp+".translateY", 0.5)
                cmds.setAttr(toe2BackInstance.moduleGrp+".translateZ", -5.33)
                toe2BackInstance.changeJointNumber(2)
                cmds.setAttr(toe2BackInstance.cvJointLoc+".translateZ", 0.25)
                toe2BackInstance.changeJointNumber(3)
                cmds.setAttr(toe2BackInstance.cvJointLoc+".translateZ", 0.25)
                cmds.setAttr(toe2BackInstance.cvEndJoint+".translateZ", 0.2)
                cmds.setAttr(toe2BackInstance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(toe2BackInstance.moduleGrp+".flip", 1)
                toe2BackInstance.displayAnnotation(0)
                
                # parent toe1 guide to foot middle guide:
                cmds.parent(toe2BackInstance.moduleGrp, backFootInstance.cvRFELoc, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+toeName+backName+'_3'))
                
                # create toe3 module instance:
                toe3BackInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe3BackInstance.editUserName(toeName+backName+"_3")
                # editing toe base guide informations:
                cmds.setAttr(toe3BackInstance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(toe3BackInstance.moduleGrp+".translateX", 3.15)
                cmds.setAttr(toe3BackInstance.moduleGrp+".translateY", 0.5)
                cmds.setAttr(toe3BackInstance.moduleGrp+".translateZ", -5.33)
                toe3BackInstance.changeJointNumber(2)
                cmds.setAttr(toe3BackInstance.cvJointLoc+".translateZ", 0.25)
                toe3BackInstance.changeJointNumber(3)
                cmds.setAttr(toe3BackInstance.cvJointLoc+".translateZ", 0.25)
                cmds.setAttr(toe3BackInstance.cvEndJoint+".translateZ", 0.2)
                cmds.setAttr(toe3BackInstance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(toe3BackInstance.moduleGrp+".flip", 1)
                toe3BackInstance.displayAnnotation(0)
                
                # parent toe1 guide to foot middle guide:
                cmds.parent(toe3BackInstance.moduleGrp, backFootInstance.cvRFELoc, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+toeName+backName+'_4'))
                
                # create toe4 module instance:
                toe4BackInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe4BackInstance.editUserName(toeName+backName+"_4")
                # editing toe base guide informations:
                cmds.setAttr(toe4BackInstance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(toe4BackInstance.moduleGrp+".translateX", 3.45)
                cmds.setAttr(toe4BackInstance.moduleGrp+".translateY", 0.5)
                cmds.setAttr(toe4BackInstance.moduleGrp+".translateZ", -5.33)
                toe4BackInstance.changeJointNumber(2)
                cmds.setAttr(toe4BackInstance.cvJointLoc+".translateZ", 0.25)
                toe4BackInstance.changeJointNumber(3)
                cmds.setAttr(toe4BackInstance.cvJointLoc+".translateZ", 0.25)
                cmds.setAttr(toe4BackInstance.cvEndJoint+".translateZ", 0.2)
                cmds.setAttr(toe4BackInstance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(toe4BackInstance.moduleGrp+".flip", 1)
                toe4BackInstance.displayAnnotation(0)
                
                # parent toe4 guide to foot middle guide:
                cmds.parent(toe4BackInstance.moduleGrp, backFootInstance.cvRFELoc, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+neckName))
                
                # woking with NeckBase system:
                # create fkLine module instance:
                neckBaseInstance = dpUIinst.initGuide('dpFkLine', guideDir, RigType.quadruped)
                # editing fkLine base guide informations:
                neckBaseInstance.editUserName(neckName+"Base")
                cmds.setAttr(neckBaseInstance.moduleGrp+".translateY", 9.5)
                cmds.setAttr(neckBaseInstance.moduleGrp+".translateZ", 5.5)
                cmds.setAttr(neckBaseInstance.moduleGrp+".rotateX", -45)
                cmds.setAttr(neckBaseInstance.radiusCtrl+".translateX", 2.8)
                
                # parent neckBase guide to spine guide:
                cmds.parent(neckBaseInstance.moduleGrp, spineInstance.cvLocator, absolute=True)
                
                # parent head guide to neckBase guide:
                cmds.parent(headInstance.moduleGrp, neckBaseInstance.cvJointLoc, absolute=True)
            
            # Close progress window
            cmds.progressWindow(endProgress=True)
            
            # select spineGuide_Base:
            cmds.select(spineInstance.moduleGrp)
            print dpUIinst.langDic[dpUIinst.langName]['m090_createdQuadruped']+"\n",
    else:
        # error checking modules in the folder:
        mel.eval('error \"'+ dpUIinst.langDic[dpUIinst.langName]['e001_GuideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
