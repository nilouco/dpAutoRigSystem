# importing libraries:
from maya import cmds
from maya import mel
from ...base import curve

# global variables to this module:    
CLASS_NAME = "EyeFlat"
TITLE = "m211_eyeFlat"
DESCRIPTION = "m099_cvControlDesc"



class EyeFlat(curve.BaseCurve):
    def __init__(self, ar):
        curve.BaseCurve.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, None)
        self.dependences = ['Lens', 'Circle']
    
    
    def cvMain(self, useUI, cvID=None, cvName=CLASS_NAME+'_Ctrl', cvSize=1.0, cvDegree=0, cvDirection='+Y', cvRot=(0, 0, 0), cvAction=1, dpGuide=False, *args):
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
        lens = self.ar.config.get_instance("Lens", [self.ar.data.curve_simple_folder])
        circle = self.ar.config.get_instance("Circle", [self.ar.data.curve_simple_folder])
        curve1 = lens.cvMain(False, cvID, cvName, cvSize, cvDegree)
        curve2 = circle.cvMain(False, cvID, cvName, cvSize, cvDegree)
        cmds.setAttr(curve1+".rotateZ", 90)
        cmds.setAttr(curve2+".scaleX", 0.38)
        cmds.setAttr(curve2+".scaleY", 0.38)
        return self.combineCurves([curve1, curve2])

