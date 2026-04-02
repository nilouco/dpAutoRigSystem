# importing libraries:
from maya import cmds
from maya import mel
from ...Base import dpBaseCurve

# global variables to this module:    
CLASS_NAME = "Smile"
TITLE = "m101_smile"
DESCRIPTION = "m099_cvControlDesc"
ICON = "/Icons/dp_smile.png"

DP_SMILE_VERSION = 1.05


class Smile(dpBaseCurve.BaseCurve):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        kwargs["WIKI"] = None
        dpBaseCurve.BaseCurve.__init__(self, *args, **kwargs)
        # dependence module list:
        self.checkModuleList = ['dpCircle', 'dpCurvedCircleUp']
    
    
    def cvMain(self, useUI, cvID=None, cvName=CLASS_NAME+'_Ctrl', cvSize=1.0, cvDegree=1, cvDirection='+Y', cvRot=(0, 0, 0), cvAction=1, dpGuide=False, *args):
        """ The principal method to call all other methods in order to build the cvControl curve.
            Return the result: new control curve or the destination list depending of action.
        """
        # check modules integrity:
        checkResultList = self.ar.check_missing_modules(self.ar.data.curve_simple_folder, self.checkModuleList)
        if len(checkResultList) == 0:
            # call combine function:
            return self.cvCreate(useUI, cvID, cvName, cvSize, cvDegree, cvDirection, cvRot, cvAction, dpGuide, True)
            
        else:
            # error checking modules in the folder:
            mel.eval('error \"'+ self.ar.data.lang['e001_guideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
    
    
    def generateCombineCurves(self, useUI, cvID, cvName, cvSize, cvDegree, cvDirection, *args):
        """ Combine controls in order to return it.
        """
        circle = self.ar.config.get_instance_info("dpCircle", [self.ar.data.curve_simple_folder])
        mouth = self.ar.config.get_instance_info("dpCurvedCircleUp", [self.ar.data.curve_simple_folder])
        curve1 = circle.cvMain(False, cvID, cvName, cvSize, cvDegree)
        curve2 = circle.cvMain(False, cvID, cvName, cvSize*0.3, cvDegree)
        curve3 = circle.cvMain(False, cvID, cvName, cvSize*0.3, cvDegree)
        curve4 = mouth.cvMain(False, cvID, cvName, cvSize, cvDegree)
        cmds.setAttr(curve2+".translateX", 0.4*cvSize)
        cmds.setAttr(curve2+".translateY", 0.3*cvSize)
        cmds.setAttr(curve3+".translateX", -0.4*cvSize)
        cmds.setAttr(curve3+".translateY", 0.3*cvSize)
        return self.combineCurves([curve1, curve2, curve3, curve4])
