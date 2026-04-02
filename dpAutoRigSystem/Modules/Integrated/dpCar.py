# importing libraries:
from maya import cmds
from maya import mel
from ..Base import dpBaseLibrary
from importlib import reload

# global variables to this module:    
CLASS_NAME = "Car"
TITLE = "m163_car"
DESCRIPTION = "m164_carDesc"
ICON = "/Icons/dp_car.png"
WIKI = "03-‐-Guides#-car"

DP_CAR_VERSION = 2.02


class Car(dpBaseLibrary.BaseLibrary):
    def __init__(self,  *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        kwargs["WIKI"] = WIKI
        dpBaseLibrary.BaseLibrary.__init__(self, *args, **kwargs)
        if self.ar.dev:
            reload(dpBaseLibrary)


    def build_template(self, *args):
        """ This function will create all guides needed to compose a car.
        """
        # check modules integrity:
        guideDir = 'Modules.Standard'
        standardDir = 'Modules/Standard'
        checkModuleList = ['dpFkLine', 'dpWheel', 'dpSteering', 'dpSuspension']
        checkResultList = self.ar.check_missing_modules(standardDir, checkModuleList)
        
        if len(checkResultList) == 0:
            self.ar.collapseEditSelModFL = True
            # defining naming:
            doingName = self.ar.data.lang['m094_doing']
            # part names:
            chassisName = self.ar.data.lang['c091_chassis']
            sterringHandleName = self.ar.data.lang['m158_steering']+self.ar.data.lang['c078_handle']
            sterringName = self.ar.data.lang['m158_steering']+self.ar.data.lang['m162_wheelShape']
            hornName = self.ar.data.lang['c081_horn']
            frontWheelName = self.ar.data.lang['c056_front']+self.ar.data.lang['m156_wheel']
            backWheelName = self.ar.data.lang['c057_back']+self.ar.data.lang['m156_wheel']
            frontSuspensionName = self.ar.data.lang['c056_front']+self.ar.data.lang['m153_suspension']
            backSuspensionName = self.ar.data.lang['c057_back']+self.ar.data.lang['m153_suspension']
            frontDoorName = self.ar.data.lang['c056_front']+self.ar.data.lang['c072_door']
            backDoorName = self.ar.data.lang['c057_back']+self.ar.data.lang['c072_door']
            frontDoorHandleName = self.ar.data.lang['c056_front']+self.ar.data.lang['c072_door']+self.ar.data.lang['c078_handle']
            backDoorHandleName = self.ar.data.lang['c057_back']+self.ar.data.lang['c072_door']+self.ar.data.lang['c078_handle']
            frontWiperAName = self.ar.data.lang['c056_front']+self.ar.data.lang['c073_wiper']+"_A"
            frontWiperBName = self.ar.data.lang['c056_front']+self.ar.data.lang['c073_wiper']+"_B"
            backWiperName = self.ar.data.lang['c057_back']+self.ar.data.lang['c073_wiper']
            trunkName = self.ar.data.lang['c074_trunk']
            gasName = self.ar.data.lang['c075_gas']
            hoodName = self.ar.data.lang['c076_hood']
            sunRoofName = self.ar.data.lang['c077_sunRoof']
            antennaName = self.ar.data.lang['c080_antenna']
            leftTurnHandleName = self.ar.data.lang['p002_left']+"_"+self.ar.data.lang['c082_turn']+self.ar.data.lang['c078_handle']
            rightTurnHandleName = self.ar.data.lang['p003_right']+"_"+self.ar.data.lang['c082_turn']+self.ar.data.lang['c078_handle']
            gearLeverName = self.ar.data.lang['c083_gear']+self.ar.data.lang['c090_lever']
            breakName = self.ar.data.lang['c084_brake']
            handBreakName = self.ar.data.lang['c092_hand']+self.ar.data.lang['c084_brake']
            acceleratorName = self.ar.data.lang['c085_accelerator']
            clutchName = self.ar.data.lang['c086_clutch']
            dashboardAName = self.ar.data.lang['c087_dashboard']+"_A"
            dashboardBName = self.ar.data.lang['c087_dashboard']+"_B"
            frontSeatName = self.ar.data.lang['c056_front']+self.ar.data.lang['c088_seat']
            backSeatName = self.ar.data.lang['c057_back']+self.ar.data.lang['c088_seat']
            frontDoorInsideHandleName = self.ar.data.lang['c056_front']+self.ar.data.lang['c072_door']+self.ar.data.lang['c011_revFoot_B'].capitalize()+self.ar.data.lang['c078_handle']
            backDoorInsideHandleName = self.ar.data.lang['c057_back']+self.ar.data.lang['c072_door']+self.ar.data.lang['c011_revFoot_B'].capitalize()+self.ar.data.lang['c078_handle']
            frontDoorWindowName = self.ar.data.lang['c056_front']+self.ar.data.lang['c072_door']+self.ar.data.lang['c079_window']
            backDoorWindowName = self.ar.data.lang['c057_back']+self.ar.data.lang['c072_door']+self.ar.data.lang['c079_window']
            mirrorName = self.ar.data.lang['m010_mirror']
            insideMirrorName = self.ar.data.lang['c011_revFoot_B']+self.ar.data.lang['m010_mirror']
            simple   = self.ar.data.lang['i175_simple']
            complete = self.ar.data.lang['i176_complete']
            cancel   = self.ar.data.lang['i132_cancel']
            userMessage = self.ar.data.lang['i177_chooseMessage']
            carGuideName = self.ar.data.lang['m163_car']+" "+self.ar.data.lang['i205_guide']
            
            # getting Simple or Complete module guides to create:
            userDetail = self.ask_build_detail(self.title, simple, complete, cancel, simple, userMessage)
            if not userDetail == cancel:
                # number of modules to create:
                if userDetail == simple:
                    maxProcess = 9
                else:
                    maxProcess = 37
                
                # Starting progress window
                self.ar.utils.setProgress(doingName, carGuideName, maxProcess, addOne=False, addNumber=False)
                
                # getting module instances:
                fkline = self.ar.config.get_instance("dpFkLine", [guideDir])
                wheel = self.ar.config.get_instance("dpWheel", [guideDir])
                steering = self.ar.config.get_instance("dpSteering", [guideDir])
                suspension = self.ar.config.get_instance("dpSuspension", [guideDir])
                
                # working with CHASSIS system:
                self.ar.utils.setProgress(doingName+chassisName)
                # create fkLine module instance:
                chassis_guide = fkline.build_raw_guide()
                # editing chassis base guide informations:
                fkline.editGuideModuleName(chassisName)
                cmds.setAttr(chassis_guide+".translateY", 12)
                cmds.setAttr(fkline.annotation+".translateY", 16)
                cmds.setAttr(fkline.radiusCtrl+".translateX", 12)
                cmds.refresh()
                
                # working with STEERING HANDLE system:
                self.ar.utils.setProgress(doingName+sterringHandleName)
                # create fkLine module instance:
                steering_handle_guide = fkline.build_raw_guide()
                # editing steering base guide informations:
                fkline.editGuideModuleName(sterringHandleName)
                cmds.setAttr(steering_handle_guide+".translateX", 4.5)
                cmds.setAttr(steering_handle_guide+".translateY", 11.2)
                cmds.setAttr(steering_handle_guide+".translateZ", 9.7)
                cmds.setAttr(steering_handle_guide+".rotateX", 10.5)
                cmds.setAttr(fkline.radiusCtrl+".translateX", 3)
                # parent steering handle guide to chassis guide:
                cmds.parent(steering_handle_guide, chassis_guide, absolute=True)
                cmds.refresh()
                
                # working with STEERING system:
                self.ar.utils.setProgress(doingName+sterringName)
                # create steering module instance:
                steering_guide = steering.build_raw_guide()
                # editing steering base guide informations:
                steering.editGuideModuleName(sterringName)
                cmds.setAttr(steering_guide+".translateX", 4.5)
                cmds.setAttr(steering_guide+".translateY", 12.1)
                cmds.setAttr(steering_guide+".translateZ", 6.8)
                cmds.setAttr(steering_guide+".rotateX", 28)
                cmds.setAttr(steering.annotation+".translateY", 2)
                # parent steering guide to steering handle guide:
                cmds.parent(steering_guide, steering_handle_guide, absolute=True)
                cmds.refresh()
                
                # working with FRONT WHEEL system:
                self.ar.utils.setProgress(doingName+frontWheelName)
                # create wheel module instance:
                front_wheel_guide = wheel.build_raw_guide()
                # change name to frontWheel:
                wheel.editGuideModuleName(frontWheelName)        
                # setting X mirror:
                wheel.changeMirror("X")
                # editing frontWheel base guide informations:
                cmds.setAttr(front_wheel_guide+".translateX", 9)
                cmds.setAttr(front_wheel_guide+".translateY", 4)
                cmds.setAttr(front_wheel_guide+".translateZ", 17)
                cmds.setAttr(front_wheel_guide+".rotateY", -90)
                cmds.setAttr(wheel.radiusCtrl+".translateX", 4)
                cmds.setAttr(front_wheel_guide+".steering", 1)
                cmds.setAttr(front_wheel_guide+".flip", 1)
                # edit location of inside and outiside guide:
                cmds.setAttr(wheel.cvInsideLoc+".translateZ", 1.4)
                cmds.setAttr(wheel.cvOutsideLoc+".translateZ", -1.4)
                # parent front wheel guide to steering base guide:
                cmds.parent(front_wheel_guide, steering_guide, absolute=True)
                cmds.refresh()
                
                # working with BACK WHEEL system:
                self.ar.utils.setProgress(doingName+backWheelName)
                # create wheel module instance:
                back_wheel_guide = wheel.build_raw_guide()
                # change name to frontWheel:
                wheel.editGuideModuleName(backWheelName)        
                # setting X mirror:
                wheel.changeMirror("X")
                # editing frontWheel base guide informations:
                cmds.setAttr(back_wheel_guide+".translateX", 9)
                cmds.setAttr(back_wheel_guide+".translateY", 4)
                cmds.setAttr(back_wheel_guide+".translateZ", -14.5)
                cmds.setAttr(back_wheel_guide+".rotateY", -90)
                cmds.setAttr(wheel.radiusCtrl+".translateX", 4)
                cmds.setAttr(back_wheel_guide+".steering", 0)
                cmds.setAttr(back_wheel_guide+".flip", 1)
                # edit location of inside and outiside guide:
                cmds.setAttr(wheel.cvInsideLoc+".translateZ", 1.4)
                cmds.setAttr(wheel.cvOutsideLoc+".translateZ", -1.4)
                # parent front wheel guide to steering base guide:
                cmds.parent(back_wheel_guide, steering_guide, absolute=True)
                cmds.refresh()
                
                # working with FRONT self.suspensionName system:
                self.ar.utils.setProgress(doingName+frontSuspensionName)
                # create FRONT self.suspensionName module instance:
                front_suspension_guide = suspension.build_raw_guide()
                suspension.editGuideModuleName(frontSuspensionName)
                # setting X mirror:
                suspension.changeMirror("X")
                # editing front suspension base guide informations:
                cmds.setAttr(front_suspension_guide+".translateX", 6.5)
                cmds.setAttr(front_suspension_guide+".translateY", 4)
                cmds.setAttr(front_suspension_guide+".translateZ", 17)
                cmds.setAttr(front_suspension_guide+".rotateX", -100)
                cmds.setAttr(front_suspension_guide+".flip", 1)
                cmds.setAttr(suspension.radiusCtrl+".translateX", 0.6)
                cmds.setAttr(suspension.cvBLoc+".translateZ", 6.5)
                # edit fatherB attribut for frontSuspension module guide?
                cmds.setAttr(front_suspension_guide+".fatherB", chassis_guide, type='string')
                # parent front suspension guide to front wheel guide:
                cmds.parent(front_suspension_guide, front_wheel_guide, absolute=True)
                cmds.refresh()
                
                # working with BACK self.suspensionName system:
                self.ar.utils.setProgress(doingName+backSuspensionName)
                # create BACK self.suspensionName module instance:
                back_suspension_guide = suspension.build_raw_guide()
                suspension.editGuideModuleName(backSuspensionName)
                # setting X mirror:
                suspension.changeMirror("X")
                # editing back suspension base guide informations:
                cmds.setAttr(back_suspension_guide+".translateX", 6)
                cmds.setAttr(back_suspension_guide+".translateY", 4)
                cmds.setAttr(back_suspension_guide+".translateZ", -14)
                cmds.setAttr(back_suspension_guide+".rotateX", -85)
                cmds.setAttr(back_suspension_guide+".flip", 1)
                cmds.setAttr(suspension.radiusCtrl+".translateX", 0.6)
                cmds.setAttr(suspension.cvBLoc+".translateZ", 6.5)
                # edit fatherB attribut for frontSuspension module guide?
                cmds.setAttr(back_suspension_guide+".fatherB", chassis_guide, type='string')
                # parent front suspension guide to front wheel guide:
                cmds.parent(back_suspension_guide, back_wheel_guide, absolute=True)
                cmds.refresh()
                
                # working with FRONT DOOR system:
                self.ar.utils.setProgress(doingName+frontDoorName)
                # create fkLine module instance:
                front_door_guide = fkline.build_raw_guide()
                fkline.editGuideModuleName(frontDoorName)
                # setting X mirror:
                fkline.changeMirror("X")
                # editing front door base guide informations:
                cmds.setAttr(front_door_guide+".flip", 1)
                cmds.setAttr(front_door_guide+".translateX", 9.9)
                cmds.setAttr(front_door_guide+".translateY", 9.9)
                cmds.setAttr(front_door_guide+".translateZ", 10.7)
                cmds.setAttr(fkline.radiusCtrl+".translateX", 3)
                # parent front door guide to chassis guide:
                cmds.parent(front_door_guide, chassis_guide, absolute=True)
                cmds.refresh()
                
                # working with BACK DOOR system:
                self.ar.utils.setProgress(doingName+backDoorName)
                # create fkLine module instance:
                back_door_guide = fkline.build_raw_guide()
                fkline.editGuideModuleName(backDoorName)
                # setting X mirror:
                fkline.changeMirror("X")
                # editing back door base guide informations:
                cmds.setAttr(back_door_guide+".flip", 1)
                cmds.setAttr(back_door_guide+".translateX", 9.9)
                cmds.setAttr(back_door_guide+".translateY", 9.9)
                cmds.setAttr(back_door_guide+".translateZ", -1)
                cmds.setAttr(fkline.radiusCtrl+".translateX", 3)
                # parent back door guide to chassis guide:
                cmds.parent(back_door_guide, chassis_guide, absolute=True)
                cmds.refresh()
                
                #
                # complete part:
                #
                if userDetail == complete:
                
                    # working with HORN system:
                    self.ar.utils.setProgress(doingName+hornName)
                    # create fkLine module instance:
                    horn_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(hornName)
                    cmds.setAttr(horn_guide+".translateX", 4.5)
                    cmds.setAttr(horn_guide+".translateY", 12.3)
                    cmds.setAttr(horn_guide+".translateZ", 6.5)
                    cmds.setAttr(horn_guide+".rotateX", 28)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.7)
                    # parent horn guide to steering guide:
                    cmds.parent(horn_guide, steering.cvJointLoc, absolute=True)
                    cmds.refresh()
                    
                    # working with FRONT DOOR HANDLE system:
                    self.ar.utils.setProgress(doingName+frontDoorHandleName)
                    # create fkLine module instance:
                    front_door_handle_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(frontDoorHandleName)
                    # setting X mirror:
                    fkline.changeMirror("X")
                    # editing front door base guide informations:
                    cmds.setAttr(front_door_handle_guide+".flip", 1)
                    cmds.setAttr(front_door_handle_guide+".translateX", 10.4)
                    cmds.setAttr(front_door_handle_guide+".translateY", 11.2)
                    cmds.setAttr(front_door_handle_guide+".translateZ", 1.7)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.8)
                    # parent front door handle guide to front door guide:
                    cmds.parent(front_door_handle_guide, front_door_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with BACK DOOR HANDLE system:
                    self.ar.utils.setProgress(doingName+backDoorHandleName)
                    # create fkLine module instance:
                    back_door_handle_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(backDoorHandleName)
                    # setting X mirror:
                    fkline.changeMirror("X")
                    # editing back door handle base guide informations:
                    cmds.setAttr(back_door_handle_guide+".flip", 1)
                    cmds.setAttr(back_door_handle_guide+".translateX", 10.4)
                    cmds.setAttr(back_door_handle_guide+".translateY", 11.2)
                    cmds.setAttr(back_door_handle_guide+".translateZ", -9.5)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.8)
                    # parent back door handle guide to back door guide:
                    cmds.parent(back_door_handle_guide, back_door_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with FRONT WIPER A system:
                    self.ar.utils.setProgress(doingName+frontWiperAName)
                    # create fkLine module instance:
                    front_wiper_a_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(frontWiperAName)
                    # editing front wiper A base guide informations:
                    cmds.setAttr(front_wiper_a_guide+".translateX", 5.5)
                    cmds.setAttr(front_wiper_a_guide+".translateY", 13.7)
                    cmds.setAttr(front_wiper_a_guide+".translateZ", 12.7)
                    cmds.setAttr(front_wiper_a_guide+".rotateX", -63)
                    cmds.setAttr(front_wiper_a_guide+".rotateZ", -8.5)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.7)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(fkline.cvJointLoc+".translateX", -5.2)
                    cmds.setAttr(fkline.cvJointLoc+".translateY", 0.2)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", -0.4)
                    cmds.setAttr(fkline.cvJointLoc+".rotateY", -10.3)
                    # parent front wiper A guide to chassis guide:
                    cmds.parent(front_wiper_a_guide, chassis_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with FRONT WIPER B system:
                    self.ar.utils.setProgress(doingName+frontWiperBName)
                    # create fkLine module instance:
                    front_wiper_b_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(frontWiperBName)
                    # editing front wiper B base guide informations:
                    cmds.setAttr(front_wiper_b_guide+".translateX", 0.7)
                    cmds.setAttr(front_wiper_b_guide+".translateY", 13.7)
                    cmds.setAttr(front_wiper_b_guide+".translateZ", 13.5)
                    cmds.setAttr(front_wiper_b_guide+".rotateX", -62)
                    cmds.setAttr(front_wiper_b_guide+".rotateY", -10.3)
                    cmds.setAttr(front_wiper_b_guide+".rotateZ", -11.6)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.7)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(fkline.cvJointLoc+".translateX", -5.2)
                    cmds.setAttr(fkline.cvJointLoc+".translateY", 0.2)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", -0.4)
                    cmds.setAttr(fkline.cvJointLoc+".rotateY", -10.3)
                    # parent front wiper B guide to chassis guide:
                    cmds.parent(front_wiper_b_guide, chassis_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with TRUNK system:
                    self.ar.utils.setProgress(doingName+trunkName)
                    # create fkLine module instance:
                    trunk_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(trunkName)
                    # editing trunk base guide informations:
                    cmds.setAttr(trunk_guide+".translateY", 19.4)
                    cmds.setAttr(trunk_guide+".translateZ", -18.7)
                    cmds.setAttr(trunk_guide+".rotateX", -36)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 3.3)
                    # parent trunk guide to chassis guide:
                    cmds.parent(trunk_guide, chassis_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with BACK WIPER system:
                    self.ar.utils.setProgress(doingName+backWiperName)
                    # create fkLine module instance:
                    back_wiper_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(backWiperName)
                    # editing back wiper base guide informations:
                    cmds.setAttr(back_wiper_guide+".translateY", 14.8)
                    cmds.setAttr(back_wiper_guide+".translateZ", -24.7)
                    cmds.setAttr(back_wiper_guide+".rotateX", 34)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.7)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(fkline.cvJointLoc+".translateX", -2.7)
                    cmds.setAttr(fkline.cvJointLoc+".translateY", 0.4)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.1)
                    cmds.setAttr(fkline.cvJointLoc+".rotateZ", -7)
                    # parent back wiper guide to trunk guide:
                    cmds.parent(back_wiper_guide, trunk_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with GAS system:
                    self.ar.utils.setProgress(doingName+gasName)
                    # create fkLine module instance:
                    gas_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(gasName)
                    # editing gas base guide informations:
                    cmds.setAttr(gas_guide+".translateX", -10)
                    cmds.setAttr(gas_guide+".translateY", 13)
                    cmds.setAttr(gas_guide+".translateZ", -17)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.6)
                    # parent gas guide to chassis guide:
                    cmds.parent(gas_guide, chassis_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with HOOD system:
                    self.ar.utils.setProgress(doingName+hoodName)
                    # create fkLine module instance:
                    hood_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(hoodName)
                    # editing hood base guide informations:
                    cmds.setAttr(hood_guide+".translateY", 13.5)
                    cmds.setAttr(hood_guide+".translateZ", 12.5)
                    cmds.setAttr(hood_guide+".rotateX", 12.5)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 5)
                    # parent hood guide to chassis guide:
                    cmds.parent(hood_guide, chassis_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with SUN ROOF system:
                    self.ar.utils.setProgress(doingName+sunRoofName)
                    # create fkLine module instance:
                    sunroof_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(sunRoofName)
                    # editing sun roof base guide informations:
                    cmds.setAttr(sunroof_guide+".translateY", 19)
                    cmds.setAttr(sunroof_guide+".translateZ", -2.5)
                    # parent sun roof guide to chassis guide:
                    cmds.parent(sunroof_guide, chassis_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with ANTENNA system:
                    self.ar.utils.setProgress(doingName+antennaName)
                    # create fkLine module instance:
                    antenna_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(antennaName)
                    # editing antenna base guide informations:
                    cmds.setAttr(antenna_guide+".translateY", 18.8)
                    cmds.setAttr(antenna_guide+".translateZ", 3.7)
                    cmds.setAttr(antenna_guide+".rotateX", -136)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.5)
                    fkline.changeJointNumber(3)
                    # parent antenna guide to chassis guide:
                    cmds.parent(antenna_guide, chassis_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with LEFT TURN HANDLE system:
                    self.ar.utils.setProgress(doingName+leftTurnHandleName)
                    # create fkLine module instance:
                    lef_turn_handle_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(leftTurnHandleName)
                    # editing left turn handle base guide informations:
                    cmds.setAttr(lef_turn_handle_guide+".translateX", 5.5)
                    cmds.setAttr(lef_turn_handle_guide+".translateY", 11.5)
                    cmds.setAttr(lef_turn_handle_guide+".translateZ", 7.3)
                    cmds.setAttr(lef_turn_handle_guide+".rotateX", 28)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 1.1)
                    # parent left turn handle guide to steering handle guide:
                    cmds.parent(lef_turn_handle_guide, steering_handle_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with RIGHT TURN HANDLE system:
                    self.ar.utils.setProgress(doingName+rightTurnHandleName)
                    # create fkLine module instance:
                    right_turn_handle_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(rightTurnHandleName)
                    # editing right turn handle base guide informations:
                    cmds.setAttr(right_turn_handle_guide+".translateX", 3.4)
                    cmds.setAttr(right_turn_handle_guide+".translateY", 11.5)
                    cmds.setAttr(right_turn_handle_guide+".translateZ", 7.3)
                    cmds.setAttr(right_turn_handle_guide+".rotateX", 28)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 1.1)
                    # parent left turn handle guide to steering handle guide:
                    cmds.parent(right_turn_handle_guide, steering_handle_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with GEAR LEVER system:
                    self.ar.utils.setProgress(doingName+gearLeverName)
                    # create fkLine module instance:
                    gear_lever_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(gearLeverName)
                    # editing gear lever base guide informations:
                    cmds.setAttr(gear_lever_guide+".translateY", 7.5)
                    cmds.setAttr(gear_lever_guide+".translateZ", 7.9)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 1.7)
                    # parent gear lever guide to chassis guide:
                    cmds.parent(gear_lever_guide, chassis_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with HAND BREAK system:
                    self.ar.utils.setProgress(doingName+handBreakName)
                    # create fkLine module instance:
                    hand_break_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(handBreakName)
                    # editing hand break base guide informations:
                    cmds.setAttr(hand_break_guide+".translateY", 7.9)
                    cmds.setAttr(hand_break_guide+".translateZ", 2.3)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 1)
                    # parent hand break guide to chassis guide:
                    cmds.parent(hand_break_guide, chassis_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with BREAK system:
                    self.ar.utils.setProgress(doingName+breakName)
                    # create fkLine module instance:
                    break_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(breakName)
                    # editing break base guide informations:
                    cmds.setAttr(break_guide+".translateX", 4.3)
                    cmds.setAttr(break_guide+".translateY", 7.3)
                    cmds.setAttr(break_guide+".translateZ", 13)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 1)
                    # parent break guide to chassis guide:
                    cmds.parent(break_guide, chassis_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with ACCELERATOR system:
                    self.ar.utils.setProgress(doingName+acceleratorName)
                    # create fkLine module instance:
                    accelerator_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(acceleratorName)
                    # editing accelerator base guide informations:
                    cmds.setAttr(accelerator_guide+".translateX", 3.2)
                    cmds.setAttr(accelerator_guide+".translateY", 7.3)
                    cmds.setAttr(accelerator_guide+".translateZ", 13)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 1)
                    # parent accelerator guide to chassis guide:
                    cmds.parent(accelerator_guide, chassis_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with CLUTCH system:
                    self.ar.utils.setProgress(doingName+clutchName)
                    # create fkLine module instance:
                    clutch_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(clutchName)
                    # editing clutch base guide informations:
                    cmds.setAttr(clutch_guide+".translateX", 5.4)
                    cmds.setAttr(clutch_guide+".translateY", 7.3)
                    cmds.setAttr(clutch_guide+".translateZ", 13)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 1)
                    # parent clutch guide to chassis guide:
                    cmds.parent(clutch_guide, chassis_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with DASHBOARD A system:
                    self.ar.utils.setProgress(doingName+dashboardAName)
                    # create fkLine module instance:
                    dashboard_a_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(dashboardAName)
                    # editing dashboard A base guide informations:
                    cmds.setAttr(dashboard_a_guide+".translateX", 5.2)
                    cmds.setAttr(dashboard_a_guide+".translateY", 12.8)
                    cmds.setAttr(dashboard_a_guide+".translateZ", 10.9)
                    cmds.setAttr(dashboard_a_guide+".rotateX", 22.5)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.4)
                    # parent dashboard A guide to chassis guide:
                    cmds.parent(dashboard_a_guide, chassis_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with DASHBOARD B system:
                    self.ar.utils.setProgress(doingName+dashboardBName)
                    # create fkLine module instance:
                    dashboard_b_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(dashboardBName)
                    # editing dashboard B base guide informations:
                    cmds.setAttr(dashboard_b_guide+".translateX", 3.7)
                    cmds.setAttr(dashboard_b_guide+".translateY", 12.8)
                    cmds.setAttr(dashboard_b_guide+".translateZ", 10.9)
                    cmds.setAttr(dashboard_b_guide+".rotateX", 22.5)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.4)
                    # parent dashboard B guide to chassis guide:
                    cmds.parent(dashboard_b_guide, chassis_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with FRONT SEAT system:
                    self.ar.utils.setProgress(doingName+frontSeatName)
                    # create fkLine module instance:
                    front_seat_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(frontSeatName)
                    # setting X mirror:
                    fkline.changeMirror("X")
                    # editing front seat base guide informations:
                    cmds.setAttr(front_seat_guide+".flip", 1)
                    cmds.setAttr(front_seat_guide+".translateX", 5.2)
                    cmds.setAttr(front_seat_guide+".translateY", 7.7)
                    cmds.setAttr(front_seat_guide+".translateZ", 2.8)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 2.5)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(fkline.cvJointLoc+".translateY", 0.6)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", -1.9)
                    fkline.changeJointNumber(3)
                    cmds.setAttr(fkline.cvJointLoc+".translateY", 6.5)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", -2.7)
                    # parent front seat guide to chassis guide:
                    cmds.parent(front_seat_guide, chassis_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with BACK SEAT system:
                    self.ar.utils.setProgress(doingName+backSeatName)
                    # create fkLine module instance:
                    back_seat_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(backSeatName)
                    # editing back seat base guide informations:
                    cmds.setAttr(back_seat_guide+".translateY", 7.7)
                    cmds.setAttr(back_seat_guide+".translateZ", -6)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 3.5)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(fkline.cvJointLoc+".translateY", 0.6)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", -1.9)
                    # parent back seat guide to chassis guide:
                    cmds.parent(back_seat_guide, chassis_guide, absolute=True)
                    
                    # working with FRONT DOOR INSIDE HANDLE system:
                    self.ar.utils.setProgress(doingName+frontDoorInsideHandleName)
                    # create fkLine module instance:
                    front_door_inside_handle_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(frontDoorInsideHandleName)
                    # setting X mirror:
                    fkline.changeMirror("X")
                    # editing front door inside handle base guide informations:
                    cmds.setAttr(front_door_inside_handle_guide+".flip", 1)
                    cmds.setAttr(front_door_inside_handle_guide+".translateX", 9.1)
                    cmds.setAttr(front_door_inside_handle_guide+".translateY", 11.4)
                    cmds.setAttr(front_door_inside_handle_guide+".translateZ", 6.3)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.6)
                    # parent front door inside handle guide to front door guide:
                    cmds.parent(front_door_inside_handle_guide, front_door_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with BACK DOOR INSIDE HANDLE system:
                    self.ar.utils.setProgress(doingName+backDoorInsideHandleName)
                    # create fkLine module instance:
                    back_door_inside_handle_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(backDoorInsideHandleName)
                    # setting X mirror:
                    fkline.changeMirror("X")
                    # editing back door inside handle base guide informations:
                    cmds.setAttr(back_door_inside_handle_guide+".flip", 1)
                    cmds.setAttr(back_door_inside_handle_guide+".translateX", 8.8)
                    cmds.setAttr(back_door_inside_handle_guide+".translateY", 11.4)
                    cmds.setAttr(back_door_inside_handle_guide+".translateZ", -3.6)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.6)
                    # parent back door inside handle guide to back door guide:
                    cmds.parent(back_door_inside_handle_guide, back_door_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with FRONT DOOR WINDOW system:
                    self.ar.utils.setProgress(doingName+frontDoorWindowName)
                    # create fkLine module instance:
                    front_door_window_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(frontDoorWindowName)
                    # setting X mirror:
                    fkline.changeMirror("X")
                    # editing front door window base guide informations:
                    cmds.setAttr(front_door_window_guide+".flip", 1)
                    cmds.setAttr(front_door_window_guide+".translateX", 9.5)
                    cmds.setAttr(front_door_window_guide+".translateY", 13)
                    cmds.setAttr(front_door_window_guide+".translateZ", 2.9)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.8)
                    # parent front door window guide to front door guide:
                    cmds.parent(front_door_window_guide, front_door_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with BACK DOOR WINDOW system:
                    self.ar.utils.setProgress(doingName+backDoorWindowName)
                    # create fkLine module instance:
                    back_door_window_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(backDoorWindowName)
                    # setting X mirror:
                    fkline.changeMirror("X")
                    # editing back door window base guide informations:
                    cmds.setAttr(back_door_window_guide+".flip", 1)
                    cmds.setAttr(back_door_window_guide+".translateX", 9.5)
                    cmds.setAttr(back_door_window_guide+".translateY", 13.5)
                    cmds.setAttr(back_door_window_guide+".translateZ", -7.1)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.8)
                    # parent back door window guide to back door guide:
                    cmds.parent(back_door_window_guide, back_door_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with MIRROR system:
                    self.ar.utils.setProgress(doingName+mirrorName)
                    # create fkLine module instance:
                    mirror_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(mirrorName)
                    # setting X mirror:
                    fkline.changeMirror("X")
                    # editing mirror base guide informations:
                    cmds.setAttr(mirror_guide+".flip", 1)
                    cmds.setAttr(mirror_guide+".translateX", 9.8)
                    cmds.setAttr(mirror_guide+".translateY", 13.1)
                    cmds.setAttr(mirror_guide+".translateZ", 8.7)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 1.1)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(fkline.cvJointLoc+".translateY", 0.8)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 1)
                    # parent mirror guide to front door guide:
                    cmds.parent(mirror_guide, front_door_guide, absolute=True)
                    cmds.refresh()
                    
                    # working with INSIDE MIRROR system:
                    self.ar.utils.setProgress(doingName+insideMirrorName)
                    # create fkLine module instance:
                    inside_mirror_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(insideMirrorName)
                    # editing inside mirror base guide informations:
                    cmds.setAttr(inside_mirror_guide+".translateY", 18)
                    cmds.setAttr(inside_mirror_guide+".translateZ", 3.5)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 1.5)
                    # parent mirror guide to front door guide:
                    cmds.parent(inside_mirror_guide, chassis_guide, absolute=True)
                
                # Close progress window
                self.ar.utils.setProgress(endIt=True)
                
                # select spineGuide_Base:
                self.ar.collapseEditSelModFL = False
                cmds.select(chassis_guide)
                print(self.ar.data.lang['m167_createdCar'])
        else:
            # error checking modules in the folder:
            mel.eval('error \"'+ self.ar.data.lang['e001_guideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
