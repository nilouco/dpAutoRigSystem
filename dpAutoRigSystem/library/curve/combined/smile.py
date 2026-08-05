# importing libraries:
from maya import cmds
from maya import mel
from ...base import curve

# global variables to this module:    
CLASS_NAME = "Smile"
TITLE = "m101_smile"
DESCRIPTION = "m099_cvControlDesc"



class Smile(curve.BaseCurve):
    def __init__(self, ar):
        curve.BaseCurve.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, None)
        self.dependences = ['Circle', 'CurvedCircleUp']
    
    
    def cvMain(self, use_ui, cv_id=None, cv_name=CLASS_NAME+'_Ctrl', cv_size=1.0, cv_degree=1, cv_direction='+Y', cv_rot=(0, 0, 0), cv_action=1, guide=False, *args):
        """ The principal method to call all other methods in order to build the cvControl curve.
            Return the result: new control curve or the destination list depending of action.
        """
        # check modules integrity:
        missing_modules = self.ar.lib.check_missing_modules(self.ar.data.curve_simple_folder, self.dependences)
        if not missing_modules:
            # call combine function:
            return self.cv_create(use_ui, cv_id, cv_name, cv_size, cv_degree, cv_direction, cv_rot, cv_action, guide, True)
        else:
            # error checking modules in the folder:
            mel.eval('error \"'+ self.ar.data.lang['e001_guideNotChecked'] +' - '+ (", ").join(missing_modules) +'\";')
    
    
    def generateCombineCurves(self, use_ui, cv_id, cv_name, cv_size, cv_degree, cv_direction, *args):
        """ Combine controls in order to return it.
        """
        circle = self.ar.config.get_instance("Circle", [self.ar.data.curve_simple_folder])
        mouth = self.ar.config.get_instance("CurvedCircleUp", [self.ar.data.curve_simple_folder])
        curve1 = circle.cvMain(False, cv_id, cv_name, cv_size, cv_degree)
        curve2 = circle.cvMain(False, cv_id, cv_name, cv_size*0.3, cv_degree)
        curve3 = circle.cvMain(False, cv_id, cv_name, cv_size*0.3, cv_degree)
        curve4 = mouth.cvMain(False, cv_id, cv_name, cv_size, cv_degree)
        cmds.setAttr(curve2+".translateX", 0.4*cv_size)
        cmds.setAttr(curve2+".translateY", 0.3*cv_size)
        cmds.setAttr(curve3+".translateX", -0.4*cv_size)
        cmds.setAttr(curve3+".translateY", 0.3*cv_size)
        return self.combine_curves([curve1, curve2, curve3, curve4])
