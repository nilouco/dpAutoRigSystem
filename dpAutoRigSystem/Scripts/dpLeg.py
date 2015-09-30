# importing libraries:
import maya.cmds as cmds
import maya.mel as mel

# global variables to this module:    
CLASS_NAME = "Leg"
TITLE = "m030_leg"
DESCRIPTION = "m031_legDesc"
ICON = "/Icons/dp_leg.png"


def Leg(self):
    """ This function will create all guides needed to compose a leg.
    """
    # check modules integrity:
    guideDir = 'Modules'
    checkModuleList = ['dpLimb', 'dpFoot']
    checkResultList = self.startGuideModules(guideDir, "check", checkModuleList)
    
    if len(checkResultList) == 0:
        # create leg module instance:
        legLimbInstance = self.initGuide('dpLimb', guideDir)
        # change limb guide to leg type:
        self.guide.Limb.changeType(legLimbInstance, self.langDic[self.langName]['m030_leg'])
        # change name to leg:
        self.guide.Limb.editUserName(legLimbInstance, checkText=self.langDic[self.langName]['m030_leg'].lower())
        
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
        footInstance = self.initGuide('dpFoot', guideDir)
        self.guide.Foot.editUserName(footInstance, checkText=self.langDic[self.langName]['m024_foot'].lower())
        cmds.setAttr(footInstance.moduleGrp+".translateX", 1.5)
        cmds.setAttr(footInstance.cvFootLoc+".translateZ", 1.5)
        
        # parent foot guide to leg ankle guide:
        cmds.parent(footInstance.moduleGrp, legLimbInstance.cvExtremLoc, absolute=True)
        
        # select the legGuide_base:
        cmds.select(legBaseGuide)
    else:
        # error checking modules in the folder:
        mel.eval('error \"'+ self.langDic[self.langName]['e001_guideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
