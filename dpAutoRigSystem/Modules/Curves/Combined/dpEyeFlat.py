# importing libraries:
from maya import cmds
from maya import mel
from ...Base import dpBaseCurve

# global variables to this module:    
CLASS_NAME = "EyeFlat"
TITLE = "m211_eyeFlat"
DESCRIPTION = "m099_cvControlDesc"
ICON = "/Icons/dp_eyeFlat.png"

DP_EYEFLAT_VERSION = 1.03


class EyeFlat(dpBaseCurve.BaseCurve):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseCurve.BaseCurve.__init__(self, *args, **kwargs)
        # dependence module list:
        self.checkModuleList = ['dpLens', 'dpCircle']
    
    
    def cvMain(self, useUI, cvID=None, cvName=CLASS_NAME+'_Ctrl', cvSize=1.0, cvDegree=0, cvDirection='+Y', cvRot=(0, 0, 0), cvAction=1, dpGuide=False, *args):
        """ The principal method to call all other methods in order to build the cvControl curve.
            Return the result: new control curve or the destination list depending of action.
        """
        # check modules integrity:
        checkResultList = self.dpUIinst.startGuideModules(self.curvesSimpleFolder, "check", None, checkModuleList=self.checkModuleList)
        if len(checkResultList) == 0:
            # call combine function:
            result = self.cvCreate(useUI, cvID, cvName, cvSize, cvDegree, cvDirection, cvRot, cvAction, dpGuide, True)
            return result
        else:
            # error checking modules in the folder:
            mel.eval('error \"'+ self.dpUIinst.lang['e001_guideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
    
    
    def generateCombineCurves(self, useUI, cvID, cvName, cvSize, cvDegree, cvDirection, *args):
        """ Combine controls in order to return it.
        """
        # load module instance
        lenFlatInstance = self.dpUIinst.initExtraModule('dpLens', self.curvesSimpleFolder.replace("/", "."))
        circleFlatInstance = self.dpUIinst.initExtraModule('dpCircle', self.curvesSimpleFolder.replace("/", "."))
        # creating curve shapes:
        curve1 = lenFlatInstance.cvMain(False, cvID, cvName, cvSize, cvDegree)
        curve2 = circleFlatInstance.cvMain(False, cvID, cvName, cvSize, cvDegree)
        cmds.setAttr(curve1+".rotateZ", 90)
        cmds.setAttr(curve2+".scaleX", 0.38)
        cmds.setAttr(curve2+".scaleY", 0.38)
        mainCurve = self.combineCurves([curve1, curve2])
        return mainCurve
