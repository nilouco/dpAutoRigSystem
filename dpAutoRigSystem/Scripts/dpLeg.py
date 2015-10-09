# importing libraries:
import maya.cmds as cmds
import maya.mel as mel

# global variables to this module:    
CLASS_NAME = "Leg"
TITLE = "m030_leg"
DESCRIPTION = "m031_legDesc"
ICON = "/Icons/dp_leg.png"


def Leg(dpAutoRigInst):
    """ This function will create all guides needed to compose a leg.
    """
    # check modules integrity:
    guideDir = 'Modules'
    checkModuleList = ['dpLimb', 'dpFoot']
    checkResultList = dpAutoRigInst.startGuideModules(guideDir, "check", None, checkModuleList=checkModuleList)
    
    if len(checkResultList) == 0:
        # create leg module instance:
        legLimbInstance = dpAutoRigInst.initGuide('dpLimb', guideDir)
        # change limb guide to leg type:
        dpAutoRigInst.guide.Limb.changeType(legLimbInstance, dpAutoRigInst.langDic[dpAutoRigInst.langName]['m030_leg'])
        # change name to leg:
        dpAutoRigInst.guide.Limb.editUserName(legLimbInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m030_leg'].capitalize())
        
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
        
        # create foot module instance:
        footInstance = dpAutoRigInst.initGuide('dpFoot', guideDir)
        dpAutoRigInst.guide.Foot.editUserName(footInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m024_foot'])
        cmds.setAttr(footInstance.moduleGrp+".translateX", 1.5)
        cmds.setAttr(footInstance.cvFootLoc+".translateZ", 1.5)
        
        # parent foot guide to leg ankle guide:
        cmds.parent(footInstance.moduleGrp, legLimbInstance.cvExtremLoc, absolute=True)
        
        # select the legGuide_Base:
        cmds.select(legBaseGuide)
    else:
        # error checking modules in the folder:
        mel.eval('error \"'+ dpAutoRigInst.langDic[dpAutoRigInst.langName]['e001_GuideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
