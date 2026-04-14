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
        kwargs["WIKI"] = None
        dpBaseCurve.BaseCurve.__init__(self, *args, **kwargs)
        if self.ar.dev:
            reload(dpBaseCurve)
        # dependence module list:
        self.check_modules = ['dpArrowFlat']
    
    
    def cvMain(self, useUI, cvID=None, cvName=CLASS_NAME+'_Ctrl', cvSize=1.0, cvDegree=1, cvDirection='+Y', cvRot=(0, 0, 0), cvAction=1, dpGuide=False, *args):
        """ The principal method to call all other methods in order to build the cvControl curve.
            Return the result: new control curve or the destination list depending of action.
        """
        # check modules integrity:
        missing_modules = self.ar.ui_manager.check_missing_modules(self.ar.data.curve_simple_folder, self.check_modules)
        if not missing_modules:
            # call combine function:
            return self.cvCreate(useUI, cvID, cvName, cvSize, cvDegree, cvDirection, cvRot, cvAction, dpGuide, True)
        else:
            # error checking modules in the folder:
            mel.eval('error \"'+ self.ar.data.lang['e001_guideNotChecked'] +' - '+ (", ").join(missing_modules) +'\";')
    
    
    def generateCombineCurves(self, useUI, cvID, cvName, cvSize, cvDegree, cvDirection, *args):
        """ Combine controls in order to return it.
        """
        arrow_flat = self.ar.config.get_instance_info("dpArrowFlat", [self.ar.data.curve_simple_folder])
        # creating curve shapes:
        curve1 = arrow_flat.cvMain(False, cvID, cvName, cvSize, cvDegree)
        curve2 = arrow_flat.cvMain(False, cvID, cvName, cvSize, cvDegree)
        cmds.setAttr(curve2+".rotateY", 90)
        return self.combineCurves([curve1, curve2])
