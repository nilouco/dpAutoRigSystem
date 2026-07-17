# importing libraries:
from maya import cmds
from maya import mel
from ...base import curve

# global variables to this module:    
CLASS_NAME = "Ball"
TITLE = "m116_ball"
DESCRIPTION = "m099_cvControlDesc"

DP_BALL_VERSION = 1.05


class Ball(curve.BaseCurve):
    def __init__(self, ar):
        curve.BaseCurve.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, None)
        self.dependences = ['Circle']
    
    
    def cvMain(self, useUI, cvID=None, cvName=CLASS_NAME+'_Ctrl', cvSize=1.0, cvDegree=1, cvDirection='+Y', cvRot=(0, 0, 0), cvAction=1, dpGuide=False, *args):
        """ The principal method to call all other methods in order to build the cvControl curve.
            Return the result: new control curve or the destination list depending of action.
        """
        # check modules integrity:
        missing_modules = self.ar.lib.check_missing_modules(self.ar.data.curve_simple_folder, self.dependences)
        if not missing_modules:
            # call combine function:
            return self.cvCreate(useUI, cvID, cvName, cvSize, cvDegree, cvDirection, cvRot, cvAction, dpGuide, True)
        else:
            # error checking modules in the folder:
            mel.eval('error \"'+ self.ar.data.lang['e001_guideNotChecked'] +' - '+ (", ").join(missing_modules) +'\";')
    
    
    def generateCombineCurves(self, useUI, cvID, cvName, cvSize, cvDegree, cvDirection, *args):
        """ Combine controls in order to return it.
        """
        circle = self.ar.config.get_instance("Circle", [self.ar.data.curve_simple_folder])
        curve1 = circle.cvMain(False, cvID, cvName, cvSize, cvDegree)
        curve2 = circle.cvMain(False, cvID, cvName, cvSize, cvDegree)
        curve3 = circle.cvMain(False, cvID, cvName, cvSize, cvDegree)
        cmds.setAttr(curve2+".rotateY", -90)
        cmds.setAttr(curve3+".rotateX", 90)
        return self.combineCurves([curve1, curve2, curve3])
