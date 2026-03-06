# importing libraries:
from maya import cmds
from maya import mel

# global variables to this module:    
CLASS_NAME = "Leg"
TITLE = "m030_leg"
DESCRIPTION = "m031_legDesc"
ICON = "/Icons/dp_leg.png"
WIKI = "03-‐-Guides#-leg"

DP_LEG_VERSION = 2.02


def getUserDetail(opt1, opt2, cancel, userMessage):
    """ Ask user the detail level we'll create the guides by a confirm dialog box window.
        Options:
            Simple
            Complete
        Returns the user choose option or None if canceled.
    """
    result = cmds.confirmDialog(title=CLASS_NAME, message=userMessage, button=[opt1, opt2, cancel], defaultButton=opt2, cancelButton=cancel, dismissString=cancel)
    return result


def Leg(ar):
    """ This function will create all guides needed to compose a leg.
    """
    # check modules integrity:
    guideDir = 'Modules.Standard'
    standardDir = 'Modules/Standard'
    checkModuleList = ['dpLimb', 'dpFoot', 'dpFkLine']
    checkResultList = ar.startGuideModules(standardDir, "check", None, checkModuleList=checkModuleList)
    
    if len(checkResultList) == 0:
        ar.collapseEditSelModFL = True
        # defining naming:
        doingName = ar.data.lang['m094_doing']
        # part names:
        legName = ar.data.lang['m030_leg'].capitalize()
        footName = ar.data.lang['c038_foot']
        toeName = ar.data.lang['c013_revFoot_D'].capitalize()
        simple   = ar.data.lang['i175_simple']
        complete = ar.data.lang['i176_complete']
        cancel   = ar.data.lang['i132_cancel']
        userMessage = ar.data.lang['i177_chooseMessage']
        legGuideName = ar.data.lang['m030_leg']+" "+ar.data.lang['i205_guide']
        
        # getting Simple or Complete module guides to create:
        userDetail = getUserDetail(simple, complete, cancel, userMessage)
        if not userDetail == cancel:
            # number of modules to create:
            if userDetail == simple:
                maxProcess = 2
            else:
                maxProcess = 7
                
            # Starting progress window
            ar.utils.setProgress(doingName, legGuideName, maxProcess, addOne=False, addNumber=False)

            ar.utils.setProgress(doingName+legName)
            # create leg module instance:
            legLimbInstance = ar.initGuide('dpLimb', guideDir)
            # change limb guide to leg type:
            legLimbInstance.changeType(legName)
            # change name to leg:
            legLimbInstance.editGuideModuleName(legName)
            # editing leg base guide informations:
            legBaseGuide = legLimbInstance.moduleGrp
            cmds.setAttr(legBaseGuide+".type", 1)
            cmds.setAttr(legBaseGuide+".translateX", 1.5)
            cmds.setAttr(legBaseGuide+".translateY", 10)
            cmds.setAttr(legBaseGuide+".rotateX", 0)
            cmds.setAttr(legLimbInstance.radiusCtrl+".translateX", 1.5)
            legLimbInstance.changeStyle(ar.data.lang['m026_biped'])
            # edit location of leg ankle guide:
            cmds.setAttr(legLimbInstance.cvExtremLoc+".translateZ", 8.5)
            cmds.refresh()
            
            ar.utils.setProgress(doingName+footName)
            # create foot module instance:
            footInstance = ar.initGuide('dpFoot', guideDir)
            footInstance.editGuideModuleName(footName)
            cmds.setAttr(footInstance.moduleGrp+".translateX", 1.5)
            cmds.setAttr(footInstance.cvFootLoc+".translateZ", 1.5)
            # parent foot guide to leg ankle guide:
            cmds.parent(footInstance.moduleGrp, legLimbInstance.cvExtremLoc, absolute=True)
            cmds.refresh()
            
            #
            # complete part:
            #
            if userDetail == complete:
                
                ar.utils.setProgress(doingName+toeName)
                # create toe1 module instance:
                toe1Instance = ar.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe1Instance.editGuideModuleName(toeName+"_1")
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
                cmds.parent(toe1Instance.moduleGrp, footInstance.cvRFFLoc, absolute=True)
                cmds.refresh()
                
                ar.utils.setProgress(doingName+toeName)
                # create toe2 module instance:
                toe2Instance = ar.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe2Instance.editGuideModuleName(toeName+"_2")
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
                # parent toe2 guide to foot middle guide:
                cmds.parent(toe2Instance.moduleGrp, footInstance.cvRFFLoc, absolute=True)
                cmds.refresh()
                
                ar.utils.setProgress(doingName+toeName)
                # create toe3 module instance:
                toe3Instance = ar.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe3Instance.editGuideModuleName(toeName+"_3")
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
                # parent toe3 guide to foot middle guide:
                cmds.parent(toe3Instance.moduleGrp, footInstance.cvRFFLoc, absolute=True)
                cmds.refresh()
                
                ar.utils.setProgress(doingName+toeName)
                # create toe4 module instance:
                toe4Instance = ar.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe4Instance.editGuideModuleName(toeName+"_4")
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
                cmds.parent(toe4Instance.moduleGrp, footInstance.cvRFFLoc, absolute=True)
                cmds.refresh()
                
                ar.utils.setProgress(doingName+toeName)
                # create toe5 module instance:
                toe5Instance = ar.initGuide('dpFkLine', guideDir)
                # change name to toe:
                toe5Instance.editGuideModuleName(toeName+"_5")
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
                # parent toe5 guide to foot middle guide:
                cmds.parent(toe5Instance.moduleGrp, footInstance.cvRFFLoc, absolute=True)
            
            # Close progress window
            ar.utils.setProgress(endIt=True)

            # select the legGuide_Base:
            ar.collapseEditSelModFL = False
            cmds.select(legBaseGuide)
            print(ar.data.lang['m092_createdLeg'])
    else:
        # error checking modules in the folder:
        mel.eval('error \"'+ ar.data.lang['e001_guideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
