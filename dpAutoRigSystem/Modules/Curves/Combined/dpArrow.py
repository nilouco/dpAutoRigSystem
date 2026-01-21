# importing libraries:
from maya import cmds
from maya import mel
from ...Base import dpBaseCurve
from importlib import reload

# global variables to this module:    
CLASS_NAME = "Arrow"
TITLE = "m113_arrow"
DESCRIPTION = "m099_cvControlDesc"
ICON = "/Icons/dp_arrow.png"

DP_ARROW_VERSION = 1.06


class Arrow(dpBaseCurve.BaseCurve):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseCurve.BaseCurve.__init__(self, *args, **kwargs)
        if self.dpUIinst.dev:
            reload(dpBaseCurve)
        # dependence module list:
        self.checkModuleList = ['dpArrowFlat']
    
    
    def cvMain(self, useUI, cvID=None, cvName=CLASS_NAME+'_Ctrl', cvSize=1.0, cvDegree=1, cvDirection='+Y', cvRot=(0, 0, 0), cvAction=1, dpGuide=False, *args):
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
        arrowFlatInstance = self.dpUIinst.initExtraModule('dpArrowFlat', self.curvesSimpleFolder.replace("/", "."))
        # creating curve shapes:
        curve1 = arrowFlatInstance.cvMain(False, cvID, cvName, cvSize, cvDegree)
        curve2 = arrowFlatInstance.cvMain(False, cvID, cvName, cvSize, cvDegree)
        cmds.setAttr(curve2+".rotateY", 90)
        mainCurve = self.combineCurves([curve1, curve2])
        return mainCurve