# importing libraries:
from maya import cmds
from maya import mel

# global variables to this module:    
CLASS_NAME = "Bike"
TITLE = "m165_bike"
DESCRIPTION = "m166_bikeDesc"
ICON = "/Icons/dp_bike.png"
WIKI = "03-‐-Guides#-bike"

DP_BIKE_VERSION = 2.03


def getUserDetail(opt1, opt2, cancel, userMessage):
    """ Ask user the detail level we'll create the guides by a confirm dialog box window.
        Options:
            Simple
            Complete
        Returns the user choose option or None if canceled.
    """
    result = cmds.confirmDialog(title=CLASS_NAME, message=userMessage, button=[opt1, opt2, cancel], defaultButton=opt2, cancelButton=cancel, dismissString=cancel)
    return result


def Bike(dpUIinst):
    """ This function will create all guides needed to compose a bike.
    """
    # check modules integrity:
    guideDir = 'Modules.Standard'
    standardDir = 'Modules/Standard'
    checkModuleList = ['dpFkLine', 'dpWheel', 'dpSteering', 'dpSuspension']
    checkResultList = dpUIinst.startGuideModules(standardDir, "check", None, checkModuleList=checkModuleList)
    
    if len(checkResultList) == 0:
        dpUIinst.collapseEditSelModFL = True
        # defining naming:
        doingName = dpUIinst.lang['m094_doing']
        # part names:
        chassisName = dpUIinst.lang['c091_chassis']
        forkName = dpUIinst.lang['m229_fork']
        handlebarName = dpUIinst.lang['m228_handlebar']
        hornName = dpUIinst.lang['c081_horn']
        frontWheelName = dpUIinst.lang['c056_front']+dpUIinst.lang['m156_wheel']
        backWheelName = dpUIinst.lang['c057_back']+dpUIinst.lang['m156_wheel']
        frontSuspensionName = dpUIinst.lang['c056_front']+dpUIinst.lang['m153_suspension']
        backSuspensionName = dpUIinst.lang['c057_back']+dpUIinst.lang['m153_suspension']
        seatName = dpUIinst.lang['c088_seat']
        mirrorName = dpUIinst.lang['m010_mirror']
        pedalName = dpUIinst.lang['c089_pedal']
        leftPedalName = dpUIinst.lang['p002_left']+"_"+dpUIinst.lang['c089_pedal']
        rightPedalName = dpUIinst.lang['p003_right']+"_"+dpUIinst.lang['c089_pedal']
        leverName = dpUIinst.lang['c090_lever']
        frontBasketName = dpUIinst.lang['c056_front']+dpUIinst.lang['c094_basket']
        backBasketName = dpUIinst.lang['c057_back']+dpUIinst.lang['c094_basket']
        simple   = dpUIinst.lang['i175_simple']
        complete = dpUIinst.lang['i176_complete']
        cancel   = dpUIinst.lang['i132_cancel']
        userMessage = dpUIinst.lang['i177_chooseMessage']
        bikeGuideName = dpUIinst.lang['m165_bike']+" "+dpUIinst.lang['i205_guide']
        
        # getting Simple or Complete module guides to create:
        userDetail = getUserDetail(simple, complete, cancel, userMessage)
        if not userDetail == cancel:
            # number of modules to create:
            if userDetail == simple:
                maxProcess = 9
            else:
                maxProcess = 16
            
            # Starting progress window
            dpUIinst.utils.setProgress(doingName, bikeGuideName, maxProcess, addOne=False, addNumber=False)
            dpUIinst.utils.setProgress(doingName+chassisName)
            
            # woking with CHASSIS system:
            # create fkLine module instance:
            chassisInstance = dpUIinst.initGuide('dpFkLine', guideDir)
            # editing chassis base guide informations:
            chassisInstance.editGuideModuleName(chassisName)
            cmds.setAttr(chassisInstance.moduleGrp+".translateY", 9)
            cmds.setAttr(chassisInstance.radiusCtrl+".translateX", 8)
            cmds.refresh()
            
            # woking with HANDLEBAR system:
            dpUIinst.utils.setProgress(doingName+handlebarName)
            # create fork instance:
            handlebarInstance = dpUIinst.initGuide('dpFkLine', guideDir)
            # editing fork base guide informations:
            handlebarInstance.editGuideModuleName(handlebarName)
            cmds.setAttr(handlebarInstance.moduleGrp+".translateY", 13.4)
            cmds.setAttr(handlebarInstance.moduleGrp+".translateZ", 4.7)
            cmds.setAttr(handlebarInstance.moduleGrp+".rotateX", 71)
            cmds.setAttr(handlebarInstance.annotation+".translateY", 2)
            # parent fork guide to Handlebar guide:
            cmds.parent(handlebarInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
            cmds.refresh()

            # woking with FORK system:
            dpUIinst.utils.setProgress(doingName+forkName)
            # create fkLine module instance:
            forkInstance = dpUIinst.initGuide('dpFkLine', guideDir)
            # editing fkLine base guide informations:
            forkInstance.editGuideModuleName(forkName)
            cmds.setAttr(forkInstance.moduleGrp+".translateY", 10.7)
            cmds.setAttr(forkInstance.moduleGrp+".translateZ", 6)
            cmds.setAttr(forkInstance.moduleGrp+".rotateX", -19)
            cmds.setAttr(forkInstance.radiusCtrl+".translateX", 1.1)
            # parent fork guide to handlebar guide:
            cmds.parent(forkInstance.moduleGrp, handlebarInstance.moduleGrp, absolute=True)
            cmds.refresh()
            
            # working with PEDAL self.wheelName system:
            dpUIinst.utils.setProgress(doingName+pedalName)
            # create pedal wheel module instance:
            pedalInstance = dpUIinst.initGuide('dpWheel', guideDir)
            pedalInstance.editGuideModuleName(pedalName)        
            # editing pedal wheel base guide informations:
            cmds.setAttr(pedalInstance.moduleGrp+".translateY", 4.5)
            cmds.setAttr(pedalInstance.moduleGrp+".translateZ", -0.8)
            cmds.setAttr(pedalInstance.moduleGrp+".rotateY", -90)
            cmds.setAttr(pedalInstance.radiusCtrl+".translateX", 1.5)
            cmds.setAttr(pedalInstance.moduleGrp+".steering", 0)
            # parent pedal wheel guide to chassis guide:
            cmds.parent(pedalInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
            cmds.refresh()
            
            # working with LEFT PEDAL system:
            dpUIinst.utils.setProgress(doingName+leftPedalName)
            # create pedal fkLine module instance:
            leftPedalInstance = dpUIinst.initGuide('dpFkLine', guideDir)
            leftPedalInstance.editGuideModuleName(leftPedalName)        
            # editing left pedal base guide informations:
            cmds.setAttr(leftPedalInstance.moduleGrp+".translateX", 1.3)
            cmds.setAttr(leftPedalInstance.moduleGrp+".translateY", 2.6)
            cmds.setAttr(leftPedalInstance.moduleGrp+".translateZ", -2.1)
            cmds.setAttr(leftPedalInstance.radiusCtrl+".translateX", 0.8)
            # parent left pedal guide to pedal base guide:
            cmds.parent(leftPedalInstance.moduleGrp, pedalInstance.cvCenterLoc, absolute=True)
            cmds.refresh()
            
            # working with RIGHT PEDAL system:
            dpUIinst.utils.setProgress(doingName+rightPedalName)
            # create pedal fkLine module instance:
            rightPedalInstance = dpUIinst.initGuide('dpFkLine', guideDir)
            rightPedalInstance.editGuideModuleName(rightPedalName)        
            # editing right pedal base guide informations:
            cmds.setAttr(rightPedalInstance.moduleGrp+".translateX", -1.3)
            cmds.setAttr(rightPedalInstance.moduleGrp+".translateY", 6.3)
            cmds.setAttr(rightPedalInstance.moduleGrp+".translateZ", 0.3)
            cmds.setAttr(rightPedalInstance.radiusCtrl+".translateX", 0.8)
            # parent right pedal guide to pedal base guide:
            cmds.parent(rightPedalInstance.moduleGrp, pedalInstance.cvCenterLoc, absolute=True)
            cmds.refresh()
            
            # working with FRONT self.wheelName system:
            dpUIinst.utils.setProgress(doingName+frontWheelName)
            # create wheel module instance:
            frontWheelInstance = dpUIinst.initGuide('dpWheel', guideDir)
            frontWheelInstance.editGuideModuleName(frontWheelName)        
            # editing frontWheel base guide informations:
            cmds.setAttr(frontWheelInstance.moduleGrp+".translateY", 4.7)
            cmds.setAttr(frontWheelInstance.moduleGrp+".translateZ", 8.4)
            cmds.setAttr(frontWheelInstance.moduleGrp+".rotateY", -90)
            cmds.setAttr(frontWheelInstance.radiusCtrl+".translateX", 4.7)
            cmds.setAttr(frontWheelInstance.moduleGrp+".steering", 0)
            # edit location of inside and outiside guide:
            cmds.setAttr(frontWheelInstance.cvInsideLoc+".translateZ", 0.35)
            cmds.setAttr(frontWheelInstance.cvOutsideLoc+".translateZ", -0.35)
            # parent front wheel guide to fork guide:
            cmds.parent(frontWheelInstance.moduleGrp, forkInstance.moduleGrp, absolute=True)
            cmds.refresh()
            
            # working with BACK self.wheelName system:
            dpUIinst.utils.setProgress(doingName+backWheelName)
            # create wheel module instance:
            backWheelInstance = dpUIinst.initGuide('dpWheel', guideDir)
            backWheelInstance.editGuideModuleName(backWheelName)        
            # editing frontWheel base guide informations:
            cmds.setAttr(backWheelInstance.moduleGrp+".translateY", 4.7)
            cmds.setAttr(backWheelInstance.moduleGrp+".translateZ", -7.8)
            cmds.setAttr(backWheelInstance.moduleGrp+".rotateY", -90)
            cmds.setAttr(backWheelInstance.radiusCtrl+".translateX", 4.7)
            cmds.setAttr(backWheelInstance.moduleGrp+".steering", 0)
            # edit location of inside and outiside guide:
            cmds.setAttr(backWheelInstance.cvInsideLoc+".translateZ", 0.35)
            cmds.setAttr(backWheelInstance.cvOutsideLoc+".translateZ", -0.35)
            # parent back wheel guide to chassis guide:
            cmds.parent(backWheelInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
            cmds.refresh()
            
            # woking with SEAT system:
            dpUIinst.utils.setProgress(doingName+seatName)
            # create fkLine module instance:
            frontSeatInstance = dpUIinst.initGuide('dpFkLine', guideDir)
            frontSeatInstance.editGuideModuleName(seatName)
            # editing seat base guide informations:
            cmds.setAttr(frontSeatInstance.moduleGrp+".translateY", 10)
            cmds.setAttr(frontSeatInstance.moduleGrp+".translateZ", -4)
            cmds.setAttr(frontSeatInstance.moduleGrp+".rotateX", -38)
            frontSeatInstance.changeJointNumber(2)
            cmds.setAttr(frontSeatInstance.cvJointLoc+".translateY", 0.9)
            cmds.setAttr(frontSeatInstance.cvJointLoc+".translateZ", 0.8)
            cmds.setAttr(frontSeatInstance.cvJointLoc+".rotateX", 38)
            # parent front seat guide to chassis guide:
            cmds.parent(frontSeatInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
            cmds.refresh()
            
            #
            # complete part:
            #
            if userDetail == complete:
            
                # woking with HORN system:
                dpUIinst.utils.setProgress(doingName+hornName)
                # create fkLine module instance:
                hornInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing eyeLookAt base guide informations:
                hornInstance.editGuideModuleName(hornName)
                cmds.setAttr(hornInstance.moduleGrp+".translateX", -1.64)
                cmds.setAttr(hornInstance.moduleGrp+".translateY", 13.3)
                cmds.setAttr(hornInstance.moduleGrp+".translateZ", 4.5)
                cmds.setAttr(hornInstance.moduleGrp+".rotateX", 17)
                cmds.setAttr(hornInstance.radiusCtrl+".translateX", 0.7)
                # parent horn guide to Handlebar guide:
                cmds.parent(hornInstance.moduleGrp, handlebarInstance.cvJointLoc, absolute=True)
                cmds.refresh()
                
                # create FRONT self.suspensionName module instance:
                dpUIinst.utils.setProgress(doingName+frontSuspensionName)
                frontSuspensionInstance = dpUIinst.initGuide('dpSuspension', guideDir)
                frontSuspensionInstance.editGuideModuleName(frontSuspensionName)
                # editing frontSuspension base guide informations:
                cmds.setAttr(frontSuspensionInstance.moduleGrp+".translateY", 7)
                cmds.setAttr(frontSuspensionInstance.moduleGrp+".translateZ", 7)
                cmds.setAttr(frontSuspensionInstance.moduleGrp+".rotateX", -110)
                cmds.setAttr(frontSuspensionInstance.radiusCtrl+".translateX", 0.7)
                # edit fatherB attribut for frontSuspension module guide?
                cmds.setAttr(frontSuspensionInstance.moduleGrp+".fatherB", forkInstance.moduleGrp, type='string')
                # parent front suspension guide to front wheel guide:
                cmds.parent(frontSuspensionInstance.moduleGrp, frontWheelInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # create BACK self.suspensionName module instance:
                dpUIinst.utils.setProgress(doingName+backSuspensionName)
                backSuspensionInstance = dpUIinst.initGuide('dpSuspension', guideDir)
                backSuspensionInstance.editGuideModuleName(backSuspensionName)
                # editing back suspension base guide informations:
                cmds.setAttr(backSuspensionInstance.moduleGrp+".translateY", 7)
                cmds.setAttr(backSuspensionInstance.moduleGrp+".translateZ", -6.6)
                cmds.setAttr(backSuspensionInstance.moduleGrp+".rotateX", -43)
                cmds.setAttr(backSuspensionInstance.radiusCtrl+".translateX", 0.7)
                # edit fatherB attribut for frontSuspension module guide?
                cmds.setAttr(backSuspensionInstance.moduleGrp+".fatherB", chassisInstance.moduleGrp, type='string')
                # parent front suspension guide to front wheel guide:
                cmds.parent(backSuspensionInstance.moduleGrp, backWheelInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with MIRROR system:
                dpUIinst.utils.setProgress(doingName+mirrorName)
                # create fkLine module instance:
                mirrorInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                mirrorInstance.editGuideModuleName(mirrorName)
                # editing mirror base guide informations:
                cmds.setAttr(mirrorInstance.moduleGrp+".translateX", 3.4)
                cmds.setAttr(mirrorInstance.moduleGrp+".translateY", 15)
                cmds.setAttr(mirrorInstance.moduleGrp+".translateZ", 4.1)
                cmds.setAttr(mirrorInstance.moduleGrp+".rotateX", -68)
                cmds.setAttr(mirrorInstance.moduleGrp+".rotateY", 8)
                cmds.setAttr(mirrorInstance.moduleGrp+".rotateZ", -10)
                cmds.setAttr(mirrorInstance.radiusCtrl+".translateX",0.7)
                mirrorInstance.changeJointNumber(2)
                cmds.setAttr(mirrorInstance.cvJointLoc+".translateY", 0)
                cmds.setAttr(mirrorInstance.cvJointLoc+".translateZ", 1.1)
                mirrorInstance.changeJointNumber(3)
                cmds.setAttr(mirrorInstance.cvJointLoc+".translateX", 1.2)
                cmds.setAttr(mirrorInstance.cvJointLoc+".translateZ", 0.5)
                # parent mirror guide to handlebar guide:
                cmds.parent(mirrorInstance.moduleGrp, handlebarInstance.cvJointLoc, absolute=True)
                cmds.refresh()
                
                # working with LEVER system:
                dpUIinst.utils.setProgress(doingName+leverName)
                # create fkLine module instance:
                leverInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                leverInstance.editGuideModuleName(leverName)
                # setting X mirror:
                leverInstance.changeMirror("X")
                # editing lever base guide informations:
                cmds.setAttr(leverInstance.moduleGrp+".flip", 1)
                cmds.setAttr(leverInstance.moduleGrp+".translateX", 4.1)
                cmds.setAttr(leverInstance.moduleGrp+".translateY", 15)
                cmds.setAttr(leverInstance.moduleGrp+".translateZ", 4)
                cmds.setAttr(leverInstance.moduleGrp+".rotateY", 10)
                cmds.setAttr(leverInstance.radiusCtrl+".translateX",0.8)
                # parent lever guide to handlebar guide:
                cmds.parent(leverInstance.moduleGrp, handlebarInstance.cvJointLoc, absolute=True)
                cmds.refresh()
                
                # woking with FRONT BASKET system:
                dpUIinst.utils.setProgress(doingName+frontBasketName)
                # create fkLine module instance:
                frontBasketInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                frontBasketInstance.editGuideModuleName(frontBasketName)
                # editing front basket base guide informations:
                cmds.setAttr(frontBasketInstance.moduleGrp+".translateY", 10)
                cmds.setAttr(frontBasketInstance.moduleGrp+".translateZ", 9)
                frontBasketInstance.changeJointNumber(2)
                cmds.setAttr(frontBasketInstance.cvJointLoc+".translateY", 0.8)
                cmds.setAttr(frontBasketInstance.cvJointLoc+".translateZ", 0)
                # parent front basket guide to front wheel guide:
                cmds.parent(frontBasketInstance.moduleGrp, frontWheelInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with BACK BASKET system:
                dpUIinst.utils.setProgress(doingName+backBasketName)
                # create fkLine module instance:
                backBasketInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                backBasketInstance.editGuideModuleName(backBasketName)
                # editing back basket base guide informations:
                cmds.setAttr(backBasketInstance.moduleGrp+".translateY", 10)
                cmds.setAttr(backBasketInstance.moduleGrp+".translateZ", -8)
                backBasketInstance.changeJointNumber(2)
                cmds.setAttr(backBasketInstance.cvJointLoc+".translateY", 0.8)
                cmds.setAttr(backBasketInstance.cvJointLoc+".translateZ", 0)
                
                # parent back basket guide to chassis guide:
                cmds.parent(backBasketInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
            
            # Close progress window
            dpUIinst.utils.setProgress(endIt=True)
            
            # select spineGuide_Base:
            dpUIinst.collapseEditSelModFL = False
            cmds.select(chassisInstance.moduleGrp)
            print(dpUIinst.lang['m168_createdBike'])
    else:
        # error checking modules in the folder:
        mel.eval('error \"'+ dpUIinst.lang['e001_guideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
