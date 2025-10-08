# importing libraries:
from maya import cmds
from maya import mel

# global variables to this module:    
CLASS_NAME = "Car"
TITLE = "m163_car"
DESCRIPTION = "m164_carDesc"
ICON = "/Icons/dp_car.png"

DP_CAR_VERSION = 2.01


def getUserDetail(opt1, opt2, cancel, userMessage):
    """ Ask user the detail level we'll create the guides by a confirm dialog box window.
        Options:
            Simple
            Complete
        Returns the user choose option or None if canceled.
    """
    result = cmds.confirmDialog(title=CLASS_NAME, message=userMessage, button=[opt1, opt2, cancel], defaultButton=opt2, cancelButton=cancel, dismissString=cancel)
    return result


def Car(dpUIinst):
    """ This function will create all guides needed to compose a car.
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
        sterringHandleName = dpUIinst.lang['m158_steering']+dpUIinst.lang['c078_handle']
        sterringName = dpUIinst.lang['m158_steering']+dpUIinst.lang['m162_wheelShape']
        hornName = dpUIinst.lang['c081_horn']
        frontWheelName = dpUIinst.lang['c056_front']+dpUIinst.lang['m156_wheel']
        backWheelName = dpUIinst.lang['c057_back']+dpUIinst.lang['m156_wheel']
        frontSuspensionName = dpUIinst.lang['c056_front']+dpUIinst.lang['m153_suspension']
        backSuspensionName = dpUIinst.lang['c057_back']+dpUIinst.lang['m153_suspension']
        frontDoorName = dpUIinst.lang['c056_front']+dpUIinst.lang['c072_door']
        backDoorName = dpUIinst.lang['c057_back']+dpUIinst.lang['c072_door']
        frontDoorHandleName = dpUIinst.lang['c056_front']+dpUIinst.lang['c072_door']+dpUIinst.lang['c078_handle']
        backDoorHandleName = dpUIinst.lang['c057_back']+dpUIinst.lang['c072_door']+dpUIinst.lang['c078_handle']
        frontWiperAName = dpUIinst.lang['c056_front']+dpUIinst.lang['c073_wiper']+"_A"
        frontWiperBName = dpUIinst.lang['c056_front']+dpUIinst.lang['c073_wiper']+"_B"
        backWiperName = dpUIinst.lang['c057_back']+dpUIinst.lang['c073_wiper']
        trunkName = dpUIinst.lang['c074_trunk']
        gasName = dpUIinst.lang['c075_gas']
        hoodName = dpUIinst.lang['c076_hood']
        sunRoofName = dpUIinst.lang['c077_sunRoof']
        antennaName = dpUIinst.lang['c080_antenna']
        leftTurnHandleName = dpUIinst.lang['p002_left']+"_"+dpUIinst.lang['c082_turn']+dpUIinst.lang['c078_handle']
        rightTurnHandleName = dpUIinst.lang['p003_right']+"_"+dpUIinst.lang['c082_turn']+dpUIinst.lang['c078_handle']
        gearLeverName = dpUIinst.lang['c083_gear']+dpUIinst.lang['c090_lever']
        breakName = dpUIinst.lang['c084_brake']
        handBreakName = dpUIinst.lang['c092_hand']+dpUIinst.lang['c084_brake']
        acceleratorName = dpUIinst.lang['c085_accelerator']
        clutchName = dpUIinst.lang['c086_clutch']
        dashboardAName = dpUIinst.lang['c087_dashboard']+"_A"
        dashboardBName = dpUIinst.lang['c087_dashboard']+"_B"
        frontSeatName = dpUIinst.lang['c056_front']+dpUIinst.lang['c088_seat']
        backSeatName = dpUIinst.lang['c057_back']+dpUIinst.lang['c088_seat']
        frontDoorInsideHandleName = dpUIinst.lang['c056_front']+dpUIinst.lang['c072_door']+dpUIinst.lang['c011_revFoot_B'].capitalize()+dpUIinst.lang['c078_handle']
        backDoorInsideHandleName = dpUIinst.lang['c057_back']+dpUIinst.lang['c072_door']+dpUIinst.lang['c011_revFoot_B'].capitalize()+dpUIinst.lang['c078_handle']
        frontDoorWindowName = dpUIinst.lang['c056_front']+dpUIinst.lang['c072_door']+dpUIinst.lang['c079_window']
        backDoorWindowName = dpUIinst.lang['c057_back']+dpUIinst.lang['c072_door']+dpUIinst.lang['c079_window']
        mirrorName = dpUIinst.lang['m010_mirror']
        insideMirrorName = dpUIinst.lang['c011_revFoot_B']+dpUIinst.lang['m010_mirror']
        simple   = dpUIinst.lang['i175_simple']
        complete = dpUIinst.lang['i176_complete']
        cancel   = dpUIinst.lang['i132_cancel']
        userMessage = dpUIinst.lang['i177_chooseMessage']
        carGuideName = dpUIinst.lang['m163_car']+" "+dpUIinst.lang['i205_guide']
        
        # getting Simple or Complete module guides to create:
        userDetail = getUserDetail(simple, complete, cancel, userMessage)
        if not userDetail == cancel:
            # number of modules to create:
            if userDetail == simple:
                maxProcess = 9
            else:
                maxProcess = 37
            
            # Starting progress window
            dpUIinst.utils.setProgress(doingName, carGuideName, maxProcess, addOne=False, addNumber=False)
            
            # woking with CHASSIS system:
            dpUIinst.utils.setProgress(doingName+chassisName)
            # create fkLine module instance:
            chassisInstance = dpUIinst.initGuide('dpFkLine', guideDir)
            # editing chassis base guide informations:
            chassisInstance.editGuideModuleName(chassisName)
            cmds.setAttr(chassisInstance.moduleGrp+".translateY", 12)
            cmds.setAttr(chassisInstance.annotation+".translateY", 16)
            cmds.setAttr(chassisInstance.radiusCtrl+".translateX", 12)
            cmds.refresh()
            
            # woking with self.steeringName HANDLE system:
            dpUIinst.utils.setProgress(doingName+sterringHandleName)
            # create fkLine module instance:
            steeringHandleInstance = dpUIinst.initGuide('dpFkLine', guideDir)
            # editing steering base guide informations:
            steeringHandleInstance.editGuideModuleName(sterringHandleName)
            cmds.setAttr(steeringHandleInstance.moduleGrp+".translateX", 4.5)
            cmds.setAttr(steeringHandleInstance.moduleGrp+".translateY", 11.2)
            cmds.setAttr(steeringHandleInstance.moduleGrp+".translateZ", 9.7)
            cmds.setAttr(steeringHandleInstance.moduleGrp+".rotateX", 10.5)
            cmds.setAttr(steeringHandleInstance.radiusCtrl+".translateX", 3)
            # parent steering handle guide to chassis guide:
            cmds.parent(steeringHandleInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
            cmds.refresh()
            
            # woking with self.steeringName system:
            dpUIinst.utils.setProgress(doingName+sterringName)
            # create steering module instance:
            steeringInstance = dpUIinst.initGuide('dpSteering', guideDir)
            # editing steering base guide informations:
            steeringInstance.editGuideModuleName(sterringName)
            cmds.setAttr(steeringInstance.moduleGrp+".translateX", 4.5)
            cmds.setAttr(steeringInstance.moduleGrp+".translateY", 12.1)
            cmds.setAttr(steeringInstance.moduleGrp+".translateZ", 6.8)
            cmds.setAttr(steeringInstance.moduleGrp+".rotateX", 28)
            cmds.setAttr(steeringInstance.annotation+".translateY", 2)
            # parent steering guide to steering handle guide:
            cmds.parent(steeringInstance.moduleGrp, steeringHandleInstance.moduleGrp, absolute=True)
            cmds.refresh()
            
            # working with FRONT self.wheelName system:
            dpUIinst.utils.setProgress(doingName+frontWheelName)
            # create wheel module instance:
            frontWheelInstance = dpUIinst.initGuide('dpWheel', guideDir)
            # change name to frontWheel:
            frontWheelInstance.editGuideModuleName(frontWheelName)        
            # setting X mirror:
            frontWheelInstance.changeMirror("X")
            # editing frontWheel base guide informations:
            cmds.setAttr(frontWheelInstance.moduleGrp+".translateX", 9)
            cmds.setAttr(frontWheelInstance.moduleGrp+".translateY", 4)
            cmds.setAttr(frontWheelInstance.moduleGrp+".translateZ", 17)
            cmds.setAttr(frontWheelInstance.moduleGrp+".rotateY", -90)
            cmds.setAttr(frontWheelInstance.radiusCtrl+".translateX", 4)
            cmds.setAttr(frontWheelInstance.moduleGrp+".steering", 1)
            cmds.setAttr(frontWheelInstance.moduleGrp+".flip", 1)
            # edit location of inside and outiside guide:
            cmds.setAttr(frontWheelInstance.cvInsideLoc+".translateZ", 1.4)
            cmds.setAttr(frontWheelInstance.cvOutsideLoc+".translateZ", -1.4)
            # parent front wheel guide to steering base guide:
            cmds.parent(frontWheelInstance.moduleGrp, steeringInstance.moduleGrp, absolute=True)
            cmds.refresh()
            
            # working with BACK self.wheelName system:
            dpUIinst.utils.setProgress(doingName+backWheelName)
            # create wheel module instance:
            backWheelInstance = dpUIinst.initGuide('dpWheel', guideDir)
            # change name to frontWheel:
            backWheelInstance.editGuideModuleName(backWheelName)        
            # setting X mirror:
            backWheelInstance.changeMirror("X")
            # editing frontWheel base guide informations:
            cmds.setAttr(backWheelInstance.moduleGrp+".translateX", 9)
            cmds.setAttr(backWheelInstance.moduleGrp+".translateY", 4)
            cmds.setAttr(backWheelInstance.moduleGrp+".translateZ", -14.5)
            cmds.setAttr(backWheelInstance.moduleGrp+".rotateY", -90)
            cmds.setAttr(backWheelInstance.radiusCtrl+".translateX", 4)
            cmds.setAttr(backWheelInstance.moduleGrp+".steering", 0)
            cmds.setAttr(backWheelInstance.moduleGrp+".flip", 1)
            # edit location of inside and outiside guide:
            cmds.setAttr(backWheelInstance.cvInsideLoc+".translateZ", 1.4)
            cmds.setAttr(backWheelInstance.cvOutsideLoc+".translateZ", -1.4)
            # parent front wheel guide to steering base guide:
            cmds.parent(backWheelInstance.moduleGrp, steeringInstance.moduleGrp, absolute=True)
            cmds.refresh()
            
            # working with FRONT self.suspensionName system:
            dpUIinst.utils.setProgress(doingName+frontSuspensionName)
            # create FRONT self.suspensionName module instance:
            frontSuspensionInstance = dpUIinst.initGuide('dpSuspension', guideDir)
            frontSuspensionInstance.editGuideModuleName(frontSuspensionName)
            # setting X mirror:
            frontSuspensionInstance.changeMirror("X")
            # editing front suspension base guide informations:
            cmds.setAttr(frontSuspensionInstance.moduleGrp+".translateX", 6.5)
            cmds.setAttr(frontSuspensionInstance.moduleGrp+".translateY", 4)
            cmds.setAttr(frontSuspensionInstance.moduleGrp+".translateZ", 17)
            cmds.setAttr(frontSuspensionInstance.moduleGrp+".rotateX", -100)
            cmds.setAttr(frontSuspensionInstance.moduleGrp+".flip", 1)
            cmds.setAttr(frontSuspensionInstance.radiusCtrl+".translateX", 0.6)
            cmds.setAttr(frontSuspensionInstance.cvBLoc+".translateZ", 6.5)
            # edit fatherB attribut for frontSuspension module guide?
            cmds.setAttr(frontSuspensionInstance.moduleGrp+".fatherB", chassisInstance.moduleGrp, type='string')
            # parent front suspension guide to front wheel guide:
            cmds.parent(frontSuspensionInstance.moduleGrp, frontWheelInstance.moduleGrp, absolute=True)
            cmds.refresh()
            
            # working with BACK self.suspensionName system:
            dpUIinst.utils.setProgress(doingName+backSuspensionName)
            # create BACK self.suspensionName module instance:
            backSuspensionInstance = dpUIinst.initGuide('dpSuspension', guideDir)
            backSuspensionInstance.editGuideModuleName(backSuspensionName)
            # setting X mirror:
            backSuspensionInstance.changeMirror("X")
            # editing back suspension base guide informations:
            cmds.setAttr(backSuspensionInstance.moduleGrp+".translateX", 6)
            cmds.setAttr(backSuspensionInstance.moduleGrp+".translateY", 4)
            cmds.setAttr(backSuspensionInstance.moduleGrp+".translateZ", -14)
            cmds.setAttr(backSuspensionInstance.moduleGrp+".rotateX", -85)
            cmds.setAttr(backSuspensionInstance.moduleGrp+".flip", 1)
            cmds.setAttr(backSuspensionInstance.radiusCtrl+".translateX", 0.6)
            cmds.setAttr(backSuspensionInstance.cvBLoc+".translateZ", 6.5)
            # edit fatherB attribut for frontSuspension module guide?
            cmds.setAttr(backSuspensionInstance.moduleGrp+".fatherB", chassisInstance.moduleGrp, type='string')
            # parent front suspension guide to front wheel guide:
            cmds.parent(backSuspensionInstance.moduleGrp, backWheelInstance.moduleGrp, absolute=True)
            cmds.refresh()
            
            # woking with FRONT DOOR system:
            dpUIinst.utils.setProgress(doingName+frontDoorName)
            # create fkLine module instance:
            frontDoorInstance = dpUIinst.initGuide('dpFkLine', guideDir)
            frontDoorInstance.editGuideModuleName(frontDoorName)
            # setting X mirror:
            frontDoorInstance.changeMirror("X")
            # editing front door base guide informations:
            cmds.setAttr(frontDoorInstance.moduleGrp+".flip", 1)
            cmds.setAttr(frontDoorInstance.moduleGrp+".translateX", 9.9)
            cmds.setAttr(frontDoorInstance.moduleGrp+".translateY", 9.9)
            cmds.setAttr(frontDoorInstance.moduleGrp+".translateZ", 10.7)
            cmds.setAttr(frontDoorInstance.radiusCtrl+".translateX", 3)
            # parent front door guide to chassis guide:
            cmds.parent(frontDoorInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
            cmds.refresh()
            
            # woking with BACK DOOR system:
            dpUIinst.utils.setProgress(doingName+backDoorName)
            # create fkLine module instance:
            backDoorInstance = dpUIinst.initGuide('dpFkLine', guideDir)
            backDoorInstance.editGuideModuleName(backDoorName)
            # setting X mirror:
            backDoorInstance.changeMirror("X")
            # editing back door base guide informations:
            cmds.setAttr(backDoorInstance.moduleGrp+".flip", 1)
            cmds.setAttr(backDoorInstance.moduleGrp+".translateX", 9.9)
            cmds.setAttr(backDoorInstance.moduleGrp+".translateY", 9.9)
            cmds.setAttr(backDoorInstance.moduleGrp+".translateZ", -1)
            cmds.setAttr(backDoorInstance.radiusCtrl+".translateX", 3)
            # parent back door guide to chassis guide:
            cmds.parent(backDoorInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
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
                cmds.setAttr(hornInstance.moduleGrp+".translateX", 4.5)
                cmds.setAttr(hornInstance.moduleGrp+".translateY", 12.3)
                cmds.setAttr(hornInstance.moduleGrp+".translateZ", 6.5)
                cmds.setAttr(hornInstance.moduleGrp+".rotateX", 28)
                cmds.setAttr(hornInstance.radiusCtrl+".translateX", 0.7)
                # parent horn guide to steering guide:
                cmds.parent(hornInstance.moduleGrp, steeringInstance.cvJointLoc, absolute=True)
                cmds.refresh()
                
                # woking with FRONT DOOR HANDLE system:
                dpUIinst.utils.setProgress(doingName+frontDoorHandleName)
                # create fkLine module instance:
                frontDoorHandleInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                frontDoorHandleInstance.editGuideModuleName(frontDoorHandleName)
                # setting X mirror:
                frontDoorHandleInstance.changeMirror("X")
                # editing front door base guide informations:
                cmds.setAttr(frontDoorHandleInstance.moduleGrp+".flip", 1)
                cmds.setAttr(frontDoorHandleInstance.moduleGrp+".translateX", 10.4)
                cmds.setAttr(frontDoorHandleInstance.moduleGrp+".translateY", 11.2)
                cmds.setAttr(frontDoorHandleInstance.moduleGrp+".translateZ", 1.7)
                cmds.setAttr(frontDoorHandleInstance.radiusCtrl+".translateX", 0.8)
                # parent front door handle guide to front door guide:
                cmds.parent(frontDoorHandleInstance.moduleGrp, frontDoorInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with BACK DOOR HANDLE system:
                dpUIinst.utils.setProgress(doingName+backDoorHandleName)
                # create fkLine module instance:
                backDoorHandleInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                backDoorHandleInstance.editGuideModuleName(backDoorHandleName)
                # setting X mirror:
                backDoorHandleInstance.changeMirror("X")
                # editing back door handle base guide informations:
                cmds.setAttr(backDoorHandleInstance.moduleGrp+".flip", 1)
                cmds.setAttr(backDoorHandleInstance.moduleGrp+".translateX", 10.4)
                cmds.setAttr(backDoorHandleInstance.moduleGrp+".translateY", 11.2)
                cmds.setAttr(backDoorHandleInstance.moduleGrp+".translateZ", -9.5)
                cmds.setAttr(backDoorHandleInstance.radiusCtrl+".translateX", 0.8)
                # parent back door handle guide to back door guide:
                cmds.parent(backDoorHandleInstance.moduleGrp, backDoorInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with FRONT WIPER A system:
                dpUIinst.utils.setProgress(doingName+frontWiperAName)
                # create fkLine module instance:
                frontWiperAInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                frontWiperAInstance.editGuideModuleName(frontWiperAName)
                # editing front wiper A base guide informations:
                cmds.setAttr(frontWiperAInstance.moduleGrp+".translateX", 5.5)
                cmds.setAttr(frontWiperAInstance.moduleGrp+".translateY", 13.7)
                cmds.setAttr(frontWiperAInstance.moduleGrp+".translateZ", 12.7)
                cmds.setAttr(frontWiperAInstance.moduleGrp+".rotateX", -63)
                cmds.setAttr(frontWiperAInstance.moduleGrp+".rotateZ", -8.5)
                cmds.setAttr(frontWiperAInstance.radiusCtrl+".translateX", 0.7)
                frontWiperAInstance.changeJointNumber(2)
                cmds.setAttr(frontWiperAInstance.cvJointLoc+".translateX", -5.2)
                cmds.setAttr(frontWiperAInstance.cvJointLoc+".translateY", 0.2)
                cmds.setAttr(frontWiperAInstance.cvJointLoc+".translateZ", -0.4)
                cmds.setAttr(frontWiperAInstance.cvJointLoc+".rotateY", -10.3)
                # parent front wiper A guide to chassis guide:
                cmds.parent(frontWiperAInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with FRONT WIPER B system:
                dpUIinst.utils.setProgress(doingName+frontWiperBName)
                # create fkLine module instance:
                frontWiperBInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                frontWiperBInstance.editGuideModuleName(frontWiperBName)
                # editing front wiper B base guide informations:
                cmds.setAttr(frontWiperBInstance.moduleGrp+".translateX", 0.7)
                cmds.setAttr(frontWiperBInstance.moduleGrp+".translateY", 13.7)
                cmds.setAttr(frontWiperBInstance.moduleGrp+".translateZ", 13.5)
                cmds.setAttr(frontWiperBInstance.moduleGrp+".rotateX", -62)
                cmds.setAttr(frontWiperBInstance.moduleGrp+".rotateY", -10.3)
                cmds.setAttr(frontWiperBInstance.moduleGrp+".rotateZ", -11.6)
                cmds.setAttr(frontWiperBInstance.radiusCtrl+".translateX", 0.7)
                frontWiperBInstance.changeJointNumber(2)
                cmds.setAttr(frontWiperBInstance.cvJointLoc+".translateX", -5.2)
                cmds.setAttr(frontWiperBInstance.cvJointLoc+".translateY", 0.2)
                cmds.setAttr(frontWiperBInstance.cvJointLoc+".translateZ", -0.4)
                cmds.setAttr(frontWiperBInstance.cvJointLoc+".rotateY", -10.3)
                # parent front wiper B guide to chassis guide:
                cmds.parent(frontWiperBInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with TRUNK system:
                dpUIinst.utils.setProgress(doingName+trunkName)
                # create fkLine module instance:
                trunkInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                trunkInstance.editGuideModuleName(trunkName)
                # editing trunk base guide informations:
                cmds.setAttr(trunkInstance.moduleGrp+".translateY", 19.4)
                cmds.setAttr(trunkInstance.moduleGrp+".translateZ", -18.7)
                cmds.setAttr(trunkInstance.moduleGrp+".rotateX", -36)
                cmds.setAttr(trunkInstance.radiusCtrl+".translateX", 3.3)
                # parent trunk guide to chassis guide:
                cmds.parent(trunkInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with BACK WIPER system:
                dpUIinst.utils.setProgress(doingName+backWiperName)
                # create fkLine module instance:
                backWiperInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                backWiperInstance.editGuideModuleName(backWiperName)
                # editing back wiper base guide informations:
                cmds.setAttr(backWiperInstance.moduleGrp+".translateY", 14.8)
                cmds.setAttr(backWiperInstance.moduleGrp+".translateZ", -24.7)
                cmds.setAttr(backWiperInstance.moduleGrp+".rotateX", 34)
                cmds.setAttr(backWiperInstance.radiusCtrl+".translateX", 0.7)
                backWiperInstance.changeJointNumber(2)
                cmds.setAttr(backWiperInstance.cvJointLoc+".translateX", -2.7)
                cmds.setAttr(backWiperInstance.cvJointLoc+".translateY", 0.4)
                cmds.setAttr(backWiperInstance.cvJointLoc+".translateZ", 0.1)
                cmds.setAttr(backWiperInstance.cvJointLoc+".rotateZ", -7)
                # parent back wiper guide to trunk guide:
                cmds.parent(backWiperInstance.moduleGrp, trunkInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with GAS system:
                dpUIinst.utils.setProgress(doingName+gasName)
                # create fkLine module instance:
                gasInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                gasInstance.editGuideModuleName(gasName)
                # editing gas base guide informations:
                cmds.setAttr(gasInstance.moduleGrp+".translateX", -10)
                cmds.setAttr(gasInstance.moduleGrp+".translateY", 13)
                cmds.setAttr(gasInstance.moduleGrp+".translateZ", -17)
                cmds.setAttr(gasInstance.radiusCtrl+".translateX", 0.6)
                # parent gas guide to chassis guide:
                cmds.parent(gasInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with HOOD system:
                dpUIinst.utils.setProgress(doingName+hoodName)
                # create fkLine module instance:
                hoodInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                hoodInstance.editGuideModuleName(hoodName)
                # editing hood base guide informations:
                cmds.setAttr(hoodInstance.moduleGrp+".translateY", 13.5)
                cmds.setAttr(hoodInstance.moduleGrp+".translateZ", 12.5)
                cmds.setAttr(hoodInstance.moduleGrp+".rotateX", 12.5)
                cmds.setAttr(hoodInstance.radiusCtrl+".translateX", 5)
                # parent hood guide to chassis guide:
                cmds.parent(hoodInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with SUN ROOF system:
                dpUIinst.utils.setProgress(doingName+sunRoofName)
                # create fkLine module instance:
                sunroofInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                sunroofInstance.editGuideModuleName(sunRoofName)
                # editing sun roof base guide informations:
                cmds.setAttr(sunroofInstance.moduleGrp+".translateY", 19)
                cmds.setAttr(sunroofInstance.moduleGrp+".translateZ", -2.5)
                # parent sun roof guide to chassis guide:
                cmds.parent(sunroofInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with ANTENNA system:
                dpUIinst.utils.setProgress(doingName+antennaName)
                # create fkLine module instance:
                antennaInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                antennaInstance.editGuideModuleName(antennaName)
                # editing antenna base guide informations:
                cmds.setAttr(antennaInstance.moduleGrp+".translateY", 18.8)
                cmds.setAttr(antennaInstance.moduleGrp+".translateZ", 3.7)
                cmds.setAttr(antennaInstance.moduleGrp+".rotateX", -136)
                cmds.setAttr(antennaInstance.radiusCtrl+".translateX", 0.5)
                antennaInstance.changeJointNumber(3)
                # parent antenna guide to chassis guide:
                cmds.parent(antennaInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with LEFT TURN HANDLE system:
                dpUIinst.utils.setProgress(doingName+leftTurnHandleName)
                # create fkLine module instance:
                leftTurnHandleInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                leftTurnHandleInstance.editGuideModuleName(leftTurnHandleName)
                # editing left turn handle base guide informations:
                cmds.setAttr(leftTurnHandleInstance.moduleGrp+".translateX", 5.5)
                cmds.setAttr(leftTurnHandleInstance.moduleGrp+".translateY", 11.5)
                cmds.setAttr(leftTurnHandleInstance.moduleGrp+".translateZ", 7.3)
                cmds.setAttr(leftTurnHandleInstance.moduleGrp+".rotateX", 28)
                cmds.setAttr(leftTurnHandleInstance.radiusCtrl+".translateX", 1.1)
                # parent left turn handle guide to steering handle guide:
                cmds.parent(leftTurnHandleInstance.moduleGrp, steeringHandleInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with RIGHT TURN HANDLE system:
                dpUIinst.utils.setProgress(doingName+rightTurnHandleName)
                # create fkLine module instance:
                rightTurnHandleInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                rightTurnHandleInstance.editGuideModuleName(rightTurnHandleName)
                # editing right turn handle base guide informations:
                cmds.setAttr(rightTurnHandleInstance.moduleGrp+".translateX", 3.4)
                cmds.setAttr(rightTurnHandleInstance.moduleGrp+".translateY", 11.5)
                cmds.setAttr(rightTurnHandleInstance.moduleGrp+".translateZ", 7.3)
                cmds.setAttr(rightTurnHandleInstance.moduleGrp+".rotateX", 28)
                cmds.setAttr(rightTurnHandleInstance.radiusCtrl+".translateX", 1.1)
                # parent left turn handle guide to steering handle guide:
                cmds.parent(rightTurnHandleInstance.moduleGrp, steeringHandleInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with GEAR LEVER system:
                dpUIinst.utils.setProgress(doingName+gearLeverName)
                # create fkLine module instance:
                gearLeverInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                gearLeverInstance.editGuideModuleName(gearLeverName)
                # editing gear lever base guide informations:
                cmds.setAttr(gearLeverInstance.moduleGrp+".translateY", 7.5)
                cmds.setAttr(gearLeverInstance.moduleGrp+".translateZ", 7.9)
                cmds.setAttr(gearLeverInstance.radiusCtrl+".translateX", 1.7)
                # parent gear lever guide to chassis guide:
                cmds.parent(gearLeverInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with HAND BREAK system:
                dpUIinst.utils.setProgress(doingName+handBreakName)
                # create fkLine module instance:
                handBreakInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                handBreakInstance.editGuideModuleName(handBreakName)
                # editing hand break base guide informations:
                cmds.setAttr(handBreakInstance.moduleGrp+".translateY", 7.9)
                cmds.setAttr(handBreakInstance.moduleGrp+".translateZ", 2.3)
                cmds.setAttr(handBreakInstance.radiusCtrl+".translateX", 1)
                # parent hand break guide to chassis guide:
                cmds.parent(handBreakInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with BREAK system:
                dpUIinst.utils.setProgress(doingName+breakName)
                # create fkLine module instance:
                breakInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                breakInstance.editGuideModuleName(breakName)
                # editing break base guide informations:
                cmds.setAttr(breakInstance.moduleGrp+".translateX", 4.3)
                cmds.setAttr(breakInstance.moduleGrp+".translateY", 7.3)
                cmds.setAttr(breakInstance.moduleGrp+".translateZ", 13)
                cmds.setAttr(breakInstance.radiusCtrl+".translateX", 1)
                # parent break guide to chassis guide:
                cmds.parent(breakInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with ACCELERATOR system:
                dpUIinst.utils.setProgress(doingName+acceleratorName)
                # create fkLine module instance:
                acceleratorInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                acceleratorInstance.editGuideModuleName(acceleratorName)
                # editing accelerator base guide informations:
                cmds.setAttr(acceleratorInstance.moduleGrp+".translateX", 3.2)
                cmds.setAttr(acceleratorInstance.moduleGrp+".translateY", 7.3)
                cmds.setAttr(acceleratorInstance.moduleGrp+".translateZ", 13)
                cmds.setAttr(acceleratorInstance.radiusCtrl+".translateX", 1)
                # parent accelerator guide to chassis guide:
                cmds.parent(acceleratorInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with CLUTCH system:
                dpUIinst.utils.setProgress(doingName+clutchName)
                # create fkLine module instance:
                clutchInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                clutchInstance.editGuideModuleName(clutchName)
                # editing clutch base guide informations:
                cmds.setAttr(clutchInstance.moduleGrp+".translateX", 5.4)
                cmds.setAttr(clutchInstance.moduleGrp+".translateY", 7.3)
                cmds.setAttr(clutchInstance.moduleGrp+".translateZ", 13)
                cmds.setAttr(clutchInstance.radiusCtrl+".translateX", 1)
                # parent clutch guide to chassis guide:
                cmds.parent(clutchInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with DASHBOARD A system:
                dpUIinst.utils.setProgress(doingName+dashboardAName)
                # create fkLine module instance:
                dashboardAInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                dashboardAInstance.editGuideModuleName(dashboardAName)
                # editing dashboard A base guide informations:
                cmds.setAttr(dashboardAInstance.moduleGrp+".translateX", 5.2)
                cmds.setAttr(dashboardAInstance.moduleGrp+".translateY", 12.8)
                cmds.setAttr(dashboardAInstance.moduleGrp+".translateZ", 10.9)
                cmds.setAttr(dashboardAInstance.moduleGrp+".rotateX", 22.5)
                cmds.setAttr(dashboardAInstance.radiusCtrl+".translateX", 0.4)
                # parent dashboard A guide to chassis guide:
                cmds.parent(dashboardAInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with DASHBOARD B system:
                dpUIinst.utils.setProgress(doingName+dashboardBName)
                # create fkLine module instance:
                dashboardBInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                dashboardBInstance.editGuideModuleName(dashboardBName)
                # editing dashboard B base guide informations:
                cmds.setAttr(dashboardBInstance.moduleGrp+".translateX", 3.7)
                cmds.setAttr(dashboardBInstance.moduleGrp+".translateY", 12.8)
                cmds.setAttr(dashboardBInstance.moduleGrp+".translateZ", 10.9)
                cmds.setAttr(dashboardBInstance.moduleGrp+".rotateX", 22.5)
                cmds.setAttr(dashboardBInstance.radiusCtrl+".translateX", 0.4)
                # parent dashboard B guide to chassis guide:
                cmds.parent(dashboardBInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with FRONT SEAT system:
                dpUIinst.utils.setProgress(doingName+frontSeatName)
                # create fkLine module instance:
                frontSeatInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                frontSeatInstance.editGuideModuleName(frontSeatName)
                # setting X mirror:
                frontSeatInstance.changeMirror("X")
                # editing front seat base guide informations:
                cmds.setAttr(frontSeatInstance.moduleGrp+".flip", 1)
                cmds.setAttr(frontSeatInstance.moduleGrp+".translateX", 5.2)
                cmds.setAttr(frontSeatInstance.moduleGrp+".translateY", 7.7)
                cmds.setAttr(frontSeatInstance.moduleGrp+".translateZ", 2.8)
                cmds.setAttr(frontSeatInstance.radiusCtrl+".translateX", 2.5)
                frontSeatInstance.changeJointNumber(2)
                cmds.setAttr(frontSeatInstance.cvJointLoc+".translateY", 0.6)
                cmds.setAttr(frontSeatInstance.cvJointLoc+".translateZ", -1.9)
                frontSeatInstance.changeJointNumber(3)
                cmds.setAttr(frontSeatInstance.cvJointLoc+".translateY", 6.5)
                cmds.setAttr(frontSeatInstance.cvJointLoc+".translateZ", -2.7)
                # parent front seat guide to chassis guide:
                cmds.parent(frontSeatInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with BACK SEAT system:
                dpUIinst.utils.setProgress(doingName+backSeatName)
                # create fkLine module instance:
                backSeatInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                backSeatInstance.editGuideModuleName(backSeatName)
                # editing back seat base guide informations:
                cmds.setAttr(backSeatInstance.moduleGrp+".translateY", 7.7)
                cmds.setAttr(backSeatInstance.moduleGrp+".translateZ", -6)
                cmds.setAttr(backSeatInstance.radiusCtrl+".translateX", 3.5)
                backSeatInstance.changeJointNumber(2)
                cmds.setAttr(backSeatInstance.cvJointLoc+".translateY", 0.6)
                cmds.setAttr(backSeatInstance.cvJointLoc+".translateZ", -1.9)
                # parent back seat guide to chassis guide:
                cmds.parent(backSeatInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
                
                # woking with FRONT DOOR INSIDE HANDLE system:
                dpUIinst.utils.setProgress(doingName+frontDoorInsideHandleName)
                # create fkLine module instance:
                frontDoorInsideHandleInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                frontDoorInsideHandleInstance.editGuideModuleName(frontDoorInsideHandleName)
                # setting X mirror:
                frontDoorInsideHandleInstance.changeMirror("X")
                # editing front door inside handle base guide informations:
                cmds.setAttr(frontDoorInsideHandleInstance.moduleGrp+".flip", 1)
                cmds.setAttr(frontDoorInsideHandleInstance.moduleGrp+".translateX", 9.1)
                cmds.setAttr(frontDoorInsideHandleInstance.moduleGrp+".translateY", 11.4)
                cmds.setAttr(frontDoorInsideHandleInstance.moduleGrp+".translateZ", 6.3)
                cmds.setAttr(frontDoorInsideHandleInstance.radiusCtrl+".translateX", 0.6)
                # parent front door inside handle guide to front door guide:
                cmds.parent(frontDoorInsideHandleInstance.moduleGrp, frontDoorInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with BACK DOOR INSIDE HANDLE system:
                dpUIinst.utils.setProgress(doingName+backDoorInsideHandleName)
                # create fkLine module instance:
                backDoorInsideHandleInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                backDoorInsideHandleInstance.editGuideModuleName(backDoorInsideHandleName)
                # setting X mirror:
                backDoorInsideHandleInstance.changeMirror("X")
                # editing back door inside handle base guide informations:
                cmds.setAttr(backDoorInsideHandleInstance.moduleGrp+".flip", 1)
                cmds.setAttr(backDoorInsideHandleInstance.moduleGrp+".translateX", 8.8)
                cmds.setAttr(backDoorInsideHandleInstance.moduleGrp+".translateY", 11.4)
                cmds.setAttr(backDoorInsideHandleInstance.moduleGrp+".translateZ", -3.6)
                cmds.setAttr(backDoorInsideHandleInstance.radiusCtrl+".translateX", 0.6)
                # parent back door inside handle guide to back door guide:
                cmds.parent(backDoorInsideHandleInstance.moduleGrp, backDoorInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with FRONT DOOR WINDOW system:
                dpUIinst.utils.setProgress(doingName+frontDoorWindowName)
                # create fkLine module instance:
                frontDoorWindowInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                frontDoorWindowInstance.editGuideModuleName(frontDoorWindowName)
                # setting X mirror:
                frontDoorWindowInstance.changeMirror("X")
                # editing front door window base guide informations:
                cmds.setAttr(frontDoorWindowInstance.moduleGrp+".flip", 1)
                cmds.setAttr(frontDoorWindowInstance.moduleGrp+".translateX", 9.5)
                cmds.setAttr(frontDoorWindowInstance.moduleGrp+".translateY", 13)
                cmds.setAttr(frontDoorWindowInstance.moduleGrp+".translateZ", 2.9)
                cmds.setAttr(frontDoorWindowInstance.radiusCtrl+".translateX", 0.8)
                # parent front door window guide to front door guide:
                cmds.parent(frontDoorWindowInstance.moduleGrp, frontDoorInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with BACK DOOR WINDOW system:
                dpUIinst.utils.setProgress(doingName+backDoorWindowName)
                # create fkLine module instance:
                backDoorWindowInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                backDoorWindowInstance.editGuideModuleName(backDoorWindowName)
                # setting X mirror:
                backDoorWindowInstance.changeMirror("X")
                # editing back door window base guide informations:
                cmds.setAttr(backDoorWindowInstance.moduleGrp+".flip", 1)
                cmds.setAttr(backDoorWindowInstance.moduleGrp+".translateX", 9.5)
                cmds.setAttr(backDoorWindowInstance.moduleGrp+".translateY", 13.5)
                cmds.setAttr(backDoorWindowInstance.moduleGrp+".translateZ", -7.1)
                cmds.setAttr(backDoorWindowInstance.radiusCtrl+".translateX", 0.8)
                # parent back door window guide to back door guide:
                cmds.parent(backDoorWindowInstance.moduleGrp, backDoorInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with MIRROR system:
                dpUIinst.utils.setProgress(doingName+mirrorName)
                # create fkLine module instance:
                mirrorInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                mirrorInstance.editGuideModuleName(mirrorName)
                # setting X mirror:
                mirrorInstance.changeMirror("X")
                # editing mirror base guide informations:
                cmds.setAttr(mirrorInstance.moduleGrp+".flip", 1)
                cmds.setAttr(mirrorInstance.moduleGrp+".translateX", 9.8)
                cmds.setAttr(mirrorInstance.moduleGrp+".translateY", 13.1)
                cmds.setAttr(mirrorInstance.moduleGrp+".translateZ", 8.7)
                cmds.setAttr(mirrorInstance.radiusCtrl+".translateX", 1.1)
                mirrorInstance.changeJointNumber(2)
                cmds.setAttr(mirrorInstance.cvJointLoc+".translateY", 0.8)
                cmds.setAttr(mirrorInstance.cvJointLoc+".translateZ", 1)
                # parent mirror guide to front door guide:
                cmds.parent(mirrorInstance.moduleGrp, frontDoorInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with INSIDE MIRROR system:
                dpUIinst.utils.setProgress(doingName+insideMirrorName)
                # create fkLine module instance:
                insideMirrorInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                insideMirrorInstance.editGuideModuleName(insideMirrorName)
                # editing inside mirror base guide informations:
                cmds.setAttr(insideMirrorInstance.moduleGrp+".translateY", 18)
                cmds.setAttr(insideMirrorInstance.moduleGrp+".translateZ", 3.5)
                cmds.setAttr(insideMirrorInstance.radiusCtrl+".translateX", 1.5)
                # parent mirror guide to front door guide:
                cmds.parent(insideMirrorInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
            
            # Close progress window
            dpUIinst.utils.setProgress(endIt=True)
            
            # select spineGuide_Base:
            dpUIinst.collapseEditSelModFL = False
            cmds.select(chassisInstance.moduleGrp)
            print(dpUIinst.lang['m167_createdCar'])
    else:
        # error checking modules in the folder:
        mel.eval('error \"'+ dpUIinst.lang['e001_guideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
