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
        # dependence module list:
        self.check_modules = ['dpFkLine', 'dpWheel', 'dpSteering', 'dpSuspension']


    def build_template(self, *args):
        """ This function will create all guides needed to compose a bike.
        """
        # check modules integrity:
        missing_modules = self.ar.ui_manager.check_missing_modules(self.ar.data.standard_folder, self.check_modules)
        if not missing_modules:
            self.ar.data.collapse_edit_sel_mod = True
            
            # TODO remove doingName
            doingName = self.ar.data.lang['m094_doing']
            
            # defining naming:
            chassis = self.ar.data.lang['c091_chassis']
            fork = self.ar.data.lang['m229_fork']
            handlebar = self.ar.data.lang['m228_handlebar']
            horn = self.ar.data.lang['c081_horn']
            front_wheel = self.ar.data.lang['c056_front']+self.ar.data.lang['m156_wheel']
            back_wheel = self.ar.data.lang['c057_back']+self.ar.data.lang['m156_wheel']
            front_suspension = self.ar.data.lang['c056_front']+self.ar.data.lang['m153_suspension']
            back_suspension = self.ar.data.lang['c057_back']+self.ar.data.lang['m153_suspension']
            seat = self.ar.data.lang['c088_seat']
            mirror = self.ar.data.lang['m010_mirror']
            pedal = self.ar.data.lang['c089_pedal']
            left_pedal = self.ar.data.lang['p002_left']+"_"+self.ar.data.lang['c089_pedal']
            right_pedal = self.ar.data.lang['p003_right']+"_"+self.ar.data.lang['c089_pedal']
            lever = self.ar.data.lang['c090_lever']
            front_basket = self.ar.data.lang['c056_front']+self.ar.data.lang['c094_basket']
            back_basket = self.ar.data.lang['c057_back']+self.ar.data.lang['c094_basket']
            simple = self.ar.data.lang['i175_simple']
            complete = self.ar.data.lang['i176_complete']
            cancel = self.ar.data.lang['i132_cancel']
            user_message = self.ar.data.lang['i177_chooseMessage']
            bike_guide_name = self.ar.data.lang['m165_bike']+" "+self.ar.data.lang['i205_guide']
            
            # getting Simple or Complete module guides to create:
            user_choice = self.ask_build_detail(self.title, simple, complete, cancel, simple, user_message)
            if not user_choice == cancel:
                # number of modules to create:
                maxProcess = 16
                if user_choice == simple:
                    maxProcess = 9
                
                # Starting progress window
                self.ar.utils.setProgress(self.ar.data.lang['m094_doing'], bike_guide_name, maxProcess, addOne=False, addNumber=False)
            
            
                
                # create guides:
                fkline, chassis_guide = self.ar.maker.set_new_guide("dpFkLine", chassis, t=(0, 9, 0), radius=8)
 
                # editing chassis base guide informations:
#                fkline.editGuideModuleName(chassis)
#                cmds.setAttr(chassis_guide+".translateY", 9)
#                cmds.setAttr(fkline.radiusCtrl+".translateX", 8)
#                cmds.refresh()
                
                # woking with HANDLEBAR system:
            #    self.ar.utils.setProgress(doingName+handlebar)
                # create Handlebar instance:
 
                fkline, handlebar_guide = self.ar.maker.set_new_guide("dpFkLine", handlebar, t=(0, 13.4, 4.7), r=(71, 0, 0), parent=chassis_guide)

#                handlebar_cv_joint_loc = fkline.cvJointLoc
#                cmds.setAttr(fkline.annotation+".translateY", 2)
#                cmds.parent(handlebar_guide, chassis_guide, absolute=True)
 
#                 # editing Handlebar base guide informations:
# #                fkline.editGuideModuleName(handlebar)
#                 cmds.setAttr(handlebar_guide+".translateY", 13.4)
#                 cmds.setAttr(handlebar_guide+".translateZ", 4.7)
#                 cmds.setAttr(handlebar_guide+".rotateX", 71)
#                 # parent Handlebar guide to Chassis guide:
#                 cmds.refresh()

                # woking with FORK system:
            #    self.ar.utils.setProgress(doingName+fork)
                # create fkLine module instance:

                fkline, fork_guide = self.ar.maker.set_new_guide("dpFkLine", fork, t=(0, 10.7, 6), r=(-19, 0, 0), radius=1.1, parent=handlebar_guide)
                
