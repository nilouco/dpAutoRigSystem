# importing libraries:
import maya.cmds as cmds
import maya.mel as mel

# global variables to this module:    
CLASS_NAME = "Leg"
TITLE = "m030_leg"
DESCRIPTION = "m031_legDesc"
ICON = "/Icons/dp_leg.png"



def getUserDetail(opt1, opt2, cancel, userMessage):
    """ Ask user the detail level we'll create the guides by a confirm dialog box window.
        Options:
            Simple
            Complete
        Returns the user choose option or None if canceled.
    """
    result = cmds.confirmDialog(title=CLASS_NAME, message=userMessage, button=[opt1, opt2, cancel], defaultButton=opt2, cancelButton=cancel, dismissString=cancel)
    return result


def Leg(dpUIinst):
    """ This function will create all guides needed to compose a leg.
    """
    # check modules integrity:
    guideDir = 'Modules'
    checkModuleList = ['dpLimb', 'dpFoot', 'dpFkLine']
    checkResultList = dpUIinst.startGuideModules(guideDir, "check", None, checkModuleList=checkModuleList)
    
    if len(checkResultList) == 0:
        # defining naming:
        doingName = dpUIinst.langDic[dpUIinst.langName]['m094_doing']
        # part names:
        legName = dpUIinst.langDic[dpUIinst.langName]['m030_leg'].capitalize()
        footName = dpUIinst.langDic[dpUIinst.langName]['c038_foot']
        toeName = dpUIinst.langDic[dpUIinst.langName]['c013_RevFoot_D'].capitalize()
        simple   = dpUIinst.langDic[dpUIinst.langName]['i175_simple']
        complete = dpUIinst.langDic[dpUIinst.langName]['i176_complete']
        cancel   = dpUIinst.langDic[dpUIinst.langName]['i132_cancel']
        userMessage = dpUIinst.langDic[dpUIinst.langName]['i177_chooseMessage']
        
        # getting Simple or Complete module guides to create:
        userDetail = getUserDetail(simple, complete, cancel, userMessage)
        if not userDetail == cancel:
            # number of modules to create:
            if userDetail == simple:
                maxProcess = 2
            else:
                maxProcess = 7
                
            # Starting progress window
            progressAmount = 0
            cmds.progressWindow(title='Leg Guides', progress=progressAmount, status=doingName+': 0%', isInterruptable=False)

            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+legName))
            
            # create leg module instance:
            legLimbInstance = dpUIinst.initGuide('dpLimb', guideDir)
            # change limb guide to leg type:
            legLimbInstance.changeType(legName)
            # change name to leg:
            legLimbInstance.editUserName(legName)
            
            # editing leg base guide informations:
            legBaseGuide = legLimbInstance.moduleGrp
            cmds.setAttr(legBaseGuide+".type", 1)
            cmds.setAttr(legBaseGuide+".translateX", 1.5)
            cmds.setAttr(legBaseGuide+".translateY", 10)
            cmds.setAttr(legBaseGuide+".rotateX", 0)
            cmds.setAttr(legLimbInstance.radiusCtrl+".translateX", 1.5)
            
            # edit location of leg ankle guide:
            cmds.setAttr(legLimbInstance.cvExtremLoc+".translateZ", 8.5)
            
            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+footName))
            
            # create foot module instance:
            footInstance = dpUIinst.initGuide('dpFoot', guideDir)
            footInstance.editUserName(footName)
            cmds.setAttr(footInstance.moduleGrp+".translateX", 1.5)
            cmds.setAttr(footInstance.cvFootLoc+".translateZ", 1.5)
            
            # parent foot guide to leg ankle guide:
            cmds.parent(footInstance.moduleGrp, legLimbInstance.cvExtremLoc, absolute=True)
            
            # complete part:
            if userDetail == complete:
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+toeName+'_1'))
                
                # create toe1 module instance:
                toe1Instance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe1Instance.editUserName(toeName+"_1")
                # editing toe base guide informations:
                cmds.setAttr(toe1Instance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(toe1Instance.moduleGrp+".translateX", 1)
                cmds.setAttr(toe1Instance.moduleGrp+".translateY", 0.5)
                cmds.setAttr(toe1Instance.moduleGrp+".translateZ", 2.7)
                toe1Instance.changeJointNumber(2)
                cmds.setAttr(toe1Instance.cvJointLoc+".translateZ", 0.25)
                toe1Instance.changeJointNumber(3)
                cmds.setAttr(toe1Instance.cvJointLoc+".translateZ", 0.25)
                cmds.setAttr(toe1Instance.cvEndJoint+".translateZ", 0.2)
                cmds.setAttr(toe1Instance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(toe1Instance.moduleGrp+".flip", 1)
                toe1Instance.displayAnnotation(0)
                
                # parent toe1 guide to foot middle guide:
                cmds.parent(toe1Instance.moduleGrp, footInstance.cvRFELoc, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+toeName+'_2'))
                
                # create toe2 module instance:
                toe2Instance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe2Instance.editUserName(toeName+"_2")
                # editing toe base guide informations:
                cmds.setAttr(toe2Instance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(toe2Instance.moduleGrp+".translateX", 1.35)
                cmds.setAttr(toe2Instance.moduleGrp+".translateY", 0.5)
                cmds.setAttr(toe2Instance.moduleGrp+".translateZ", 2.7)
                toe2Instance.changeJointNumber(2)
                cmds.setAttr(toe2Instance.cvJointLoc+".translateZ", 0.25)
                toe2Instance.changeJointNumber(3)
                cmds.setAttr(toe2Instance.cvJointLoc+".translateZ", 0.25)
                cmds.setAttr(toe2Instance.cvEndJoint+".translateZ", 0.2)
                cmds.setAttr(toe2Instance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(toe2Instance.moduleGrp+".flip", 1)
                toe2Instance.displayAnnotation(0)
                
                # parent toe1 guide to foot middle guide:
                cmds.parent(toe2Instance.moduleGrp, footInstance.cvRFELoc, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+toeName+'_3'))
                
                # create toe3 module instance:
                toe3Instance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe3Instance.editUserName(toeName+"_3")
                # editing toe base guide informations:
                cmds.setAttr(toe3Instance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(toe3Instance.moduleGrp+".translateX", 1.65)
                cmds.setAttr(toe3Instance.moduleGrp+".translateY", 0.5)
                cmds.setAttr(toe3Instance.moduleGrp+".translateZ", 2.7)
                toe3Instance.changeJointNumber(2)
                cmds.setAttr(toe3Instance.cvJointLoc+".translateZ", 0.25)
                toe3Instance.changeJointNumber(3)
                cmds.setAttr(toe3Instance.cvJointLoc+".translateZ", 0.25)
                cmds.setAttr(toe3Instance.cvEndJoint+".translateZ", 0.2)
                cmds.setAttr(toe3Instance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(toe3Instance.moduleGrp+".flip", 1)
                toe3Instance.displayAnnotation(0)
                
                # parent toe1 guide to foot middle guide:
                cmds.parent(toe3Instance.moduleGrp, footInstance.cvRFELoc, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+toeName+'_4'))
                
                # create toe4 module instance:
                toe4Instance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe4Instance.editUserName(toeName+"_4")
                # editing toe base guide informations:
                cmds.setAttr(toe4Instance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(toe4Instance.moduleGrp+".translateX", 1.95)
                cmds.setAttr(toe4Instance.moduleGrp+".translateY", 0.5)
                cmds.setAttr(toe4Instance.moduleGrp+".translateZ", 2.7)
                toe4Instance.changeJointNumber(2)
                cmds.setAttr(toe4Instance.cvJointLoc+".translateZ", 0.25)
                toe4Instance.changeJointNumber(3)
                cmds.setAttr(toe4Instance.cvJointLoc+".translateZ", 0.25)
                cmds.setAttr(toe4Instance.cvEndJoint+".translateZ", 0.2)
                cmds.setAttr(toe4Instance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(toe4Instance.moduleGrp+".flip", 1)
                toe4Instance.displayAnnotation(0)
                
                # parent toe4 guide to foot middle guide:
                cmds.parent(toe4Instance.moduleGrp, footInstance.cvRFELoc, absolute=True)
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+toeName+'_5'))
                
                # create toe5 module instance:
                toe5Instance = dpUIinst.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe5Instance.editUserName(toeName+"_5")
                # editing toe base guide informations:
                cmds.setAttr(toe5Instance.moduleGrp+".shapeSize", 0.3)
                cmds.setAttr(toe5Instance.moduleGrp+".translateX", 2.25)
                cmds.setAttr(toe5Instance.moduleGrp+".translateY", 0.5)
                cmds.setAttr(toe5Instance.moduleGrp+".translateZ", 2.7)
                toe5Instance.changeJointNumber(2)
                cmds.setAttr(toe5Instance.cvJointLoc+".translateZ", 0.25)
                toe5Instance.changeJointNumber(3)
                cmds.setAttr(toe5Instance.cvJointLoc+".translateZ", 0.25)
                cmds.setAttr(toe5Instance.cvEndJoint+".translateZ", 0.2)
                cmds.setAttr(toe5Instance.radiusCtrl+".translateX", 0.2)
                cmds.setAttr(toe5Instance.moduleGrp+".flip", 1)
                toe5Instance.displayAnnotation(0)
                
                # parent toe1 guide to foot middle guide:
                cmds.parent(toe5Instance.moduleGrp, footInstance.cvRFELoc, absolute=True)
            
            # Close progress window
            cmds.progressWindow(endProgress=True)

            # select the legGuide_Base:
            cmds.select(legBaseGuide)
            print dpUIinst.langDic[dpUIinst.langName]['m092_createdLeg']+"\n",
    else:
        # error checking modules in the folder:
        mel.eval('error \"'+ dpUIinst.langDic[dpUIinst.langName]['e001_GuideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
