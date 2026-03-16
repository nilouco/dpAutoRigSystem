# importing libraries:
from maya import cmds
from maya import mel
from ...Base import dpBaseCurve

# global variables to this module:    
CLASS_NAME = "Hexagram"
TITLE = "m103_hexagram"
DESCRIPTION = "m099_cvControlDesc"
ICON = "/Icons/dp_hexagram.png"

DP_HEXAGRAM_VERSION = 1.05


class Hexagram(dpBaseCurve.BaseCurve):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        kwargs["WIKI"] = None
        dpBaseCurve.BaseCurve.__init__(self, *args, **kwargs)
        # dependence module list:
        self.checkModuleList = ['dpTriangle']
    
    
    def cvMain(self, useUI, cvID=None, cvName=CLASS_NAME+'_Ctrl', cvSize=1.0, cvDegree=1, cvDirection='+Y', cvRot=(0, 0, 0), cvAction=1, dpGuide=False, *args):
        """ The principal method to call all other methods in order to build the cvControl curve.
            Return the result: new control curve or the destination list depending of action.
        """
        # check modules integrity:
        checkResultList = self.ar.startGuideModules(self.ar.data.curve_simple_folder, "check", checkModuleList=self.checkModuleList)
        if len(checkResultList) == 0:
            # call combine function:
            return self.cvCreate(useUI, cvID, cvName, cvSize, cvDegree, cvDirection, cvRot, cvAction, dpGuide, True)
            
        else:
            # error checking modules in the folder:
            mel.eval('error \"'+ self.ar.data.lang['e001_guideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
    
    
    def generateCombineCurves(self, useUI, cvID, cvName, cvSize, cvDegree, cvDirection, *args):
        """ Combine controls in order to return it.
        """
        triangle = self.ar.config.get_instance_info("dpTriangle", [self.ar.data.curve_simple_folder])
        curve1 = triangle.cvMain(False, cvID, cvName, cvSize, cvDegree)
        curve2 = triangle.cvMain(False, cvID, cvName, cvSize, cvDegree)
        cmds.setAttr(curve2+".rotateZ", 180)
        return self.combineCurves([curve1, curve2])
