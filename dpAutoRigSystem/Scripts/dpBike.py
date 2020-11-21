# importing libraries:
import maya.cmds as cmds
import maya.mel as mel

# global variables to this module:    
CLASS_NAME = "Bike"
TITLE = "m165_bike"
DESCRIPTION = "m166_bikeDesc"
ICON = "/Icons/dp_bike.png"


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
    guideDir = 'Modules'
    checkModuleList = ['dpFkLine', 'dpWheel', 'dpSteering', 'dpSuspension']
    checkResultList = dpUIinst.startGuideModules(guideDir, "check", None, checkModuleList=checkModuleList)
    
    if len(checkResultList) == 0:
        # defining naming:
        doingName = dpUIinst.langDic[dpUIinst.langName]['m094_doing']
        # part names:
        chassisName = dpUIinst.langDic[dpUIinst.langName]['c091_chassis']
        sterringHandleName = dpUIinst.langDic[dpUIinst.langName]['m158_steering']+dpUIinst.langDic[dpUIinst.langName]['c078_handle']
        sterringName = dpUIinst.langDic[dpUIinst.langName]['m158_steering']+dpUIinst.langDic[dpUIinst.langName]['m162_wheelShape']
        hornName = dpUIinst.langDic[dpUIinst.langName]['c081_horn']
        frontWheelName = dpUIinst.langDic[dpUIinst.langName]['c056_front']+dpUIinst.langDic[dpUIinst.langName]['m156_wheel']
        backWheelName = dpUIinst.langDic[dpUIinst.langName]['c057_back']+dpUIinst.langDic[dpUIinst.langName]['m156_wheel']
        frontSuspensionName = dpUIinst.langDic[dpUIinst.langName]['c056_front']+dpUIinst.langDic[dpUIinst.langName]['m153_suspension']
        backSuspensionName = dpUIinst.langDic[dpUIinst.langName]['c057_back']+dpUIinst.langDic[dpUIinst.langName]['m153_suspension']
        seatName = dpUIinst.langDic[dpUIinst.langName]['c088_seat']
        mirrorName = dpUIinst.langDic[dpUIinst.langName]['m010_Mirror']
        pedalName = dpUIinst.langDic[dpUIinst.langName]['c089_pedal']
        leftPedalName = dpUIinst.langDic[dpUIinst.langName]['p002_left']+"_"+dpUIinst.langDic[dpUIinst.langName]['c089_pedal']
        rightPedalName = dpUIinst.langDic[dpUIinst.langName]['p003_right']+"_"+dpUIinst.langDic[dpUIinst.langName]['c089_pedal']
        leverName = dpUIinst.langDic[dpUIinst.langName]['c090_lever']
        frontBasketName = dpUIinst.langDic[dpUIinst.langName]['c056_front']+dpUIinst.langDic[dpUIinst.langName]['c094_basket']
        backBasketName = dpUIinst.langDic[dpUIinst.langName]['c057_back']+dpUIinst.langDic[dpUIinst.langName]['c094_basket']
        simple   = dpUIinst.langDic[dpUIinst.langName]['i175_simple']
        complete = dpUIinst.langDic[dpUIinst.langName]['i176_complete']
        cancel   = dpUIinst.langDic[dpUIinst.langName]['i132_cancel']
        userMessage = dpUIinst.langDic[dpUIinst.langName]['i177_chooseMessage']
        
        # getting Simple or Complete module guides to create:
        userDetail = getUserDetail(simple, complete, cancel, userMessage)
        if not userDetail == cancel:
            # number of modules to create:
            if userDetail == simple:
                maxProcess = 9
            else:
                maxProcess = 16
            
            # Starting progress window
            progressAmount = 0
            cmds.progressWindow(title='Bike Guides', progress=progressAmount, status=doingName+': 0%', isInterruptable=False)
            
            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+chassisName))
            
            # woking with CHASSIS system:
            # create fkLine module instance:
            chassisInstance = dpUIinst.initGuide('dpFkLine', guideDir)
            # editing chassis base guide informations:
            chassisInstance.editUserName(chassisName)
            cmds.setAttr(chassisInstance.moduleGrp+".translateY", 9)
            cmds.setAttr(chassisInstance.radiusCtrl+".translateX", 8)
            
            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+sterringHandleName))
            
            # woking with STEERING HANDLE system:
            # create fkLine module instance:
            steeringHandleInstance = dpUIinst.initGuide('dpFkLine', guideDir)
            # editing steering base guide informations:
            steeringHandleInstance.editUserName(sterringHandleName)
            cmds.setAttr(steeringHandleInstance.moduleGrp+".translateY", 11.7)
            cmds.setAttr(steeringHandleInstance.moduleGrp+".translateZ", 5.1)
            cmds.setAttr(steeringHandleInstance.moduleGrp+".rotateX", -19)
            cmds.setAttr(steeringHandleInstance.radiusCtrl+".translateX", 1.1)
            
            # parent steering handle guide to chassis guide:
            cmds.parent(steeringHandleInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
            
            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+sterringName))
            
            # woking with STEERING system:
            # create steering module instance:
            steeringInstance = dpUIinst.initGuide('dpSteering', guideDir)
            # editing steering base guide informations:
            steeringInstance.editUserName(sterringName)
            cmds.setAttr(steeringInstance.moduleGrp+".translateY", 12.7)
            cmds.setAttr(steeringInstance.moduleGrp+".translateZ", 4.7)
            cmds.setAttr(steeringInstance.moduleGrp+".rotateX", 71)
            cmds.setAttr(steeringInstance.annotation+".translateY", 2)
            
            # parent steering guide to steering handle guide:
            cmds.parent(steeringInstance.moduleGrp, steeringHandleInstance.moduleGrp, absolute=True)
            
            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+pedalName))
            
            # working with PEDAL WHEEL system:
            # create pedal wheel module instance:
            pedalInstance = dpUIinst.initGuide('dpWheel', guideDir)
            pedalInstance.editUserName(pedalName)        
            # editing pedal wheel base guide informations:
            cmds.setAttr(pedalInstance.moduleGrp+".translateY", 4.5)
            cmds.setAttr(pedalInstance.moduleGrp+".translateZ", -0.8)
            cmds.setAttr(pedalInstance.moduleGrp+".rotateY", -90)
            cmds.setAttr(pedalInstance.radiusCtrl+".translateX", 1.5)
            cmds.setAttr(pedalInstance.moduleGrp+".steering", 0)
            
            # parent pedal wheel guide to steering base guide:
            cmds.parent(pedalInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
            
            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+leftPedalName))
            
            # working with LEFT PEDAL system:
            # create pedal fkLine module instance:
            leftPedalInstance = dpUIinst.initGuide('dpFkLine', guideDir)
            leftPedalInstance.editUserName(leftPedalName)        
            # editing left pedal base guide informations:
            cmds.setAttr(leftPedalInstance.moduleGrp+".translateX", 1.3)
            cmds.setAttr(leftPedalInstance.moduleGrp+".translateY", 2.6)
            cmds.setAttr(leftPedalInstance.moduleGrp+".translateZ", -2.1)
            cmds.setAttr(leftPedalInstance.radiusCtrl+".translateX", 0.8)
            
            # parent left pedal guide to pedal base guide:
            cmds.parent(leftPedalInstance.moduleGrp, pedalInstance.cvCenterLoc, absolute=True)
            
            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+rightPedalName))
            
            # working with RIGHT PEDAL system:
            # create pedal fkLine module instance:
            rightPedalInstance = dpUIinst.initGuide('dpFkLine', guideDir)
            rightPedalInstance.editUserName(rightPedalName)        
            # editing right pedal base guide informations:
            cmds.setAttr(rightPedalInstance.moduleGrp+".translateX", -1.3)
            cmds.setAttr(rightPedalInstance.moduleGrp+".translateY", 6.3)
            cmds.setAttr(rightPedalInstance.moduleGrp+".translateZ", 0.3)
            cmds.setAttr(rightPedalInstance.radiusCtrl+".translateX", 0.8)
            
            # parent right pedal guide to pedal base guide:
            cmds.parent(rightPedalInstance.moduleGrp, pedalInstance.cvCenterLoc, absolute=True)
            
            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+frontWheelName))
            
            # working with FRONT WHEEL system:
            # create wheel module instance:
            frontWheelInstance = dpUIinst.initGuide('dpWheel', guideDir)
            frontWheelInstance.editUserName(frontWheelName)        
            # editing frontWheel base guide informations:
            cmds.setAttr(frontWheelInstance.moduleGrp+".translateY", 4.7)
            cmds.setAttr(frontWheelInstance.moduleGrp+".translateZ", 8.4)
            cmds.setAttr(frontWheelInstance.moduleGrp+".rotateY", -90)
            cmds.setAttr(frontWheelInstance.radiusCtrl+".translateX", 4.7)
            cmds.setAttr(frontWheelInstance.moduleGrp+".steering", 1)
            # edit location of inside and outiside guide:
            cmds.setAttr(frontWheelInstance.cvInsideLoc+".translateZ", 0.35)
            cmds.setAttr(frontWheelInstance.cvOutsideLoc+".translateZ", -0.35)
            
            # parent front wheel guide to steering base guide:
            cmds.parent(frontWheelInstance.moduleGrp, steeringInstance.moduleGrp, absolute=True)
            
            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+backWheelName))
            
            # working with BACK WHEEL system:
            # create wheel module instance:
            backWheelInstance = dpUIinst.initGuide('dpWheel', guideDir)
            backWheelInstance.editUserName(backWheelName)        
            # editing frontWheel base guide informations:
            cmds.setAttr(backWheelInstance.moduleGrp+".translateY", 4.7)
            cmds.setAttr(backWheelInstance.moduleGrp+".translateZ", -7.8)
            cmds.setAttr(backWheelInstance.moduleGrp+".rotateY", -90)
            cmds.setAttr(backWheelInstance.radiusCtrl+".translateX", 4.7)
            cmds.setAttr(backWheelInstance.moduleGrp+".steering", 0)
            # edit location of inside and outiside guide:
            cmds.setAttr(backWheelInstance.cvInsideLoc+".translateZ", 0.35)
            cmds.setAttr(backWheelInstance.cvOutsideLoc+".translateZ", -0.35)
            
            # parent front wheel guide to steering base guide:
            cmds.parent(backWheelInstance.moduleGrp, steeringInstance.moduleGrp, absolute=True)
            
            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+seatName))
            
            # woking with SEAT system:
            # create fkLine module instance:
            frontSeatInstance = dpUIinst.initGuide('dpFkLine', guideDir)
            frontSeatInstance.editUserName(seatName)
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
            
            
            # complete part:
            if userDetail == complete:
            
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+hornName))
                
                # woking with HORN system:
                # create fkLine module instance:
                hornInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                # editing eyeLookAt base guide informations:
                hornInstance.editUserName(hornName)
                cmds.setAttr(hornInstance.moduleGrp+".translateX", -0.64)
                cmds.setAttr(hornInstance.moduleGrp+".translateY", 13.3)
                cmds.setAttr(hornInstance.moduleGrp+".translateZ", 4.5)
                cmds.setAttr(hornInstance.moduleGrp+".rotateX", 17)
                cmds.setAttr(hornInstance.radiusCtrl+".translateX", 0.7)
                
                # parent horn guide to steering guide:
                cmds.parent(hornInstance.moduleGrp, steeringInstance.cvJointLoc, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+frontSuspensionName))
                
                # create FRONT SUSPENSION module instance:
                frontSuspensionInstance = dpUIinst.initGuide('dpSuspension', guideDir)
                frontSuspensionInstance.editUserName(frontSuspensionName)
                # editing frontSuspension base guide informations:
                cmds.setAttr(frontSuspensionInstance.moduleGrp+".translateY", 7)
                cmds.setAttr(frontSuspensionInstance.moduleGrp+".translateZ", 7)
                cmds.setAttr(frontSuspensionInstance.moduleGrp+".rotateX", -110)
                cmds.setAttr(frontSuspensionInstance.radiusCtrl+".translateX", 0.7)
                # edit fatherB attribut for frontSuspension module guide?
                cmds.setAttr(frontSuspensionInstance.moduleGrp+".fatherB", chassisInstance.moduleGrp, type='string')
                
                # parent front suspension guide to front wheel guide:
                cmds.parent(frontSuspensionInstance.moduleGrp, frontWheelInstance.moduleGrp, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+backSuspensionName))
                
                # create BACK SUSPENSION module instance:
                backSuspensionInstance = dpUIinst.initGuide('dpSuspension', guideDir)
                backSuspensionInstance.editUserName(backSuspensionName)
                # editing back suspension base guide informations:
                cmds.setAttr(backSuspensionInstance.moduleGrp+".translateY", 7)
                cmds.setAttr(backSuspensionInstance.moduleGrp+".translateZ", -6.6)
                cmds.setAttr(backSuspensionInstance.moduleGrp+".rotateX", -43)
                cmds.setAttr(backSuspensionInstance.radiusCtrl+".translateX", 0.7)
                # edit fatherB attribut for frontSuspension module guide?
                cmds.setAttr(backSuspensionInstance.moduleGrp+".fatherB", chassisInstance.moduleGrp, type='string')
                
                # parent front suspension guide to front wheel guide:
                cmds.parent(backSuspensionInstance.moduleGrp, backWheelInstance.moduleGrp, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+mirrorName))
                
                # woking with MIRROR system:
                # create fkLine module instance:
                mirrorInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                mirrorInstance.editUserName(mirrorName)
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
                
                # parent mirror guide to steering guide:
                cmds.parent(mirrorInstance.moduleGrp, steeringInstance.cvJointLoc, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+leverName))
                
                # woking with LEVER system:
                # create fkLine module instance:
                leverInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                leverInstance.editUserName(leverName)
                # setting X mirror:
                leverInstance.changeMirror("X")
                # editing lever base guide informations:
                cmds.setAttr(leverInstance.moduleGrp+".flip", 1)
                cmds.setAttr(leverInstance.moduleGrp+".translateX", 4.1)
                cmds.setAttr(leverInstance.moduleGrp+".translateY", 15)
                cmds.setAttr(leverInstance.moduleGrp+".translateZ", 4)
                cmds.setAttr(leverInstance.moduleGrp+".rotateY", 10)
                cmds.setAttr(leverInstance.radiusCtrl+".translateX",0.8)
                
                # parent lever guide to steering guide:
                cmds.parent(leverInstance.moduleGrp, steeringInstance.cvJointLoc, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+frontBasketName))
                
                # woking with FRONT BASKET system:
                # create fkLine module instance:
                frontBasketInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                frontBasketInstance.editUserName(frontBasketName)
                # editing front basket base guide informations:
                cmds.setAttr(frontBasketInstance.moduleGrp+".translateY", 10)
                cmds.setAttr(frontBasketInstance.moduleGrp+".translateZ", 9)
                frontBasketInstance.changeJointNumber(2)
                cmds.setAttr(frontBasketInstance.cvJointLoc+".translateY", 0.8)
                cmds.setAttr(frontBasketInstance.cvJointLoc+".translateZ", 0)
                
                # parent front basket guide to front wheel guide:
                cmds.parent(frontBasketInstance.moduleGrp, frontWheelInstance.moduleGrp, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+backBasketName))
                
                # woking with BACK BASKET system:
                # create fkLine module instance:
                backBasketInstance = dpUIinst.initGuide('dpFkLine', guideDir)
                backBasketInstance.editUserName(backBasketName)
                # editing back basket base guide informations:
                cmds.setAttr(backBasketInstance.moduleGrp+".translateY", 10)
                cmds.setAttr(backBasketInstance.moduleGrp+".translateZ", -8)
                backBasketInstance.changeJointNumber(2)
                cmds.setAttr(backBasketInstance.cvJointLoc+".translateY", 0.8)
                cmds.setAttr(backBasketInstance.cvJointLoc+".translateZ", 0)
                
                # parent back basket guide to chassis guide:
                cmds.parent(backBasketInstance.moduleGrp, chassisInstance.moduleGrp, absolute=True)
            
            
            # Close progress window
            cmds.progressWindow(endProgress=True)
            
            # select spineGuide_Base:
            cmds.select(chassisInstance.moduleGrp)
            print dpUIinst.langDic[dpUIinst.langName]['m168_createdBike']+"\n",
    else:
        # error checking modules in the folder:
        mel.eval('error \"'+ dpUIinst.langDic[dpUIinst.langName]['e001_GuideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
