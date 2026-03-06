# importing libraries:
from maya import cmds
from maya import mel

# global variables to this module:    
CLASS_NAME = "Car"
TITLE = "m163_car"
DESCRIPTION = "m164_carDesc"
ICON = "/Icons/dp_car.png"
WIKI = "03-‐-Guides#-car"

DP_CAR_VERSION = 2.02


def getUserDetail(opt1, opt2, cancel, userMessage):
    """ Ask user the detail level we'll create the guides by a confirm dialog box window.
        Options:
            Simple
            Complete
        Returns the user choose option or None if canceled.
    """
    result = cmds.confirmDialog(title=CLASS_NAME, message=userMessage, button=[opt1, opt2, cancel], defaultButton=opt2, cancelButton=cancel, dismissString=cancel)
    return result


def Car(ar):
    """ This function will create all guides needed to compose a car.
    """
    # check modules integrity:
    guideDir = 'Modules.Standard'
    standardDir = 'Modules/Standard'
    checkModuleList = ['dpFkLine', 'dpWheel', 'dpSteering', 'dpSuspension']
    checkResultList = ar.startGuideModules(standardDir, "check", None, checkModuleList=checkModuleList)
    
    if len(checkResultList) == 0:
        ar.collapseEditSelModFL = True
        # defining naming:
        doingName = ar.data.lang['m094_doing']
        # part names:
        chassisName = ar.data.lang['c091_chassis']
        sterringHandleName = ar.data.lang['m158_steering']+ar.data.lang['c078_handle']
        sterringName = ar.data.lang['m158_steering']+ar.data.lang['m162_wheelShape']
        hornName = ar.data.lang['c081_horn']
        frontWheelName = ar.data.lang['c056_front']+ar.data.lang['m156_wheel']
        backWheelName = ar.data.lang['c057_back']+ar.data.lang['m156_wheel']
        frontSuspensionName = ar.data.lang['c056_front']+ar.data.lang['m153_suspension']
        backSuspensionName = ar.data.lang['c057_back']+ar.data.lang['m153_suspension']
        frontDoorName = ar.data.lang['c056_front']+ar.data.lang['c072_door']
        backDoorName = ar.data.lang['c057_back']+ar.data.lang['c072_door']
        frontDoorHandleName = ar.data.lang['c056_front']+ar.data.lang['c072_door']+ar.data.lang['c078_handle']
        backDoorHandleName = ar.data.lang['c057_back']+ar.data.lang['c072_door']+ar.data.lang['c078_handle']
        frontWiperAName = ar.data.lang['c056_front']+ar.data.lang['c073_wiper']+"_A"
        frontWiperBName = ar.data.lang['c056_front']+ar.data.lang['c073_wiper']+"_B"
        backWiperName = ar.data.lang['c057_back']+ar.data.lang['c073_wiper']
        trunkName = ar.data.lang['c074_trunk']
        gasName = ar.data.lang['c075_gas']
        hoodName = ar.data.lang['c076_hood']
        sunRoofName = ar.data.lang['c077_sunRoof']
        antennaName = ar.data.lang['c080_antenna']
        leftTurnHandleName = ar.data.lang['p002_left']+"_"+ar.data.lang['c082_turn']+ar.data.lang['c078_handle']
        rightTurnHandleName = ar.data.lang['p003_right']+"_"+ar.data.lang['c082_turn']+ar.data.lang['c078_handle']
        gearLeverName = ar.data.lang['c083_gear']+ar.data.lang['c090_lever']
        breakName = ar.data.lang['c084_brake']
        handBreakName = ar.data.lang['c092_hand']+ar.data.lang['c084_brake']
        acceleratorName = ar.data.lang['c085_accelerator']
        clutchName = ar.data.lang['c086_clutch']
        dashboardAName = ar.data.lang['c087_dashboard']+"_A"
        dashboardBName = ar.data.lang['c087_dashboard']+"_B"
        frontSeatName = ar.data.lang['c056_front']+ar.data.lang['c088_seat']
        backSeatName = ar.data.lang['c057_back']+ar.data.lang['c088_seat']
        frontDoorInsideHandleName = ar.data.lang['c056_front']+ar.data.lang['c072_door']+ar.data.lang['c011_revFoot_B'].capitalize()+ar.data.lang['c078_handle']
        backDoorInsideHandleName = ar.data.lang['c057_back']+ar.data.lang['c072_door']+ar.data.lang['c011_revFoot_B'].capitalize()+ar.data.lang['c078_handle']
        frontDoorWindowName = ar.data.lang['c056_front']+ar.data.lang['c072_door']+ar.data.lang['c079_window']
        backDoorWindowName = ar.data.lang['c057_back']+ar.data.lang['c072_door']+ar.data.lang['c079_window']
        mirrorName = ar.data.lang['m010_mirror']
        insideMirrorName = ar.data.lang['c011_revFoot_B']+ar.data.lang['m010_mirror']
        simple   = ar.data.lang['i175_simple']
        complete = ar.data.lang['i176_complete']
        cancel   = ar.data.lang['i132_cancel']
        userMessage = ar.data.lang['i177_chooseMessage']
        carGuideName = ar.data.lang['m163_car']+" "+ar.data.lang['i205_guide']
        
        # getting Simple or Complete module guides to create:
        userDetail = getUserDetail(simple, complete, cancel, userMessage)
        if not userDetail == cancel:
            # number of modules to create:
            if userDetail == simple:
                maxProcess = 9
            else:
                maxProcess = 37
            
            # Starting progress window
            ar.utils.setProgress(doingName, carGuideName, maxProcess, addOne=False, addNumber=False)
            
            # woking with CHASSIS system:
            ar.utils.setProgress(doingName+chassisName)
            # create fkLine module instance:
            chassisInstance = ar.initGuide('dpFkLine', guideDir)
            # editing chassis base guide informations:
            chassisInstance.editGuideModuleName(chassisName)
            cmds.setAttr(chassisInstance.moduleGrp+".translateY", 12)
            cmds.setAttr(chassisInstance.annotation+".translateY", 16)
            cmds.setAttr(chassisInstance.radiusCtrl+".translateX", 12)
            cmds.refresh()
            
            # woking with self.steeringName HANDLE system:
            ar.utils.setProgress(doingName+sterringHandleName)
            # create fkLine module instance:
            steeringHandleInstance = ar.initGuide('dpFkLine', guideDir)
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
            ar.utils.setProgress(doingName+sterringName)
            # create steering module instance:
            steeringInstance = ar.initGuide('dpSteering', guideDir)
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
            ar.utils.setProgress(doingName+frontWheelName)
            # create wheel module instance:
            frontWheelInstance = ar.initGuide('dpWheel', guideDir)
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
            ar.utils.setProgress(doingName+backWheelName)
            # create wheel module instance:
            backWheelInstance = ar.initGuide('dpWheel', guideDir)
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
            ar.utils.setProgress(doingName+frontSuspensionName)
            # create FRONT self.suspensionName module instance:
            frontSuspensionInstance = ar.initGuide('dpSuspension', guideDir)
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
            ar.utils.setProgress(doingName+backSuspensionName)
            # create BACK self.suspensionName module instance:
            backSuspensionInstance = ar.initGuide('dpSuspension', guideDir)
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
            ar.utils.setProgress(doingName+frontDoorName)
            # create fkLine module instance:
            frontDoorInstance = ar.initGuide('dpFkLine', guideDir)
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
            ar.utils.setProgress(doingName+backDoorName)
            # create fkLine module instance:
            backDoorInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+hornName)
                # create fkLine module instance:
                hornInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+frontDoorHandleName)
                # create fkLine module instance:
                frontDoorHandleInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+backDoorHandleName)
                # create fkLine module instance:
                backDoorHandleInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+frontWiperAName)
                # create fkLine module instance:
                frontWiperAInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+frontWiperBName)
                # create fkLine module instance:
                frontWiperBInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+trunkName)
                # create fkLine module instance:
                trunkInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+backWiperName)
                # create fkLine module instance:
                backWiperInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+gasName)
                # create fkLine module instance:
                gasInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+hoodName)
                # create fkLine module instance:
                hoodInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+sunRoofName)
                # create fkLine module instance:
                sunroofInstance = ar.initGuide('dpFkLine', guideDir)
                sunroofInstance.editGuideModuleName(sunRoofName)
                # editing sun roof base guide informations:
                cmds.setAttr(sunroofInstance.moduleGrp+".translateY", 19)
                cmds.setAttr(sunroofInstance.moduleGrp+".translateZ", -2.5)
                # parent sun roof guide to chassis guide:
                cmds.parent(sunroofInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with ANTENNA system:
                ar.utils.setProgress(doingName+antennaName)
                # create fkLine module instance:
                antennaInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+leftTurnHandleName)
                # create fkLine module instance:
                leftTurnHandleInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+rightTurnHandleName)
                # create fkLine module instance:
                rightTurnHandleInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+gearLeverName)
                # create fkLine module instance:
                gearLeverInstance = ar.initGuide('dpFkLine', guideDir)
                gearLeverInstance.editGuideModuleName(gearLeverName)
                # editing gear lever base guide informations:
                cmds.setAttr(gearLeverInstance.moduleGrp+".translateY", 7.5)
                cmds.setAttr(gearLeverInstance.moduleGrp+".translateZ", 7.9)
                cmds.setAttr(gearLeverInstance.radiusCtrl+".translateX", 1.7)
                # parent gear lever guide to chassis guide:
                cmds.parent(gearLeverInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with HAND BREAK system:
                ar.utils.setProgress(doingName+handBreakName)
                # create fkLine module instance:
                handBreakInstance = ar.initGuide('dpFkLine', guideDir)
                handBreakInstance.editGuideModuleName(handBreakName)
                # editing hand break base guide informations:
                cmds.setAttr(handBreakInstance.moduleGrp+".translateY", 7.9)
                cmds.setAttr(handBreakInstance.moduleGrp+".translateZ", 2.3)
                cmds.setAttr(handBreakInstance.radiusCtrl+".translateX", 1)
                # parent hand break guide to chassis guide:
                cmds.parent(handBreakInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
                cmds.refresh()
                
                # woking with BREAK system:
                ar.utils.setProgress(doingName+breakName)
                # create fkLine module instance:
                breakInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+acceleratorName)
                # create fkLine module instance:
                acceleratorInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+clutchName)
                # create fkLine module instance:
                clutchInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+dashboardAName)
                # create fkLine module instance:
                dashboardAInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+dashboardBName)
                # create fkLine module instance:
                dashboardBInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+frontSeatName)
                # create fkLine module instance:
                frontSeatInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+backSeatName)
                # create fkLine module instance:
                backSeatInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+frontDoorInsideHandleName)
                # create fkLine module instance:
                frontDoorInsideHandleInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+backDoorInsideHandleName)
                # create fkLine module instance:
                backDoorInsideHandleInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+frontDoorWindowName)
                # create fkLine module instance:
                frontDoorWindowInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+backDoorWindowName)
                # create fkLine module instance:
                backDoorWindowInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+mirrorName)
                # create fkLine module instance:
                mirrorInstance = ar.initGuide('dpFkLine', guideDir)
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
                ar.utils.setProgress(doingName+insideMirrorName)
                # create fkLine module instance:
                insideMirrorInstance = ar.initGuide('dpFkLine', guideDir)
                insideMirrorInstance.editGuideModuleName(insideMirrorName)
                # editing inside mirror base guide informations:
                cmds.setAttr(insideMirrorInstance.moduleGrp+".translateY", 18)
                cmds.setAttr(insideMirrorInstance.moduleGrp+".translateZ", 3.5)
                cmds.setAttr(insideMirrorInstance.radiusCtrl+".translateX", 1.5)
                # parent mirror guide to front door guide:
                cmds.parent(insideMirrorInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
            
            # Close progress window
            ar.utils.setProgress(endIt=True)
            
            # select spineGuide_Base:
            ar.collapseEditSelModFL = False
            cmds.select(chassisInstance.moduleGrp)
            print(ar.data.lang['m167_createdCar'])
    else:
        # error checking modules in the folder:
        mel.eval('error \"'+ ar.data.lang['e001_guideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