#                # editing fkLine base guide informations:
#                fkline.editGuideModuleName(fork)
#                cmds.setAttr(fork_guide+".translateY", 10.7)
#                cmds.setAttr(fork_guide+".translateZ", 6)
#                cmds.setAttr(fork_guide+".rotateX", -19)
#                cmds.setAttr(fkline.radiusCtrl+".translateX", 1.1)
#                # parent fork guide to Handlebar guide:
#                cmds.parent(fork_guide, handlebar_guide, absolute=True)
#                cmds.refresh()
                
                # working with PEDAL self.wheelName system:
            #    self.ar.utils.setProgress(doingName+pedal)
                # create pedal wheel module instance:
                wheel, pedal_guide = wheel.build_raw_guide()
                wheel.editGuideModuleName(pedal)
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
            #    self.ar.utils.setProgress(doingName+left_pedal)
                # create pedal fkLine module instance:
                fkline, left_pedal_guide = self.ar.maker.set_new_guide("dpFkLine")
                fkline.editGuideModuleName(left_pedal)        
                # editing left pedal base guide informations:
                cmds.setAttr(left_pedal_guide+".translateX", 1.3)
                cmds.setAttr(left_pedal_guide+".translateY", 2.6)
                cmds.setAttr(left_pedal_guide+".translateZ", -2.1)
                cmds.setAttr(fkline.radiusCtrl+".translateX", 0.8)
                # parent left pedal guide to pedal base guide:
                cmds.parent(left_pedal_guide, pedal_cv_center_loc, absolute=True)
                cmds.refresh()
                
                # working with RIGHT PEDAL system:
            #    self.ar.utils.setProgress(doingName+right_pedal)
                # create pedal fkLine module instance:
                fkline, right_pedal_guide = self.ar.maker.set_new_guide("dpFkLine")
                fkline.editGuideModuleName(right_pedal)
                # editing right pedal base guide informations:
                cmds.setAttr(right_pedal_guide+".translateX", -1.3)
                cmds.setAttr(right_pedal_guide+".translateY", 6.3)
                cmds.setAttr(right_pedal_guide+".translateZ", 0.3)
                cmds.setAttr(fkline.radiusCtrl+".translateX", 0.8)
                # parent right pedal guide to pedal base guide:
                cmds.parent(right_pedal_guide, pedal_cv_center_loc, absolute=True)
                cmds.refresh()
                
                # working with FRONT self.wheelName system:
            #    self.ar.utils.setProgress(doingName+front_wheel)
                # create wheel module instance:
                wheel, front_wheel_guide = wheel.build_raw_guide()
                wheel.editGuideModuleName(front_wheel)        
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
            #    self.ar.utils.setProgress(doingName+back_wheel)
                # create wheel module instance:
                wheel, back_wheel_guide = wheel.build_raw_guide()
                wheel.editGuideModuleName(back_wheel)        
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
            #    self.ar.utils.setProgress(doingName+seat)
                # create fkLine module instance:
                fkline, front_seat_guide = self.ar.maker.set_new_guide("dpFkLine")
                fkline.editGuideModuleName(seat)
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
                if user_choice == complete:
                
                    # woking with HORN system:
                #    self.ar.utils.setProgress(doingName+horn)
                    # create fkLine module instance:
                    fkline, horn_guide = self.ar.maker.set_new_guide("dpFkLine")
                    # editing eyeLookAt base guide informations:
                    fkline.editGuideModuleName(horn)
                    cmds.setAttr(horn_guide+".translateX", -1.64)
                    cmds.setAttr(horn_guide+".translateY", 13.3)
                    cmds.setAttr(horn_guide+".translateZ", 4.5)
                    cmds.setAttr(horn_guide+".rotateX", 17)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.7)
                    # parent horn guide to Handlebar guide:
                    cmds.parent(horn_guide, handlebar_cv_joint_loc, absolute=True)
                    cmds.refresh()
                    
                    # create FRONT self.suspensionName module instance:
                #    self.ar.utils.setProgress(doingName+front_suspension)
                    suspension, front_suspension_guide = suspension.build_raw_guide()
                    suspension.editGuideModuleName(front_suspension)
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
                #    self.ar.utils.setProgress(doingName+back_suspension)
                    suspension, back_suspension_guide = suspension.build_raw_guide()
                    suspension.editGuideModuleName(back_suspension)
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
                #    self.ar.utils.setProgress(doingName+mirror)
                    # create fkLine module instance:
                    fkline, mirror_guide = self.ar.maker.set_new_guide("dpFkLine")
                    fkline.editGuideModuleName(mirror)
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
                #    self.ar.utils.setProgress(doingName+lever)
                    # create fkLine module instance:
                    fkline, lever_guide = self.ar.maker.set_new_guide("dpFkLine")
                    fkline.editGuideModuleName(lever)
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
                #    self.ar.utils.setProgress(doingName+front_basket)
                    # create fkLine module instance:
                    fkline, front_basket_guide = self.ar.maker.set_new_guide("dpFkLine")
                    fkline.editGuideModuleName(front_basket)
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
                #    self.ar.utils.setProgress(doingName+back_basket)
                    # create fkLine module instance:
                    fkline, back_basket_guide = self.ar.maker.set_new_guide("dpFkLine")
                    fkline.editGuideModuleName(back_basket)
                    # editing back basket base guide informations:
                    cmds.setAttr(back_basket_guide+".translateY", 10)
                    cmds.setAttr(back_basket_guide+".translateZ", -8)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(fkline.cvJointLoc+".translateY", 0.8)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0)
                    
                    # parent back basket guide to chassis guide:
                    cmds.parent(back_basket_guide, chassis_guide, absolute=True)
                
                # Close progress window
            #    self.ar.utils.setProgress(endIt=True)
                
                # select spineGuide_Base:
                self.ar.data.collapse_edit_sel_mod = False
                cmds.select(chassis_guide)
                print(self.ar.data.lang['m168_createdBike'])
        else:
            # error checking modules in the folder:
            mel.eval('error \"'+ self.ar.data.lang['e001_guideNotChecked'] +' - '+ (", ").join(missing_modules) +'\";')
