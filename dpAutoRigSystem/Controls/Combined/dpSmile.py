# importing libraries:
import maya.cmds as cmds
import dpAutoRigSystem.Controls.dpBaseControlClass as BaseControl
reload(BaseControl)

# global variables to this module:    
CLASS_NAME = "Smile"
TITLE = "m101_smile"
DESCRIPTION = "m099_cvControlDesc"
ICON = "/Icons/dp_smile.png"

dpSmileVersion = 1.0

class Smile(BaseControl.ControlStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        BaseControl.ControlStartClass.__init__(self, *args, **kwargs)
        # dependence module list:
        self.checkModuleList = ['dpCircle', 'dpCurvedCircleUp']
    
    
    def cvMain(self, useUI, cvID=None, cvName=CLASS_NAME+'_Ctrl', cvSize=1.0, cvDegree=1, cvDirection='+Y', cvAction=1, dpGuide=False, *args):
        """ The principal method to call all other methods in order to build the cvControl curve.
            Return the result: new control curve or the destination list depending of action.
        """
        # check modules integrity:
        checkResultList = self.dpUIinst.startGuideModules(self.controlsGuideDir, "check", None, checkModuleList=self.checkModuleList)
        if len(checkResultList) == 0:
            # call combine function:
            result = self.cvCreate(useUI, cvID, cvName, cvSize, cvDegree, cvDirection, cvAction, dpGuide, True)
            return result
        else:
            # error checking modules in the folder:
            mel.eval('error \"'+ self.langDic[self.langName]['e001_GuideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
    
    
    def generateCombineCurves(self, useUI, cvID, cvName, cvSize, cvDegree, cvDirection, *args):
        """ Combine controls in order to return it.
        """
        # load module instance
        circleInstance = self.dpUIinst.initControlModule('dpCircle', self.controlsGuideDir)
        mouthInstance = self.dpUIinst.initControlModule('dpCurvedCircleUp', self.controlsGuideDir)
        # creating curve shapes:
        curve1 = circleInstance.cvMain(False, cvID, cvName, cvSize, cvDegree, "+Y", 1)
        curve2 = circleInstance.cvMain(False, cvID, cvName, cvSize*0.3, cvDegree, "+Y", 1)
        curve3 = circleInstance.cvMain(False, cvID, cvName, cvSize*0.3, cvDegree, "+Y", 1)
        curve4 = mouthInstance.cvMain(False, cvID, cvName, cvSize, cvDegree, "+Y", 1)
        cmds.setAttr(curve2+".translateX", 0.4)
        cmds.setAttr(curve2+".translateY", 0.3)
        cmds.setAttr(curve3+".translateX", -0.4)
        cmds.setAttr(curve3+".translateY", 0.3)
        mainCurve = self.combineCurves([curve1, curve2, curve3, curve4])
        return mainCurve