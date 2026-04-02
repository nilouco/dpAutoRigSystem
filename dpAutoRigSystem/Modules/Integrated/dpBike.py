# importing libraries:
from maya import cmds
from maya import mel
from ..Base import dpBaseLibrary
from importlib import reload

# global variables to this module:    
CLASS_NAME = "Bike"
TITLE = "m165_bike"
DESCRIPTION = "m166_bikeDesc"
ICON = "/Icons/dp_bike.png"
WIKI = "03-‐-Guides#-bike"

DP_BIKE_VERSION = 2.03


class Bike(dpBaseLibrary.BaseLibrary):
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
        """ This function will create all guides needed to compose a bike.
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
            forkName = self.ar.data.lang['m229_fork']
            handlebarName = self.ar.data.lang['m228_handlebar']
            hornName = self.ar.data.lang['c081_horn']
            frontWheelName = self.ar.data.lang['c056_front']+self.ar.data.lang['m156_wheel']
            backWheelName = self.ar.data.lang['c057_back']+self.ar.data.lang['m156_wheel']
            frontSuspensionName = self.ar.data.lang['c056_front']+self.ar.data.lang['m153_suspension']
            backSuspensionName = self.ar.data.lang['c057_back']+self.ar.data.lang['m153_suspension']
            seatName = self.ar.data.lang['c088_seat']
            mirrorName = self.ar.data.lang['m010_mirror']
            pedalName = self.ar.data.lang['c089_pedal']
            leftPedalName = self.ar.data.lang['p002_left']+"_"+self.ar.data.lang['c089_pedal']
            rightPedalName = self.ar.data.lang['p003_right']+"_"+self.ar.data.lang['c089_pedal']
            leverName = self.ar.data.lang['c090_lever']
            frontBasketName = self.ar.data.lang['c056_front']+self.ar.data.lang['c094_basket']
            backBasketName = self.ar.data.lang['c057_back']+self.ar.data.lang['c094_basket']
            simple   = self.ar.data.lang['i175_simple']
            complete = self.ar.data.lang['i176_complete']
            cancel   = self.ar.data.lang['i132_cancel']
            userMessage = self.ar.data.lang['i177_chooseMessage']
            bikeGuideName = self.ar.data.lang['m165_bike']+" "+self.ar.data.lang['i205_guide']
            
            # getting Simple or Complete module guides to create:
            userDetail = self.ask_build_detail(self.title, simple, complete, cancel, simple, userMessage)
            if not userDetail == cancel:
                # number of modules to create:
                if userDetail == simple:
                    maxProcess = 9
                else:
                    maxProcess = 16
                
                # Starting progress window
                self.ar.utils.setProgress(doingName, bikeGuideName, maxProcess, addOne=False, addNumber=False)
                self.ar.utils.setProgress(doingName+chassisName)
                
                # getting module instances:
                fkline = self.ar.config.get_instance("dpFkLine", [guideDir])
                wheel = self.ar.config.get_instance("dpWheel", [guideDir])
                steering = self.ar.config.get_instance("dpSteering", [guideDir])
                suspension = self.ar.config.get_instance("dpSuspension", [guideDir])

                # woking with CHASSIS system:
                # create fkLine module instance:
                chassis_guide = fkline.build_raw_guide()
                # editing chassis base guide informations:
                fkline.editGuideModuleName(chassisName)
                cmds.setAttr(chassis_guide+".translateY", 9)
                cmds.setAttr(fkline.radiusCtrl+".translateX", 8)
                cmds.refresh()
                
                # woking with HANDLEBAR system:
                self.ar.utils.setProgress(doingName+handlebarName)
                # create Handlebar instance:
                handlebar_guide = fkline.build_raw_guide()
                # editing Handlebar base guide informations:
                fkline.editGuideModuleName(handlebarName)
                handlebar_cv_joint_loc = fkline.cvJointLoc
                cmds.setAttr(handlebar_guide+".translateY", 13.4)
                cmds.setAttr(handlebar_guide+".translateZ", 4.7)
                cmds.setAttr(handlebar_guide+".rotateX", 71)
                cmds.setAttr(fkline.annotation+".translateY", 2)
                # parent Handlebar guide to Chassis guide:
                cmds.parent(handlebar_guide, chassis_guide, absolute=True)
                cmds.refresh()

                # woking with FORK system:
                self.ar.utils.setProgress(doingName+forkName)
                # create fkLine module instance:
                fork_guide = fkline.build_raw_guide()
                # editing fkLine base guide informations:
                fkline.editGuideModuleName(forkName)
                cmds.setAttr(fork_guide+".translateY", 10.7)
                cmds.setAttr(fork_guide+".translateZ", 6)
                cmds.setAttr(fork_guide+".rotateX", -19)
                cmds.setAttr(fkline.radiusCtrl+".translateX", 1.1)
                # parent fork guide to Handlebar guide:
                cmds.parent(fork_guide, handlebar_guide, absolute=True)
                cmds.refresh()
                
                # working with PEDAL self.wheelName system:
                self.ar.utils.setProgress(doingName+pedalName)
                # create pedal wheel module instance:
                pedal_guide = wheel.build_raw_guide()
                wheel.editGuideModuleName(pedalName)
                pedal_cv_center_loc = wheel.cvCenterLoc
                # editing pedal wheel base guide informations:
                cmds.setAttr(pedal_guide+".translateY", 4.5)
                cmds.setAttr(pedal_guide+".translateZ", -0.8)
                cmds.setAttr(pedal_guide+".rotateY", -90)
                cmds.setAttr(wheel.radiusCtrl+".translateX", 1.5)
                cmds.setAttr(pedal_guide+".steering", 0)
                # parent pedal wheel guide to chassis guide:
                cmds.parent(pedal_guide, chassis_guide, absolute=True)
                cmds.refresh()
                
                # working with LEFT PEDAL system:
                self.ar.utils.setProgress(doingName+leftPedalName)
                # create pedal fkLine module instance:
                left_pedal_guide = fkline.build_raw_guide()
                fkline.editGuideModuleName(leftPedalName)        
                # editing left pedal base guide informations:
                cmds.setAttr(left_pedal_guide+".translateX", 1.3)
                cmds.setAttr(left_pedal_guide+".translateY", 2.6)
                cmds.setAttr(left_pedal_guide+".translateZ", -2.1)
                cmds.setAttr(fkline.radiusCtrl+".translateX", 0.8)
                # parent left pedal guide to pedal base guide:
                cmds.parent(left_pedal_guide, pedal_cv_center_loc, absolute=True)
                cmds.refresh()
                
                # working with RIGHT PEDAL system:
                self.ar.utils.setProgress(doingName+rightPedalName)
                # create pedal fkLine module instance:
                right_pedal_guide = fkline.build_raw_guide()
                fkline.editGuideModuleName(rightPedalName)
                # editing right pedal base guide informations:
                cmds.setAttr(right_pedal_guide+".translateX", -1.3)
                cmds.setAttr(right_pedal_guide+".translateY", 6.3)
                cmds.setAttr(right_pedal_guide+".translateZ", 0.3)
                cmds.setAttr(fkline.radiusCtrl+".translateX", 0.8)
                # parent right pedal guide to pedal base guide:
                cmds.parent(right_pedal_guide, pedal_cv_center_loc, absolute=True)
                cmds.refresh()
                
                # working with FRONT self.wheelName system:
                self.ar.utils.setProgress(doingName+frontWheelName)
                # create wheel module instance:
                front_wheel_guide = wheel.build_raw_guide()
                wheel.editGuideModuleName(frontWheelName)        
                # editing frontWheel base guide informations:
                cmds.setAttr(front_wheel_guide+".translateY", 4.7)
                cmds.setAttr(front_wheel_guide+".translateZ", 8.4)
                cmds.setAttr(front_wheel_guide+".rotateY", -90)
                cmds.setAttr(wheel.radiusCtrl+".translateX", 4.7)
                cmds.setAttr(front_wheel_guide+".steering", 0)
                # edit location of inside and outiside guide:
                cmds.setAttr(wheel.cvInsideLoc+".translateZ", 0.35)
                cmds.setAttr(wheel.cvOutsideLoc+".translateZ", -0.35)
                # parent front wheel guide to fork guide:
                cmds.parent(front_wheel_guide, fork_guide, absolute=True)
                cmds.refresh()
                
                # working with BACK self.wheelName system:
                self.ar.utils.setProgress(doingName+backWheelName)
                # create wheel module instance:
                back_wheel_guide = wheel.build_raw_guide()
                wheel.editGuideModuleName(backWheelName)        
                # editing frontWheel base guide informations:
                cmds.setAttr(back_wheel_guide+".translateY", 4.7)
                cmds.setAttr(back_wheel_guide+".translateZ", -7.8)
                cmds.setAttr(back_wheel_guide+".rotateY", -90)
                cmds.setAttr(wheel.radiusCtrl+".translateX", 4.7)
                cmds.setAttr(back_wheel_guide+".steering", 0)
                # edit location of inside and outiside guide:
                cmds.setAttr(wheel.cvInsideLoc+".translateZ", 0.35)
                cmds.setAttr(wheel.cvOutsideLoc+".translateZ", -0.35)
                # parent back wheel guide to chassis guide:
                cmds.parent(back_wheel_guide, chassis_guide, absolute=True)
                cmds.refresh()
                
                # woking with SEAT system:
                self.ar.utils.setProgress(doingName+seatName)
                # create fkLine module instance:
                front_seat_guide = fkline.build_raw_guide()
                fkline.editGuideModuleName(seatName)
                # editing seat base guide informations:
                cmds.setAttr(front_seat_guide+".translateY", 10)
                cmds.setAttr(front_seat_guide+".translateZ", -4)
                cmds.setAttr(front_seat_guide+".rotateX", -38)
                fkline.changeJointNumber(2)
                cmds.setAttr(fkline.cvJointLoc+".translateY", 0.9)
                cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.8)
                cmds.setAttr(fkline.cvJointLoc+".rotateX", 38)
                # parent front seat guide to chassis guide:
                cmds.parent(front_seat_guide, chassis_guide, absolute=True)
                cmds.refresh()
                
                #
                # complete part:
                #
                if userDetail == complete:
                
                    # woking with HORN system:
                    self.ar.utils.setProgress(doingName+hornName)
                    # create fkLine module instance:
                    horn_guide = fkline.build_raw_guide()
                    # editing eyeLookAt base guide informations:
                    fkline.editGuideModuleName(hornName)
                    cmds.setAttr(horn_guide+".translateX", -1.64)
                    cmds.setAttr(horn_guide+".translateY", 13.3)
                    cmds.setAttr(horn_guide+".translateZ", 4.5)
                    cmds.setAttr(horn_guide+".rotateX", 17)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.7)
                    # parent horn guide to Handlebar guide:
                    cmds.parent(horn_guide, handlebar_cv_joint_loc, absolute=True)
                    cmds.refresh()
                    
                    # create FRONT self.suspensionName module instance:
                    self.ar.utils.setProgress(doingName+frontSuspensionName)
                    front_suspension_guide = suspension.build_raw_guide()
                    suspension.editGuideModuleName(frontSuspensionName)
                    # editing frontSuspension base guide informations:
                    cmds.setAttr(front_suspension_guide+".translateY", 7)
                    cmds.setAttr(front_suspension_guide+".translateZ", 7)
                    cmds.setAttr(front_suspension_guide+".rotateX", -110)
                    cmds.setAttr(suspension.radiusCtrl+".translateX", 0.7)
                    # edit fatherB attribut for frontSuspension module guide?
                    cmds.setAttr(front_suspension_guide+".fatherB", fork_guide, type='string')
                    # parent front suspension guide to front wheel guide:
                    cmds.parent(front_suspension_guide, front_wheel_guide, absolute=True)
                    cmds.refresh()
                    
                    # create BACK self.suspensionName module instance:
                    self.ar.utils.setProgress(doingName+backSuspensionName)
                    back_suspension_guide = suspension.build_raw_guide()
                    suspension.editGuideModuleName(backSuspensionName)
                    # editing back suspension base guide informations:
                    cmds.setAttr(back_suspension_guide+".translateY", 7)
                    cmds.setAttr(back_suspension_guide+".translateZ", -6.6)
                    cmds.setAttr(back_suspension_guide+".rotateX", -43)
                    cmds.setAttr(suspension.radiusCtrl+".translateX", 0.7)
                    # edit fatherB attribut for frontSuspension module guide?
                    cmds.setAttr(back_suspension_guide+".fatherB", chassis_guide, type='string')
                    # parent front suspension guide to front wheel guide:
                    cmds.parent(back_suspension_guide, back_wheel_guide, absolute=True)
                    cmds.refresh()
                    
                    # woking with MIRROR system:
                    self.ar.utils.setProgress(doingName+mirrorName)
                    # create fkLine module instance:
                    mirror_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(mirrorName)
                    # editing mirror_guide base guide informations:
                    cmds.setAttr(mirror_guide+".translateX", 3.4)
                    cmds.setAttr(mirror_guide+".translateY", 15)
                    cmds.setAttr(mirror_guide+".translateZ", 4.1)
                    cmds.setAttr(mirror_guide+".rotateX", -68)
                    cmds.setAttr(mirror_guide+".rotateY", 8)
                    cmds.setAttr(mirror_guide+".rotateZ", -10)
                    cmds.setAttr(fkline.radiusCtrl+".translateX",0.7)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(fkline.cvJointLoc+".translateY", 0)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 1.1)
                    fkline.changeJointNumber(3)
                    cmds.setAttr(fkline.cvJointLoc+".translateX", 1.2)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.5)
                    # parent mirror guide to Handlebar guide:
                    cmds.parent(mirror_guide, handlebar_cv_joint_loc, absolute=True)
                    cmds.refresh()
                    
                    # working with LEVER system:
                    self.ar.utils.setProgress(doingName+leverName)
                    # create fkLine module instance:
                    lever_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(leverName)
                    # setting X mirror:
                    fkline.changeMirror("X")
                    # editing lever base guide informations:
                    cmds.setAttr(lever_guide+".flip", 1)
                    cmds.setAttr(lever_guide+".translateX", 4.1)
                    cmds.setAttr(lever_guide+".translateY", 15)
                    cmds.setAttr(lever_guide+".translateZ", 4)
                    cmds.setAttr(lever_guide+".rotateY", 10)
                    cmds.setAttr(fkline.radiusCtrl+".translateX",0.8)
                    # parent lever guide to Handlebar guide:
                    cmds.parent(lever_guide, handlebar_cv_joint_loc, absolute=True)
                    cmds.refresh()
                    
                    # woking with FRONT BASKET system:
                    self.ar.utils.setProgress(doingName+frontBasketName)
                    # create fkLine module instance:
                    front_basket_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(frontBasketName)
                    # editing front basket base guide informations:
                    cmds.setAttr(front_basket_guide+".translateY", 10)
                    cmds.setAttr(front_basket_guide+".translateZ", 9)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(fkline.cvJointLoc+".translateY", 0.8)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0)
                    # parent front basket guide to front wheel guide:
                    cmds.parent(front_basket_guide, front_wheel_guide, absolute=True)
                    cmds.refresh()
                    
                    # woking with BACK BASKET system:
                    self.ar.utils.setProgress(doingName+backBasketName)
                    # create fkLine module instance:
                    back_basket_guide = fkline.build_raw_guide()
                    fkline.editGuideModuleName(backBasketName)
                    # editing back basket base guide informations:
                    cmds.setAttr(back_basket_guide+".translateY", 10)
                    cmds.setAttr(back_basket_guide+".translateZ", -8)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(fkline.cvJointLoc+".translateY", 0.8)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0)
                    
                    # parent back basket guide to chassis guide:
                    cmds.parent(back_basket_guide, chassis_guide, absolute=True)
                
                # Close progress window
                self.ar.utils.setProgress(endIt=True)
                
                # select spineGuide_Base:
                self.ar.collapseEditSelModFL = False
                cmds.select(chassis_guide)
                print(self.ar.data.lang['m168_createdBike'])
        else:
            # error checking modules in the folder:
            mel.eval('error \"'+ self.ar.data.lang['e001_guideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
