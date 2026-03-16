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
        checkResultList = self.ar.startGuideModules(standardDir, "check", checkModuleList=checkModuleList)
        
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
            userDetail = self.ask_build_detail(simple, complete, cancel, userMessage)
            if not userDetail == cancel:
                # number of modules to create:
                if userDetail == simple:
                    maxProcess = 9
                else:
                    maxProcess = 16
                
                # Starting progress window
                self.ar.utils.setProgress(doingName, bikeGuideName, maxProcess, addOne=False, addNumber=False)
                self.ar.utils.setProgress(doingName+chassisName)
                
                # woking with CHASSIS system:
                # create fkLine module instance:
                chassisInstance = self.ar.initGuide('dpFkLine', guideDir)
                # editing chassis base guide informations:
                chassisInstance.editGuideModuleName(chassisName)
                cmds.setAttr(chassisInstance.moduleGrp+".translateY", 9)
                cmds.setAttr(chassisInstance.radiusCtrl+".translateX", 8)
                cmds.refresh()
                
                # woking with HANDLEBAR system:
                self.ar.utils.setProgress(doingName+handlebarName)
                # create fork instance:
                handlebarInstance = self.ar.initGuide('dpFkLine', guideDir)
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
                self.ar.utils.setProgress(doingName+forkName)
                # create fkLine module instance:
                forkInstance = self.ar.initGuide('dpFkLine', guideDir)
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
                self.ar.utils.setProgress(doingName+pedalName)
                # create pedal wheel module instance:
                pedalInstance = self.ar.initGuide('dpWheel', guideDir)
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
                self.ar.utils.setProgress(doingName+leftPedalName)
                # create pedal fkLine module instance:
                leftPedalInstance = self.ar.initGuide('dpFkLine', guideDir)
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
                self.ar.utils.setProgress(doingName+rightPedalName)
                # create pedal fkLine module instance:
                rightPedalInstance = self.ar.initGuide('dpFkLine', guideDir)
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
                self.ar.utils.setProgress(doingName+frontWheelName)
                # create wheel module instance:
                frontWheelInstance = self.ar.initGuide('dpWheel', guideDir)
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
                self.ar.utils.setProgress(doingName+backWheelName)
                # create wheel module instance:
                backWheelInstance = self.ar.initGuide('dpWheel', guideDir)
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
                self.ar.utils.setProgress(doingName+seatName)
                # create fkLine module instance:
                frontSeatInstance = self.ar.initGuide('dpFkLine', guideDir)
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
                    self.ar.utils.setProgress(doingName+hornName)
                    # create fkLine module instance:
                    hornInstance = self.ar.initGuide('dpFkLine', guideDir)
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
                    self.ar.utils.setProgress(doingName+frontSuspensionName)
                    frontSuspensionInstance = self.ar.initGuide('dpSuspension', guideDir)
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
                    self.ar.utils.setProgress(doingName+backSuspensionName)
                    backSuspensionInstance = self.ar.initGuide('dpSuspension', guideDir)
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
                    self.ar.utils.setProgress(doingName+mirrorName)
                    # create fkLine module instance:
                    mirrorInstance = self.ar.initGuide('dpFkLine', guideDir)
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
                    self.ar.utils.setProgress(doingName+leverName)
                    # create fkLine module instance:
                    leverInstance = self.ar.initGuide('dpFkLine', guideDir)
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
                    self.ar.utils.setProgress(doingName+frontBasketName)
                    # create fkLine module instance:
                    frontBasketInstance = self.ar.initGuide('dpFkLine', guideDir)
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
                    self.ar.utils.setProgress(doingName+backBasketName)
                    # create fkLine module instance:
                    backBasketInstance = self.ar.initGuide('dpFkLine', guideDir)
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
                self.ar.utils.setProgress(endIt=True)
                
                # select spineGuide_Base:
                self.ar.collapseEditSelModFL = False
                cmds.select(chassisInstance.moduleGrp)
                print(self.ar.data.lang['m168_createdBike'])
        else:
            # error checking modules in the folder:
            mel.eval('error \"'+ self.ar.data.lang['e001_guideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
