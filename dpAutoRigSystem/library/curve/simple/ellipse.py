# importing libraries:
from ...base import curve

# global variables to this module:    
CLASS_NAME = "Ellipse"
TITLE = "m122_ellipse"
DESCRIPTION = "m099_cvControlDesc"



class Ellipse(curve.BaseCurve):
    def __init__(self, ar):
        curve.BaseCurve.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, None)
    
    
    def cv_main(self, use_ui, cv_id=None, cv_name=CLASS_NAME+'_Ctrl', cv_size=1.0, cv_degree=1, cv_direction='+Y', cv_rot=(0, 0, 0), cv_action=1, guide=False):
        """ The principal method to call all other methods in order to build the create_controller curve.
            Return the result: new control curve or the destination list depending of action.
        """
        return self.cv_create(use_ui, cv_id, cv_name, cv_size, cv_degree, cv_direction, cv_rot, cv_action, guide)
        
    
    def get_linear_points(self):
        """ Get a list of linear points for this kind of control curve.
            Set class object variables cv_points, cvKnotList and cv_periodic.
        """
        r = self.cv_size
        self.cv_points = [(0.784*r, 0.47*r, 0), (0, 0.665*r, 0), (-0.784*r, 0.47*r, 0), (-1.108*r, 0, 0), (-0.784*r, -0.47*r, 0),
                            (0, -0.665*r, 0), (0.784*r, -0.47*r, 0), (1.108*r, 0, 0), (0.784*r, 0.47*r, 0)]
        self.cv_knots = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.cv_periodic = True #closed
    
    
    def get_cubic_points(self):
        """ Get a list of cubic points for this kind of control curve.
            Set class object variables cv_points, cvKnotList and cv_periodic.
        """
        r = self.cv_size
        self.cv_points = [(0.784*r, 0.47*r, 0), (0, 0.665*r, 0), (-0.784*r, 0.47*r, 0), (-1.108*r, 0, 0), (-0.784*r, -0.47*r, 0),
                            (0, -0.665*r, 0), (0.784*r, -0.47*r, 0), (1.108*r, 0, 0), (0.784*r, 0.47*r, 0), (0, 0.665*r, 0), (-0.784*r, 0.47*r, 0)]
        self.cv_knots = [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        self.cv_periodic = True #closed
