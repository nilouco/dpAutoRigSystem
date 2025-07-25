# importing libraries:
from maya import cmds
from maya import mel
from ..Base.dpBaseStandard import RigType

# global variables to this module:    
CLASS_NAME = "Quadruped"
TITLE = "m037_quadruped"
DESCRIPTION = "m038_quadrupedDesc"
ICON = "/Icons/dp_quadruped.png"

DP_QUADRUPED_VERSION = 2.3


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
    guideDir = 'Modules.Standard'
    standardDir = 'Modules/Standard'
    checkModuleList = ['dpLimb', 'dpFoot', 'dpSpine', 'dpHead', 'dpFkLine', 'dpEye', 'dpNose', 'dpSingle']
    checkResultList = dpUIinst.startGuideModules(standardDir, "check", None, checkModuleList=checkModuleList)
    
    if len(checkResultList) == 0:
        dpUIinst.collapseEditSelModFL = True
        # defining naming:
        doingName = dpUIinst.lang['m094_doing']
        bipedStyleName = dpUIinst.lang['m026_biped']
        quadrupedStyleName = dpUIinst.lang['m155_quadrupedExtra']
        # part names:
        spineName = dpUIinst.lang['m011_spine']
        headName = dpUIinst.lang['c024_head']
        eyeName = dpUIinst.lang['c036_eye']
        legName = dpUIinst.lang['m030_leg'].capitalize()
        footName = dpUIinst.lang['c038_foot']
        earName = dpUIinst.lang['m040_ear']
        upperTeethName = dpUIinst.lang['m075_upperTeeth']
        upperTeethMiddleName = dpUIinst.lang['m075_upperTeeth']+dpUIinst.lang['c029_middle'].capitalize()
        upperTeethSideName = dpUIinst.lang['m075_upperTeeth']+dpUIinst.lang['c016_revFoot_G'].capitalize()
        lowerTeethName = dpUIinst.lang['m076_lowerTeeth']
        lowerTeethMiddleName = dpUIinst.lang['m076_lowerTeeth']+dpUIinst.lang['c029_middle'].capitalize()
        lowerTeethSideName = dpUIinst.lang['m076_lowerTeeth']+dpUIinst.lang['c016_revFoot_G'].capitalize()
        noseName = dpUIinst.lang['m078_nose']
        tongueName = dpUIinst.lang['m077_tongue']
        tailName = dpUIinst.lang['m039_tail']
        toeName = dpUIinst.lang['c013_revFoot_D'].capitalize()
        frontName = dpUIinst.lang['c056_front']
        backName = dpUIinst.lang['c057_back']
        simple   = dpUIinst.lang['i175_simple']
        complete = dpUIinst.lang['i176_complete']
        cancel   = dpUIinst.lang['i132_cancel']
        userMessage = dpUIinst.lang['i177_chooseMessage']
        breathName = dpUIinst.lang['c095_breath']
        bellyName = dpUIinst.lang['c096_belly']
        baseName = dpUIinst.lang['c106_base']
        upperName = dpUIinst.lang['c044_upper']
        lowerName = dpUIinst.lang['c045_lower']
        quadrupedGuideName = dpUIinst.lang['m037_quadruped']+" "+dpUIinst.lang['i205_guide']
        
        # getting Simple or Complete module guides to create:
        userDetail = getUserDetail(simple, complete, cancel, userMessage)
        if not userDetail == cancel:
            # number of modules to create:
            if userDetail == simple:
                maxProcess = 8
            else:
                maxProcess = 22
                
            # Starting progress window
            dpUIinst.utils.setProgress(doingName, quadrupedGuideName, maxProcess, addOne=False, addNumber=False)

            # woking with SPINE system:
            dpUIinst.utils.setProgress(doingName+spineName)
            # create spine module instance:
            spineInstance = dpUIinst.initGuide('dpSpine', guideDir, RigType.quadruped)
            # editing spine base guide informations:
            spineInstance.editGuideModuleName(spineName)
            cmds.setAttr(spineInstance.moduleGrp+".translateY", 10)
            cmds.setAttr(spineInstance.moduleGrp+".translateZ", -5)
            cmds.setAttr(spineInstance.moduleGrp+".rotateX", 0)
            cmds.setAttr(spineInstance.moduleGrp+".rotateY", 0)
            cmds.setAttr(spineInstance.moduleGrp+".rotateZ", 90)
            cmds.setAttr(spineInstance.cvLocator+".translateZ", 6)
            cmds.setAttr(spineInstance.annotation+".translateX", 6)
            cmds.setAttr(spineInstance.annotation+".translateY", 0)
            spineInstance.changeStyle(bipedStyleName)
            cmds.refresh()
            
            # woking with HEAD system:
            dpUIinst.utils.setProgress(doingName+headName)
            # create head module instance:
            headInstance = dpUIinst.initGuide('dpHead', guideDir, RigType.quadruped)
            # editing head base guide informations:
            headInstance.editGuideModuleName(headName)
            cmds.setAttr(headInstance.moduleGrp+".translateY", 9.5)
            cmds.setAttr(headInstance.moduleGrp+".translateZ", 5.5)
            cmds.setAttr(headInstance.moduleGrp+".rotateX", 0)
            cmds.setAttr(headInstance.moduleGrp+".rotateY", 45)
            cmds.setAttr(headInstance.moduleGrp+".rotateZ", 90)
            cmds.setAttr(headInstance.cvHeadLoc+".translateY", 5)
            cmds.setAttr(headInstance.cvHeadLoc+".rotateX", -45)
            cmds.setAttr(headInstance.cvUpperJawLoc+".translateY", 0.5)
            cmds.setAttr(headInstance.cvUpperJawLoc+".translateZ", 1.3)
            cmds.setAttr(headInstance.cvJawLoc+".translateY", -1.0)
            cmds.setAttr(headInstance.cvJawLoc+".translateZ", 2.0)
            cmds.setAttr(headInstance.cvJawLoc+".rotateY", 0)
            cmds.setAttr(headInstance.cvLCornerLipLoc+".translateX", 0.6)
            cmds.setAttr(headInstance.cvLCornerLipLoc+".translateY", -0.15)
            cmds.setAttr(headInstance.cvLCornerLipLoc+".translateZ", 1.6)
            cmds.setAttr(headInstance.cvUpperLipLoc+".translateY", -1.4)
            cmds.setAttr(headInstance.cvUpperLipLoc+".translateZ", 3.5)
            cmds.setAttr(headInstance.cvLowerLipLoc+".translateY", -0.2)
            cmds.setAttr(headInstance.cvLowerLipLoc+".translateZ", 2.5)
            cmds.setAttr(headInstance.annotation+".translateX", 4)
            cmds.setAttr(headInstance.annotation+".translateY", 0)
            headInstance.changeJointNumber(3)
            # parent head guide to chest guide:
            cmds.parent(headInstance.moduleGrp, spineInstance.cvLocator, absolute=True)
            cmds.refresh()
            
            # woking with Eye system:
            dpUIinst.utils.setProgress(doingName+eyeName)
            # create eyeLookAt module instance:
            eyeInstance = dpUIinst.initGuide('dpEye', guideDir, RigType.quadruped)
            # editing eyeLookAt base guide informations:
            eyeInstance.editGuideModuleName(eyeName)
            # setting X mirror:
            eyeInstance.changeMirror("X")
            cmds.setAttr(eyeInstance.moduleGrp+".translateX", 0.5)
            cmds.setAttr(eyeInstance.moduleGrp+".translateY", 13.5)
            cmds.setAttr(eyeInstance.moduleGrp+".translateZ", 11)
            cmds.setAttr(eyeInstance.annotation+".translateY", 3.5)
            cmds.setAttr(eyeInstance.radiusCtrl+".translateX", 0.5)
            cmds.setAttr(eyeInstance.cvEndJoint+".translateZ", 7)
            cmds.setAttr(eyeInstance.moduleGrp+".flip", 1)
            # parent head guide to spine guide:
            cmds.parent(eyeInstance.moduleGrp, headInstance.cvUpperHeadLoc, absolute=True)
            cmds.refresh()
            
            # working with BACK LEG (B) system:
            dpUIinst.utils.setProgress(doingName+legName)
            # create back leg module instance:
            backLegLimbInstance = dpUIinst.initGuide('dpLimb', guideDir, RigType.quadruped)
            # change limb guide to back leg type:
            backLegLimbInstance.changeType(legName)
            # change limb guide to back leg style (quadruped):
            backLegLimbInstance.changeStyle(quadrupedStyleName)
            # change name to back leg:
            backLegLimbInstance.editGuideModuleName(legName+backName)
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
            cmds.refresh()
            
            dpUIinst.utils.setProgress(doingName+footName)
            # create BACK FOOT (B) module instance:
            backFootInstance = dpUIinst.initGuide('dpFoot', guideDir, RigType.quadruped)
            backFootInstance.editGuideModuleName(footName+backName)
            cmds.setAttr(backFootInstance.annotation+".translateY", -3)
            cmds.setAttr(backFootInstance.moduleGrp+".translateX", 3)
            cmds.setAttr(backFootInstance.moduleGrp+".translateZ", -6.5)
            cmds.setAttr(backFootInstance.cvFootLoc+".translateZ", 1.5)
            cmds.setAttr(backFootInstance.cvRFALoc+".translateX", 0)
            cmds.setAttr(backFootInstance.cvRFBLoc+".translateX", 0)
            cmds.setAttr(backFootInstance.cvRFDLoc+".translateX", -1.5)
            cmds.setAttr(backFootInstance.cvRFFLoc+".translateZ", 1)
            # parent back foot guide to back leg ankle guide:
            cmds.parent(backFootInstance.moduleGrp, backLegLimbInstance.cvExtremLoc, absolute=True)
            cmds.refresh()
            
            # working with FRONT LEG (A) system:
            dpUIinst.utils.setProgress(doingName+legName)
            # create front leg module instance:
            frontLegLimbInstance = dpUIinst.initGuide('dpLimb', guideDir, RigType.quadruped)
            # change limb guide to front leg type:
            frontLegLimbInstance.changeType(legName)
            # change limb guide to front leg style (biped):
            frontLegLimbInstance.changeStyle(quadrupedStyleName)
            # change name to front leg:
            frontLegLimbInstance.editGuideModuleName(legName+frontName)
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
            cmds.setAttr(frontLegLimbInstance.mainAic+".offsetY", -1)
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
            cmds.refresh()

            dpUIinst.utils.setProgress(doingName+footName)
            # create FRONT FOOT (A) module instance:
            frontFootInstance = dpUIinst.initGuide('dpFoot', guideDir, RigType.quadruped)
            frontFootInstance.editGuideModuleName(footName+frontName)
            cmds.setAttr(frontFootInstance.annotation+".translateY", -3)
            cmds.setAttr(frontFootInstance.moduleGrp+".translateX", 2.5)
            cmds.setAttr(frontFootInstance.moduleGrp+".translateZ", 5.5)
            cmds.setAttr(frontFootInstance.cvFootLoc+".translateZ", 1.5)
            cmds.setAttr(frontFootInstance.cvRFALoc+".translateX", 0)
            cmds.setAttr(frontFootInstance.cvRFBLoc+".translateX", 0)
            cmds.setAttr(frontFootInstance.cvRFDLoc+".translateX", -1.5)
            cmds.setAttr(frontFootInstance.cvRFFLoc+".translateZ", 1)
            # parent front foot guide to front leg ankle guide:
            cmds.parent(frontFootInstance.moduleGrp, frontLegLimbInstance.cvExtremLoc, absolute=True)
            cmds.refresh()
            
            # woking with TAIL system:
            dpUIinst.utils.setProgress(doingName+tailName)
            # create FkLine module instance:
            tailInstance = dpUIinst.initGuide('dpFkLine', guideDir, RigType.quadruped)
            # editing tail base guide informations:
            tailInstance.editGuideModuleName(tailName)
            cmds.setAttr(tailInstance.moduleGrp+".translateY", 9.8)
            cmds.setAttr(tailInstance.moduleGrp+".translateZ", -7.6)
            cmds.setAttr(tailInstance.moduleGrp+".rotateX", 180)
            cmds.setAttr(tailInstance.moduleGrp+".rotateY", 20)
            cmds.setAttr(tailInstance.moduleGrp+".rotateZ", 90)
            cmds.setAttr(tailInstance.annotation+".translateX", 4)
            cmds.setAttr(tailInstance.annotation+".translateY", 0)
            cmds.setAttr(tailInstance.radiusCtrl+".translateX", 1)
            cmds.setAttr(tailInstance.moduleGrp+".mainControls", 1)
            # change the number of joints to the tail module:
            tailInstance.changeJointNumber(3)
            
            if userDetail == simple:
                # parent tail guide to spine guide:
                cmds.parent(tailInstance.moduleGrp, spineInstance.moduleGrp, absolute=True)
            
            #
            # complete part:
            #
            if userDetail == complete:
                
                # woking with TAIL system:
                dpUIinst.utils.setProgress(doingName+tailName+baseName)
                # create FkLine module instance:
                tailBaseInstance = dpUIinst.initGuide('dpFkLine', guideDir, RigType.quadruped)
                # editing tail base guide informations:
                tailBaseInstance.editGuideModuleName(tailName+baseName)
                cmds.setAttr(tailBaseInstance.moduleGrp+".translateY", 10.0)
                cmds.setAttr(tailBaseInstance.moduleGrp+".translateZ", -7)
                cmds.setAttr(tailBaseInstance.moduleGrp+".rotateX", 180)
                cmds.setAttr(tailBaseInstance.moduleGrp+".rotateZ", 90)
                cmds.setAttr(tailBaseInstance.annotation+".translateX", 4)
                cmds.setAttr(tailBaseInstance.annotation+".translateY", 0)
                # parent tail base guide to spine guide:
                cmds.parent(tailBaseInstance.moduleGrp, spineInstance.moduleGrp, absolute=True)
                # parent tail guide to tail base guide:
                cmds.parent(tailInstance.moduleGrp, tailBaseInstance.moduleGrp, absolute=True)
                cmds.refresh()

                # set guides attributes to complete system
                headInstance.changeDeformer(1)
                headInstance.changeFacial(1)
                backLegLimbInstance.setCorrective(1)
                frontLegLimbInstance.setCorrective(1)
                eyeInstance.setCorrective(1)
                
                # woking with EAR system:
                dpUIinst.utils.setProgress(doingName+earName)
                # create FkLine module instance:
                earBaseInstance = dpUIinst.initGuide('dpFkLine', guideDir, RigType.quadruped)
                # editing ear base guide informations:
                earBaseInstance.editGuideModuleName(earName+baseName)
                cmds.setAttr(earBaseInstance.moduleGrp+".translateX", 0.11)
                cmds.setAttr(earBaseInstance.moduleGrp+".translateY", 14)
                cmds.setAttr(earBaseInstance.moduleGrp+".translateZ", 10)
                cmds.setAttr(earBaseInstance.moduleGrp+".rotateX", 90)
                cmds.setAttr(earBaseInstance.moduleGrp+".rotateY", 20)
                cmds.setAttr(earBaseInstance.moduleGrp+".rotateZ", 127)
                cmds.setAttr(earBaseInstance.annotation+".translateX", 4)
                cmds.setAttr(earBaseInstance.annotation+".translateY", 0)
                cmds.setAttr(earBaseInstance.radiusCtrl+".translateX", 0.5)
                cmds.setAttr(earBaseInstance.cvEndJoint+".translateZ", 0.5)

                dpUIinst.utils.setProgress(doingName+earName)
                # create FkLine module instance:
                earInstance = dpUIinst.initGuide('dpFkLine', guideDir, RigType.quadruped)
                # editing ear base guide informations:
                earInstance.editGuideModuleName(earName)
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
                cmds.setAttr(earInstance.moduleGrp+".mainControls", 1)
                cmds.setAttr(earInstance.moduleGrp+".deformedBy", 1)
                cmds.setAttr(earInstance.moduleGrp+".scaleX", 0.5)
                cmds.setAttr(earInstance.moduleGrp+".scaleY", 0.5)
                cmds.setAttr(earInstance.moduleGrp+".scaleZ", 0.5)
                # change the number of joints to the ear module:
                earInstance.changeJointNumber(2)

                dpUIinst.utils.setProgress(doingName+upperName+earName)
                # create FkLine module instance:
                earUpperInstance = dpUIinst.initGuide('dpFkLine', guideDir, RigType.quadruped)
                # editing ear upper guide informations:
                earUpperInstance.editGuideModuleName(upperName+earName)
                cmds.setAttr(earUpperInstance.moduleGrp+".translateX", 1.401)
                cmds.setAttr(earUpperInstance.moduleGrp+".translateY", 15.365)
                cmds.setAttr(earUpperInstance.moduleGrp+".translateZ", 9.88)
                cmds.setAttr(earUpperInstance.moduleGrp+".rotateX", 90)
                cmds.setAttr(earUpperInstance.moduleGrp+".rotateY", 20)
                cmds.setAttr(earUpperInstance.moduleGrp+".rotateZ", 127)
                cmds.setAttr(earUpperInstance.annotation+".translateX", 4)
                cmds.setAttr(earUpperInstance.annotation+".translateY", 0)
                cmds.setAttr(earUpperInstance.radiusCtrl+".translateX", 0.3)
                cmds.setAttr(earUpperInstance.cvEndJoint+".translateZ", 0.5)
                cmds.setAttr(earUpperInstance.moduleGrp+".scaleX", 0.4)
                cmds.setAttr(earUpperInstance.moduleGrp+".scaleY", 0.4)
                cmds.setAttr(earUpperInstance.moduleGrp+".scaleZ", 0.4)
                
                dpUIinst.utils.setProgress(doingName+lowerName+earName)
                # create FkLine module instance:
                earLowerInstance = dpUIinst.initGuide('dpFkLine', guideDir, RigType.quadruped)
                # editing ear upper guide informations:
                earLowerInstance.editGuideModuleName(lowerName+earName)
                cmds.setAttr(earLowerInstance.moduleGrp+".translateX", 1.796)
                cmds.setAttr(earLowerInstance.moduleGrp+".translateY", 14.839)
                cmds.setAttr(earLowerInstance.moduleGrp+".translateZ", 10.12)
                cmds.setAttr(earLowerInstance.moduleGrp+".rotateX", 90)
                cmds.setAttr(earLowerInstance.moduleGrp+".rotateY", 20)
                cmds.setAttr(earLowerInstance.moduleGrp+".rotateZ", 127)
                cmds.setAttr(earLowerInstance.annotation+".translateX", 4)
                cmds.setAttr(earLowerInstance.annotation+".translateY", 0)
                cmds.setAttr(earLowerInstance.radiusCtrl+".translateX", 0.3)
                cmds.setAttr(earLowerInstance.cvEndJoint+".translateZ", 0.5)
                cmds.setAttr(earLowerInstance.moduleGrp+".scaleX", 0.4)
                cmds.setAttr(earLowerInstance.moduleGrp+".scaleY", 0.4)
                cmds.setAttr(earLowerInstance.moduleGrp+".scaleZ", 0.4)

                # parent ears guides to spine and other ear guides:
                cmds.parent(earBaseInstance.moduleGrp, headInstance.cvUpperHeadLoc, absolute=True)
                cmds.parent(earUpperInstance.moduleGrp, earInstance.cvJointLoc, absolute=True)
                cmds.parent(earLowerInstance.moduleGrp, earInstance.cvJointLoc, absolute=True)
                cmds.parent(earInstance.moduleGrp, earBaseInstance.moduleGrp, absolute=True)
                # setting X mirror:
                earBaseInstance.changeMirror("X")
                cmds.setAttr(earBaseInstance.moduleGrp+".flip", 1)
                cmds.refresh()
                
                # woking with Teeth system:
                dpUIinst.utils.setProgress(doingName+upperTeethName)
                # create FkLine module instance:
                upperTeethInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing upperTeeth base guide informations:
                upperTeethInstance.editGuideModuleName(upperTeethName)
                cmds.setAttr(upperTeethInstance.moduleGrp+".translateY", 12.5)
                cmds.setAttr(upperTeethInstance.moduleGrp+".translateZ", 12.7)
                cmds.setAttr(upperTeethInstance.radiusCtrl+".translateX", 0.5)
                cmds.setAttr(upperTeethInstance.cvEndJoint+".translateZ", 0.1)
                cmds.setAttr(upperTeethInstance.moduleGrp+".shapeSize", 0.5)
                cmds.setAttr(upperTeethInstance.moduleGrp+".deformedBy", 3)
                # create FkLine module instance:
                upperTeethMiddleInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing upperTeethMiddle base guide informations:
                upperTeethMiddleInstance.editGuideModuleName(upperTeethMiddleName)
                cmds.setAttr(upperTeethMiddleInstance.moduleGrp+".translateY", 12.3)
                cmds.setAttr(upperTeethMiddleInstance.moduleGrp+".translateZ", 12.7)
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
                upperTeethSideInstance.editGuideModuleName(upperTeethSideName)
                cmds.setAttr(upperTeethSideInstance.moduleGrp+".translateX", 0.2)
                cmds.setAttr(upperTeethSideInstance.moduleGrp+".translateY", 12.3)
                cmds.setAttr(upperTeethSideInstance.moduleGrp+".translateZ", 12.3)
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
                lowerTeethInstance.editGuideModuleName(lowerTeethName)
                cmds.setAttr(lowerTeethInstance.moduleGrp+".translateY", 11.7)
                cmds.setAttr(lowerTeethInstance.moduleGrp+".translateZ", 12.7)
                cmds.setAttr(lowerTeethInstance.radiusCtrl+".translateX", 0.5)
                cmds.setAttr(lowerTeethInstance.cvEndJoint+".translateZ", 0.1)
                cmds.setAttr(lowerTeethInstance.moduleGrp+".shapeSize", 0.5)
                cmds.setAttr(lowerTeethInstance.moduleGrp+".deformedBy", 3)
                # parent lowerTeeth guide to head guide:
                cmds.parent(lowerTeethInstance.moduleGrp, headInstance.cvChinLoc, absolute=True)
                # create FkLine module instance:
                lowerTeethMiddleInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing lowerTeethMiddle base guide informations:
                lowerTeethMiddleInstance.editGuideModuleName(lowerTeethMiddleName)
                cmds.setAttr(lowerTeethMiddleInstance.moduleGrp+".translateY", 11.9)
                cmds.setAttr(lowerTeethMiddleInstance.moduleGrp+".translateZ", 12.7)
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
                lowerTeethSideInstance.editGuideModuleName(lowerTeethSideName)
                cmds.setAttr(lowerTeethSideInstance.moduleGrp+".translateX", 0.2)
                cmds.setAttr(lowerTeethSideInstance.moduleGrp+".translateY", 11.9)
                cmds.setAttr(lowerTeethSideInstance.moduleGrp+".translateZ", 12.3)
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
                
                # woking with Tongue system:
                dpUIinst.utils.setProgress(doingName+tongueName)
                # create FkLine module instance:
                tongueInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing tongue base guide informations:
                tongueInstance.editGuideModuleName(tongueName)
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
                cmds.setAttr(tongueInstance.moduleGrp+".deformedBy", 3)
                # parent tongue guide to head guide:
                cmds.parent(tongueInstance.moduleGrp, headInstance.cvChinLoc, absolute=True)
                cmds.refresh()
                
                # woking with Nose system:
                dpUIinst.utils.setProgress(doingName+noseName)
                # create Nose module instance:
                noseInstance = dpUIinst.initGuide('dpNose', guideDir)
                # editing upperTeeth base guide informations:
                noseInstance.editGuideModuleName(noseName)
                cmds.setAttr(noseInstance.moduleGrp+".translateY", 13)
                cmds.setAttr(noseInstance.moduleGrp+".translateZ", 11.5)
                cmds.setAttr(noseInstance.radiusCtrl+".translateX", 0.3)
                cmds.setAttr(noseInstance.cvTopLoc+".rotateX", 25)
                noseInstance.changeJointNumber(2)
                cmds.setAttr(noseInstance.cvTopLoc+".translateY", 0.1)
                cmds.setAttr(noseInstance.cvTopLoc+".translateZ", 0.7)
                cmds.setAttr(noseInstance.cvTopLoc+".rotateX", -17)
                cmds.setAttr(noseInstance.cvMiddleLoc+".translateY", 0.3)
                cmds.setAttr(noseInstance.cvMiddleLoc+".translateZ", 1.3)
                cmds.setAttr(noseInstance.cvMiddleLoc+".rotateX", -25)
                cmds.setAttr(noseInstance.moduleGrp+".shapeSize", 0.5)
                # parent nose guide and upperTeeth to head guide:
                cmds.parent(upperTeethInstance.moduleGrp, noseInstance.moduleGrp, absolute=True)
                cmds.parent(noseInstance.moduleGrp, headInstance.cvUpperJawLoc, absolute=True)
                cmds.refresh()
                
                dpUIinst.utils.setProgress(doingName+toeName+frontName)
                # create toe1 module instance:
                toe1FrontInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe1FrontInstance.editGuideModuleName(toeName+frontName+"_1")
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
                cmds.parent(toe1FrontInstance.moduleGrp, frontFootInstance.cvRFFLoc, absolute=True)
                cmds.refresh()
                
                dpUIinst.utils.setProgress(doingName+toeName+frontName)
                # create toe2 module instance:
                toe2FrontInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe2FrontInstance.editGuideModuleName(toeName+frontName+"_2")
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
                cmds.parent(toe2FrontInstance.moduleGrp, frontFootInstance.cvRFFLoc, absolute=True)
                cmds.refresh()
                
                dpUIinst.utils.setProgress(doingName+toeName+frontName)
                # create toe3 module instance:
                toe3FrontInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe3FrontInstance.editGuideModuleName(toeName+frontName+"_3")
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
                cmds.parent(toe3FrontInstance.moduleGrp, frontFootInstance.cvRFFLoc, absolute=True)
                cmds.refresh()

                dpUIinst.utils.setProgress(doingName+toeName+frontName)
                # create toe4 module instance:
                toe4FrontInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe4FrontInstance.editGuideModuleName(toeName+frontName+"_4")
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
                cmds.parent(toe4FrontInstance.moduleGrp, frontFootInstance.cvRFFLoc, absolute=True)
                cmds.refresh()

                dpUIinst.utils.setProgress(doingName+toeName+backName)
                # create toe1 module instance:
                toe1BackInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe1BackInstance.editGuideModuleName(toeName+backName+"_1")
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
                cmds.parent(toe1BackInstance.moduleGrp, backFootInstance.cvRFFLoc, absolute=True)
                cmds.refresh()
                
                dpUIinst.utils.setProgress(doingName+toeName+backName)
                # create toe2 module instance:
                toe2BackInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe2BackInstance.editGuideModuleName(toeName+backName+"_2")
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
                # parent toe2 guide to foot middle guide:
                cmds.parent(toe2BackInstance.moduleGrp, backFootInstance.cvRFFLoc, absolute=True)
                cmds.refresh()
                
                dpUIinst.utils.setProgress(doingName+toeName+backName)
                # create toe3 module instance:
                toe3BackInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe3BackInstance.editGuideModuleName(toeName+backName+"_3")
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
                # parent toe3 guide to foot middle guide:
                cmds.parent(toe3BackInstance.moduleGrp, backFootInstance.cvRFFLoc, absolute=True)
                cmds.refresh()
                
                dpUIinst.utils.setProgress(doingName+toeName+backName)
                # create toe4 module instance:
                toe4BackInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe4BackInstance.editGuideModuleName(toeName+backName+"_4")
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
                cmds.parent(toe4BackInstance.moduleGrp, backFootInstance.cvRFFLoc, absolute=True)
                cmds.refresh()

                dpUIinst.utils.setProgress(doingName+breathName)
                # create breath module instance:
                breathInstance = dpUIinst.initGuide('dpSingle', guideDir)
                # change name to breath:
                breathInstance.editGuideModuleName(breathName)
                # editing breath base guide informations:
                cmds.setAttr(breathInstance.radiusCtrl+".translateX", 0.8)
                cmds.setAttr(breathInstance.moduleGrp+".translateY", 7)
                cmds.setAttr(breathInstance.moduleGrp+".translateZ", 4)
                cmds.setAttr(breathInstance.moduleGrp+".indirectSkin", 1)
                # parent breath guide to spine chest guide:
                cmds.parent(breathInstance.moduleGrp, spineInstance.cvLocator, absolute=True)
                cmds.refresh()

                dpUIinst.utils.setProgress(doingName+bellyName)
                # create belly module instance:
                bellyInstance = dpUIinst.initGuide('dpSingle', guideDir)
                # change name to belly:
                bellyInstance.editGuideModuleName(bellyName)
                # editing belly base guide informations:
                cmds.setAttr(bellyInstance.radiusCtrl+".translateX", 0.8)
                cmds.setAttr(bellyInstance.moduleGrp+".translateY", 8.5)
                cmds.setAttr(bellyInstance.moduleGrp+".translateZ", -3.5)
                cmds.setAttr(bellyInstance.moduleGrp+".indirectSkin", 1)
                # parent breath guide to spine chest guide:
                cmds.parent(bellyInstance.moduleGrp, spineInstance.moduleGrp, absolute=True)
            
            # Close progress window
            dpUIinst.utils.setProgress(endIt=True)
            
            # select spineGuide_Base:
            dpUIinst.collapseEditSelModFL = False
            cmds.select(spineInstance.moduleGrp)
            print(dpUIinst.lang['m090_createdQuadruped'])
    else:
        # error checking modules in the folder:
        mel.eval('error \"'+ dpUIinst.lang['e001_guideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
