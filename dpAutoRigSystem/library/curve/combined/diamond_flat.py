# importing libraries:
from maya import cmds
from maya import mel
from ...base import curve

# global variables to this module:    
CLASS_NAME = "DiamondFlat"
TITLE = "m177_diamondFlat"
DESCRIPTION = "m099_cvControlDesc"



class DiamondFlat(curve.BaseCurve):
    def __init__(self, ar):
        curve.BaseCurve.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, None)
        self.dependences = ['Square']
    
    
    def cv_main(self, use_ui, cv_id=None, cv_name=CLASS_NAME+'_Ctrl', cv_size=1.0, cv_degree=1, cv_direction='+Y', cv_rot=(0, 0, 0), cv_action=1, guide=False):
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
    
    
    def create_combined_curves(self, cv_id, cv_name, cv_size, cv_degree):
        """ Combine controllers in order to return it.
        """
        square = self.ar.config.get_instance("Square", [self.ar.data.curve_simple_folder])
        curve1 = square.cv_main(False, cv_id, cv_name, cv_size, cv_degree)
        cmds.setAttr(curve1+".rotateZ", 45)
        return self.combine_curves([curve1])
