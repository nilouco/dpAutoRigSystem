# importing libraries:
import maya.cmds as cmds
import maya.mel as mel

# global variables to this module:    
CLASS_NAME = "Leg"
TITLE = "m030_leg"
DESCRIPTION = "m031_legDesc"
ICON = "/Icons/dp_leg.png"


def Leg(dpUIinst):
    """ This function will create all guides needed to compose a leg.
    """
    # check modules integrity:
    guideDir = 'Modules'
    checkModuleList = ['dpLimb', 'dpFoot']
    checkResultList = dpUIinst.startGuideModules(guideDir, "check", None, checkModuleList=checkModuleList)
    
    if len(checkResultList) == 0:
        # defining naming:
        doingName = dpUIinst.langDic[dpUIinst.langName]['m094_doing']
        # part names:
        legName = dpUIinst.langDic[dpUIinst.langName]['m030_leg']
        footName = dpUIinst.langDic[dpUIinst.langName]['c038_foot']
        
        # Starting progress window
        progressAmount = 0
        cmds.progressWindow(title='Leg Guides', progress=progressAmount, status=doingName+': 0%', isInterruptable=False)
        maxProcess = 12 # number of modules to create

        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+legName))
        
        # create leg module instance:
        legLimbInstance = dpUIinst.initGuide('dpLimb', guideDir)
        # change limb guide to leg type:
        legLimbInstance.changeType(legName)
        # change name to leg:
        legLimbInstance.editUserName(legName.capitalize())
        
        # editing leg base guide informations:
        legBaseGuide = legLimbInstance.moduleGrp
        cmds.setAttr(legBaseGuide+".type", 1)
        cmds.setAttr(legBaseGuide+".translateX", 1.5)
        cmds.setAttr(legBaseGuide+".translateY", 10)
        cmds.setAttr(legBaseGuide+".rotateX", 0)
        cmds.setAttr(legBaseGuide+".displayAnnotation", 0)
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
        
        # Close progress window
        cmds.progressWindow(endProgress=True)

        # select the legGuide_Base:
        cmds.select(legBaseGuide)
        print dpUIinst.langDic[dpUIinst.langName]['m092_createdLeg'],
    else:
        # error checking modules in the folder:
        mel.eval('error \"'+ dpUIinst.langDic[dpUIinst.langName]['e001_GuideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
